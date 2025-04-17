#for adding the sentence context to the entities in pkl files
import os
import pickle
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')  # For sentence splitting

TXT_DIR = "TPT/TXTs"
PKL_DIR = "TPT/Entities"
OUTPUT_DIR = "TPT/EntitiesWithContext"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_word_context_window(text, start_char, end_char, window_size=3):
    """
    Returns ±`window_size` words around the entity based on its character span.
    """
    tokens = word_tokenize(text)
    
    # Map character positions to token index
    char_index = 0
    token_spans = []
    for token in tokens:
        char_index = text.find(token, char_index)
        token_spans.append((token, char_index, char_index + len(token)))
        char_index += len(token)

    # Find the token index where the entity starts
    target_index = None
    for i, (_, start, end) in enumerate(token_spans):
        if start <= start_char < end:
            target_index = i
            break

    if target_index is None:
        return ""  # fallback

    # Get surrounding tokens
    start_idx = max(0, target_index - window_size)
    end_idx = min(len(tokens), target_index + window_size + 1)

    return " ".join(tokens[start_idx:end_idx])

def attach_sentences_to_entities(txt_path, pkl_path, out_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()

    with open(pkl_path, "rb") as f:
        entities = pickle.load(f)

    for entity in entities:
        start = entity.get("start", -1)
        end = entity.get("end", -1)

        if start >= 0:
            entity["sentence"] = get_word_context_window(text, start,end, window_size=3)

    # Save updated entities
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        pickle.dump(entities, f)

def batch_process():
    for root, dirs, files in os.walk(PKL_DIR):
        for file in files:
            if file.endswith(".pkl"):
                rel_path = os.path.relpath(os.path.join(root, file), PKL_DIR)
                pkl_path = os.path.join(PKL_DIR, rel_path)
                txt_path = os.path.join(TXT_DIR, rel_path.replace(".pkl", ".txt"))
                out_path = os.path.join(OUTPUT_DIR, rel_path)

                if os.path.exists(txt_path):
                    attach_sentences_to_entities(txt_path, pkl_path, out_path)
                    print(f"✅ Context added: {rel_path}")
                else:
                    print(f"⚠️ Missing text file: {rel_path}")

batch_process()
