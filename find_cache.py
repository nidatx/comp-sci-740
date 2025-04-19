import os
import pandas as pd
import json
from collections import defaultdict
def find_cached_links(dir, website, output_file="curr_cache.txt"):
    mismatched_websites = set()
    logs = os.listdir(dir)
    for filename in logs:
        if filename.endswith(".csv"):
            file_path = os.path.join(dir, filename)
            # website,timestamp,action,duration,user
            df = pd.read_csv(file_path, header=None)
            df = df[1:]
            df.columns = ['website', 'timestamp', 'action', 'duration', 'user']
            mismatches = df[df['website'] != website]['website'].dropna()
            mismatched_websites.update(mismatches)

    with open(output_file, 'w', encoding='utf-8') as f:
        for website in sorted(mismatched_websites):
            f.write(website + '\n')
    print(f"Found {len(mismatched_websites)} mismatched websites.")
    return list(mismatched_websites) # use this filepath instead of the original one to pick websites from the cache

def read_websites_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        websites = [line.strip() for line in f if line.strip()]
    print(f"Read {len(websites)} websites from {file_path}")
    print(websites)
    return websites

def save_cache(cache_dict, output_path="google_search_cache.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cache_dict, f, indent=2)
        
def build_google_search_cache(log_dir, website):
    cache = defaultdict()
    current_search = None
    logs = os.listdir(log_dir)

    for filename in logs:
        if filename.endswith(".csv"):
            file_path = os.path.join(log_dir, filename)
            df = pd.read_csv(file_path)
            for i, row in df.iterrows():
                if row['action'] == "search":
                    cache[row['duration']] = []
                    current_search = row['duration']
                    # current_search = row['duration']
                elif row['action'] == 'open_website' and row['website'] != website:
                    cache[current_search].append(row['website'])
    save_cache(cache, output_path="google_search_cache.json")
    print(f'Saved cache to google_search_cache.json: {cache}')
    return cache





def load_cache(input_path="google_search_cache.json"):
    if not os.path.exists(input_path):
        return {}
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)