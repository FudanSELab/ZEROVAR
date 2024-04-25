# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.


import re
import torch
import torch.nn as nn
from transformers import RobertaTokenizer, RobertaModel, RobertaConfig, T5ForConditionalGeneration

class UniXcoder(nn.Module):
    def __init__(self, model_name):
        """
            Build UniXcoder.

            Parameters:

            * `model_name`- huggingface model card name. e.g. microsoft/unixcoder-base
        """
        super(UniXcoder, self).__init__()
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.config = RobertaConfig.from_pretrained(model_name)
        self.config.is_decoder = True
        self.model = RobertaModel.from_pretrained(model_name, config=self.config)

        self.register_buffer("bias", torch.tril(torch.ones((1024, 1024), dtype=torch.uint8)).view(1,1024, 1024))
        self.lm_head = nn.Linear(self.config.hidden_size, self.config.vocab_size, bias=False)
        self.lm_head.weight = self.model.embeddings.word_embeddings.weight
        self.lsm = nn.LogSoftmax(dim=-1)

        self.tokenizer.add_tokens(["<mask0>"],special_tokens=True)

    def tokenize(self, inputs, mode="<encoder-only>", max_length=512, padding=False):
        """
        Convert string to token ids

        Parameters:

        * `inputs`- list of input strings.
        * `max_length`- The maximum total source sequence length after tokenization.
        * `padding`- whether to pad source sequence length to max_length.
        * `mode`- which mode the sequence will use. i.e. <encoder-only>, <decoder-only>, <encoder-decoder>
        """
        assert mode in ["<encoder-only>", "<decoder-only>", "<encoder-decoder>"]

        tokenizer = self.tokenizer

        tokens_ids = []
        for x in inputs:
            tokens = tokenizer.tokenize(x)
            if mode == "<encoder-only>":
                tokens = tokens[:max_length-4]
                tokens = [tokenizer.cls_token,mode,tokenizer.sep_token] + tokens + [tokenizer.sep_token]
            elif mode == "<decoder-only>":
                tokens = tokens[-(max_length-3):]
                tokens = [tokenizer.cls_token,mode,tokenizer.sep_token] + tokens
            else:
                tokens = tokens[:max_length-5]
                tokens = [tokenizer.cls_token,mode,tokenizer.sep_token] + tokens + [tokenizer.sep_token]

            tokens_id = tokenizer.convert_tokens_to_ids(tokens)
            if padding:
                tokens_id = tokens_id + [self.config.pad_token_id] * (max_length-len(tokens_id))
            tokens_ids.append(tokens_id)
        return tokens_ids

    def decode(self, source_ids):
        """ Convert token ids to string """
        predictions = []
        for x in source_ids:
            prediction = []
            for y in x:
                t = y.cpu().numpy()
                t = list(t)
                if 0 in t:
                    t = t[:t.index(0)]
                text = self.tokenizer.decode(t,clean_up_tokenization_spaces=False)
                prediction.append(text)
            predictions.append(prediction)
        return predictions

    def forward(self, source_ids):
        """ Obtain token embeddings and sentence embeddings """
        mask = source_ids.ne(self.config.pad_token_id)
        token_embeddings = self.model(source_ids,attention_mask = mask.unsqueeze(1) * mask.unsqueeze(2))[0]
        sentence_embeddings = (token_embeddings * mask.unsqueeze(-1)).sum(1) / mask.sum(-1).unsqueeze(-1)
        return token_embeddings, sentence_embeddings

    def generate(self, source_ids, decoder_only = True, eos_id = None, beam_size = 5, max_length = 64):
        """ Generate sequence given context (source_ids) """

        # Set encoder mask attention matrix: bidirectional for <encoder-decoder>, unirectional for <decoder-only>
        if decoder_only:
            mask = self.bias[:,:source_ids.size(-1),:source_ids.size(-1)]
        else:
            mask = source_ids.ne(self.config.pad_token_id)
            mask = mask.unsqueeze(1) * mask.unsqueeze(2)

        if eos_id is None:
            eos_id = self.config.eos_token_id

        device = source_ids.device

        # Decoding using beam search
        preds = []
        zero = torch.LongTensor(1).fill_(0).to(device)
        source_len = list(source_ids.ne(1).sum(-1).cpu().numpy())
        length = source_ids.size(-1)
        encoder_output = self.model(source_ids,attention_mask=mask)
        for i in range(source_ids.shape[0]):
            context = [[x[i:i+1,:,:source_len[i]].repeat(beam_size,1,1,1) for x in y]
                     for y in encoder_output.past_key_values]
            beam = Beam(beam_size,eos_id,device)
            input_ids = beam.getCurrentState().clone()
            context_ids = source_ids[i:i+1,:source_len[i]].repeat(beam_size,1)
            out = encoder_output.last_hidden_state[i:i+1,:source_len[i]].repeat(beam_size,1,1)
            for _ in range(max_length):
                if beam.done():
                    break
                if _ == 0:
                    hidden_states = out[:,-1,:]
                    out = self.lsm(self.lm_head(hidden_states)).data
                    beam.advance(out)
                    input_ids.data.copy_(input_ids.data.index_select(0, beam.getCurrentOrigin()))
                    input_ids = beam.getCurrentState().clone()
                else:
                    length = context_ids.size(-1)+input_ids.size(-1)
                    out = self.model(input_ids,attention_mask=self.bias[:,context_ids.size(-1):length,:length],
                                       past_key_values=context).last_hidden_state
                    hidden_states = out[:,-1,:]
                    out = self.lsm(self.lm_head(hidden_states)).data
                    beam.advance(out)
                    input_ids.data.copy_(input_ids.data.index_select(0, beam.getCurrentOrigin()))
                    input_ids = torch.cat((input_ids,beam.getCurrentState().clone()),-1)
            hyp = beam.getHyp(beam.getFinal())
            pred = beam.buildTargetTokens(hyp)[:beam_size]
            pred = [torch.cat([x.view(-1) for x in p]+[zero]*(max_length-len(p))).view(1,-1) for p in pred]
            preds.append(torch.cat(pred,0).unsqueeze(0))

        preds = torch.cat(preds,0)

        return preds



class Beam(object):
    def __init__(self, size, eos, device):
        self.size = size
        self.device = device
        # The score for each translation on the beam.
        self.scores = torch.FloatTensor(size).zero_().to(device)
        # The backpointers at each time-step.
        self.prevKs = []
        # The outputs at each time-step.
        self.nextYs = [torch.LongTensor(size).fill_(0).to(device)]
        # Has EOS topped the beam yet.
        self._eos = eos
        self.eosTop = False
        # Time and k pair for finished.
        self.finished = []

    def getCurrentState(self):
        "Get the outputs for the current timestep."
        batch = self.nextYs[-1].view(-1, 1)
        return batch

    def getCurrentOrigin(self):
        "Get the backpointers for the current timestep."
        return self.prevKs[-1]

    def advance(self, wordLk):
        """
        Given prob over words for every last beam `wordLk` and attention
        `attnOut`: Compute and update the beam search.

        Parameters:

        * `wordLk`- probs of advancing from the last step (K x words)
        * `attnOut`- attention at the last step

        Returns: True if beam search is complete.
        """
        numWords = wordLk.size(1)

        # Sum the previous scores.
        if len(self.prevKs) > 0:
            beamLk = wordLk + self.scores.unsqueeze(1).expand_as(wordLk)

            # Don't let EOS have children.
            for i in range(self.nextYs[-1].size(0)):
                if self.nextYs[-1][i] == self._eos:
                    beamLk[i] = -1e20
        else:
            beamLk = wordLk[0]
        flatBeamLk = beamLk.view(-1)
        bestScores, bestScoresId = flatBeamLk.topk(self.size, 0, True, True)

        self.scores = bestScores

        # bestScoresId is flattened beam x word array, so calculate which
        # word and beam each score came from
        prevK = bestScoresId // numWords
        self.prevKs.append(prevK)
        self.nextYs.append((bestScoresId - prevK * numWords))


        for i in range(self.nextYs[-1].size(0)):
            if self.nextYs[-1][i] == self._eos:
                s = self.scores[i]
                self.finished.append((s, len(self.nextYs) - 1, i))

        # End condition is when top-of-beam is EOS and no global score.
        if self.nextYs[-1][0] == self._eos:
            self.eosTop = True

    def done(self):
        return self.eosTop and len(self.finished) >= self.size

    def getFinal(self):
        if len(self.finished) == 0:
            self.finished.append((self.scores[0], len(self.nextYs) - 1, 0))
        self.finished.sort(key=lambda a: -a[0])
        if len(self.finished) != self.size:
            unfinished=[]
            for i in range(self.nextYs[-1].size(0)):
                if self.nextYs[-1][i] != self._eos:
                    s = self.scores[i]
                    unfinished.append((s, len(self.nextYs) - 1, i))
            unfinished.sort(key=lambda a: -a[0])
            self.finished+=unfinished[:self.size-len(self.finished)]
        return self.finished[:self.size]

    def getHyp(self, beam_res):
        """
        Walk back to construct the full hypothesis.
        """
        hyps=[]
        for _,timestep, k in beam_res:
            hyp = []
            for j in range(len(self.prevKs[:timestep]) - 1, -1, -1):
                hyp.append(self.nextYs[j+1][k])
                k = self.prevKs[j][k]
            hyps.append(hyp[::-1])
        return hyps

    def buildTargetTokens(self, preds):
        sentence=[]
        for pred in preds:
            tokens = []
            for tok in pred:
                if tok==self._eos:
                    break
                tokens.append(tok)
            sentence.append(tokens)
        return sentence


class HybirdVarExplainer:
    def __init__(self, device="cpu", prompt_checkpoint=None, explain_checkpoint=None):
        # super(HybirdVarExplainer, self).__init__()
        self.device = torch.device(device)
        self.prompt_model = UniXcoder("microsoft/unixcoder-base")
        if prompt_checkpoint:
            self.prompt_model.load_state_dict(torch.load(prompt_checkpoint, map_location=self.device))
        self.prompt_model.to(self.device)
        self.prompt_model.eval()

        self.explain_model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base')
        if explain_checkpoint:
            self.explain_model.load_state_dict(torch.load(explain_checkpoint, map_location=self.device))
        self.explain_tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
        self.explain_model.to(self.device)
        self.explain_model.eval()

    def explain(self, methods: list, vars_list: list, docstrings=None,  prompt_num=3, cand_num=10) -> dict:
        '''
            给不带注释的数据生成参数解释
        '''
        if not isinstance(methods, (list, tuple)):
            methods = [methods]
            vars_list = [vars_list]
            if docstrings is not None:
                docstrings = [docstrings]
        if docstrings is not None:
            prompt_templates_list = [[docstring] for docstring in docstrings]
        else:
            prompt_templates_list = self.generate_prompt_templates(methods, prompt_num=prompt_num)

        explanations_list = self.explain_for_vars(methods, vars_list, prompt_templates_list, cand_num)
        return prompt_templates_list, explanations_list

    def filter_exps_for_var(self, var: str, exps: list):
        article_pattern = re.compile(r"^(the|The|a|A|an|An) ")
        exps = [article_pattern.sub("", exp) for exp in exps]
        exps = [exp for exp in exps if exp != var and not exp.startswith("@")]
        return exps

    def generate_prompt_templates(self, methods:str, prompt_num=3) -> list:
        with torch.no_grad():
            tokens_ids = self.prompt_model.tokenize(["<mask0>\n" + method for method in methods], max_length=512, mode="<encoder-decoder>", padding=True)
            source_ids = torch.tensor(tokens_ids).to(self.device)
            prediction_ids = self.prompt_model.generate(source_ids, decoder_only=False, beam_size=prompt_num, max_length=128)
            predictions = self.prompt_model.decode(prediction_ids)
            prompt_templates = [[p.replace("<mask0>","").strip() for p in pred] for pred in predictions]
            # remove the meta character '%' in templates
            # prompt_templates = [[p.replace("%","%%").strip() for p in temps] for temps in prompt_templates]
            # prompt_templates = [[p + f"\n@param %s {PLACEHOLDER}.\n" for p in temps] for temps in prompt_templates]
        return prompt_templates

    def explain_for_vars(self, methods: str, vars_list: list, prompt_templates_list: list, cand_num=10, batch_size=32) -> list:
        inputs = []
        for method, vars, prompt_templates in zip(methods, vars_list, prompt_templates_list):
            for var in vars:
                for template in prompt_templates:
                    prompt = template + f"\n@param {var} <extra_id_0>.\n"
                    inputs.append(prompt + "\n" + method)

        outputs = []
        with torch.no_grad():
            for beg, end in zip(range(0, len(inputs), batch_size), range(batch_size, len(inputs)+batch_size, batch_size)):
                batch = inputs[beg:end]
                input_ids = self.explain_tokenizer(batch, return_tensors="pt", padding=True, truncation=True).input_ids
                input_ids = input_ids.to(self.device)
                generated_ids = self.explain_model.generate(input_ids, max_length=16, num_beams=cand_num, num_return_sequences=cand_num)

                generated_ids = generated_ids.reshape(len(batch), cand_num, generated_ids.shape[-1])
                batch_results = [[self.explain_tokenizer.decode(ids, skip_special_tokens=True) for ids in beams] for beams in generated_ids]
                outputs.extend(batch_results)

        explanations_list = []
        idx = 0
        for vars,prompt_templates in zip(vars_list, prompt_templates_list):
            method_exps = []
            for var in vars:
                template_dict = dict()
                for template in prompt_templates:
                    template_dict[template] = outputs[idx]
                    idx += 1
                method_exps.append(template_dict)
            explanations_list.append(method_exps)
        return explanations_list