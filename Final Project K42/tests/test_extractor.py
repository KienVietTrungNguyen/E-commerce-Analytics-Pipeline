import os
import sys 

# Tự động tìm đường dẫn gốc project và thêm vào hệ thống
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Lùi 2 cấp thư mục
sys.path.append(project_root)

import pandas as pd
from extractors.shopify_extractor import Shopify_Extractor
from extractors.payment_extractor import Payment_Extractor
from extractors.sapo_extractor import Sapo_Extractor
from extractors.tracking_extractor import trackingExtractor

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


bucket = 'minpy'

product = Shopify_Extractor(bucket)
product_data = product.extract_all_orders_files()



print(product_data.head(10))
