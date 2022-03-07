import os
import csv
import pandas as pd
import numpy as np
import json


def read_transactions():
    path = os.path.join(os.getcwd(), 'myinvestments', 'static')
    new_cols = ['date', 'account', 'reference', 'description', 'unit_cost', 'units']
    df = pd.DataFrame(columns=new_cols)
    for filename in  os.listdir(path):
        if filename[-4:] == '.csv' and 'transaction-history' in filename:
            full_path = os.path.join(path, filename)
            if 'isa' in filename:
                account = 'isa'
            else:
                account = 'sipp'
            
            cols = ['Trade date', 'Reference', 'Description', 'Unit cost (p)', 'Quantity']
            df_temp = pd.read_csv(full_path, usecols=cols, encoding= 'unicode_escape')
            cols = ['date', 'reference', 'description', 'unit_cost', 'units']
            df_temp.columns = cols
            df_temp['account'] = account

            df_temp = df_temp.loc[df_temp['reference'].str.lower() != 'transfer']
            df_temp = df_temp.loc[df_temp['reference'].str.lower() != 'manage fee']
            df_temp = df_temp.loc[df_temp['unit_cost'].notnull()]
            df_temp = df_temp.astype({'unit_cost': 'string', 'units': 'string'})
            df_temp['units'] = df_temp['units'].str.replace(',', '')
            df_temp['unit_cost'] = df_temp['unit_cost'].str.replace(',', '')
            df_temp['date'] = df_temp['date'].str[-4:] + '-' + \
                df_temp['date'].str[3:5] + '-' + df_temp['date'].str[0:2]

            
            df_temp = df_temp.astype({'unit_cost': np.float, 'units': np.float})
            df = pd.concat([df, df_temp])
            
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    
    return parsed


def read_factsheets(local: str = False):
    if local:
        path = os.path.join(os.getcwd())
    else:    
        path = os.path.join(os.getcwd(), 'myinvestments')
    
    path = os.path.join(path, 'static', 'investment-factsheets.csv')
    
    with open(path, mode='r') as f:
        urls = list(csv.DictReader(f))

    url = urls[0]['url']
    
    # new_cols = ['date', 'account', 'reference', 'description', 'unit_cost', 'units']
    # df = pd.DataFrame(columns=new_cols)
    # for filename in  os.listdir(path):
    
    tables_raw = pd.read_html(url)
    tables = []

    for table in tables_raw:
        tables.append(table)

    #     idx = 0
    for table in tables:
        df_temp = pd.DataFrame(table)
        print(df_temp.iloc[0, :])
        print('-----')
        print()

    #     df_temp['Stock'] = stock
    #     df_temp['Date'] = date
    #     if 'Security' in df_temp.columns:
    #         df_security = pd.concat([df_security, df_temp])
    #     elif 'Sector' in df_temp.columns:
    #         df_sector = pd.concat([df_sector, df_temp])
    #     elif 'Country' in df_temp.columns:
    #         df_country = pd.concat([df_country, df_temp])


if __name__ == '__main__':
    # read_transactions()
    read_factsheets(local = True)
