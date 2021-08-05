import pytest
import biopharm
import os


def test_generate_clean_csv():
    rv = biopharm.generate_clean_csv()
    assert len(rv.columns) == 5


def test_generate_url():
    rv = biopharm.generate_url("1")
    assert rv == "https://finance.yahoo.com/quote/1/profile?p=1"


def test_create_urls(test_df):
    rv = biopharm.create_urls(test_df)
    assert len(rv) == len(test_df)


def test_merge_data(test_df_url, sample_multi_thread_result):
    results, results_url = sample_multi_thread_result
    rv = biopharm.merge_data(test_df_url, results, results_url)
    assert len(rv.columns) == len(test_df_url.columns) + 1


def test_merge_data_drop(test_df_url, sample_multi_thread_result):
    results, results_url = sample_multi_thread_result
    rv = biopharm.merge_data(test_df_url, results, results_url)
    assert len(rv.loc[rv["Description"] == "No Profile available"]) == 0


@pytest.mark.parametrize("column", ["Phase 3 Ready", "Phase 2b Ready", "alzheimer"])
def test_flag_key_terms_columns(test_df_merged, column):
    rv = biopharm.flag_key_terms(test_df_merged)
    assert column in rv.columns


@pytest.mark.parametrize("column", ["Phase 3 Ready", "Phase 2b Ready", "alzheimer"])
def test_flag_key_terms_values(test_df_merged, column):
    rv = biopharm.flag_key_terms(test_df_merged)
    assert len(rv.loc[rv[column] == 1]) > 0


def test_write_data(test_df_flagged):
    biopharm.write_data(test_df_flagged)
    assert os.path.exists("stock_info.csv")
