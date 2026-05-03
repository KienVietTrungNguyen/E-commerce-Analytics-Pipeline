#test loader
if __name__ == '__main__':
    import os
    import sys
    import pandas as pd


    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # Lùi 1 cấp thư mục
    sys.path.append(project_root)

    from extractors.shopify_extractor import Shopify_Extractor
    from extractors.payment_extractor import Payment_Extractor
    from extractors.sapo_extractor import Sapo_Extractor
    from extractors.tracking_extractor import trackingExtractor
    from transformers.dimension_transformer import DimTransformer
    from loaders.bigquery_loader import BigQueryLoader


    bucket = 'minpy'
    dataset_id = 'end_to_end_project'
    table_name = 'dim_customer'



    data_extract = Shopify_Extractor(bucket)
    dim_table = DimTransformer()
    loader = BigQueryLoader()

    customer_data = data_extract.extract_all_customers_files()
    dim_customer = dim_table.create_dim_customer(customer_data)
    
       # TEST 1: EMPTY DATA
    # =====================
    print("\n=== TEST EMPTY DATA ===")
    empty_df = pd.DataFrame()
    loader.load_dataframe(empty_df, dataset_id, 'dim_empty')

    # =====================
    # TEST 2: CREATE DATASET + LOAD
    # =====================
    print("\n=== TEST LOAD DATA ===")
    loader.check_dataset_available(dataset_id)

    loader.load_dataframe(
        df=dim_customer,
        dataset_id=dataset_id,
        bq_table_name=table_name,
        write_disposition='WRITE_TRUNCATE'
    )

    # =====================
    # TEST 3: LOAD AGAIN (IDEMPOTENT TEST)
    # =====================
    print("\n=== TEST LOAD AGAIN ===")
    loader.load_dataframe(
        df=dim_customer,
        dataset_id=dataset_id,
        bq_table_name=table_name,
        write_disposition='WRITE_TRUNCATE'
    )

    print("\n>>> ALL TESTS COMPLETED SUCCESSFULLY <<<")