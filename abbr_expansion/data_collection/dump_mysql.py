import pymysql
from pymysql import cursors
import json
from tqdm import tqdm


class RemoteMYSQL:
    HOST = '47.116.194.87'
    PORT = 3306
    USERNAME = 'root'
    PASSWORD = 'Cloudfdse2022+'


def save_data(jsonfilepath="./sofile.json", data=[]):
    with open(jsonfilepath, 'w') as f:
        json.dump(data, f, indent=4)

def language_filter(tags:str):
    """
        输入so tag,判断该帖子是否是java相关代码
    """
    java_feature = ["<java>"]    #找与java相关的标签, 暂时只考虑java, 也可以加入<spring>等
    for feat in java_feature:
        if feat in tags:
            return True
    return False

def get_so_posts(language, begin_id: int, count: int = 0, save_dir="./"):
    """
    so数据库总共约58,000,000条数据
    :param language:
    :param begin_id:
    :param count
    :return:
    """
    total = 100000 if count == 0 else count
    res = []
    connect = pymysql.connect(
        host=RemoteMYSQL.HOST, user=RemoteMYSQL.USERNAME, password=RemoteMYSQL.PASSWORD, db='stackoverflow_2021'
    )
    cursor = connect.cursor(cursor=cursors.SSDictCursor)
    sql = """SELECT Id, Score, Title, Body, Tags FROM posts WHERE Id>%d AND PostTypeId=1 AND Tags LIKE %s""" \
          % (begin_id, '"%<' + language + '>%"')
    print(sql)
    if count > 0:
        sql = sql + f'LIMIT {count}'
    cursor.execute(sql)
    pbar = tqdm(total=total)
    end_id = 0
    num = 0
    while True:
        so_post = cursor.fetchone()
        if not so_post:
            break
        pbar.update(1)
        res.append({
            "Id": so_post['Id'],
            "Score": so_post['Score'],
            "Title": so_post['Title'],
            "Body": so_post['Body'],
            "Tags": so_post['Tags']
        })
        num += 1
        end_id = so_post['Id']
        if num % total != 0:
            continue
        pbar.close()
        save_fname = f'{language}_{begin_id}_{end_id}.json'   #要保存的文件名
        save_data(f'{save_dir}/{save_fname}', res)
        begin_id = end_id
        res = []
        if num < count or count == 0:
            pbar = tqdm(total=total)
    pbar.close()
    if res:
        save_fname = f'{language}_{begin_id}_{end_id}.json'  
        save_data(f'{save_dir}/{save_fname}', res)
    cursor.close()
    connect.close()
    return save_fname   #返回文件名方便保存


