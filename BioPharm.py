import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def generate_url(row):
    '''creates urls from .xlsx for scraping'''
    url = f'https://finance.yahoo.com/quote/{row}/profile?p={row}'
    return url

def parse(url):
    '''scrapes company descriptions from yahoo finance html using beautiful soup'''
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, 'html5lib')
    search = soup.find_all('p', {'class':'Mt(15px) Lh(1.6)'})
    results_url.append(url)
    if search == []:
        results.append('No Profile available')
    else:
        results.append(search[0].text)

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

df['urls'] = np.vectorize(generate_url)(df['Ticker'])
urls = list(df['urls'])

results = []
results_url = []

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

# get next item in queue until there are none left
# "with" statement ensures threads are cleaned up promptly
with ThreadPoolExecutor() as executor:
    future = executor.map(parse, urls)

#clean up and merge results
results_df = pd.DataFrame(zip(results, results_url), 
                          columns =['Description', 'urls'])
df = df.merge(results_df)
df.drop(df[df['Description']=='No Profile available'].index, inplace=True)

#flag key terms
pattern = "phase\s{1,}3"
pattern2 = "phase\s{1,}I{3}"
pattern3 = "phase\s{1,}2"
pattern4 = "phase\s{1,}I{2}"
pattern5 = "alzheimer"

df['Phase 3 Ready'] = np.where(df['Description'].str.contains(pattern, case=False) | 
                         df['Description'].str.contains(pattern2, case=False), 1, 0)

df['Phase 2b Ready'] = np.where(df['Description'].str.contains(pattern3, case=False) | 
                         df['Description'].str.contains(pattern4, case=False), 1, 0)

df['alzheimer'] = np.where(df['Description'].str.contains(pattern5, case=False), 1, 0)

df.to_csv('stock_info.csv', index=False)