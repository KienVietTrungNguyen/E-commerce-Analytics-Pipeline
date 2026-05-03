import pandas as pd
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Lùi 1 cấp thư mục
sys.path.append(project_root)

from utils.logger import setup_logger

#Import Extractors
from extractors.shopify_extractor import Shopify_Extractor
from extractors.payment_extractor import Payment_Extractor
from extractors.sapo_extractor import Sapo_Extractor
from extractors.tracking_extractor import trackingExtractor

#Import Transformers
from transformers.dimension_transformer import DimTransformer
from transformers.fact_transformer import FactTransformer

#Import Loaders
from loaders.bigquery_loader import BigQueryLoader


class PipelineOrchestrator:
    """
    The Orchestrator class responsible for managing the End-to-End ETL Pipeline.
    It coordinates the Extraction, Transformation, and Loading (ETL) phases
    for both Dimension and Fact tables.
    """

    def __init__(self, bucket_name, dataset_id):
        self.logger = setup_logger(__name__)
        self.bucket_name = bucket_name
        self.dataset_id = dataset_id

        # Initialize Transformers
        self.dim_transformer = DimTransformer()
        self.fact_transformer = FactTransformer()
        
        # Initialize Loaders
        self.loader = BigQueryLoader()
        
        
    def process_dimensions(self):
        """
        Orchestrates the ETL process for all Dimension Tables.
        Current implementation: Dim_Customer, Dim_Product.
        """
        self.logger.info('--- Starting Process: DIMENSION TABLES ---')  
        # -- Dim_customer:
        
        #Process DIM_CUSTOMER
        try:
            self.logger.info("Processing 'dim_customer'...")
            
            #Extract
            extractor = Shopify_Extractor(self.bucket_name)
            customer_data_raw = extractor.extract_all_customers_files()

            #Transform
            dim_customer = self.dim_transformer.create_dim_customer(customer_data_raw)

            #Data quality check
            self.dim_transformer.data_quality_check(
                df= dim_customer,
                table_name= 'dim_customer',
            )

            #Loader
            self.loader.load_dataframe(
                df= dim_customer,
                dataset_id= self.dataset_id,
                partition_by= 'created_at',
                bq_table_name= 'dim_customer',
            )
            
            self.logger.info("Finished 'dim_customer'.")

        except Exception as e:
            self.logger.critical(f'Fail when processing DIM_CUSTOMER: {e}')
            raise e
        
        #Process DIM_PRODUCT
        try:
            self.logger.info("Processing 'dim_product'...")
            
            #Extract
            extractor = Shopify_Extractor(self.bucket_name)
            product_data_raw = extractor.extract_products()

            #Transform
            dim_product = self.dim_transformer.create_dim_product(product_data_raw)

            #Data quality check
            self.dim_transformer.data_quality_check(
                df= dim_product,
                table_name= 'dim_product',
            )

            #Loader
            self.loader.load_dataframe(
                df= dim_product,
                dataset_id= self.dataset_id,
                bq_table_name= 'dim_product',
            )
            
            self.logger.info("Finished 'dim_product'.")

        except Exception as e:
            self.logger.critical(f'Fail when processing dim_product: {e}')
            raise e
        

        #Process DIM_LOCATION
        try:
            self.logger.info("Processing 'dim_location'...")
            
            #Extract
            extractor = Sapo_Extractor(self.bucket_name)
            location_data_raw = extractor.extract_locations()

            #Transform
            dim_location = self.dim_transformer.create_dim_location(location_data_raw)

            #Data quality check
            self.dim_transformer.data_quality_check(
                df= dim_location,
                table_name= 'dim_location',
            )

            #Loader
            self.loader.load_dataframe(
                df= dim_location,
                dataset_id= self.dataset_id,
                bq_table_name= 'dim_location',  
            )

            
            self.logger.info("Finished 'dim_location'.")

        except Exception as e:
            self.logger.critical(f'Fail when processing dim_location: {e}')
            raise e
        

        #Process DIM_DATE
        try:
            self.logger.info("Processing 'dim_date'...")

            # 1. Transform → tạo trực tiếp (KHÔNG phụ thuộc df)
            dim_date = self.dim_transformer.create_dim_date()

            # 2. Load → BigQuery
            self.loader.load_dataframe(
                df=dim_date,
                dataset_id=self.dataset_id,
                bq_table_name='dim_date',
                write_disposition='WRITE_TRUNCATE'
            )

            self.logger.info("dim_date processed successfully")

        except Exception as e:
            self.logger.error(f"Error processing dim_date: {e}")
            raise e


    # def process_facts(self):
    #     """
    #     Orchestrates the ETL process for all Fact Tables.
    #     Current implementation: 
    #         - Fact_Orders (Merged from Shopify & Online).
    #         - Fact_Order_Items (Merged from Shopify & Online)
    #         - Fact_Order_Payement (Merged from Zalopay and Momo)
    #             * Note: Due to seriously lacking data, we decided to remove all data from PayPal source. 
    #             For details: see ... in the Report.
    #         - Fact_Cart_Event
    #         - Fact_Bank_Transaction
    #     """
    #     self.logger.info('--- Starting Process: FACT TABLES ---')
        
    #     #PROCESSING FACT_ORDERS
    #     try:
    #         self.logger.info("Processing 'fact_orders'...")
    #         #EXTRACT
    #         # Extract shopify
    #         shopify = Shopify_Extractor(self.bucket_name)
    #         shopify_data_raw = shopify.extract_all_orders_files()

    #         # Extract online_orders
    #         online_orders = Sapo_Extractor(self.bucket_name)
    #         online_orders_data_raw = online_orders.extract_online_orders_file()

    #         #TRANSFORM
    #         fact_shopify_order = self.fact_transformer.fact_orders_shopify(shopify_data_raw)
    #         fact_online_orders = self.fact_transformer.fact_orders_online(online_orders_data_raw)

    #         # Union table
    #         fact_orders = self.fact_transformer.create_fact_orders(fact_shopify_order, fact_online_orders)

    #         #Loader
    #         self.loader.load_dataframe(
    #             df= fact_orders,
    #             dataset_id= self.dataset_id,
    #             bq_table_name= 'fact_orders',
    #             write_disposition= 'WRITE_TRUNCATE',
    #             partition_by= 'order_date_key',
    #             cluster_by= ['customer_id', 'channel']
    #         )
    #         self.logger.info("Finished 'fact_orders'.")

    #     except Exception as e:
    #         self.logger.critical(f'Fail when processing FACT_ORDERS: {e}')
    #         raise e
        
        
    #     #PROCESSING FACT_ORDER_ITEMS
    #     try:
    #         self.logger.info("Processing 'fact_order_items'...")
    #         #EXTRACT
    #         # Extract shopify
    #         shopify = Shopify_Extractor(self.bucket_name)
    #         shopify_data_raw = shopify.extract_all_orders_files()

    #         # Extract online_orders
    #         online_orders = Sapo_Extractor(self.bucket_name)
    #         online_orders_data_raw = online_orders.extract_online_orders_file()

    #         #TRANSFORM
    #         fact_shopify_orders = self.fact_transformer.fact_orders_shopify(shopify_data_raw)
    #         fact_shopify_order_items = self.fact_transformer.fact_order_items_shopify(fact_shopify_orders, shopify_data_raw)
            
    #         fact_online_orders = self.fact_transformer.fact_orders_online(online_orders_data_raw)
    #         fact_online_order_items = self.fact_transformer.fact_order_items_online(fact_online_orders, online_orders_data_raw)

    #         # Union table
    #         fact_order_items = self.fact_transformer.create_fact_orders(fact_shopify_order_items, fact_online_order_items)

    #         #Data quality check
    #         self.fact_transformer.data_quality_check(
    #             df= fact_order_items,
    #             table_name= 'fact_order_items',
    #         )
            
    #         #Loader
    #         self.loader.load_dataframe(
    #             df= fact_order_items,
    #             dataset_id= self.dataset_id,
    #             bq_table_name= 'fact_order_items',
    #             write_disposition= 'WRITE_TRUNCATE',
    #             partition_by= 'order_date_key',
    #             cluster_by= ['product_id']
    #         )
    #         self.logger.info("Finished 'fact_order_items'.")
            
    #     except Exception as e:
    #         self.logger.critical(f'Fail when processing fact_order_items: {e}')
    #         raise e
        
    #     #PROCESSING FACT_PAYMENT
    #     try:
    #         self.logger.info("Processing 'fact_payment'...")
    #         #EXTRACT
    
    #         payement = Payment_Extractor(self.bucket_name)
    #         momo_data_raw = payement.payment_momo_extract()
    #         zalopay_data_raw = payement.payment_zalopay_extract()
    #         paypal_data_raw = payement.payment_paypal_extract()


    #         #TRANSFORM
    #         fact_payment_momo = self.fact_transformer.fact_payment_momo(momo_data_raw)
    #         fact_payment_zalopay = self.fact_transformer.fact_payment_zalo(zalopay_data_raw)
    #         fact_payment_paypal = self.fact_transformer.fact_payment_paypal(paypal_data_raw)


    #         # Union table
    #         fact_payment = self.fact_transformer.create_fact_payment(fact_payment_momo, fact_payment_zalopay,fact_payment_paypal) 

    #         #Data quality check
    #         self.fact_transformer.data_quality_check(
    #             df= fact_payment,
    #             table_name= 'fact_payment',
    #         )

    #         #Loader
    #         self.loader.load_dataframe(
    #             df= fact_payment,
    #             dataset_id= self.dataset_id,
    #             bq_table_name= 'fact_payment',
    #             write_disposition= 'WRITE_TRUNCATE',
    #             partition_by= 'payment_date_key',
    #             cluster_by= ['customer_id', 'payment_gateway']
    #         )
    #         self.logger.info("Finished 'fact_payment'.")
            
    #     except Exception as e:
    #         self.logger.critical(f'Fail when processing fact_payment: {e}')
    #         raise e
        
    #     #PROCESSING FACT_BANK_TRANSACTIONS
    #     try:
    #         self.logger.info("Processing 'fact_bank_transactions'...")
    #         #EXTRACT
    #         payment = Payment_Extractor(self.bucket_name)

    #         bank_transactions_data = payment.extract_payment_mercury()
    #         bank_transactions_data_raw = bank_transactions_data ['transactions']

    #         #TRANSFORM
    #         fact_mercury_bank = self.fact_transformer.fact_bank_transactions(bank_transactions_data_raw)


    #         #Data quality check
    #         self.fact_transformer.data_quality_check(
    #             df= fact_mercury_bank,
    #             table_name= 'fact_bank_transactions',
    #             allow_negative_amounts= True,
    #         )

    #         #Loader
    #         self.loader.load_dataframe(
    #             df= fact_mercury_bank,
    #             dataset_id= self.dataset_id,
    #             bq_table_name= 'fact_bank_transactions',
    #             partition_by= 'transaction_date_key',
    #             write_disposition= 'WRITE_TRUNCATE'
    #         )
    #         self.logger.info("Finished 'fact_bank_transactions'.")
            
    #     except Exception as e:
    #         self.logger.critical(f'Fail when processing fact_bank_transactions: {e}')
    #         raise e


    #     #PROCESSING FACT_CART_EVENTS
    #     try:
    #         self.logger.info("Processing 'fact_cart_events'...")
    #         #EXTRACT
    #         tracking = trackingExtractor(self.bucket_name)
    #         cart_events_data_raw = tracking.extract_tracking_file()
          


    #         #TRANSFORM
    #         fact_cart_events = self.fact_transformer.fact_cart_events(cart_events_data_raw)

    #         #Data quality check
    #         self.fact_transformer.data_quality_check(
    #             df= fact_cart_events,
    #             table_name= 'fact_cart_events',
    #         )

    #         #Loader
    #         self.loader.load_dataframe(
    #             df= fact_cart_events,
    #             dataset_id= self.dataset_id,
    #             bq_table_name= 'fact_cart_events',
    #             partition_by= 'event_date_key',
    #             cluster_by=['customer_id', 'session_id', 'event_type'],
    #             write_disposition= 'WRITE_TRUNCATE'
    #         )
    #         self.logger.info("Finished 'fact_cart_events'.")
            
    #     except Exception as e:
    #         self.logger.critical(f'Fail when processing fact_cart_events: {e}')
    #         raise e


    def orchestrator_run(self):
        self.logger.info(">>> PIPELINE STARTED <<<")
        try:
            self.loader.check_dataset_available(self.dataset_id)

            self.process_dimensions()

            # self.process_facts()

            self.logger.info(">>> PIPELINE FINISHED SUCCESSFULLY <<<")
    
        except Exception as e:
            self.logger.critical(f">>> PIPELINE FAILED: {e} <<<")
            raise e  


### TEST Zone

if __name__ == '__main__':
    from orchestration import PipelineOrchestrator

    bucket_name = 'minpy'
    dataset_id = 'end_to_end_project'

    orchestrator = PipelineOrchestrator(bucket_name, dataset_id)

    run = orchestrator.orchestrator_run()

    