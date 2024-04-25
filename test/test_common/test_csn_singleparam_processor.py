from common.dataprocessor.csn_single_param_processor import CSNParamProcessor
from common.database import Database

if __name__ == "__main__":
    preprocessor = CSNParamProcessor()
    db: Database = Database(preprocessor)

    src_path = "/home/fdse/Data/CodeSearchNet/resources/data/java/final/jsonl/test"
    output_path = "data/database/csn_database2.pkl"
    db.generate_database(src_path, output_path)

    db2 = Database.load(output_path)
    for example in db2[:1]:
        print(example)