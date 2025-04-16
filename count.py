import os

directory = "TPT/TXTs"
count = sum(len([file for file in files if file.endswith(".txt")]) for _, _, files in os.walk(directory))

print(f"Total .txt files: {count}")