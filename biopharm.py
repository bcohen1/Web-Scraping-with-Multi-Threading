import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def load_fidelity_csv(file, input_dir):
    """returns cleaned and properly formatted df from Fidelity .csv"""
    df = pd.read_csv(input_dir + f"{file}.csv")

    col_mapping = {
        "Symbol": "Ticker",
        "Company Name": "Company",
        "Security Type": "Type",
        "Security Price": "Price",
        "Market Capitalization": "Market Cap",
    }

    df = df[col_mapping.keys()]
    df.rename(columns=col_mapping, inplace=True)
    df.drop(df[df["Type"] != "Common Stock"].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def generate_url(ticker):
    """returns formatted url used for scraping"""
    return f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"


def create_urls(tickers):
    """returns url list by calling generate_url() on all provided tickers"""
    urls = np.vectorize(generate_url)(tickers)
    return urls


def scrape_yahoo_finance(url):
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
    """gets next url in queue and calls scrape_yahoo_finance() until queue is empty"""
    with ThreadPoolExecutor() as executor:
        return executor.map(scrape_yahoo_finance, urls)


def flag_key_terms(df, key_terms):
    """returns df with new columns that flag key terms in 'Description'"""
    for key, value in key_terms.items():
        df[key] = np.where(
            df["Description"].str.contains(value, case=False),
            1,
            0,
        )
    return df


def main(file, input_dir, output_dir, key_terms_list=None, ticker_list=None):
    try:
        df = load_fidelity_csv(file, input_dir)
        tickers = df["Ticker"]
    except FileNotFoundError:
        tickers = ticker_list
        df = pd.DataFrame()
    urls = create_urls(tickers)
    df["Description"] = list(multi_thread_parse(urls))
    key_terms = {
        "phase_3": r"phase(?:\s{1,}3|\s{1,}I{3})",
        "phase_2": r"phase(?:\s{1,}2|\s{1,}I{2})"
    }
    [key_terms.update({term: term}) for term in key_terms_list]
    df = flag_key_terms(df, key_terms)
    df.to_csv(output_dir + "stock_info.csv", index=False)


if __name__ == "__main__":
    main("screener_results", "", "", key_terms_list=["alzheimer"])
