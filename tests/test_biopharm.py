import pytest
import biopharm
import pandas as pd


def test_clean_csv():
    rv = biopharm.clean_csv()
    assert len(rv.columns) == 5


def test_generate_url():
    rv = biopharm.generate_url("1")
    assert rv == "https://finance.yahoo.com/quote/1/profile?p=1"


def test_create_urls(test_df):
    rv = biopharm.create_urls(test_df)
    assert len(rv) == len(test_df)


@pytest.mark.parametrize("column", ["Phase 3 Ready", "Phase 2b Ready", "alzheimer"])
def test_flag_key_terms_columns(test_df_url, sample_multi_thread_result, column):
    test_df_url['Description'] = pd.Series(sample_multi_thread_result)
    rv = biopharm.flag_key_terms(test_df_url)
    assert column in rv.columns


@pytest.mark.parametrize("column", ["Phase 3 Ready", "Phase 2b Ready", "alzheimer"])
def test_flag_key_terms_values(test_df_url, sample_multi_thread_result, column):
    test_df_url['Description'] = pd.Series(sample_multi_thread_result)
    rv = biopharm.flag_key_terms(test_df_url)
    assert len(rv.loc[rv[column] == 1]) > 0
