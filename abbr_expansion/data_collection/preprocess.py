import pickle
import json
import re
from guesslang import Guess
from tqdm import tqdm

def load(so_file_path):
    with open(so_file_path, 'rb') as f:
        return pickle.load(f)

def judge_codelang(code:str, lang:str):
    """
    传入一段字符串类型的代码，以及期望语言，判断出该代码是否为要求的语言的代码
    使用guesslang实现，不一定准确，只有当代码多的时候才能判断得比较准
    """
    lang = lang.lower()
    assert(lang in ["java", "python", "C", "SQL"]), f"不存在的编程语言类型：{lang}"
    langname = Guess().language_name(code)
    if langname:
        return langname.lower() == lang
    return False

def preprocess_rawSO(corrupted_num=-1, jsonpath="./data/post_data/java_0_3038417.json", processed_jsonpath="./data/post_data/processed_java_0_3038417.json"):
    """
    将用pymysql提取出来的SO的原始json数据处理为code2text的形式
    corrupted_num: 程序上一次被中断时跑到的数据条数，默认为-1，即完全重新跑，可以从第一条json对象开始处理。
    例如，若上一次运行数据处理程序到第197403条数据时，程序被杀死。此时需要从197403开始往后继续处理数据，则设置corrupted_num为197403即可
    """ 
    
    """
    按照so id对应到文本，再对应到一个帖子文本context对应的多个代码
    例如：{
        "12345":{
            "text": "which goes against what I was taught",
            "code": ["import com.bean", "public static void main", "System.out.println()"]
        }
    }
    """
    with open(jsonpath, 'r') as f:
        with open(processed_jsonpath, 'a') as f2:
            raw_data = json.load(f)   #读出来的raw_data就是一个包含多个dict的列表
            indexnum = 0   #之前在197403断了，需要继续处理
            for sopost in tqdm(raw_data):
                if indexnum > corrupted_num:
                    id2text2code = {}
                    body = sopost["Body"]   #未处理的帖子主题，需要从里面提取出来文本和代码
                    body = body.replace("&#xA;",'')
                    
                    #获取生代码，并删除掉所有<pre><code>代码框
                    precode_pattern = r'<pre><code>(.*?)</code></pre>'
                    raw_code_list = re.findall(precode_pattern, body)
                    
                    delcode_pattern = r'(<pre><code>.*?</code></pre>)'
                    raw_context = re.sub(delcode_pattern, '', body)   
                    
                    
                    #匹配并删除行内代码
                    codeline_pattern = r'(<code>.*?</code>)'  
                    raw_context = re.sub(codeline_pattern, '', raw_context)
                    
                    #删除文本内的超链接
                    text_pattern = r'(<a href.*?>.*?</a>)'  
                    raw_context = re.sub(text_pattern, '', raw_context)
                    
                    #去掉文本<p>内的脏标签
                    raw_context = raw_context.replace('<em>','')   
                    raw_context = raw_context.replace('</em>','')
                    raw_context = raw_context.replace('<strong>','')   
                    raw_context = raw_context.replace('</strong>','')
                    raw_context = raw_context.replace('<br>','')
                    
                    #提取出完整文本
                    cook_pattern = r'<p>(.*?)</p>' 
                    cooked_context_list = re.findall(cook_pattern, raw_context)
                    full_context = " ".join(cooked_context_list)
                    
                    #去掉完整文本中的连续的空白字符
                    empty_pattern = r'(\s\s+)'
                    full_context = re.sub(empty_pattern, ' ', full_context)
                    
                    #去掉完整文本中的特殊符号，如连续的句点和横杠
                    empty_pattern = r'(\.\.+)'
                    full_context = re.sub(empty_pattern, '.', full_context) 
                    empty_pattern = r'(\-\-+)'
                    pure_context = re.sub(empty_pattern, '', full_context)  #最终过滤好的文本
                    
                    if len(raw_code_list) == 0:   #不存在代码块的，直接筛除
                        continue
                    postid = sopost["Id"]
                    id2text2code[postid] = {
                        "text": "",
                        "code": []
                    }
                    for code in raw_code_list:
                        if code and judge_codelang(code, "java"):  #如果为java代码，那么就加入id2text2code字典
                            id2text2code[postid]["text"] = pure_context
                            id2text2code[postid]["code"].append(code)
                    if not id2text2code[postid]["text"] == "" and not len(id2text2code[postid]["code"])==0:
                        res = str(id2text2code)
                        f2.write(f"{res}\n")
                
                indexnum += 1