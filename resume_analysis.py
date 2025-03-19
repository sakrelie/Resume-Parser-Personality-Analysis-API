import PyPDF2
import os
from ibm_watson import PersonalityInsightsV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def extract_text_from_pdf(pdf_path):
    """Extract text from a given PDF file."""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text.replace('o ', '').replace('|', '')

def analyze_personality(text, api_key, url):
    """Analyze personality traits using IBM Watson Personality Insights."""
    authenticator = IAMAuthenticator(api_key)
    personality_insights = PersonalityInsightsV3(
        version='2017-10-13',
        authenticator=authenticator
    )
    personality_insights.set_service_url(url)
    
    profile = personality_insights.profile(text, accept='application/json').get_result()
    return profile

def visualize_results(profile):
    """Generate a bar chart visualization for personality needs."""
    needs = profile.get('needs', [])
    result = {need['name']: need['percentile'] for need in needs}
    df = pd.DataFrame.from_dict(result, orient='index')
    df.reset_index(inplace=True)
    df.columns = ['Need', 'Percentile']
    
    plt.figure(figsize=(15,5))
    sns.barplot(y='Percentile', x='Need', data=df).set_title('Needs Analysis')
    plt.show()


