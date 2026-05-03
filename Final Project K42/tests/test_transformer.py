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
    from transformers.base_transformer import BaseTransformer

    #import data test: payment_momo
    payment = Payment_Extractor('minpy')
    momo_data = payment.payment_momo_extract()
    momo_data.info()
    
    #import data test: shopify
    shopify= Shopify_Extractor('minpy')
    shopify_data = shopify.extract_all_orders_files()


    #test create date_key
    transformer = BaseTransformer()
    momo_data_transform = transformer.to_date(momo_data, ['responseTimeISO'])
    momo_data_transform = transformer.create_date_key(momo_data, 'responseTimeISO', "payment_date_key")
   
   #test creat_order_key
    shopify_data_transform = transformer.create_surrogate_key(shopify_data, 'source', 'order_number')
    shopify_data_transform.head()

    #test unflatten list
    shopify_line_items = transformer.unflatten_list(shopify_data, 'line_items',['order_key','order_date_key' ,'transaction_id_original'])
    shopify_line_items.head()


#test dim_transformer
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

    #test dim_product
    product = Shopify_Extractor(bucket)
    product_data = product.extract_products()

    print(product_data.info())

    dim_table = DimTransformer()
    dim_product = dim_table.create_dim_product(product_data)

    print(dim_product.head(20))
    print(dim_product.info())

    #test dim_customer
    
    customer = Shopify_Extractor(bucket)
    customer_data = customer.extract_all_customers_files()

    print(customer_data.info())

    dim_table = DimTransformer()
    dim_customer = dim_table.create_dim_customer(customer_data)

    print(dim_customer.head(20))
    print(dim_customer.info())

#test fact_transformers
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
    
    from transformers.fact_transformer import FactTransformer

    bucket = 'minpy'
    fact_table = FactTransformer()

    #test fact_order_shopify
    shopify = Shopify_Extractor(bucket)
    shopify_data = shopify.extract_all_orders_files()

    fact_orders_shopify = fact_table.fact_orders_shopify(shopify_data)
    
    #test fact_order_online
    online_orders = Sapo_Extractor(bucket)
    online_orders_data = online_orders.extract_online_orders_file()

    fact_orders_online = fact_table.fact_orders_online(online_orders_data)
    
    #test union
    fact_orders = fact_table.create_fact_orders(fact_orders_shopify, fact_orders_online)

    print(fact_orders.head())
    print(fact_orders.info())



    momo_data = payment.payment_momo_extract()
    zalopay_data = payment.payment_zalopay_extract()
    paypal_data = payment.payment_paypal_extract()

    fact_payment_momo = fact_table.fact_payment_momo(momo_data)
    fact_payment_zalopay = fact_table.fact_payment_zalo(zalopay_data)
    fact_payment_paypal = fact_table.fact_payment_paypal(paypal_data)

    fact_payment = fact_table.create_fact_payment(fact_payment_zalopay, fact_payment_momo, fact_payment_paypal)

    print(fact_payment.head(10))

    print(fact_payment.info())

    #fact_order_items
    shopify = Shopify_Extractor(bucket)
    shopify_data = shopify.extract_all_orders_files()

    fact_order_shopify = fact_table.fact_orders_shopify(shopify_data)

    fact_order_items_shopify = fact_table.fact_order_items_shopify(fact_order_shopify, shopify_data)


    online = Sapo_Extractor(bucket)
    online_data = online.extract_online_orders_file()

    fact_order_online = fact_table.fact_orders_online(online_data)

    fact_order_items_online = fact_table.fact_order_items_online(fact_order_online, online_data)

    fact_order_items = fact_table.create_fact_orders(fact_order_items_shopify, fact_order_items_online)

    fact_order_items.info()

    cart_events = trackingExtractor(bucket)
    cart_events_data = cart_events.extract_tracking_file()

    fact_cart_events = fact_table.fact_cart_events(cart_events_data)

    print(fact_cart_events.head(10))