from extractors.base_extractor import BaseExtractor 
import pandas as pd
from pandas import json_normalize



class trackingExtractor(BaseExtractor):
    def __init__(self, bucket_name):
        super().__init__(bucket_name)

    def extract_tracking_file(self):
        tracking_blob_path = "cart_tracking/"
        list_file_extract = self.list_file(tracking_blob_path)
        print(f"Found files: {list_file_extract}")

        data_extract = []
        for i in list_file_extract:
            data = self.extract_json_file(i)
            if isinstance(data, list):
                data_extract.extend(data)
            elif isinstance(data, dict):
                data_extract.extend(data.get('id', [data]))

        df = pd.DataFrame(data_extract)

        return df
    
