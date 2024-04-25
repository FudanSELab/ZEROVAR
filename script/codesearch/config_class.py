from transformers import RobertaModel,RobertaConfig,RobertaTokenizer

class Config:
    def __init__(self,
                encoder_epoches=4,
                classifier_epoches=3,
                data_path = "data/database/codesearch-new",
                saved_path = "data/codesearchmodel",
                train_batch_size = 8,
                eval_batch_size = 16,
                use_cuda = True,
                max_nl_len=32,
                max_pl_len=480,
                filter_K = 100,
                final_K = 15,
                run_way = 'test',
                confidence = 0.5,
                margin=0.5
                ):
        self.encoder_epoches = encoder_epoches
        self.classifier_epoches=classifier_epoches
        self.data_path = data_path
        self.saved_path = saved_path
        self.train_batch_size = train_batch_size
        self.eval_batch_size = eval_batch_size
        self.use_cuda = use_cuda
        self.max_nl_len = max_nl_len
        self.max_pl_len = max_pl_len
        self.filter_K = filter_K
        self.final_K = final_K
        # self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.test_path = self.data_path+"/origin_data/java_test_1.jsonl"
        self.run_way = run_way
        self.confidence = confidence
        self.margin = margin