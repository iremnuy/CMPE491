import os
from transformers import pipeline
from multiprocessing import Pool, cpu_count
import pickle

'''
This script extracts and saves entities into different files (based on legislative period and year) for time series data.
Uses multiprocessing to speed up the process.
The entities are saved in the TPT/Entities directory.

Requirements:
Put the TPT dataset in the same directory as the script.

'''


# Configuration
TXT_DIR = "TPT/TXTs"
ENTITY_DIR = "TPT/Entities"
MODEL_NAME = "akdeniz27/bert-base-turkish-cased-ner"
AGG_STRATEGY = "simple"


os.makedirs(ENTITY_DIR, exist_ok=True)

# 1 Find all text file directories
def find_all_text_files(txt_root):
    txt_paths = []
    for root, dirs, files in os.walk(txt_root):
        for file in files:
            if file.endswith(".txt"):
                full_path = os.path.join(root, file)
                txt_paths.append(full_path)
    return txt_paths

# 2 Process a single file and save entities
def process_file(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Create 
        #  inside worker process
        ner_pipeline = pipeline("ner", model=MODEL_NAME, aggregation_strategy=AGG_STRATEGY)
        entities = ner_pipeline(text)

        # Define output .pkl path, mirroring folder structure
        relative_path = os.path.relpath(txt_path, TXT_DIR)
        pkl_path = os.path.join(ENTITY_DIR, relative_path.replace(".txt", ".pkl"))

        # Create subfolders if needed
        os.makedirs(os.path.dirname(pkl_path), exist_ok=True)

        # Save entities
        with open(pkl_path, "wb") as f:
            pickle.dump(entities, f)

        print(f"✅ Saved: {pkl_path}")
        return True

    except Exception as e:
        print(f"❌ Error in {txt_path}: {e}")
        return False


if __name__ == "__main__":
    txt_files = find_all_text_files(TXT_DIR)
    print(f"📄 Found {len(txt_files)} .txt files")

    with Pool(processes=4) as pool:
        pool.map(process_file, txt_files)

    print("✅ All entity files saved under:", ENTITY_DIR)

