import os
import pickle
from bertopic import BERTopic
from tqdm import tqdm
from nltk.corpus import stopwords
import re
import nltk
nltk.download('stopwords')


def clean_text(text):
    text = re.sub(r'\W+', ' ', text.lower())  # remove punctuation and lowercase
    words = [word for word in text.split() if word not in stop_words and len(word) > 2]
    return ' '.join(words)


# Directory paths
TXT_DIR = "TPT/TXTs"
TOPIC_DIR = "TPT/Topics"
os.makedirs(TOPIC_DIR, exist_ok=True)
stop_words = set(stopwords.words('turkish'))

def find_and_load_all_texts(txt_root):
    txt_paths, documents = [], []
    for root, _, files in os.walk(txt_root):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                txt_paths.append(path)
                with open(path, "r", encoding="utf-8") as f:
                    documents.append(clean_text(f.read()))
    return txt_paths, documents

from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic

def fit_topic_model(documents):
    print("📚 Fitting BERTopic model (Test Mode)...")

    # Parameters to play with
    '''too coarse'''
    # umap_model = UMAP(n_neighbors=30, n_components=5, metric='cosine')
    # hdbscan_model = HDBSCAN(min_cluster_size=50, min_samples=10, prediction_data=True)

    umap_model = UMAP(n_neighbors=15, n_components=10, metric='cosine')
    hdbscan_model = HDBSCAN(min_cluster_size=20, min_samples=5, prediction_data=True)


    topic_model = BERTopic(
        language="turkish",
        calculate_probabilities=True,
        verbose=True,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model
)

    topics, probs = topic_model.fit_transform(documents)
    print("✅ Model trained.")
    return topic_model, topics, probs



def save_topics(txt_paths, topics, probs):
    for path, topic, prob in tqdm(zip(txt_paths, topics, probs), total=len(txt_paths)):
        relative_path = os.path.relpath(path, TXT_DIR)
        pkl_path = os.path.join(TOPIC_DIR, relative_path.replace(".txt", ".pkl"))
        os.makedirs(os.path.dirname(pkl_path), exist_ok=True)
        try:
            with open(pkl_path, "wb") as f:
                pickle.dump({"topic": topic, "probability": prob}, f)
            print(f"✅ Saved: {pkl_path}")
        except Exception as e:
            print(f"❌ Error in {path}: {e}")


if __name__ == "__main__":
    nltk.download('stopwords')

    txt_paths, documents = find_and_load_all_texts(TXT_DIR)
    topic_model, topics, probs = fit_topic_model(documents)
    topic_model.save("bertopic_model_tpt")
    save_topics(txt_paths, topics, probs)
    print("🎉 All topics saved.")

      # Load the previously saved model
    topic_model = BERTopic.load("bertopic_model_tpt")

    # Print a summary of the topics
    print(topic_model.get_topic_info())

    # Optional: print detailed keywords per topic
    for topic_id in topic_model.get_topic_info()["Topic"]:
        if topic_id == -1:
            continue  # Skip outlier topic
        print(f"\nTopic {topic_id}:")
        print(topic_model.get_topic(topic_id))