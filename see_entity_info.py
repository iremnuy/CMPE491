import pickle

# Path to your .pkl file
pkl_path = "TPT/EntitiesWithContext/d22-y1_txts/tbmm22013076.pkl"

# Load the entities
with open(pkl_path, "rb") as f:
    entities = pickle.load(f)

# Show the first 2 entities
for i, ent in enumerate(entities):
    print(f"Entity {i+1}:")
    for k, v in ent.items():
        print(f"  {k}: {v}")
    print("-" * 30)
