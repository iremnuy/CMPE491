import pickle
import requests

# --- Wikipedia search function ---
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
    return [r["title"] for r in results]

# --- Load entities from pickle file ---
entity_file_path = "TPT/EntitiesWithContext/d22-y1_txts/tbmm22016fih.pkl"
with open(entity_file_path, "rb") as f:
    entities = pickle.load(f)

# --- Loop and search only for persons ---
for ent in entities[:]:  # test with first 10 entities
    if ent.get("entity_group") == "PER":
        word = ent["word"].replace("##", "").strip()
        sentence = ent.get("sentence", "")
        query = f"{word} {sentence}"

        print(f"\n🔍 Searching for: {query}")
        results = search_wikipedia(query)

        for title in results:
            print(f"🔗 https://tr.wikipedia.org/wiki/{title.replace(' ', '_')}")
