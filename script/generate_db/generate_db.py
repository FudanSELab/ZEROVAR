from py import process
from common.database import Database
from common.dataprocessor.dataprocessor_factory import DataProcessorFactory
from common.config import DATABASE_PATH, CSN_DATA_DIR, DATABASE_TYPES


if __name__ == "__main__":
    # tmp op
    src_path = "data/database/codesearch/IR_NEW/java_test_new.jsonl"
    processor = DataProcessorFactory.get_processor("vars_in_method")
    output_path = "data/database/codesearch/IR_NEW/csn_test_db.pkl"
    if processor:
        db: Database = Database(processor)
        db.generate_database(src_path, output_path)

    # origin op
    # 使用database_type指定生成的数据库，注意与comon.config里列举的一致
    # database_type = "vars_in_method"
    # assert database_type in DATABASE_TYPES, "wrong database type"

    # target_types = ["train", "valid", "test"]
    # for target_type in target_types:
    #     src_path = CSN_DATA_DIR + target_type
    #     output_path = DATABASE_PATH[database_type][target_type]
    #     processor = DataProcessorFactory.get_processor(database_type)
    #     if processor:
    #         db: Database = Database(processor)
    #         db.generate_database(src_path, output_path)

    # 查看生成效果
    db2 = Database.load(output_path)
    for i in db2[:1]:
        print(i)