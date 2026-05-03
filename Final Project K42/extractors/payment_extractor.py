from extractors.base_extractor import BaseExtractor 
import pandas as pd

class Payment_Extractor(BaseExtractor):

    def extract_payment_mercury(self):
        blob_path = "mercury/"
        list_file_extract = self.list_file(blob_path)
        print(f"Found file: {list_file_extract}")

        data_extract = {} #creat a dict due to there are 2 different data structure
        for i in list_file_extract:

            data = self.extract_json_file(i)
            df = pd.DataFrame(data) 

            clean_key = i.split('/')[-1].replace('.json.gz','') 
            data_extract[clean_key] = df 

        return data_extract
        
    
    def payment_momo_extract(self):
        "Create extract function for payment gateway: momo"
        blob_path = r'momo/'
        list_file_extract = self.list_file(blob_path)
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
    
    def payment_paypal_extract(self):
        "Create extract function for payment gateway: paypal"
        blob_path = r'paypal/'
        list_file_extract = self.list_file(blob_path)
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
    
    def payment_zalopay_extract(self):
        "Create extract function for payment gateway: zalopay"
        blob_path = r'zalopay/'
        list_file_extract = self.list_file(blob_path)
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
    
