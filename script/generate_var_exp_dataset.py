

from var_exp.common.database import Database


if __name__ == '__main__':
    # db = Database()
    # db = Database.load_from_rawdata_json("data/processed_data/processed_java_0_36251080.json")
    # db.save("data/var_exp/database.pkl")

    db = Database.load("data/var_exp/database.pkl")

    for i in db[:100]:
        print(i.so_id)
        print(i.vars)
        print(i.method)
    