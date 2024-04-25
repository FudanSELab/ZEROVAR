import sys
sys.path.append('..')
from abbr_expansion.data_collection.preprocess import preprocess_rawSO
from abbr_expansion.data_collection.dump_mysql import get_so_posts
from abbr_expansion.data_collection.code_process import check_so_abbr

if __name__ == "__main__":    
    
    #so下载的json数据的保存路径
    raw_savedir = "/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/data/post_data"
    #预处理后的json数据的保存路径
    processed_savedir = "/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/data/processed_data"
    
    #从so数据库抽取so信息
    #lang = input('Language: ').lower()
    #下载好后的文件名
    #save_fname = get_so_posts(lang, int(input('BEGIN_ID: ')), int(input('COUNT: ')), save_dir=raw_savedir)        
    
    #预处理保存好的数据
    #如果没有跑下载的话，需要自定义下载的so的save_fname
    save_fname = "java_0_36251080.json"
    preprocess_rawSO(corrupted_num=282303,jsonpath=f"{raw_savedir}/{save_fname}", processed_jsonpath=f"{processed_savedir}/processed_{save_fname}")
    #是按行保存的json，读取的时候需要按行读取json对象
    
    # check_so_abbr(processed_filepath="/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/data/processed_data/processed_java_0_36251080.json", abbr_pair_filepath="/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/data/abbr_extracted/whole_test_java_0_36251080.json")