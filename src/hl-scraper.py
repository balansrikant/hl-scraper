"""Process Hargreaves Lansdown investment files

Analyse investments to look for growth over time and percentage of stocks
across funds

Arguments:
root_path - where account summary and investment files are stored

Script steps:
1. Perform pre-requisite steps as per readme doc
2. Execute python script/docker container with root_path as argument

"""

import os
import sys
import pandas as pd


def get_account_summary_metadata(root_path: str) -> list:
    """Load account summary csv file metadata into list

    Keyword arguments:
    :root_path - path containing csv files

    Returns:
    :accounts - list of dicts (accounts)
    """
    accounts_file_path = root_path + 'Account-Summary'

    accounts = [{'filename': f}
                for dp, dn, filenames in os.walk(accounts_file_path)
                for f in filenames
                if (os.path.splitext(f)[1] == '.csv')
                and ('_processed' not in os.path.splitext(f)[0])]

    for account in accounts:
        # get account type
        char_pos_start = account['filename'] \
            .find('-', 0, len(account['filename']))
        char_pos_end = account['filename'] \
            .find('-', char_pos_start+1, len(account['filename']))
        acc_type = account['filename'][char_pos_start + 1:char_pos_end]
        account['account_type'] = acc_type

        # get date
        date_str = account['filename'][:4] \
            + '-' + account['filename'][4:6] \
            + '-' + account['filename'][6:8]
        account['date'] = date_str

    return accounts


def get_investment_metadata(root_path: str) -> list:
    """Get list of investment files

    Keyword arguments:
    :root_path - path containing csv files
    """

    # get list of recursive sub-folders; the first item is set of dates
    folders = [(dn) for dp, dn, f in os.walk(root_path) if 'Investments' in dp]
    date_folders = folders[0]

    # process each date sub-folder
    investments = []
    for inv_date in date_folders:
        new_path = os.path.join(root_path, 'Investments', inv_date)
        file_list_list = [f for dp, dn, f in os.walk(new_path)
                          if dp == new_path]

        for file_list in file_list_list:
            for file in file_list:
                new_row = {'date': inv_date,
                           'stock': file.replace('.html', '')}
                investments.append(new_row)

    return investments


def process_account_summary_files(
        root_path: str,
        accounts: list) -> pd.DataFrame:
    """Process each account summary file and load into dataframe

    Keyword arguments:
    :root_path - path containing csv files
    :accounts - list of dicts of account summary containing
      - file_name
      - account_type
      - date
    """
    accounts_file_path = root_path + 'Account-Summary'
    cols = [
        'code',
        'stock',
        'units',
        'price',
        'value',
        'cost',
        'gain',
        'gain_percent'
        ]
    df_accounts = pd.DataFrame(columns=cols)
    df_stock_replacement = pd.read_csv(root_path + 'StockReplacementName.csv')

    for account in accounts:
        print('Processing file {}'.format(account['filename']))
        path = os.path.join(accounts_file_path, account['filename'])
        df_temp = pd.read_csv(path, encoding='unicode_escape')
        df_temp.columns = cols

        df_temp['account_type'] = account['account_type']
        df_temp['date'] = account['date']
        df_accounts = pd.concat([df_accounts, df_temp])

    df_accounts['units'] = df_accounts['units'].str.replace(',', '')
    df_accounts['price'] = df_accounts['price'].str.replace(',', '')
    df_accounts['value'] = df_accounts['value'].str.replace(',', '')
    df_accounts['cost'] = df_accounts['cost'].str.replace(',', '')
    df_accounts['gain'] = df_accounts['gain'].str.replace(',', '')

    df_accounts = df_accounts.astype(
        {
            'price': 'float64',
            'value': 'float64',
            'cost': 'float64',
            'gain': 'float64',
            'gain_percent': 'float64',
            'units': 'float64',
            }
    )
    df_accounts['date'] = pd.to_datetime(df_accounts['date'])
    df_accounts['price'] = df_accounts['price'] / 100
    df_accounts['gain_percent'] = df_accounts['gain_percent'] / 100

    # fill replacement if any
    cols = list(df_accounts.columns)
    cols.append('replacement')
    df_accounts = pd.merge(
        df_accounts,
        df_stock_replacement,
        how='left',
        on=['stock'],
        suffixes=[None, '_y']
        )
    df_accounts['replacement'].fillna(df_accounts['stock'], inplace=True)
    df_accounts['stock'] = df_accounts['replacement']
    df_accounts.drop(['replacement'], axis=1, inplace=True)

    return df_accounts


def process_investment_files_sec(
        root_path: str,
        investment_files: list) -> pd.DataFrame:
    """Get securities breakdown from investment html file

    Keyword arguments:
    :root_path - path containing csv files
    :investment_files_in - list of dicts of investment files containing
      - stock
      - date

    Returns:
    :df_sec - dataframe with top 10 percentage of stocks in funds
    """

    df_sec = pd.DataFrame(columns=['stock', 'date', 'security', 'weight'])
    fails = []
    for investment in investment_files:
        print('Processing file {}'.format(investment['stock']))
        found = False
        stock = investment['stock']
        date = investment['date']

        if ('comm stk' in investment['stock'].lower()) \
                or ('com stk' in investment['stock'].lower()):
            print('Stock found {}'.format(investment['stock']))
            new_row = {
                'stock': stock,
                'date': date,
                'security': stock,
                'weight': 1
                }
            df_temp = pd.DataFrame.from_dict([new_row])
            df_sec = pd.concat([df_sec, df_temp])
            continue

        path = os.path.join(
            root_path,
            "Investments",
            investment['date'],
            investment['stock']
            )
        path += ".html"
        path = path.replace('\\', '/')
        tables_raw = pd.read_html(path)

        tables = []

        for table in tables_raw:
            tables.append(table)

        for table in tables:
            df_temp = pd.DataFrame(table)
            if 'Security' in df_temp.columns:

                cols = ['security', 'weight']
                df_temp.columns = cols
                df_temp['stock'] = stock
                df_temp['date'] = date
                if (len(df_temp.loc[df_temp['security'].isnull(), :]
                    .index) == 0) \
                    and (len(df_temp.loc[df_temp['weight'].isnull(), :]
                             .index) == 0):
                    df_temp['weight'] = pd.to_numeric(
                        df_temp['weight'].str.replace('%', ''))/100
                    df_sec = pd.concat([df_sec, df_temp])
                    found = True

        if not found:
            failed_file = {
                'stock': investment['stock'],
                'date': investment['date']
            }
            fails.append(failed_file)
    print(df_sec['date'].unique())
    df_sec['date'] = pd.to_datetime(df_sec['date'], format='%Y-%m-%d')
    print('Created sec dataframe')
    return df_sec


def merge_account_securities(
        df_sec: pd.DataFrame,
        df_acc_summary: pd.DataFrame) -> pd.DataFrame:

    """Associate security details with accounts

    Keyword arguments:
    :df_sec - dataframe containing securities
    :df_acc_summary - dataframe containing account summary

    Returns:
    :df_sec_combined - dataframe merged between accounts and securities
    """

    # associate security with account
    df_acc_summary_merge = df_acc_summary
    df_acc_summary_merge['stock_lower'] = df_acc_summary_merge['stock'] \
        .str.lower()
    df_security_merge = df_sec
    df_security_merge['stock_lower'] = df_security_merge['stock'] \
        .str.lower()

    df_sec_combined = pd.merge(
        df_acc_summary_merge,
        df_security_merge,
        how='left',
        on=['date', 'stock_lower'],
        suffixes=[None, '_y']
        )
    df_sec_combined.drop(['stock_y', 'stock_lower'], axis=1, inplace=True)

    # populate security value
    df_sec_combined['security_value'] = df_sec_combined['weight'] \
        * df_sec_combined['value']

    df_fails = df_sec_combined.loc[
        df_sec_combined['security'].isnull(), :
        ]

    if not df_fails.empty:
        print(df_fails.loc[:, ['account_type', 'stock', 'date']])

    return df_sec_combined


def acc_sec_analysis(
        df_sec_combined: pd.DataFrame) -> pd.DataFrame:

    """Perform basic analysis on combined account-investment dataframe
    returning proportion of stocks across investments

    Keyword arguments:
    :df_sec_combined - dataframe merged between accounts and securities

    Returns:
    :df_sec_analysis - dataframe with proportion of securities across accounts
    """

    df_sec_analysis = df_sec_combined \
        .groupby(['date', 'security']) \
        .sum('security_value').reset_index()
    cols = ['date', 'security', 'security_value']
    df_sec_analysis = df_sec_analysis[cols]
    df_sec_analysis.sort_values(
        by=['security_value'],
        ascending=False,
        inplace=True,
        ignore_index=True
    )

    return df_sec_analysis


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ROOT_PATH = sys.argv[1]
    else:
        ROOT_PATH = 'D:/MyDocuments/Logs/HL/'

    # load metadata
    acc_metadata = get_account_summary_metadata(ROOT_PATH)
    investment_metadata = get_investment_metadata(ROOT_PATH)

    # process files
    df_acc_summary = process_account_summary_files(ROOT_PATH, acc_metadata)
    print()
    print('Account Summary')
    print(df_acc_summary.head())

    df_sec = process_investment_files_sec(ROOT_PATH, investment_metadata)
    # merge accounts and investments (securities)
    df_sec_combined = merge_account_securities(
        df_sec,
        df_acc_summary
    )
    print()
    print('Security combined')
    print(df_sec_combined.head())

    # analyse securities
    df_sec_analysis = acc_sec_analysis(df_sec_combined)
    print()
    print('Security analysis')
    print(df_sec_analysis.head())
