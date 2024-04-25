'''
    DataProcessor的简单工厂
'''

from common.config import DATABASE_TO_PROCESSOR, DATABASE_TYPES
from common.dataprocessor.abstract_data_processor import AbstractDataProcessor
from common.dataprocessor.csn_single_param_processor import CSNParamProcessor
from common.dataprocessor.csn_multi_param_at_end_processor import CSNMultiparamAtEndProcessor
from common.dataprocessor.csn_multi_param_in_place_processor import CSNMultiparamInplaceProcessor
from common.dataprocessor.so_processor import SOProcessor
from common.dataprocessor.vars_in_method_processor import VarsInMethodProcessor


class DataProcessorFactory:
    @staticmethod
    def get_processor(database_type: str) -> AbstractDataProcessor:
        '''
            传入的database_type需要属于
        '''
        assert database_type in DATABASE_TYPES, f"{database_type} not in DATABASE_TYPES"

        pakage_name = 'common.dataprocessor'
        pakage = __import__(pakage_name, fromlist=[""])

        module_name = database_type+"_processor"
        module = getattr(pakage, module_name)

        cls_name = getattr(module, DATABASE_TO_PROCESSOR[database_type])
        return cls_name()