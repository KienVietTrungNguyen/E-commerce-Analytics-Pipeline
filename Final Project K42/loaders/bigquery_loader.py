import os
import sys
import pandas as pd 
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

#import logger from utils
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
from utils.logger import setup_logger
from utils.gcs_helper import load_env_variables, get_bigquery_credentials_path

class BigQueryLoader:
    """
    Handles interactions with Google BigQuery, including connecting to Google BigQuery, dataset management, 
    loading Pandas DataFrames into BigQuery tables and executing SQL.
    
    """

    def __init__(self):
        """
        Connecting to a specific project in Google BigQuery
        """
        self.logger = setup_logger(__name__)

        try:
            # Load environment variables
            load_env_variables()
            
            # Set credentials from environment variable
            self.client = bigquery.Client.from_service_account_json( get_bigquery_credentials_path())


            self.logger.info(f"Successfully initialized BigQuery Client, project: '{self.client.project}'.")

        except Exception as e:
            self.logger.critical(f"Failed to connect to BigQuery: {e}")
            raise e

    def check_dataset_available(self, new_dataset_id, data_location='asia-southeast1'):
        try:
            dataset_ref = f"{self.client.project}.{new_dataset_id}"

            try:
                dataset = self.client.get_dataset(dataset_ref)
                self.logger.info(f"Dataset {new_dataset_id} already exists")

                # 🔥 CHECK LOCATION
                if dataset.location != data_location:
                    raise ValueError(
                        f"Dataset location mismatch! Existing: {dataset.location}, Expected: {data_location}"
                    )

            except Exception:
                self.logger.info(f"Dataset {new_dataset_id} not found → creating...")
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = data_location
                self.client.create_dataset(dataset)
                self.logger.info(f"Created dataset: {new_dataset_id} in {data_location}")

            return True

        except Exception as e:
            self.logger.error(f"Error in check_dataset_available: {e}")
            raise e

    def load_dataframe(self, df, dataset_id, bq_table_name, write_disposition = 'WRITE_TRUNCATE', partition_by = None, cluster_by=None):
        """
        Loads a DataFrame to BigQuery.

        Args:
            df (pd.DataFrame): Data to load.
            dataset_id (str): Target Dataset ID.
            bq_table_name (str): Target Table Name (in BigQuery).
            write_disposition (str): 'WRITE_TRUNCATE' or 'WRITE_APPEND'.
            cluster_by (list, optional): List of columns for clustering.
        """
        try:
            #check empty dataframe, avoid loading a empty dataframe to BigQuery
            if df.empty:
                self.logger.warning(f"Data source for '{bq_table_name}' is empty. Can not upload to Big Query")
                return
            
            #config destination
            destination_table = f"{self.client.project}.{dataset_id}.{bq_table_name}"

            #Config write_disposition
            if write_disposition == 'WRITE_TRUNCATE':
                write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            elif write_disposition == 'WRITE_APPEND': 
                write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            
            job_config = bigquery.LoadJobConfig(
                write_disposition = write_disposition,)
            
            #Config Partitioning
            if partition_by:
                self.logger.info(f"Table is cluster by {partition_by} column")
                job_config.time_partitioning = bigquery.TimePartitioning(
                    type_= bigquery.TimePartitioningType.DAY,
                   field= partition_by,
                   expiration_ms=None 
                )
            
            #Config clustering
            if cluster_by:
                self.logger.info(f"Table is cluster by {cluster_by} column")
                job_config.clustering_fields = cluster_by
            

            #Load table to BigQuery
            table_load = self.client.load_table_from_dataframe(
                dataframe= df,
                destination= destination_table,
                 job_config= job_config
            )
            
            table_load.result() #waiting the result from bigquery
            self.logger.info(f"Upload succesfully. {len(df)} rows are loaded to {bq_table_name}")

            # Detailed Error Handling check
            if table_load.errors:
                self.logger.error(f"Errors occurred during load: {table_load.errors}")
                raise RuntimeError(f"BigQuery Load Job failed: {table_load.errors}")

            self.logger.info(f"Upload successful: {bq_table_name}")

        except Exception as e:
            self.logger.error(f"Upload fail: {e}")
            raise e
   

        #test loader
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
    from transformers.fact_transformer import FactTransformer


    bucket = 'minpy'
    
    data_extract = Shopify_Extractor(bucket)
    dim_table = DimTransformer()
    fact_table = FactTransformer()
    loader = BigQueryLoader()

    #customer_data = data_extract.extract_file()
    #dim_customer = dim_table.create_dim_customer(customer_data)


    
    #test data_source empty
    #empty_df = pd.DataFrame()
    #loader.load_dataframe(empty_df, 'end_to_end_project', 'dim_empty')
    
    #check upload - successfull scenario
    
    #test fact_order_shopify
    # shopify = Shopify_Extractor(bucket)
    # shopify_data = shopify.extract_all_orders_files()

    # fact_orders_shopify = fact_table.fact_orders_shopify(shopify_data)
    
    # #test fact_order_online
    # online_orders = Sapo_Extractor(bucket)
    # online_orders_data = online_orders.extract_online_orders_file()

    # fact_orders_online = fact_table.fact_orders_online(online_orders_data)
    # fact_orders = fact_table.create_fact_orders(fact_orders_shopify, fact_orders_online)
      #  TẠO dim_date
    dim_date = dim_table.create_dim_date()

    # 🔍 DEBUG (cực quan trọng)
    print("MIN:", dim_date['date'].min())
    print("MAX:", dim_date['date'].max())
    print("ROWS:", len(dim_date))
    print(dim_date.head(5))
    print(dim_date.tail(5))

    # LOAD
    loader.check_dataset_available('end_to_end_project')

    loader.load_dataframe(
        df=dim_date,
        dataset_id='end_to_end_project',
        bq_table_name='dim_date',
        write_disposition='WRITE_TRUNCATE'
    )
    # #check upload - successfull fail
    # #check_data = loader.check_dataset_available('new')
    # #loader.load_dataframe(dim_customer, 'end_to_end_project', 'dim_customer', write_diposition='WRITE_EMPTY')