from var_exp.pseudo_param.hybird import HybirdVarExplainer
checkpoint = f"data/param_exp_tuning/csn_multi_param_in_place-epoch2-1020-0135.bin"
explainer = HybirdVarExplainer(device="cuda:1", explain_checkpoint=checkpoint)
code = '''
public static void adjustHue(ColorMatrix cm, float value)
{
    value = cleanValue(value, 180f) / 180f * (float) Math.PI;
    if (value == 0)
    {
        return;
    }
    float cosVal = (float) Math.cos(value);
    float sinVal = (float) Math.sin(value);
    float lumR = 0.213f;
    float lumG = 0.715f;
    float lumB = 0.072f;
    float[] mat = new float[]
    { 
            lumR + cosVal * (1 - lumR) + sinVal * (-lumR), lumG + cosVal * (-lumG) + sinVal * (-lumG), lumB + cosVal * (-lumB) + sinVal * (1 - lumB), 0, 0, 
            lumR + cosVal * (-lumR) + sinVal * (0.143f), lumG + cosVal * (1 - lumG) + sinVal * (0.140f), lumB + cosVal * (-lumB) + sinVal * (-0.283f), 0, 0,
            lumR + cosVal * (-lumR) + sinVal * (-(1 - lumR)), lumG + cosVal * (-lumG) + sinVal * (lumG), lumB + cosVal * (1 - lumB) + sinVal * (lumB), 0, 0, 
            0f, 0f, 0f, 1f, 0f, 
            0f, 0f, 0f, 0f, 1f };
    cm.postConcat(new ColorMatrix(mat));
}
'''
methods = [code]
vars_list = [["lumR"]]
prompt_templates_list, explanations_list = explainer.explain(methods, vars_list, prompt_num=1, cand_num=3)
print(explanations_list)
