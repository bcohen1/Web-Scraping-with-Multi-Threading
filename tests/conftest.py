import pytest
import biopharm


@pytest.fixture(scope="session")
def test_df():
    return biopharm.generate_clean_csv()


@pytest.fixture(scope="session")
def test_df_url(test_df):
    return biopharm.create_urls(test_df)


@pytest.fixture(scope="session")
def sample_multi_thread_result():
    results = [
        "Nymox Pharmaceutical Corporation, a biopharmaceutical company, engages in the research and development of drugs for the aging population in Canada, the United States, Europe, and internationally. Its lead drug candidate is Fexapotide Triflutate (NX-1207), which has completed Phase III clinical trials for the treatment of benign prostatic hyperplasia, and Phase II clinical trials for low grade localized prostate cancer, as well as is in preclinical studies for hepatocellular carcinoma. The company also develops and markets NicAlert and TobacAlert test strips that use urine or saliva to detect use of tobacco products. In addition, it offers AlzheimAlert, a proprietary urine assay that aids physicians in the diagnosis of Alzheimer's disease. The company was founded in 1989 and is headquartered in Nassau, The Bahamas.",
        "No Profile available",
    ]
    results_url = [
        "https://finance.yahoo.com/quote/NYMX/profile?p=NYMX",
        "https://finance.yahoo.com/quote/PMCBD/profile?p=PMCBD",
    ]
    return results, results_url


@pytest.fixture(scope="session")
def test_df_merged(test_df_url, sample_multi_thread_result):
    results, results_url = sample_multi_thread_result
    return biopharm.merge_data(test_df_url, results, results_url)


@pytest.fixture(scope="session")
def test_df_flagged(test_df_merged):
    return biopharm.flag_key_terms(test_df_merged)
