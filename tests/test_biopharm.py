import pytest
import biopharm
import responses
import requests
import pandas as pd


def test_load_fidelity_csv():
    rv = biopharm.load_fidelity_csv("screener_results", "")
    assert len(rv.columns) == 5


def test_generate_url():
    rv = biopharm.generate_url("1")
    assert rv == "https://finance.yahoo.com/quote/1/profile?p=1"


def test_create_urls(test_df):
    rv = biopharm.create_urls(test_df)
    assert len(rv) == len(test_df)


@responses.activate
def test_scrape_yahoo_fiannce():
    url = biopharm.generate_url("1")
    responses.add(
        responses.GET, url=url, body="{}", status=200, content_type="application/json"
    )
    resp = requests.get(url)
    assert resp.status_code == 200


@pytest.mark.parametrize("column", ["phase_3", "phase_2", "alzheimer"])
def test_flag_key_terms_columns(
    test_df, sample_multi_thread_result, sample_key_terms, column
):
    test_df["Description"] = pd.Series(sample_multi_thread_result)
    rv = biopharm.flag_key_terms(test_df, sample_key_terms)
    assert column in rv.columns


@pytest.mark.parametrize("column", ["phase_3", "phase_2", "alzheimer"])
def test_flag_key_terms_values(
    test_df, sample_multi_thread_result, sample_key_terms, column
):
    test_df["Description"] = pd.Series(sample_multi_thread_result)
    rv = biopharm.flag_key_terms(test_df, sample_key_terms)
    assert len(rv.loc[rv[column] == 1]) > 0
