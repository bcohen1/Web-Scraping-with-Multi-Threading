import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def clean_csv():
    """returns cleaned and properly formatted df from original .csv"""
    df = pd.read_csv("screener_results.csv")
    df = df[
        [
            "Symbol",
            "Company Name",
            "Security Type",
            "Security Price",
            "Market Capitalization",
        ]
    ]
    df.rename(
        columns={
            "Symbol": "Ticker",
            "Company Name": "Company",
            "Security Type": "Type",
            "Security Price": "Price",
            "Market Capitalization": "Market Cap",
        },
        inplace=True,
    )
    df.drop(df[df["Type"] != "Common Stock"].index, inplace=True)
    # df.drop(df[df['Price']<=1.0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def generate_url(ticker):
    """returns formatted url used for scraping"""
    return f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"


def create_urls(df):
    """returns url list by calling "generate_url" for all tickers in .csv"""
    df["urls"] = np.vectorize(generate_url)(df["Ticker"])
    return df


def scrape_url(url):
    """scrapes company descriptions from yahoo finance html using beautiful soup"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, "html5lib")
    search = soup.find_all("p", {"class": "Mt(15px) Lh(1.6)"})
    if search == []:
        return "No Profile available"
    else:
        return search[0].text


def multi_thread_parse(urls):
    """gets next url in queue and calls "scrape_url" until queue is empty"""
    # "with" statement ensures threads are cleaned up promptly
    with ThreadPoolExecutor() as executor:
        return executor.map(scrape_url, urls)


def flag_key_terms(df):
    '''returns df with new columns that flag key terms in "Description"'''
    pattern = r"phase\s{1,}3"
    pattern2 = r"phase\s{1,}I{3}"
    pattern3 = r"phase\s{1,}2"
    pattern4 = r"phase\s{1,}I{2}"
    pattern5 = r"alzheimer"

    df["Phase 3 Ready"] = np.where(
        df["Description"].str.contains(pattern, case=False)
        | df["Description"].str.contains(pattern2, case=False),
        1,
        0,
    )

    df["Phase 2b Ready"] = np.where(
        df["Description"].str.contains(pattern3, case=False)
        | df["Description"].str.contains(pattern4, case=False),
        1,
        0,
    )

    df["alzheimer"] = np.where(
        df["Description"].str.contains(pattern5, case=False), 1, 0
    )
    return df


def main():
    df = clean_csv()
    df = create_urls(df)
    urls = list(df["urls"])
    results = []
    for result in multi_thread_parse(urls):
        results.append(result)
    df['Description'] = results
    df = flag_key_terms(df)
    df.to_csv("stock_info.csv", index=False)


if __name__ == "__main__":
    main()
