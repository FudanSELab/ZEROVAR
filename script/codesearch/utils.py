from config_class import Config
import torch
import math
import numpy as np

# 为了方便处理encoder的数据所使用的数据结构
class InputFeatures(object):
  def __init__(self,nl_tokens,nl_ids,pl_tokens,pl_ids,id):
    self.nl_tokens = nl_tokens
    self.nl_ids = nl_ids
    self.pl_tokens = pl_tokens
    self.pl_ids = pl_ids
    self.id = id

# 为了方便处理simpleclassifier的数据使用的数据结构
class SimpleClassifierFeatures(object):
  def __init__(self,tokens,token_ids,label):
    self.token_ids=token_ids
    self.tokens = tokens
    self.label = label

#
class CasClassifierFeatures:
  def __init__(self,pl_tokens,pl_ids,nl_tokens,nl_ids,label):
    self.pl_tokens = pl_tokens
    self.pl_ids = pl_ids
    self.nl_tokens = nl_tokens
    self.nl_ids = nl_ids
    self.label = label

# 运行整个流程，即进行代码搜索时使用的数据结构
class CodeStruct(object):
  def __init__(self,code_vec,code_tokens,code,no):
    self.code_tokens = code_tokens
    self.code_vec = code_vec
    self.code = code
    self.no = no

# 用来暂时模拟代码库的数据结构，里面存放的是codestruct
class CodeBase(object):
  def __init__(self,code_base):
    self.base_size = len(code_base)
    self.code_base = code_base
    self.code_vecs = self.get_code_vecs()

  def get_code_vecs(self):
    code_vecs = []
    for code in self.code_base:
      code_vecs.append(code.code_vec)
    return torch.tensor(code_vecs)

  def get_code(self,index):
    return self.code_base[index].code

  def get_code_vec(self,index):
    return self.code_base[index].code_vec

  def get_info(self):
    for c in self.code_base:
      print("code:",c.code)


# 把数据转换成模型能够处理的形式
# type=0时转换成encoder使用的形式
# type=1时转换成SimpleClassifier使用的形式
# 其它时候转换成CasClassifer使用的形式
def convert_examples_to_features(js, no, config, res_type, type=0):
  if type==0:
    nl = " ".join(js['original_docstring_tokens'])
    nl_tokens = config.tokenizer.tokenize(nl)
    nl_tokens = nl_tokens[:config.max_seq_length-2]
    nl_tokens = [config.tokenizer.cls_token]+nl_tokens+[config.tokenizer.sep_token]
    nl_ids = config.tokenizer.convert_tokens_to_ids(nl_tokens)
    # 现在nl、pl的padding都在dataloader中使用collate_fn函数进行
    # padding_length = config.max_seq_length - len(nl_ids)
    # nl_ids += [config.tokenizer.pad_token_id]*padding_length

    # 原代码
    if res_type == 'original_code':
        pl = js['original_code']
    # 加入了变量注释的代码
    elif res_type == 'enriched_code':
        pl = js['enriched_code']
    # 加入了方法注释的代码
    elif res_type == 'docstring_original_code':
        pl = js['generated_docstring'] + "\n" + js["original_code"]
    # 同时加入变量注释和方法注释的代码
    else:
        pl = js['generated_docstring'] + "\n" + js["enriched_code"]

    pl_tokens = config.tokenizer.tokenize(pl)
    pl_tokens = pl_tokens[:config.max_seq_length-2]
    pl_tokens = [config.tokenizer.cls_token]+pl_tokens+[config.tokenizer.sep_token]
    pl_ids = config.tokenizer.convert_tokens_to_ids(pl_tokens)
    return InputFeatures(nl_tokens,nl_ids,pl_tokens,pl_ids,no)
  elif type == 1:
    nl = " ".join(js['original_docstring_tokens'])
    nl_tokens = config.tokenizer.tokenize(nl)
    pl = js['code']
    pl_tokens = config.tokenizer.tokenize(pl)
    input_tokens = [config.tokenizer.cls_token]+nl_tokens+[config.tokenizer.sep_token]
    input_tokens += pl_tokens
    input_tokens = input_tokens[:config.max_seq_length-1]
    input_tokens +=[config.tokenizer.sep_token]
    padding_length = config.max_seq_length - len(input_tokens)
    input_tokens += [config.tokenizer.pad_token]*padding_length
    input_ids = config.tokenizer.convert_tokens_to_ids(input_tokens)
    label = js['label']
    return SimpleClassifierFeatures(input_tokens,input_ids,label)
  else:
    nl = " ".join(js['original_docstring_tokens'])
    nl_tokens = config.tokenizer.tokenize(nl)
    nl_tokens = nl_tokens[:config.max_seq_length-2]
    nl_tokens = [config.tokenizer.cls_token]+nl_tokens+[config.tokenizer.sep_token]
    nl_ids = config.tokenizer.convert_tokens_to_ids(nl_tokens)
    padding_length = config.max_seq_length - len(nl_ids)
    nl_ids += [config.tokenizer.pad_token_id]*padding_length

    pl = js['code']
    pl_tokens = config.tokenizer.tokenize(pl)
    pl_tokens = pl_tokens[:config.max_seq_length-2]
    pl_tokens = [config.tokenizer.cls_token]+pl_tokens+[config.tokenizer.sep_token]
    pl_ids = config.tokenizer.convert_tokens_to_ids(pl_tokens)
    padding_length = config.max_seq_length - len(pl_ids)
    pl_ids += [config.tokenizer.pad_token_id]*padding_length
    label = js['label']
    return CasClassifierFeatures(pl_tokens,pl_ids,nl_tokens,nl_ids,label)

def print_features(features):
  for f in features:
    print("idx:{},nl_tokens:{},nl_ids:{},pl_tokens:{},pl_ids:{}".format(f.idx,f.nl_tokens,f.nl_ids,f.pl_tokens,f.pl_ids))


# 计算两个矩阵中向量之间的余弦相似度——返回的scores是一个二维数组，每一行为nl对每个pl的相似度得分
def cos_similarity(mat_a,mat_b):
  scores = torch.matmul(mat_a,mat_b.T)
  # 分别存储a、b矩阵中各个向量的模长
  a_mode = []
  b_mode = []
  # 计算向量的模长并存储起来
  for vec_a in mat_a:
    a_mode.append(math.sqrt(torch.matmul(vec_a,vec_a.T)))
  for vec_b in mat_b:
    b_mode.append(math.sqrt(torch.matmul(vec_b,vec_b.T)))
  for row in range(len(a_mode)):
    for col in range(len(b_mode)):
      scores[row][col] /= a_mode[row]*b_mode[col]
  # print(a_mode)
  # print(b_mode)
  return scores

# 利用编码器输出的向量表示，经相似度计算后获得的一个初步的结果——result返回二维数组，其中每一行为nl对pl的相似度的降序排序
# 其中K表示的是初步选取相似度最高的K个结果
def get_priliminary(score, codebase, config):
  # np.argsort的功能是给一个数组排序，返回排序后的数字对应原来数字所在位置的下标
  # 默认升序排序，这里添加负号即可实现降序
  sort_ids = np.argsort(-score,axis=-1,kind='quicksort',order=None)
  results = []
  for sort_id in sort_ids:
    result = []
    for index in sort_id:
      if len(result)<config.filter_K:
        result.append(codebase.code_base[index])
    results.append(result)
  return results


# 在用快速编码器得到初步的结果之后，用慢速分类器对初步的结果进行re-rank
def rerank(query_tokens,pre_results,classifier,config):
  final = []
  re_scores = np.array([])
  #pre_results会拿到经过encoder的一个初步结果，pre_results是一个列表，每个元素是一个用来表示每条代码段的数据结构（CodeStruct）
  #接下来是用查询的query_tokens和每个pre_result拼在一起送入分类器，判断它们相匹配的概率，并把概率存到re_scores中
  for pr in pre_results:
    code_tokens = pr.code_tokens
    input_tokens = [config.tokenizer.cls_token]+query_tokens+[config.tokenizer.sep_token]
    input_tokens += code_tokens
    input_tokens = input_tokens[:config.max_seq_length-1]
    input_tokens += [config.tokenizer.sep_token]
    padding_length = config.max_seq_length - len(input_tokens)
    input_tokens += padding_length*[config.tokenizer.pad_token]
    input_ids = torch.tensor([config.tokenizer.convert_tokens_to_ids(input_tokens)])
    if config.use_cuda:
      classifier = classifier.cuda()
      input_ids = input_ids.cuda()
    logit = classifier(input_ids)
    probs = torch.reshape(torch.softmax(logit,dim=-1).cpu().detach(),(2,))
    re_scores = np.append(re_scores,probs[1].item())

  #print("预处理结果中与查询匹配的概率：",re_scores)
  script = np.argsort(-re_scores,-1,'quicksort',None)
  #print("预处理结果中按概率降序的下标:",script)
  for i in script:
    if len(final)<config.final_K:
      final.append(pre_results[i])
  return final

# 读取从codebase里获取的结果数组的信息
def get_info(result):
  for res in result:
    print(res.code)