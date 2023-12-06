# URL Crawler Tool

## Overview

The URL Crawler Tool is a versatile Python script designed to crawl and extract URLs from a given starting URL. It is equipped with features to explore both HTML and JSON data, making it suitable for a wide range of web scraping scenarios.

## Features

1. **Initial URL Input:**
   - The tool accepts an initial URL using the `-u` or `--url` command-line argument.

2. **Custom Headers:**
   - Users can provide custom headers using the `-H` or `--header` command-line argument. This allows for flexibility in making requests with specific headers.

3. **URL Extraction from HTML:**
   - The tool extracts URLs from HTML content, focusing on `<a>` (anchor) tags and `<script>` tags. Additional tags can be included as needed.

4. **URL Extraction from JSON:**
   - JSON responses are processed, and URLs are extracted from string values. Users can customize the extraction logic within the `extract_urls_from_json` function.

5. **Domain-based Crawling:**
   - URLs are categorized into same-domain and different-domain sets. The tool performs recursive crawling on same-domain URLs to explore deeper levels.

6. **Sorting Results:**
   - Results are sorted alphabetically for better readability.

7. **Console Output Formatting:**
   - The tool uses `end='\r'` for console output to provide a cleaner and more dynamic display, especially during processing.

## Usage

```bash
python linkfinder.py -u <initial_url> -H "Header1: Value1" -H "Header2: Value2"
