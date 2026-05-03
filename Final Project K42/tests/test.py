import os
import sys

# Add project root to path to import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from google.cloud import bigquery
from google.cloud import storage 
from utils.gcs_helper import load_env_variables, get_bigquery_credentials_path, get_gcs_credentials_path

# -------Load environment variables-------
# load_env_variables()
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = get_bigquery_credentials_path()

# def test_bigquery_connection():
#     client = bigquery.Client()
    
#     datasets = list(client.list_datasets())
    
#     if datasets:
#         print(f"✅ KẾT NỐI THÀNH CÔNG! Tìm thấy {len(datasets)} dataset:")
#         for dataset in datasets:
#             print(f"   Dataset ID: {dataset.dataset_id}")
#             print(f"   Dataset: {dataset}")
#     else:
#         print("✅ KẾT NỐI THÀNH CÔNG!")
#         print("   (Tuy nhiên Project này đang trống, chưa có dataset nào)")
    
#     return dataset

# test_bigquery_connection()



# ------Load environment variables------
# load_env_variables()
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = get_gcs_credentials_path()

# def test_connect_gcs():
#     " This function is used to creat connect to GCS and test connection is successfully"
#     client = storage.Client()

#     bucket_name = 'minpy'
#     bucket = client.bucket(bucket_name)

#     blobs = list(client.list_blobs(bucket_name))
#     for i in blobs:
#         print("Name: ", i.name)
#     return True

# test_connect_gcs()




#---- Test Extractor -------

import pandas as pd
from extractors.shopify_extractor import Shopify_Extractor
from extractors.payment_extractor import Payment_Extractor
from extractors.sapo_extractor import Sapo_Extractor
from extractors.tracking_extractor import trackingExtractor

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


bucket = 'minpy'

product = Shopify_Extractor(bucket)
product_data = product.extract_products()



print(product_data.head(50))
print(product_data.info())



