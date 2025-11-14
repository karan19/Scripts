# Documentation Scraper

This repository contains a small utility script, `documentationScraper.py`, that crawls a documentation or marketing website, downloads the HTML content and linked images, and saves them locally. It can be helpful when you want an offline snapshot of a site for reference, archiving, or manual review.

## How it works

- Starts from a user-provided URL and restricts crawling to the same domain.
- Follows hyperlinks discovered in `<a>` tags (excluding common binary file types) and keeps a queue of pages to visit.
- Fetches HTML with `requests`, removes `<script>` and `<svg>` elements using `BeautifulSoup`, and writes each page to an `.html` file with the source URL embedded as a comment at the top.
- Downloads images referenced in `<img>` tags into an `images/` subdirectory alongside the HTML files.
- Records successfully crawled URLs in `crawled_urls.txt` and skipped or failed URLs in `not_crawled_urls.txt` inside the chosen output folder.

## Requirements

- Python 3.8+
- The following Python packages:
  - [`requests`](https://pypi.org/project/requests/)
  - [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)

Install the dependencies with:

```bash
pip install -r requirements.txt
```

> If you do not have a `requirements.txt`, you can install packages directly: `pip install requests beautifulsoup4`.

## Usage

1. Run the script from the repository root:
   ```bash
   python documentationScraper.py
   ```
2. When prompted, enter the starting URL you want to crawl.
3. Optionally provide a name for the output folder; press **Enter** to accept the suggested default (based on the domain).
4. The script will show progress in the console while it downloads pages and images. When it finishes, it prints the locations of:
   - Saved HTML files (inside the output directory)
   - Downloaded images (inside `output/images/`)
   - `crawled_urls.txt` (list of successfully downloaded pages)
   - `not_crawled_urls.txt` (pages that were skipped or returned errors)

## Potential use cases

- **Offline reference:** Capture documentation or marketing content to review without an internet connection.
- **Content backup:** Keep a point-in-time archive of public web pages that might change or be removed.
- **Compliance review:** Provide downloadable copies of external documentation for auditing or record keeping.
- **Research:** Collect publicly available pages and their assets for manual analysis.

Always respect the target website's terms of service and robots.txt guidelines before running a crawler.
