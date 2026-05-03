from extractors.base_extractor import BaseExtractor 
import pandas as pd


class Sapo_Extractor(BaseExtractor):
        
    def extract_sapo_json_file(self):
        blob_path = "sapo/"
        list_file_extract = self.list_file(blob_path)
        print(f"Found files: {list_file_extract}")

        data_extract = {} #creat a dict due to there are 2 different data structure
        for i in list_file_extract:

            data = self.extract_json_file(i)
            df = pd.DataFrame(data) #tạo dataframe luôn để giảm memory

            clean_key = i.split('/')[-1].replace('.json.gz','') #làm sạch key để dễ gọi ra sau này
            data_extract[clean_key] = df #gán df vào từng key tránh bị mất

        return data_extract


    def extract_odoo_json_file(self):
        blob_path = "odoo/"
        list_file_extract = self.list_file(blob_path)
        print(f"Found files: {list_file_extract}")

        data_extract = {} #creat a dict due to there are 2 different data structure
        for i in list_file_extract:

            data = self.extract_json_file(i)
            df = pd.DataFrame(data) #tạo dataframe luôn để giảm memory

            clean_key = i.split('/')[-1].replace('.json.gz','') #làm sạch key để dễ gọi ra sau này
            data_extract[clean_key] = df #gán df vào từng key tránh bị mất

        return data_extract

    def extract_online_orders_file(self):
        blob_path = "online_orders/"
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
       


    def extract_locations(self):
        blob_path = r'shared/'
        list_file_in_shared = self.list_file(blob_path) #list all files in "shared" folder
        target_file = [f for f in list_file_in_shared if 'sapo_locations' in f and 'json.gz' in f] #find out the file contains "product"
        print(f"Found files: {target_file}")                   

        data_extract = []

        for i in  target_file:
            data = self.extract_json_file(i)
            if isinstance(data, list):
                 data_extract.extend(data)
            elif isinstance(data, dict):
                data_extract.extend(data.get('id', [data]))

        df = pd.DataFrame(data_extract)

        return df



