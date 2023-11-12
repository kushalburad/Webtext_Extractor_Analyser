import spacy
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_urls_and_text(url, num_urls=100):
    response = requests.get(url)
    results_df = pd.DataFrame(columns=["HTTP Link","word_count","noun_count","proper_noun_count","adjective_count","prepositions_count","verb_count","num_sentences"])

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        all_links = soup.find_all('a')
        extracted_urls = [link.get('href') for link in all_links if link.get('href')]
        valid_urls = [url for url in extracted_urls if url and url.startswith('http')][:num_urls]

        for i, url in enumerate(valid_urls, start=1):
            page_response = requests.get(url)

            if page_response.status_code == 200:
                page_soup = BeautifulSoup(page_response.text, 'html.parser')

                # Extract the text content from the page
                text_content = page_soup.get_text()

                result = analyse_text(text_content)
                
                new_row_data = {
                "HTTP Link": url,
                "word_count":result.get('word_count') ,
                "noun_count": result.get('noun_count'),
                "proper_noun_count": result.get('proper_noun_count'),
                "adjective_count": result.get('adjective_count'),
                "prepositions_count": result.get('prepositions_count'),
                "verb_count": result.get('verb_count'),
                "num_sentences": result.get('num_sentences')
            }

                results_df.loc[len(results_df)] = new_row_data

            else:
                print(f"Failed to retrieve content from {url}. Status code: {page_response.status_code}")
    
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return results_df    


def analyse_text(paragraph):
    doc = nlp(paragraph)
    
    word_count=len(doc)
    num_sentences = len(list(doc.sents))
    noun_count = sum(1 for token in doc if token.pos_ in ['NOUN', 'PROPN'])
    proper_noun_count = sum(1 for token in doc if token.pos_ in ['PROPN'])
    adjective_count = sum(1 for token in doc if token.pos_ in ['ADJ'])
    prepositions_count = sum(1 for token in doc if token.pos_ in ['ADP'])
    verb_count = sum(1 for token in doc if token.pos_ in ['VERB'])
   
    return {
        "word_count": len(doc),
        "noun_count": noun_count,
        "proper_noun_count": proper_noun_count,
        "adjective_count": adjective_count,
        "prepositions_count": prepositions_count,
        "verb_count": verb_count,
        "num_sentences": num_sentences,
    }

script_directory = os.path.dirname(os.path.abspath(__file__))

# Save the DataFrame to a CSV file in the same folder
csv_file_path_100_page_results = os.path.join(script_directory, "output_100_Page_results.csv")  # You can change the file name if needed
csv_file_path_Average_results = os.path.join(script_directory, "output_average.csv")

# Specify the HTTP Link of the website
result_df=extract_urls_and_text('https://www.medicalnewstoday.com/')
print(result_df)
result_df.to_csv(csv_file_path_100_page_results, index=False)

column_averages = pd.DataFrame(columns=["HTTP Link",
                                         "word_count",
                                         "noun_count",
                                         "proper_noun_count",
                                         "adjective_count",
                                         "prepositions_count",
                                         "verb_count",
                                         "num_sentences"])


column_averages.loc[1] = result_df.iloc[:, 1:].mean()

# Print column averages
print(column_averages)
column_averages.to_csv(csv_file_path_Average_results, index=False)
print(f"DataFrame saved to {csv_file_path_100_page_results}")
