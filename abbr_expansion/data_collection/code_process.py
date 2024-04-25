from codetoolkit.delimiter import Delimiter
from codetoolkit.javalang.parse import parse
import codetoolkit
from codetoolkit.javalang.tree import *
from codetoolkit.delimiter import Delimiter
from codetoolkit.code_pos import CodePOS
from nltk.util import ngrams
from nltk.corpus import stopwords
import spacy
from codetoolkit.pair_checker import PairChecker
import re
from tqdm import tqdm


def segName2NgramWord(segmented_name, mode="code"):
        """
            输入分词后用空格分隔的变量名segmented_name，返回其按每个ngram合并的字符串列表。该ngram列表按照ngram的长度排序。
            例如:输入"lum R", 返回['lum r', 'lum', 'r']。一律小写。
            :param segmented_name:
                是用空格分隔的词语，例如"get Element By Id"
            :param mode:
                选择处理的ngram是code的还是text的，如果是text，ngram的N会取得大一些。
            :return ngramList:
                由ngram中每个gram内的各个字符串拼接成的字符串列表
                例如对于上述"get Element By Id"输入，
                输出['get element by id', 'get element by', 'element by id', 'get element', 'element by', 'by id', 'get', 'element', 'by', 'id']
        """
        ngramList = []
        segNameList = segmented_name.split()
        segNameCount = len(segNameList)
        
        gram_N = segNameCount if mode == "code" else 20   #设置ngram的最长长度，代码默认按分词长度，文本按最长20
        
        for i in range(gram_N, 0, -1): 
          #每轮循环取出当前按长度为n切分的ngram，n为从大到小输出，长的ngram在前面
            for eachgram in list(ngrams(segNameList,i)):     #eachgram是tuple类型的序列,例如("hello","who","you"),是具体的每个gram
                selectName = " ".join([str(word) for word in eachgram])    #将该gram的内容合并起来组合成一个词语，便于匹配文本中的变量名
                ngramList.append(selectName)
        return ngramList

    
def lemmatize(keyword, lemmatizer=spacy.load("en_core_web_sm", disable=["parser", "ner"])):
    """
        **调用时需要传入一个词形还原器**，如下：
        lemmatizer = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        
        输入一个包含多个单词的字符串，返回将字符串内所有词都还原为单词原型的字符串
        例如：输入"external files type entries editor"，返回"external file type entry editor"
    """
    return " ".join(token.lemma_.lower() for token in lemmatizer(keyword))

def extractNounFromVarName(segmented_name, code_pos=CodePOS.get_inst()):
        """
            输入Var变量的的名称，返回去掉动词后的名词。如果没有名词，返回的是空串。
            :param segmented_name:
                对应node的segmented_name
            :return results:
                返回去掉动词后的变量名（空格分隔）
        """
        results = list()
        queue = list()
        _method_name = Delimiter.split_camel(segmented_name)  #？
        for word, pos in code_pos(_method_name):  #pos:词性
            #将方法名中的名词提取出来，在库中进行搜索
            # print(word, pos)
            if pos in {"verb", "closedlist", "adv"}:
                if pos == "verb":
                    lemma = lemmatize(word)   #词的还原形式
                if len(queue) == 0:
                    continue
                noun = " ".join(queue)
                lemma = lemmatize(noun)
                queue.clear()
                results.append(noun)
                results.append(lemma)
            else:
                queue.append(word)
        if len(queue) > 0:
            noun = " ".join(queue)
            lemma = lemmatize(noun)
            results.append(noun)   
            results.append(lemma)#名词和其还原形式都应当在库中进行分别搜索，先搜索noun的位词，没有的话再搜索lemma的位词
        return " ".join(list(set(results)))

def unify_so_snippet(method):    #处理java代码为可解析的形式，如果不可解析，返回None。反之，返回可解析的完整代码。
    '''code: input a method or a class or code snippet ->
    a class header added and extracted by extractor '''
    try:
        ast = parse(method)
        for _, node in ast:
            #如果本身已经是类了，则直接返回源代码即可
            if isinstance(node, codetoolkit.javalang.tree.ClassDeclaration):    
                return method
    except Exception:
        try: 
            ast = parse(f"public class Foo {{{method}}}")
        except:
            try:
                #如果加了类和方法头还报错, 就返回None说明代码有问题, 处理不了, 返回None
                ast = parse(f"public class Foo {{ public void foo(){{{method}}} }}")   
            except:
                return None
            return f"public class Foo {{ public void foo(){{{method}}} }}"
        return f"public class Foo {{{method}}}"

def get_all_variables(code):
    """
        如果代码有问题，返回None。
        如果代码正常可解析，返回局部变量和变量引用的名字的列表
    """
    code = unify_so_snippet(code)
    declarator_set = set()
    member_reference_set = set()
    if code == None:
    #    print("Code Error!")
        return None, None
    ast = parse(code)
    #print("co de good!")
    for _, declaration_node in ast.filter(LocalVariableDeclaration):
        for declarator in declaration_node.declarators:
            declarator_set.add(declarator.name)  #使用set去重得到不重复的完整变量集合
    # TODO declarator.name就是局部变量的名字
    for _, mf in ast.filter(MemberReference):
        # TODO mf.member 就是变量引用的名字
        member_reference_set.add(mf.member)
    return list(declarator_set), list(member_reference_set)

def del_stop_words(segmented_words):
    """
    传入按空格分隔的sentence（多个单词按空格分隔，例如'my own data'这种）
    输出去除掉首尾停用词后的新的sentence。
    注意：只是如果第一个或者最后一个词为停用词，才去掉。即只去掉首尾停用词。
    """
    segmented_words = re.sub('[^ a-zA-Z0-9]', '', segmented_words.lower())  #去掉除字母和空格数字外的所有字符
    #改：特殊字符跳过
    words_list = segmented_words.split()
    if len(words_list) > 0 and words_list[0] in stopwords.words():
        words_list.pop(0)
    if len(words_list) > 0 and words_list[-1] in stopwords.words():
        words_list.pop(-1)
    return " ".join(words_list)

def get_variable_ngram(var_name):
    """
        传入变量名，返回按变量名的ngram生成的所有变量名排列组合。
        可以只考虑名词以及名词别名，不考虑动词。但目前不作此区分，直接处理变量名分词和Ngram
    """
    var_name = Delimiter.split_camel(var_name)
    #抽取变量中的名词来做ngram
    var_name = extractNounFromVarName(var_name)
    varname_ngramlist = segName2NgramWord(var_name)  #获得按ngram从长到短排列组合的变量名列表
    return varname_ngramlist

def get_text_ngram(text, sentence_breaker=spacy.load("en_core_web_sm")):
    """
        传入一段文本，返回将其所有句子的ngram组合在一起ngram的列表。
        返回的是一整个列表的文本ngram
    """
    #去掉除字母和空格、逗号、句号外的所有字符
    text = re.sub('[^ a-zA-Z,\.]', '', text)  
    
    #使用spacy分句
    sentenced_text = sentence_breaker(text)
    sentenced_text = list(sentenced_text.sents)
    
    #对于每个句子，抽取其ngram
    sentence_ngram = []
    sentence_chunks_set = set()
    
    #提取sentence中的名词短语
    for sentence in sentenced_text:
        sentence_chunks_set = set.union(set(sentence.noun_chunks), sentence_chunks_set)
    sentence_chunks_list = list(sentence_chunks_set)
     
    #只取sentence中的名词短语来做ngram
    for noun_sentence in sentence_chunks_list:
        sent_ngram_list = segName2NgramWord(str(noun_sentence), mode="text")
        sentence_ngram.extend(sent_ngram_list)
    
    #对于所有生成好的ngram，把开头和结尾的停用词去掉。比如the luminance of这个3-gram，去完首尾停用词只剩下luminance
    for index, eachgram in enumerate(sentence_ngram):
        #todo检查特殊字符跳过，dilemeter再次切分
        sentence_ngram[index] = Delimiter.split_camel(del_stop_words(eachgram)) 
    
    return list(set(sentence_ngram))

def add_new_abbr_json(so_id, abbr_type, var_type, text_gram, var_gram, save_path):
    """
    将gram配对结果保存到json文件
    so_id：so帖子的id
    abbr_type:缩写类型，可选是var是text中gram的缩写，还是text是var中gram的缩写
    var_type:变量类型，可选本地变量local_var或变量引用member_ref。如果两者合并了不用分，就填var即可。
    text_gram:字符串类型的文本的gram，词与词之间有空格分隔。例如：otherwise leave the XML as
    var_gram：字符串类型的变量名的gram，词与词之间有空格分隔。
    save_path：保存路径，默认与check_so_abbr的保持一致
    """
    res = {
        "so_id": so_id,
        "abbr_type": abbr_type,
        "var_type": var_type,
        "text_gram": text_gram,
        "var_gram": var_gram
    }
    res = str(res)
    with open(save_path, 'a') as f:
        f.write(f"{res}\n")

def check_so_abbr(processed_filepath="/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/data/processed_data/processed_java_0_36251080.json", abbr_pair_filepath="/home/fdse/zoubaihan/CodeCompletion/CodeLM-Prompt/data/abbr_extracted/whole_test_java_0_36251080.json"):
    """
    检查so的text2code文件，匹配每个帖子的文本和代码检查是否存在缩写词对，如果有，将其保存下来
    对应的输入是经过abbr_expansion/data_collection/preprocess.py处理后的文件
    输出的保存路径在CodeLM-Prompt/data/abbr_extracted下
    """
    sentence_breaker = spacy.load("en_core_web_sm")   #分词器
    #需要清洗掉代码和文本中的&gt、&lt、&quot、&amp、<sub>、<sup>、&frasl、连续空格、&nbsp、&mdash等特殊字符
    with open(processed_filepath, 'r') as f1:
        lines = f1.readlines()
        for line in tqdm(lines):
            idx_text_code = eval(line[:-1])
            idx = list(idx_text_code.keys())[0]
            text = idx_text_code[idx]["text"]
            codes = idx_text_code[idx]["code"]
            
            char_need_del_list = ['&gt','&lt','&quot','&amp','<sub>','<sup>','&frasl','&nbsp','&mdash']
            text_ngram_list = get_text_ngram(text, sentence_breaker=sentence_breaker)
            for ch in char_need_del_list:
                text = text.replace(ch, '')
            text = re.sub(r'(\s\s*)', ' ', text)
            for code in codes:
                #清洗特殊字符
                for ch in char_need_del_list:
                    code = code.replace(ch, '')
                
                #获得局部变量名、变量引用名
                localvar_name_list, member_ref_name_list = get_all_variables(code)
                
                if localvar_name_list and member_ref_name_list:
                    localvar_ngram = []
                    for localvar in localvar_name_list:
                        lv_ngram = get_variable_ngram(localvar)  #获得该局部变量的ngram
                        localvar_ngram.extend(lv_ngram)          #整合所有局部变量的ngram
                        #不必考虑lv_ngram为空列表，因为extend不受空列表影响

                    memberref_ngram = []        #获得变量引用的ngram
                    for memberref in member_ref_name_list:
                        mf_ngram = get_variable_ngram(memberref)
                        memberref_ngram.extend(mf_ngram)
                    
                    #将变量引用和所有局部变量的ngram合并
                    localvar_ngram.extend(memberref_ngram)   
                    #去重
                    localvar_ngram = list(set(localvar_ngram))   
                    #按ngram从长到短排序的ngram列表
                    localvar_ngram = sorted(localvar_ngram, key=len, reverse=True)   
                    
                    for text_gram in text_ngram_list:
                        for var_gram in localvar_ngram:
                            #如果text的ngram是var的ngram的全称
                            if text_gram and var_gram:  #gram必须不为空
                                if PairChecker.check_abbr(text_gram, var_gram):
                                    #保存该对应关系到json文件,var2text表示var是text的缩写；text2var表示text是var的缩写
                                    add_new_abbr_json(idx, "var2text", "var", text_gram, var_gram, abbr_pair_filepath)
                                elif PairChecker.check_abbr(var_gram, text_gram):
                                    #text是local_var的缩写
                                    add_new_abbr_json(idx, "text2var", "var", text_gram, var_gram, abbr_pair_filepath) 
                                    
# code = """
# public static void main(String[] args) {
#         int a = 5;
# 		ApplicationContext cxt = new ClassPathXmlApplicationContext("spring.xml");
# 		Student demo = (Student)cxt.getBean("demo");
# 		System.out.println(demo);}
# """
# # get_all_variables(code)
# text = """I have a in java, created with the parser. I want to replace the content of a tag in this with my own data."""
# sentence_breaker=spacy.load("en_core_web_sm")
# sentenced_text = sentence_breaker(text)
# sentenced_text = list(sentenced_text.sents)
# for sentence in sentenced_text:
#     print(str(sentence))
#     print(set(sentence.noun_chunks))
# print(get_text_ngram(text))
#print(PairChecker.check_abbr("a","and"))
# segmented_words = "the luminance of"
# print(get_text_ngram(segmented_words))