import os
import re
import pickle
import requests
import logging
from bs4 import BeautifulSoup
logging.basicConfig(
    level=logging.INFO,
    filename='logs/wikisearch.log',  # Save to a file
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def merge_subword_entities(entities):
    merged = []
    current = None
    for ent in entities:
        word = ent["word"]
        group = ent.get("entity_group")
        if word.startswith("##") and current and current.get("entity_group") == group:
            current["word"] += word[2:]
            current["end"] = ent["end"]
        else:
            if current:
                merged.append(current)
            current = ent.copy()
    if current:
        merged.append(current)
    return merged

def extract_period_from_path(pickle_path):
    # Expecting path like ".../d22-y3/filename.pkl"
    match = re.search(r'd(\d+)-y\d+', pickle_path)
    if match : 
        print(f"Extracted period from path: {match.group(1)}")
        return int(match.group(1))
    else:
        print("No period found in path")
        return None
    
def find_person_uri_in_member_list(name, period): #if person is found within a wiki page, extract the hyperlink 
    url = f"https://tr.wikipedia.org/wiki/TBMM_{period}._dönem_milletvekilleri_listesi"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a")
        for link in links:
            text = link.get_text().strip().lower()
            if name.lower() in text:
                href = link.get("href")
                if href and href.startswith("/wiki/") and not href.startswith("/wiki/TBMM_"):
                    return f"https://tr.wikipedia.org{href}"

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def search_in_member_list(name, period):
    url = f"https://tr.wikipedia.org/wiki/TBMM_{period}._dönem_milletvekilleri_listesi"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, "html.parser")
        # Check if name is mentioned
        links = soup.find_all("a")
        for link in links:
            if name.lower() in link.get_text().lower():
                href = link.get("href")
                if href and href.startswith("/wiki/"):
                    return f"https://tr.wikipedia.org{href}"
        return None
    except Exception as e:
        print(f"Error searching Wikipedia member list: {e}")
        return None

def person_in_member_list(name, html_text):
    return name.lower() in html_text.lower()

def get_member_list(period):
    url = f"https://tr.wikipedia.org/wiki/TBMM_{period}._dönem_milletvekilleri_listesi"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        logger.info(f"Fetched member list for period {period}, list is  \n ************ \n {soup.get_text()}")
        return soup.get_text()
    except Exception as e:
        print(f"Error fetching member list: {e}")
        return None

def search_wikipedia(query, lang="tr"):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    response = requests.get(url, params=params)
    results = response.json().get("query", {}).get("search", [])
    return results

# ==== Main ====
entity_file_path = "TPT/EntitiesWithContext/d22-y1_txts/tbmm22002019.pkl" #TODO: word contextli tokenization çok uzun sürdü yarım bıraktım tamamlayacağım
period = extract_period_from_path(entity_file_path)

# Load entities
with open(entity_file_path, "rb") as f:
    saved_entities = pickle.load(f)

# Merge BERT subwords
merged_entities = merge_subword_entities(saved_entities)

# Load HTML once for the member list
html_members = get_member_list(period) if period else None

# Loop over entities
for ent in merged_entities:
    if ent.get("entity_group") == "PER":
        name = ent["word"]
        sentence= ent.get("sentence")
        print(f"\n🔍 Checking: {name}")

        if html_members and person_in_member_list(name, html_members): #if there are members and the name is in the list
            wiki_title = f"TBMM {period}. dönem milletvekilleri listesi"
            #https://tr.wikipedia.org/wiki/TBMM_22._dönem_milletvekilleri_listesi
            print(f"✅ Found in list → https://tr.wikipedia.org/wiki/{wiki_title.replace(' ', '_')}")
            # return the uri of this person in the page  then 
            person_uri=find_person_uri_in_member_list(name, period)
            if person_uri:
                print(f"🔗 Found member link: {person_uri}")
            else:
                print("❌ Member link not found.")




        else:
            # Fallback to full-text search
            query = f"{name} {sentence}." 
            print(f"🔁 Not in list, searching: {query}")
            results = search_wikipedia(query)
            for r in results[:3]:
                print(f"🔗 https://tr.wikipedia.org/wiki/{r['title'].replace(' ', '_')}")
