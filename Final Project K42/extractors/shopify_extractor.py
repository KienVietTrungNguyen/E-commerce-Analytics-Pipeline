from base_extractor import BaseExtractor 
import pandas as pd

class Shopify_Extractor(BaseExtractor):
        
    def extract_products(self):
        blob_path = r'shared/'
        list_file_in_shared = self.list_file(blob_path) #list all files in "shared" folder
        target_file = [f for f in list_file_in_shared if 'products' in f and 'json.gz' in f] #find out the file contains "product"
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



    def extract_all_customers_files(self):

        """
        Extract all customers from files in folder shared/customers
        
        """

        blob_path = "shared/customers/"
        files = self.list_file(blob_path)                    
        customers_files = [f for f in files if "customers_batch_" in f]    

        data_extract = []

        for i in customers_files:
            data = self.extract_json_file(i)
            if isinstance(data, list):
                 data_extract.extend(data)
            elif isinstance(data, dict):
                data_extract.extend(data.get('id', [data]))

        df = pd.DataFrame(data_extract)

        return df


    def extract_all_orders_files(self):
        """Extract all orders from files in folder shopify/"""
        blob_path = "shopify/"
        files = self.list_file(blob_path)                    
        order_files = [f for f in files if "orders_batch_" in f]    

        data_extract = []

        for i in order_files:
            data = self.extract_json_file(i)
            if isinstance(data, list):
                 data_extract.extend(data)
            elif isinstance(data, dict):
                data_extract.extend(data.get('id', [data]))
        df = pd.DataFrame(data_extract)
        return df


bucket = 'minpy'

customer = Shopify_Extractor(bucket)
customer_data = customer.extract_all_customers_files()

print(customer_data.info())