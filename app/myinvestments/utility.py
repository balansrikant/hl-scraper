import os
import csv
import pandas as pd
import numpy as np
import json
import urllib
import urllib.request


def read_transactions(url: str = ''):
    if url == '':
        url = "https://raw.githubusercontent.com/balansrikant/logs/master/data/portfolio-summary-metadata.txt"
    
    cols = ['account', 'trade_date', 'reference', 'description', 'unit_cost', 'units', 'value']
    df = pd.DataFrame(columns=cols)
    
    with urllib.request.urlopen(url) as f:
        files = f.read().decode('utf-8')
    
    for file in files.split('\n'):
        if 'isa' in file:
            account = 'isa'
        else:
            account = 'sipp'
        file_url = 'https://raw.githubusercontent.com/balansrikant/logs/master/data/' + file
        df_temp = pd.read_csv(file_url)
        
        temp_cols = ['trade_date', 'settle_date', 'reference', 'description', 'unit_cost', 'units', 'value']
        df_temp.columns = temp_cols
        df_temp['account'] = account
        df_temp = df_temp[cols]
        df_temp = df_temp.astype({'unit_cost': 'string', 'units': 'string'})
        df_temp['units'] = df_temp['units'].str.replace(',', '')
        df_temp['unit_cost'] = df_temp['unit_cost'].str.replace(',', '')
        df_temp = df_temp.astype({'unit_cost': float, 'units': float})
        df_temp['trade_date'] = df_temp['trade_date'].str[-4:] + '-' + \
            df_temp['trade_date'].str[3:5] + '-' + df_temp['trade_date'].str[0:2]
        df_temp['trade_date'] = pd.to_datetime(df_temp['trade_date'].astype(str), format='%Y-%m-%d')
        df = pd.concat([df, df_temp])

        result = serialize_transactions(df)
    return result


def serialize_transactions(df: pd.DataFrame) -> list:
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return parsed


if __name__ == '__main__':
    df = read_transactions()
    result = serialize_transactions(df)
    print(result)
