import pandas as pd
from transformers.base_transformer import BaseTransformer

class DimTransformer(BaseTransformer):
    def __init__(self):
        super().__init__()

    
    def create_dim_customer(self, df):

        #select column and set a new name:
        col_mapping = {
            'id': 'customer_id',
            'email': 'email',
            'full_name':'full_name',
            'phone':'phone',
            'city':'city',
            'country':'country',
            'created_at':'created_at',
            'total_spent_vnd':'life_time_value_vnd',
            'total_orders':'total_orders'
        }

        #create dim_customer table
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        df_dim = df[selected_cols].copy()

        #rename
        df_dim.rename(columns = col_mapping, inplace = True)

        #change dtype
        df_dim = self.to_date(df_dim, ['created_at'])

        #create new columns
         
        def segment_customer(row):
            if row['total_orders'] == 1:
                return 'New'
            elif row['life_time_value_vnd'] >= 5000000:
                return 'VIP'
            elif row['life_time_value_vnd'] >= 1000000:
                return 'Loyal'
            else:
                return 'Regular'

        df_dim['customer_segment'] = df_dim.apply(segment_customer, axis=1)

        return df_dim
    

    def create_dim_product(self, df):

        #select column and set a new name:
        col_mapping = {
            'id': 'product_id',
            'name': 'product_name',
            'sku':'sku',
            'barcode':'barcode',
            'category':'category',
            'brand':'brand',
            'price_vnd':'price_vnd',
            'price_usd':'price_usd',
            'stock_quantity':'stock_quantity'
        }

        #create dim_product table
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        df_dim = df[selected_cols].copy()

        #rename
        df_dim.rename(columns = col_mapping, inplace = True)

        #create new columns
        df_dim['is_active'] =df_dim['stock_quantity'] > 0
        df_dim['is_active'] = df_dim['is_active'].astype(bool)

        return df_dim
    
    def create_dim_location(self, df):

        #select column and set a new name:
        col_mapping = {
            'tenant_id': 'location_id',
            'code': 'location_code',
            'name': 'location_name',
            'address': 'address',
            'city': 'city',
            'phone': 'phone',
            'status':'is_active'
        }

        #create dim_customer table
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        df_dim = df[selected_cols].copy()

        #create location_type
        df_dim['location_type'] = 'store'

        #rename
        df_dim.rename(columns = col_mapping, inplace = True)

        return df_dim
    

    def create_dim_date(self):

        dim_date = pd.DataFrame({
        'date': pd.date_range(
            start='2024-01-01',
            end='2027-12-31',
            freq='D'   #  daily
        )
            })

        dim_date['date'] = pd.to_datetime(dim_date['date'])
        dim_date['date_key'] = dim_date['date'].dt.strftime('%Y%m%d').astype(int)
        dim_date['year'] = dim_date['date'].dt.year
        dim_date['quarter'] = dim_date['date'].dt.quarter
        dim_date['month'] = dim_date['date'].dt.month
        dim_date['month_name'] = dim_date['date'].dt.month_name()

        dim_date['week'] = dim_date['date'].dt.isocalendar().week.astype(int)
        dim_date['day_of_month'] = dim_date['date'].dt.day
        dim_date['day_of_week'] = dim_date['date'].dt.weekday + 1
        dim_date['day_name'] = dim_date['date'].dt.day_name()

        dim_date['is_weekend'] = dim_date['day_of_week'].isin([6,7])

        dim_date['fiscal_year'] = dim_date['year']
        dim_date['fiscal_quarter'] = dim_date['quarter']

        return dim_date.sort_values('date')

if __name__ == '__main__':
    import os
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # Lùi 1 cấp thư mục
    sys.path.append(project_root)

    from extractors.shopify_extractor import Shopify_Extractor
    from extractors.payment_extractor import Payment_Extractor
    from extractors.sapo_extractor import Sapo_Extractor
    from extractors.tracking_extractor import trackingExtractor
    
    from transformers.dimension_transformer import DimTransformer


    bucket = 'minpy'

    customer = Sapo_Extractor(bucket)
    customer_data = customer.extract_locations()

    

    dim_table = DimTransformer()
    dim_customer = dim_table.create_dim_location(customer_data)
    # dim_date = dim_table.create_dim_date(dim_customer, 'created_at')
    print(dim_customer)
