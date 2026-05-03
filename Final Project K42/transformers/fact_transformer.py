import pandas as pd
from transformers.base_transformer import BaseTransformer

class FactTransformer(BaseTransformer):

    def __init__(self):
        super().__init__()
    

    ## Create fact_orders

    # fact_orders_shopify
    def fact_orders_shopify(self, df):
        
        #select column and set a new name:
        col_mapping = {
            'order_number': 'order_id',
            'transaction_id':'transaction_id',
            'customer_id':'customer_id',
            'order_date':'order_date',
            'channel':'channel',
            'source':'source',
            'fulfillment_status':'status',
            'payment_status':'payment_status',
            'total_vnd':'total_vnd',
            'total_usd':'total_usd'
        }

        #create fact_order_shopify and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_orders_shopify = df[selected_cols].copy()

        #rename
        fact_orders_shopify.rename(columns = col_mapping, inplace = True)
        
        #format date
        fact_orders_shopify = self.to_date(fact_orders_shopify, ['order_date'])

        #converse ns to us
        fact_orders_shopify = self.convert_ns_to_us(fact_orders_shopify, 'order_date')

        #create order_date_key
        fact_orders_shopify = self.create_date_key(fact_orders_shopify, 'order_date', key_date_name='order_date_key')

        #format lại source và channel cho đồng bộ với online_orders
        fact_orders_shopify['source'] = fact_orders_shopify['source'].replace(to_replace= 'shopify', value= 'shopify_platform')
        fact_orders_shopify['channel'] = fact_orders_shopify['channel'].replace(to_replace= 'online', value= 'shopify')

        #tạo orderkey
        fact_orders_shopify = self.create_surrogate_key(fact_orders_shopify, ['channel', 'order_id', 'transaction_id'], 'order_key')

        # đảo order_key lên đầu
        new_col_order = ['order_key'] + [c for c in fact_orders_shopify.columns if c != 'order_key']
        fact_orders_shopify = fact_orders_shopify[new_col_order]

        return fact_orders_shopify
    

    # create fact_online_order
    def fact_orders_online(self, df):
        
        #select column and set a new name:
        col_mapping = {
            'order_id': 'order_id',
            'transaction_id':'transaction_id',
            'customer_id':'customer_id',
            'created_at':'order_date',
            'channel':'channel',
            'source':'source',
            'status':'status',
            'payment_status':'payment_status',
            'total':'total_vnd',
            
        }

        #create fact_order_shopify 
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_orders_online = df[selected_cols].copy()

        #rename
        fact_orders_online.rename(columns = col_mapping, inplace = True)
        
        #format date
        fact_orders_online = self.to_date(fact_orders_online, ['order_date'])

        #converse ns to us
        fact_orders_online = self.convert_ns_to_us(fact_orders_online, 'order_date')

        #create order_date_key
        fact_orders_online = self.create_date_key(fact_orders_online, 'order_date', key_date_name='order_date_key')

         #calculate total_usd

        fact_orders_online['total_usd'] = round((fact_orders_online['total_vnd'] / 24000), 2)  #exchange rate: 1 usd = 24000 vnd

        #format lại source và channel cho đồng bộ với online_orders
        fact_orders_online['source'] = fact_orders_online['source'].replace(to_replace= 'shopify', value= 'shopify_platform')
        fact_orders_online['channel'] = fact_orders_online['channel'].replace(to_replace= 'online', value= 'shopify')

        #tạo orderkey
        fact_orders_online = self.create_surrogate_key(fact_orders_online, ['channel', 'order_id', 'transaction_id'], 'order_key')

        # đảo order_key lên đầu
        new_col_order = ['order_key'] + [c for c in fact_orders_online.columns if c != 'order_key']
        fact_orders_online = fact_orders_online[new_col_order]

        return fact_orders_online
    
    #Combine two fact_orders dataframe
    def create_fact_orders(self, df1, df2):
        fact_orders = pd.concat([df1, df2], ignore_index= True)
        return fact_orders
    


    ## ------Create fact_order_items--------

    def fact_order_items_shopify(self, df, original_source):

        #từ fact_order_shopify merge thêm line_item từ data gốc
        selected_cols = ['order_key', 'order_id', 'transaction_id', 'order_date_key']
        order_items_shopify = df[selected_cols].copy()

        order_items_shopify = order_items_shopify.merge(original_source,on = 'transaction_id')

        #rename cột transaction_id để tránh xung đột khi exploded
        order_items_shopify = order_items_shopify.rename(columns={'transaction_id':'transaction_id_original'})
    
        #bỏ các cột không cần thiết
        keep_cols = ['order_key', 'order_date_key', 'transaction_id_original', 'line_items']
        order_items_shopify = order_items_shopify[keep_cols]

        #unflatten 
        exploded_order_items_shopify = self.unflatten_list(order_items_shopify, 'line_items',['order_key', 'order_date_key','transaction_id_original'])

        #create order_item_key
        exploded_order_items_shopify = self.create_surrogate_key(exploded_order_items_shopify,['order_key', 'id'], 'order_item_key')

        #calculate line_total
        exploded_order_items_shopify['line_total_vnd'] = exploded_order_items_shopify['quantity'] * exploded_order_items_shopify['price_vnd']

        #finalize fact table

        col_mapping ={
            'order_item_key': 'order_item_key',
            'order_key': 'order_key',
            'order_date_key': 'order_date_key',
            'transaction_id': 'transaction_id',
            'product_id': 'product_id',
            'quantity': 'quantity',
            'price_vnd': 'unit_price_vnd',
            'line_total_vnd': 'line_total_vnd',
        }

        final_col = [ c for c in col_mapping.keys() if c in exploded_order_items_shopify.columns]
        fact_order_items_shopify = exploded_order_items_shopify[final_col].copy()

        fact_order_items_shopify = fact_order_items_shopify.rename(columns = col_mapping, inplace = True)

        
        return fact_order_items_shopify
    

    #create order_item table from online_source
    def fact_order_items_online(self, df, original_source):
    
        #từ fact_order_shopify merge thêm line_items từ data gốc
        selected_cols = ['order_key', 'order_id', 'transaction_id', 'order_date_key']
        order_items_online = df[selected_cols].copy()

        order_items_online = order_items_online.merge(original_source, how='inner', on=['transaction_id'])

        #rename cột transaction_id để tránh xung đột khi exploded
        order_items_online = order_items_online.rename(columns={'transaction_id':'transaction_id_original'})
        
        #bỏ các cột không cần thiết
        keep_cols = ['order_key', 'order_date_key', 'transaction_id_original', 'line_items']
        order_items_online = order_items_online[keep_cols]

        #create exploded table
        exploded_order_items_online = self.unflatten_list(order_items_online, 'line_items', ['order_key','order_date_key' ,'transaction_id_original'])
        
        #create order_item_key
        exploded_order_items_online = self.create_surrogate_key(exploded_order_items_online, ['order_key', 'line_id'], 'order_item_key')
        

        #finalize fact table: selected column, name standardize, 
        col_mapping = {
            'order_item_key': 'order_item_key',
            'order_key': 'order_key',
            'order_date_key': 'order_date_key',
            'transaction_id_original': 'transaction_id',
            'product_id': 'product_id',
            'quantity': 'quantity',
            'unit_price': 'unit_price_vnd',
            'line_total': 'line_total_vnd',
        }

        final_col = [c for c in col_mapping.keys() if c in exploded_order_items_online.columns]
        fact_order_items_online = exploded_order_items_online[final_col].copy()

        fact_order_items_online.rename(columns=col_mapping, inplace= True)

        return fact_order_items_online
    

    #Combine two fact_items_orders dataframe
    def create_fact_orders(self, df1, df2):
        fact_orders_items = pd.concat([df1, df2], ignore_index= True)
        return fact_orders_items
    


    ## ------Create fact_payment--------


    # Fact payment paypal
    def fact_payment_paypal(self, df):

        #select column and set a new name:
        col_mapping = {
            'transaction_id': 'transaction_id',
            'invoice_id': 'order_id',
            'customer_id':'customer_id',
            'source':'payment_gateway',
            'transaction_amount_vnd': 'amount_vnd',
            'transaction_status' : 'payment_status',
            'transaction_initiation_date' : 'payment_date'
        }

        #create fact_payment_paypal and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_payment_paypal = df[selected_cols].copy()

        fact_payment_paypal.rename(columns = col_mapping, inplace = True)

        #create payment_method: due to there is no payment_method infomation available in data raw, so I label it "e-wallet"
        fact_payment_paypal['payment_method'] = 'e-wallet'

        #covert to the datetime
        fact_payment_paypal = self.to_date(fact_payment_paypal, ['payment_date'])

        #convert ns to us
        fact_payment_paypal = self.convert_ns_to_us(fact_payment_paypal, 'payment_date')

        #create payment_date key
        fact_payment_paypal = self.create_date_key(fact_payment_paypal, 'payment_date','payment_date_key')

        #create payment_key
        fact_payment_paypal = self.create_surrogate_key(fact_payment_paypal,['payment_gateway','transaction_id'], 'payment_key' )

        #bring payment_key into 1st columns
        new_col_order = ['payment_key'] + [c for c in fact_payment_paypal.columns if c != 'payment_key']
        fact_payment_paypal = fact_payment_paypal[new_col_order]

        return fact_payment_paypal
    
    
    # Fact payment zalo
    def fact_payment_zalo(self, df):


        #select column and set a new name:
        col_mapping = {
            'transaction_id': 'transaction_id',
            'description': 'order_id',
            'customer_id':'customer_id',
            'source':'payment_gateway',
            'amount': 'amount_vnd',
            'return_message' : 'payment_status',
            'app_time' : 'payment_date'
        }

        #create fact_payment_paypal and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_payment_zalo = df[selected_cols].copy()

        fact_payment_zalo.rename(columns = col_mapping, inplace = True)

        #create payment_method: due to there is no payment_method infomation available in data raw, so I label it "e-wallet"
        fact_payment_zalo['payment_method'] = 'e-wallet'

        #covert to the datetime
        fact_payment_zalo = self.to_date(fact_payment_zalo, ['payment_date'])

        #convert ns to us
        fact_payment_zalo = self.convert_ns_to_us(fact_payment_zalo, 'payment_date')

        #create payment_date key
        fact_payment_zalo = self.create_date_key(fact_payment_zalo, 'payment_date','payment_date_key')

        #create payment_key
        fact_payment_zalo = self.create_surrogate_key(fact_payment_zalo,['payment_gateway','transaction_id'], 'payment_key' )

        #bring payment_key into 1st columns
        new_col_order = ['payment_key'] + [c for c in fact_payment_zalo.columns if c != 'payment_key']
        fact_payment_zalo = fact_payment_zalo[new_col_order]

        return fact_payment_zalo

    #create fact_payment_momo
    def fact_payment_momo(self, df):


        #select column and set a new name:
        col_mapping = {
            'transaction_id': 'transaction_id',
            'orderId': 'order_id',
            'customer_id':'customer_id',
            'source':'payment_gateway',
            'amount': 'amount_vnd',
            'message' : 'payment_status',
            'responseTimeISO' : 'payment_date',
            'payType':'payment_method'
        }

        #create fact_payment_paypal and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_payment_momo = df[selected_cols].copy()

        fact_payment_momo.rename(columns = col_mapping, inplace = True)


        #covert to the datetime
        fact_payment_momo = self.to_date(fact_payment_momo, ['payment_date'])

        #convert ns to us
        fact_payment_momo = self.convert_ns_to_us(fact_payment_momo, 'payment_date')

        #create payment_date key
        fact_payment_momo = self.create_date_key(fact_payment_momo, 'payment_date','payment_date_key')

        #create payment_key
        fact_payment_momo = self.create_surrogate_key(fact_payment_momo,['payment_gateway','transaction_id'], 'payment_key' )

        #bring payment_key into 1st columns
        new_col_order = ['payment_key'] + [c for c in fact_payment_momo.columns if c != 'payment_key']
        fact_payment_momo = fact_payment_momo[new_col_order]

        return fact_payment_momo
    
    #combined into fact_payment
    def create_fact_payment(self, df1 = None, df2 =None, df3 = None):
        fact_payment = pd.concat([df1, df2, df3])
        return fact_payment



    ## ------Create fact_cart_events--------

    def fact_cart_events(self, df):


        #select column and set a new name:
        col_mapping = {
            'event_id': 'event_id',
            'session_id': 'session_id',
            'customer_id':'customer_id',
            'event_type':'event_type',
            'timestamp':'event_timestamp',
            'product_id':'product_id',
            'source':'source',
            'device':'device',
            'utm_source':'utm_source',
            'utm_campaign':'utm_campaign'
        }

        #create fact_cart_events and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_cart_events = df[selected_cols].copy()

        fact_cart_events.rename(columns = col_mapping, inplace = True)


        #covert to the datetime
        fact_cart_events = self.to_date(fact_cart_events, ['event_timestamp'])

        #create event_date_key
        fact_cart_events = self.create_date_key(fact_cart_events, 'event_timestamp', 'event_date_key')

        #convert ns to us
        fact_cart_events = self.convert_ns_to_us(fact_cart_events, 'event_timestamp')

        #create events_key
        fact_cart_events = self.create_surrogate_key(fact_cart_events,['event_type', 'event_id'], 'events_key' )

        #bring events_key into 1st columns
        new_col_order = ['events_key'] + [c for c in fact_cart_events.columns if c != 'events_key']
        fact_cart_events = fact_cart_events[new_col_order]

         #handle missing value
        fact_cart_events = self.handle_missing_value(fact_cart_events,
                                                     {'customer_id' : '-1',
                                                      'product_id': '-1',
                                                      'utm_source': 'unidentified',
                                                      'utm_campaign': 'unidentified'})
        
        fact_cart_events['customer_id'] = fact_cart_events['customer_id'].astype('int64')
        fact_cart_events['product_id'] = fact_cart_events['product_id'].astype('int64')

        return fact_cart_events
    

    
    ## ------CREATE FACT_BANK_TRANSACTIONS--------

    def fact_bank_transactions(self, df):

        #select column and set a new name:
        col_mapping = {
            'transaction_id': 'transaction_id',
            'accountId': 'account_id',
            'kind':'transaction_type',
            'amount_vnd':'amount_vnd',
            'status':'status',
            'createdAt':'transaction_date',
            'source':'source'
        }

        #create fact_bank_transactions and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_bank_transactions = df[selected_cols].copy()

        fact_bank_transactions.rename(columns = col_mapping, inplace = True)

        #format date
        fact_bank_transactions = self.to_date(fact_bank_transactions, ['transaction_date'])

        #creat transaction_date_key
        fact_bank_transactions = self.create_date_key(fact_bank_transactions, 'transaction_date', 'transaction_date_key')

        #tạo transaction_key
        fact_bank_transactions = self.create_surrogate_key(fact_bank_transactions, ['source', 'transaction_id'], 'transaction_key')
        
        #đảo transaction_key lên đầu
        new_col_order = ['transaction_key'] + [c for c in fact_bank_transactions.columns if c != 'transaction_key']
        fact_bank_transactions = fact_bank_transactions[new_col_order]
        
        return fact_bank_transactions
    


    def fact_sapo_transactions(self, df):

        #select column and set a new name:
        col_mapping = {
            'transaction_id': 'transaction_id',
            'accountId': 'account_id',
            'kind':'transaction_type',
            'amount_vnd':'amount_vnd',
            'status':'status',
            'createdAt':'transaction_date',
            'source':'source'
        }

        #create fact_bank_transactions and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_sapo_transactions = df[selected_cols].copy()

        fact_sapo_transactions.rename(columns = col_mapping, inplace = True)

        #format date
        fact_sapo_transactions = self.to_date(fact_sapo_transactions, ['transaction_date'])

        #creat transaction_date_key
        fact_sapo_transactions = self.create_date_key(fact_sapo_transactions, 'transaction_date', 'transaction_date_key')

        #tạo transaction_key
        fact_sapo_transactions = self.create_surrogate_key(fact_sapo_transactions, ['source', 'transaction_id'], 'transaction_key')
        
        #đảo transaction_key lên đầu
        new_col_order = ['transaction_key'] + [c for c in fact_sapo_transactions.columns if c != 'transaction_key']
        fact_sapo_transactions = fact_sapo_transactions[new_col_order]
        
        return fact_sapo_transactions
    
    def fact_odoo_transactions(self, df):

        #select column and set a new name:
        col_mapping = {
            'transaction_id': 'transaction_id',
            'accountId': 'account_id',
            'kind':'transaction_type',
            'amount_vnd':'amount_vnd',
            'status':'status',
            'createdAt':'transaction_date',
            'source':'source'
        }

        #create fact_bank_transactions and rename columns
        selected_cols = [c for c in col_mapping.keys() if c in df.columns]
        fact_odoo_transactions = df[selected_cols].copy()

        fact_odoo_transactions.rename(columns = col_mapping, inplace = True)

        #format date
        fact_odoo_transactions = self.to_date(fact_odoo_transactions, ['transaction_date'])

        #creat transaction_date_key
        fact_odoo_transactions = self.create_date_key(fact_odoo_transactions, 'transaction_date', 'transaction_date_key')

        #tạo transaction_key
        fact_odoo_transactions = self.create_surrogate_key(fact_odoo_transactions, ['source', 'transaction_id'], 'transaction_key')
        
        #đảo transaction_key lên đầu
        new_col_order = ['transaction_key'] + [c for c in fact_odoo_transactions.columns if c != 'transaction_key']
        fact_odoo_transactions = fact_odoo_transactions[new_col_order]
        
        return fact_odoo_transactions
    

     #combined into fact_bank_payment
    def create_fact_bank_transactions(self, df1 = None, df2 =None, df3 = None):
        fact_bank_payment = pd.concat([df1, df2, df3])
        return fact_bank_payment

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
    from utils.logger import setup_logger

    from transformers.dimension_transformer import DimTransformer


    bucket = 'minpy'
    fact_table = FactTransformer()

    # shopify = Shopify_Extractor(bucket)
    online = Sapo_Extractor(bucket)
    payment =Payment_Extractor(bucket)

    # shopify_data = shopify.extract_all_orders_files()
    online_data = online.extract_sapo_json_file()
    online_data_raw = fact_table.fact_sapo_transactions(online_data['transactions'])

    sonline_data = online.extract_odoo_json_file()
    sonline_data_raw = fact_table.fact_odoo_transactions(sonline_data['transactions'])

    ssonline_data = payment.extract_payment_mercury()
    ssonline_data_raw = fact_table.fact_bank_transactions(ssonline_data['transactions'])

    fact_bank_transaction = fact_table.create_fact_bank_transactions(online_data_raw, sonline_data_raw, ssonline_data_raw)


    # fact_order_shopify = fact_table.fact_orders_shopify(shopify_data)
    # fact_order_online = fact_table.fact_orders_online(online_data)
    
    # fact_orders = fact_table.create_fact_orders(fact_order_shopify, fact_order_online)
    
    
    # fact_order_items_shopify = fact_table.fact_order_items_shopify(fact_order_shopify, shopify_data)
    # fact_order_items_online = fact_table.fact_order_items_online(fact_order_online, online_data)

    # fact_order_items = fact_table.create_fact_orders(fact_order_items_shopify, fact_order_items_online)
    print(fact_bank_transaction.head())