from common.config import DATABASE_TYPES
from common.dataprocessor.dataprocessor_factory import DataProcessorFactory

for database_type in DATABASE_TYPES:
    a = DataProcessorFactory.get_processor(database_type)
    print(a)

# should be error
try:
    DataProcessorFactory.get_processor("hhh")
except Exception as e:
    print(f"Error: {e}")