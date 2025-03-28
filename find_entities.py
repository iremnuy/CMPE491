import os
from transformers import pipeline
import pickle

'''
Requirements:
Put the TPT dataset in the same directory as the script.
'''

def load_texts(directory):
    texts = []
    # delete count
    count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.txt'):
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                    texts.append(f.read())
    return texts


# 1. Concat parliament texts
texts = load_texts('./TPT/TXTs')


#2. Extract entities (NER)

# Create an NER pipeline
ner_pipeline = pipeline("ner", model="akdeniz27/bert-base-turkish-cased-ner", aggregation_strategy="simple")


all_entities = []
for text in texts:
    # Run the NER pipeline on the text
    entities = ner_pipeline(text)
    print(entities)
    all_entities.extend(entities)
    print("Current entities:", entities)


print("Entity extraction complete")

#3. Save entities to file
with open('entities.pkl', 'wb') as f:
    pickle.dump(all_entities, f)
print("Entities saved to entities.pkl")


# Later, to load them without re-extraction:

'''
with open('entities.pkl', 'rb') as f:
    saved_entities = pickle.load(f)
print("Loaded entities:", saved_entities)
'''