import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import threading
import queue
# from concurrent.futures import ThreadPoolExecutor

vals = pd.read_excel('screener_results.xls', sheet_name='Search Criteria')
vals.drop(vals.tail(17).index, inplace = True)
vals = vals[['Symbol', 'Company Name', 'Security Type', 'Security Price', 
         'Market Capitalization']]
vals.rename(columns={'Symbol':'Ticker', 'Company Name':'Company', 
        'Security Type':'Type', 'Security Price':'Price', 
        'Market Capitalization':'Market Cap'}, inplace=True)
vals.drop(vals[vals['Type']!='Common Stock'].index, inplace=True)
# vals.drop(vals[vals['Price']<=1.0].index, inplace=True)
vals.reset_index(drop=True, inplace=True)

def generate_url(row):
'''create urls for scraping'''
    url = 'https://finance.yahoo.com/quote/{}/profile?p={}'.format(row, row)
    return url

vals['URLs'] = np.vectorize(generate_url)(vals['Ticker'])
URLs = list(vals['URLs'])

results = []
results_url = []

def parse(url):
'''scrape company descriptions from yahoo finance html using beautiful soup'''
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html5lib')
    search = soup.find_all('p', {'class':'Mt(15px) Lh(1.6)'})
    results_url.append(url)
    if search == []:
        results.append('No Profile available')
    else:
        results.append(search[0].text)

# with ThreadPoolExecutor(max_workers=9) as executor:
#     results = executor.map(parse, URLs)

q = queue.Queue()

def worker():
'''get next item in queue until there are none left'''
    while True:
        item = q.get()
        if item is None:
            break
        parse(item)
        q.task_done()

#4 times number of cores + 1 for main
num_worker_threads = 17
threads=[]

#starts threads that are ended when script finishes
for _ in range(num_worker_threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    threads.append(t)

for item in URLs:
    q.put(item)

#block until all tasks are done
q.join()

#clean up results and flag key terms
results_df = pd.DataFrame(list(zip(results, results_url)),
               columns =['Description', 'URLs'])
vals = vals.merge(results_df)
vals.drop(vals[vals['Description']=='No Profile available'].index, inplace=True)
pattern = "phase\s{1,}3"
pattern2 = "phase\s{1,}I{3}"
pattern3 = "phase\s{1,}2"
pattern4 = "phase\s{1,}I{2}"
pattern5 = "alzheimer"

vals['Phase 3 Ready'] = [1 if re.search(pattern, vals['Description'].iloc[i], re.IGNORECASE) or 
                          re.search(pattern2, vals['Description'].iloc[i], re.IGNORECASE) else 0 
                          for i in range(len(vals['Description']))]
vals['Phase 2b Ready'] = [1 if re.search(pattern3, vals['Description'].iloc[i], re.IGNORECASE) or 
                          re.search(pattern4, vals['Description'].iloc[i], re.IGNORECASE) else 0 
                          for i in range(len(vals['Description']))]
vals['alzheimer'] = [1 if re.search(pattern5, vals['Description'].iloc[i], re.IGNORECASE) else 0 
                          for i in range(len(vals['Description']))]

vals.to_csv('stock_info.csv', index=False)
