# VNNewsToJSON

A Python web scraper for Vietnamese news websites that extracts article content and metadata, outputting structured JSON data.

## Features

- **Multi-site support**: Scrapes 11 major Vietnamese news websites
- **Flexible content extraction**: Word limit, paragraph count, or random paragraph selection
- **Structured output**: JSON format with metadata (title, author, date, description, etc.)
- **Batch processing**: Handle single URLs or lists of URLs
- **Smart parsing**: Site-specific selectors and JSON-LD metadata extraction
- **Vietnamese text handling**: Proper Unicode support and text cleaning

## Supported Websites

- VnExpress (`vnexpress.net`)
- Tuổi Trẻ (`tuoitre.vn`)
- Thanh Niên (`thanhnien.vn`)
- Kenh14 (`kenh14.vn`)
- Soha (`soha.vn`)
- Gamek (`gamek.vn`)
- TheAnh28 (`theanh28.vn`)
- Báo Chính Phủ (`chinhphu.vn`)
- VietnamNet (`vietnamnet.vn`)
- Lao Động (`laodong.vn`)
- Dan Tri (`dantri.com.vn`)

## Installation

```bash
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Usage

```python
from scrapper import Scrappers

# Simple scraping
url = "https://vnexpress.net/example-article.html"
sc = Scrappers()
result = sc(url)
sc.WriteJSON("output/", "article_data")
```

### Configuration Options

```python
# Word limit (extract first 100 words)
sc = Scrappers(word_limit=100)

# Paragraph limit (extract first 3 paragraphs)
sc = Scrappers(paragraphs=3)

# Random paragraphs (3 consecutive random paragraphs)
sc = Scrappers(paragraphs=3, take_random=True)

# Word limit takes precedence over paragraphs
sc = Scrappers(word_limit=150, paragraphs=5)  # Only word_limit applies
```

### Batch Processing

```python
urls = [
    "https://vnexpress.net/article1.html",
    "https://tuoitre.vn/article2.html",
    "https://thanhnien.vn/article3.html"
]

sc = Scrappers(word_limit=150)
sc(urls, "Data/")  # Automatically saves with numbered filenames
```

## Output Format

Each scraped article produces a JSON file with the following structure:

```json
{
    "author": "VnExpress",
    "copyright": "VnExpress",
    "date_published": "2025-07-11T16:26:06+07:00",
    "date_modified": "2025-07-11T22:44:48+07:00",
    "language": "vi-VN",
    "source": "vnexpress",
    "title": "Article Title",
    "description": "Article description/summary",
    "paragraphs": "Main article content...",
    "url": "https://vnexpress.net/example.html",
    "image": "https://example.com/image.jpg",
    "label": "..."
}
```

## API Reference

### Scrappers Class

```python
class Scrappers:
    def __init__(self, word_limit=None, paragraphs=None, take_random=False):
        """
        Initialize scraper with content extraction options.
        
        Args:
            word_limit (int): Maximum words to extract (overrides paragraphs)
            paragraphs (int): Number of paragraphs to extract  
            take_random (bool): Take random consecutive paragraphs
        """
```

### Methods

- `__call__(url, folder=None)`: Main scraping method
  - Single URL: Returns scraped data dict
  - URL list: Requires folder parameter, saves files automatically

- `WriteJSON(path, filename)`: Save scraped data to JSON file

- `run_and_write(urls, folder)`: Batch process URLs and save results

## Examples

### Extract First 200 Words

```python
sc = Scrappers(word_limit=200)
sc("https://vnexpress.net/example.html")
sc.WriteJSON("output/", "vnexpress_200words")
```

### Extract Random Paragraphs

```python
sc = Scrappers(paragraphs=5, take_random=True)
sc("https://tuoitre.vn/example.html")
sc.WriteJSON("output/", "tuoitre_random")
```

### Process Multiple Sites

```python
urls = [
    "https://vnexpress.net/politics-news.html",
    "https://thanhnien.vn/sports-news.html",
    "https://kenh14.vn/entertainment-news.html"
]

sc = Scrappers(word_limit=150)
sc(urls, "Data/")  # Saves as site_1.json, site_2.json, etc.
```

## Technical Details

- Uses `requests.Session` with Vietnamese user agent
- BeautifulSoup with lxml parser for HTML processing
- Site-specific CSS selectors for content extraction
- JSON-LD metadata parsing for structured data
- Automatic text cleaning and Unicode normalization

## License

This project is for educational and research purposes. Please respect the terms of service of the websites you scrape.
