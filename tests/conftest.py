import pytest
import biopharm


@pytest.fixture
def test_df():
    return biopharm.load_fidelity_csv("screener_results", "")


@pytest.fixture
def test_urls(test_df):
    tickers = test_df["Ticker"]
    return biopharm.create_urls(tickers)


@pytest.fixture
def sample_multi_thread_result():
    results = [
        "Nymox Pharmaceutical Corporation, a biopharmaceutical company, engages in the research and development of drugs for the aging population in Canada, the United States, Europe, and internationally. Its lead drug candidate is Fexapotide Triflutate (NX-1207), which has completed Phase III clinical trials for the treatment of benign prostatic hyperplasia, and Phase II clinical trials for low grade localized prostate cancer, as well as is in preclinical studies for hepatocellular carcinoma. The company also develops and markets NicAlert and TobacAlert test strips that use urine or saliva to detect use of tobacco products. In addition, it offers AlzheimAlert, a proprietary urine assay that aids physicians in the diagnosis of Alzheimer's disease. The company was founded in 1989 and is headquartered in Nassau, The Bahamas.",
        "No Profile available",
    ]
    return results


@pytest.fixture
def sample_key_terms():
    key_terms = {
        "phase_3": r"phase(?:\s{1,}3|\s{1,}I{3})",
        "phase_2": r"phase(?:\s{1,}2|\s{1,}I{2})",
        "alzheimer": r"alzheimer"
    }
    return key_terms
