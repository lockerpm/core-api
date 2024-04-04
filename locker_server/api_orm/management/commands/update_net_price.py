import logging

import pandas as pd
from django.core.management import BaseCommand
from django.db.models import F

from locker_server.api_orm.models.wrapper import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Step 1: read file csv
        product_file_path = "product.csv"  # Product have redeemed code
        sale_file_path = "sale.csv"  # Sale have net price
        promo_code_column_name = "License"
        key_column_name = "Order ID"
        net_price_column_name = "Your Earnings"

        product_df = pd.read_csv(product_file_path)
        sale_df = pd.read_csv(sale_file_path)
        market_df = pd.merge(product_df, sale_df, on=key_column_name)
        all_code = market_df[promo_code_column_name]
        payment_model = get_payment_model()
        payments_orm = payment_model.objects.filter(
            promo_code__code__in=all_code
        ).annotate(
            redeem_code=F('promo_code__code')
        )
        print(len(payments_orm))

        for payment_orm in payments_orm:
            logging.error(payment_orm)
            promo_code = payment_orm.redeem_code
            print(promo_code)
            # Filter rows where code equals promo_code and select the net_price
            net_price = market_df.loc[market_df[promo_code_column_name] == promo_code, net_price_column_name]
            try:
                net_price = net_price.iloc[0]
                net_price = net_price.replace("$", "")
                print(net_price)
                net_price = abs(float(net_price))
            except TypeError:
                net_price = 0
            payment_orm.net_price = net_price
            payment_orm.save()
        print("success")
