# coding: utf-8

import json
import os
import boto3
import pandas as pd


def main():
    price_list = []
    pricing = boto3.client('pricing', region_name='us-east-1')
    paginator = pricing.get_paginator('get_products')
    response_iterator = paginator.paginate(
        ServiceCode='AmazonEC2',
        Filters = [
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'termType', 'Value': 'OnDemand'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
        ]
    )

    for page in response_iterator:
        for price in page['PriceList']:
            price_list.append(json.loads(price))

    price_summary_list = []
    df = pd.DataFrame()
    for price in price_list:
        attributes = dict()
        for k,v in price['product']['attributes'].items():
            attributes[k] = v
        attributes['sku'] = price['product']['sku']
        for k1,v1 in price['terms']['OnDemand'].items():
            for k2,v2 in v1['priceDimensions'].items():
                attributes['OnDemandPrices'] = v2['pricePerUnit']['USD']
                attributes['OnDemandPricesUnit'] = v2['unit']
                attributes['OnDemandPriceDescription'] = v2['description']

        price_summary_list.append(attributes)
        ds = pd.Series(attributes)
        df = df.append(ds, ignore_index=True)

    df.to_csv('ec2-price.csv')

    
if __name__=='__main__':
    main()