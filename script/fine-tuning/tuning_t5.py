import time

from common.config import DATABASE_PATH, DATABASE_TYPES
from common.database import Database
from finetuning.codet5_tuning import CodeT5Tuning
from finetuning.config import CodeT5Config

if __name__ == "__main__":
    # config = CodeT5Config(
    #     save_dir="data/param_exp_tuning/",
    #     train_batch_size=5,
    #     valid_batch_size=5
    # )

    # model = CodeT5Tuning(config)
    # model.init_model()

    # 指明用以训练的数据库类型
    database_type = "csn_single_param"
    assert database_type in DATABASE_TYPES, "wrong database type"

    train_data_path = DATABASE_PATH[database_type]["train"]
    valid_data_path = DATABASE_PATH[database_type]["valid"]
    train_database = Database.load(train_data_path)
    print(len(train_database))
    # valid_database = Database.load(valid_data_path)

    # model.train(train_database, valid_database, database_type)