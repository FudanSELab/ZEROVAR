import os
a = "./test_mk/a.txt"
if not os.path.exists(a):
    os.makedirs(a)