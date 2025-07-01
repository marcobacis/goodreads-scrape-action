# Goodreads Scrape Action

Action to scrape a specific goodreads books shelf and export the data as json


## Usage

Example usage in workflow:
```yaml
name: Update books list
on:
  schedule:
    - cron: '0 0 * * *'
permissions:
  contents: write 

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # checkout and do other stuff

      - uses: marcobacis/goodreads-scrape-actions@v0.1.0
        with:
          user: "22830084"
          shelf: "currently-reading"
          output_path: "output.json"
    
      # other, e.g. commit output file
```