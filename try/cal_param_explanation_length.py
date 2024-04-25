import jsonlines
from itertools import groupby
import pickle

from common.config import DATABASE_PATH
from common.database import Database
from common.example import CSNExample

data_file = DATABASE_PATH["csn_single_param"]["test"]

with open(data_file, "rb") as f:
    db = pickle.load(f)

lst = []
for i in db:
    lst.append(len(i.explanation))

for k,g in groupby(sorted(lst),key=lambda x:x//10):
    print('{}-{}:{}'.format(k*10,(k+1)*10-1,len(list(g))))