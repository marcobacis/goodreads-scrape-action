import json
import sys
import os
from datetime import datetime, date

import goodreads

if len(sys.argv) <= 3:
    print("Usage: {} <user> <shelf> <output-path>".format(sys.argv[0]))
    sys.exit("Wrong number of arguments")

def load_existing(path):
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)["books"] or []
    except FileNotFoundError:
        return [] 
    except json.JSONDecodeError:
        print("Warning: existing file is not valid JSON. It will be overwritten.")
        return []

def normalized_json(content):
    def normalize_book(book):
        return {
            k: v.isoformat() if isinstance(v, (date, datetime)) else v
            for k, v in book.items()
        }

    normalized = sorted([normalize_book(b) for b in content], key=lambda b: b["title"])
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, indent=2)

user = sys.argv[1]
shelf = sys.argv[2]
output_path = sys.argv[3]

output_path = os.path.join("/github/workspace", output_path)

old_books = load_existing(output_path)
books = goodreads.get_books(user, shelf)

if normalized_json(old_books) == normalized_json(books):
    print("No Changes detected. File not updated")
    sys.exit(0)

# Write the new data
with open(output_path, "w", encoding="utf-8") as f:
    new_data = {
        "lastmod": datetime.now().isoformat(),
        "books": books,
    }
    json.dump(new_data, f, ensure_ascii=False, sort_keys=True, indent=2, default=str)
    print(f"File '{output_path}' updated.")
