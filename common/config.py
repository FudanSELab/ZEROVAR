'''
    项目里的常数设置
'''

# 参数解释位置的占位符
PLACEHOLDER = "[param explanation]"

# 从javadoc中提取参数及其解释的正则表达式
PARAM_EXP_PATTERN = r'@param (\S+)\s([A-Za-z_\s\p{P}|^$~`+=<>]*?)(?=\n@|$)'

# CodeSearchNet数据所在目录
CSN_DATA_DIR = "/home/fdse/Data/CodeSearchNet/resources/data/java/final/jsonl/"

# checkpoint所在目录
CHECKPOINT_DIR = "data/param_exp_tuning"

# 封装好的数据库所在目录
__DATABASE_DIR = "data/database/"
DATABASE_TYPES = ["csn_single_param", "csn_multi_param_in_place",
                 "csn_multi_param_at_end","so", "vars_in_method"]
__DATA_TYPES = ["train", "test", "valid"]
DATABASE_PATH = { name: {data_type: __DATABASE_DIR + name + "/" + data_type + ".pkl"
                        for data_type in __DATA_TYPES}
                    for name in DATABASE_TYPES }

# 数据预处理器相关
PROCESSOR_IMPORT_PATH = "common.dataprocessor"
PROCESSOR_CLASS_NAMES = ["CSNParamProcessor", "CSNMultiparamInplaceProcessor",
                         "CSNMultiparamAtEndProcessor", "SOProcessor", "VarsInMethodProcessor"]
DATABASE_TO_PROCESSOR = {DATABASE_TYPES[i]: PROCESSOR_CLASS_NAMES[i]
                            for i in range(len(DATABASE_TYPES))}
