import torch
from transformers import T5ForConditionalGeneration, RobertaTokenizer
from var_exp.pseudo_param.unixcoder import UniXcoder


code = '''/**
* Adjusts the hue of the color matrix.
* 
* @param cm The color matrix to adjust.
* @param value The hue to adjust.
* @param lumR <mask0>.
*/
public void adjustHue(ColorMatrix cm, float value) {
    float cosVal = (float) Math.cos(value);
    float sinVal = (float) Math.sin(value);
    float lumR = 0.213f;
    float lumG = 0.715f;
    float lumB = 0.072f;
    float[] mat = new float[] { 
            lumR + cosVal * (1 - lumR) + sinVal * (-lumR), lumG + cosVal * (-lumG) + sinVal * (-lumG), lumB + cosVal * (-lumB) + sinVal * (1 - lumB), 0, 0, 
            lumR + cosVal * (-lumR) + sinVal * (0.143f), lumG + cosVal * (1 - lumG) + sinVal * (0.140f), lumB + cosVal * (-lumB) + sinVal * (-0.283f), 0, 0,
            lumR + cosVal * (-lumR) + sinVal * (-(1 - lumR)), lumG + cosVal * (-lumG) + sinVal * (lumG), lumB + cosVal * (1 - lumB) + sinVal * (lumB), 0, 0, 
            0f, 0f, 0f, 1f, 0f, 
            0f, 0f, 0f, 0f, 1f 
    };
    cm.postConcat(new ColorMatrix(mat));
}'''

device = torch.device("cuda")
model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base')
tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
model.to(device)

input_ids = tokenizer(code, return_tensors="pt").input_ids
input_ids = input_ids.to(device)
generated_ids = model.generate(input_ids, max_length=128, num_beams=1, num_return_sequences=1)
predictions = [tokenizer.decode(x, skip_special_tokens=True) for x in generated_ids]
print(predictions)

# device = torch.device("cuda")
# model = UniXcoder("microsoft/unixcoder-base")
# model.to(device)

# tokens_ids = model.tokenize(["<mask0>\n" + code],max_length=512,mode="<encoder-decoder>")
# source_ids = torch.tensor(tokens_ids).to(device)
# prediction_ids = model.generate(source_ids, decoder_only=False, beam_size=3, max_length=128)
# predictions = model.decode(prediction_ids)
# print(predictions)