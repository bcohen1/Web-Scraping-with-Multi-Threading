import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def generate_clean_xlsx():
    '''returns cleaned and properly formatted df from original .xlsx'''
    df = pd.read_excel('screener_results.xls', sheet_name='Search Criteria')
    df.drop(df.tail(17).index, inplace = True)
    df = df[['Symbol', 'Company Name', 'Security Type', 'Security Price', 
             'Market Capitalization']]
    df.rename(columns={'Symbol':'Ticker', 'Company Name':'Company', 
            'Security Type':'Type', 'Security Price':'Price', 
            'Market Capitalization':'Market Cap'}, inplace=True)
    df.drop(df[df['Type']!='Common Stock'].index, inplace=True)
    # df.drop(df[df['Price']<=1.0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def generate_url(row):
    '''returns formatted url used for scraping'''
    return f'https://finance.yahoo.com/quote/{row}/profile?p={row}'

def create_urls(df):
    '''returns url list by calling "generate_url" for all tickers in .xlsx'''
    df['urls'] = np.vectorize(generate_url)(df['Ticker'])
    return df

def parse_html(url):
    '''scrapes company descriptions from yahoo finance html using beautiful soup'''
    results_url.append(url)
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, 'html5lib')
    search = soup.find_all('p', {'class':'Mt(15px) Lh(1.6)'})
    if search == []:
        results.append('No Profile available')
    else:
        results.append(search[0].text)

def multi_thread_parse(urls):
    '''gets next item in queue and calls "parse" until queue is empty'''
    # "with" statement ensures threads are cleaned up promptly
    with ThreadPoolExecutor() as executor:
        future = executor.map(parse_html, urls)

def merge_data(df, results, results_url):
    '''returns merged df including original .xlsx and web scrape results'''
    results_df = pd.DataFrame(zip(results, results_url), 
                              columns =['Description', 'urls'])
    df = df.merge(results_df)
    # df.drop(df[df['Description']=='No Profile available'].index, inplace=True)
    return df

def flag_key_terms(df):
    '''returns df with new columns that flag key terms in "Description"'''
    pattern = r"phase\s{1,}3"
    pattern2 = r"phase\s{1,}I{3}"
    pattern3 = r"phase\s{1,}2"
    pattern4 = r"phase\s{1,}I{2}"
    pattern5 = r"alzheimer"
    
    df['Phase 3 Ready'] = np.where(df['Description'].str.contains(pattern, case=False) | 
                             df['Description'].str.contains(pattern2, case=False), 1, 0)
    
    df['Phase 2b Ready'] = np.where(df['Description'].str.contains(pattern3, case=False) | 
                             df['Description'].str.contains(pattern4, case=False), 1, 0)
    
    df['alzheimer'] = np.where(df['Description'].str.contains(pattern5, case=False), 1, 0)
    return df

def write_data(df):
    '''writes final df to csv'''
    df.to_csv('stock_info.csv', index=False)


if __name__ == '__main__':
    results = []
    results_url = []
    df = generate_clean_xlsx()
    df = create_urls(df)
    urls = list(df['urls'])
    multi_thread_parse(urls)
    df = merge_data(df, results, results_url)
    df = flag_key_terms(df)
    write_data(df)

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
html_text = requests.get(urls[248], headers=headers).text
soup = BeautifulSoup(html_text, 'html5lib')
search = soup.find_all('p', {'class':'Mt(15px) Lh(1.6)'})
for i in search:
    print(i)
    
    
    