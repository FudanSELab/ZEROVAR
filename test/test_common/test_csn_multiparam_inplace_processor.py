from common.dataprocessor.csn_multi_param_in_place_processor import CSN_Multiparam_Inplace_Processor
from common.database import Database

if __name__ == "__main__":
    preprocessor = CSN_Multiparam_Inplace_Processor()
    db: Database = Database(preprocessor)

    src_path = "/home/fdse/Data/CodeSearchNet/resources/data/java/final/jsonl/test"
    output_path = "data/database/csn_multiparam_inplace_database.pkl"
    db.generate_database(src_path, output_path)

    db2 = Database.load(output_path)
    for example in db2[:1]:
        print(example)