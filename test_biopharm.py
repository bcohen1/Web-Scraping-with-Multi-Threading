import pytest
import biopharm
import os.path

@pytest.fixture(scope='session')
def test_df():
    return biopharm.generate_clean_xlsx()

@pytest.fixture(scope='session')
def test_df_url(test_df):
    return biopharm.create_urls(test_df)

@pytest.fixture(scope='session')
def sample_parse_html_result():
    results = ["Nymox Pharmaceutical Corporation, a biopharmaceutical company, engages in the research and development of drugs for the aging population in Canada, the United States, Europe, and internationally. Its lead drug candidate is Fexapotide Triflutate (NX-1207), which has completed Phase III clinical trials for the treatment of benign prostatic hyperplasia, and Phase II clinical trials for low grade localized prostate cancer, as well as is in preclinical studies for hepatocellular carcinoma. The company also develops and markets NicAlert and TobacAlert test strips that use urine or saliva to detect use of tobacco products. In addition, it offers AlzheimAlert, a proprietary urine assay that aids physicians in the diagnosis of Alzheimer's disease. The company was founded in 1989 and is headquartered in Nassau, The Bahamas.", "No Profile available"]
    results_url = ["https://finance.yahoo.com/quote/NYMX/profile?p=NYMX","https://finance.yahoo.com/quote/PMCBD/profile?p=PMCBD"]
    return results, results_url

@pytest.fixture(scope='session')
def sample_multi_thread_result():
    results = ["Nymox Pharmaceutical Corporation, a biopharmaceutical company, engages in the research and development of drugs for the aging population in Canada, the United States, Europe, and internationally. Its lead drug candidate is Fexapotide Triflutate (NX-1207), which has completed Phase III clinical trials for the treatment of benign prostatic hyperplasia, and Phase II clinical trials for low grade localized prostate cancer, as well as is in preclinical studies for hepatocellular carcinoma. The company also develops and markets NicAlert and TobacAlert test strips that use urine or saliva to detect use of tobacco products. In addition, it offers AlzheimAlert, a proprietary urine assay that aids physicians in the diagnosis of Alzheimer's disease. The company was founded in 1989 and is headquartered in Nassau, The Bahamas.", "No Profile available"]
    results_url = ["https://finance.yahoo.com/quote/NYMX/profile?p=NYMX","https://finance.yahoo.com/quote/PMCBD/profile?p=PMCBD"]
    return results, results_url

@pytest.fixture(scope='session')
def test_df_merged(test_df_url, sample_multi_thread_result):
    results, results_url = sample_multi_thread_result
    return biopharm.merge_data(test_df_url, results, results_url)

@pytest.fixture(scope='session')
def test_df_flagged(test_df_merged):
    return biopharm.flag_key_terms(test_df_merged)

def test_generate_clean_xlsx():
    rv = biopharm.generate_clean_xlsx()
    assert len(rv.columns) == 5

def test_generate_url():
    rv = biopharm.generate_url('1')
    assert rv == 'https://finance.yahoo.com/quote/1/profile?p=1'
    
def test_create_urls(test_df):
    rv = biopharm.create_urls(test_df)
    assert len(rv) == len(test_df)

# def test_parse_html_pass(test_df_url):
#     assert 
    
# def test_parse_html_fail(test_df_url):
#     assert 

def test_merge_data(test_df_url, sample_multi_thread_result):
    results, results_url = sample_multi_thread_result
    rv = biopharm.merge_data(test_df_url, results, results_url)
    assert len(rv.columns) == len(test_df_url.columns) + 1

def test_merge_data_drop(test_df_url, sample_multi_thread_result):
    results, results_url = sample_multi_thread_result
    rv = biopharm.merge_data(test_df_url, results, results_url)
    assert len(rv.loc[rv['Description'] == 'No Profile available']) == 0

@pytest.mark.parametrize("column", ['Phase 3 Ready','Phase 2b Ready','alzheimer'])    
def test_flag_key_terms_columns(test_df_merged, column):
    rv = biopharm.flag_key_terms(test_df_merged)
    assert column in rv.columns
    
@pytest.mark.parametrize("column", ['Phase 3 Ready','Phase 2b Ready','alzheimer'])    
def test_flag_key_terms_values(test_df_merged, column):
    rv = biopharm.flag_key_terms(test_df_merged)
    assert len(rv.loc[rv[column] == 1]) > 0
    
def test_write_data(test_df_flagged):
    biopharm.write_data(test_df_flagged)
    assert os.path.exists('stock_info.csv')
