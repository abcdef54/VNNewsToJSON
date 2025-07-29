import requests
from typing import Dict, Any, List, Tuple
import json
from bs4 import BeautifulSoup
from pathlib import Path
import os
import re
import time
import random

class Scrappers:
   session = requests.Session()
   session.headers.update({
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
   "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
   })

   # Configuration for different sites
   SITE_CONFIG = {
      'vnexpress.net': {
         'paragraph_selector': 'article.fck_detail',
      },
      'tuoitre.vn': {
         'paragraph_selector': 'div[itemprop="articleBody"]',
      },
      'thanhnien.vn': {
         'paragraph_selector': 'div[itemprop="articleBody"]',
      },
      'kenh14.vn': {
         'paragraph_selector': 'div.detail-content.afcbc-body',
      },
      'soha.vn': {
         'paragraph_selector': 'div.detail-content.afcbc-body',
      },
      'gamek.vn': {
         'paragraph_selector': 'div.rightdetail_content.detailsmallcontent',
      },
      'theanh28.vn': {
         'paragraph_selector': 'div.message-content.js-messageContent article.message-body',
         'br_replace': True,
      },
      'chinhphu.vn': {
         'paragraph_selector': 'div.detail-content.afcbc-body',
      },
      'vietnamnet.vn': {
         'paragraph_selector': 'div.maincontent.main-content',
      },
      'laodong.vn': {
         'paragraph_selector': 'div[id="gallery-ctt"]',
      },
      'dantri.com.vn': {
         'paragraph_selector': 'div.singular-content',
      },
      'tingia.gov.vn': {
          'paragraph_selector' : 'div.maincontent.main-content.post-body'
      },
      'vietgiaitri.com' : {
          'paragraph_selector' : 'div.entry.clearfix'
      },
      'webtretho.com' : {
        'paragraph_selector' : 'div.post-content'
      },
      'tiin.vn' : {
         'paragraph_selector' : 'div.detail-content'
      },
      '24h.com.vn' : {
          'paragraph_selector' : 'article.cate-24h-foot-arti-deta-info'
      },
      'baoangiang.com.vn' : {
         'paragraph_selector' : 'div.content-fck.slider-jsgallery'
      }
      
   }


   def __init__(self, word_limit: int = None, paragraphs: int = None, take_random: bool = False) -> None: # type:ignore
      """
      Initialize the Scrappers class with optional parameters for word limit, paragraphs, and random selection.
      If word_limit is specified, paragraphs will be ignored.
      If paragraphs is specified, word_limit will be ignored.
      If both are specified, word_limit will take precedence.
      If neither is specified, the default behavior will be to extract all paragraphs.

      Args:
         word_limit (int): Maximum number of words to extract from paragraphs.
         paragraphs (int): Number of paragraphs to extract.
         take_random (bool): Whether to take a random selection of paragraphs.
      """
      self.bs = None
      self.type: str = ""
      self.result: Dict[str, Any] = {}

      self.word_limit = word_limit
      self.paragraphs = paragraphs if not word_limit else None 
      self.take_random = take_random


   def _extract_tag(self, sel_key_pairs: List[Tuple[str, str]], tags: List[str] = ["meta"],
                    default_value=None, attr: str = 'content') -> str | None:
      """
      Try multiple tags and selector, key pairs to find the first matching element.
       
      Args:
         tags (List[str]): List of tag names to search for.
         sel_key_pairs (List[Tuple[str, str]]): List of tuples containing selector and key pairs.
         default_value (str, optional): Default value to return if no matching element is found.
         attr (str): The attribute to extract from the found element.
      """

      if not isinstance(tags, list):
         tags = [tags]

      for tag in tags:
         for sel, key, in sel_key_pairs:
            element = self.bs.find(tag, {sel: key}) # type:ignore
            if element:
                  return element.get(attr, default_value) # type:ignore
      return default_value


   def _extract_paragraphs(self) -> str | None:
      """
      Extract paragraphs from the HTML content based on the configured selector for the website type.
      Returns cleaned text from the paragraphs.
      """
      config = self.SITE_CONFIG.get(self.type)
      if not config:
         raise ValueError(f"Unsupported website type: {self.type}")
      
      selector = config['paragraph_selector']

      paragraph_tags = self.bs.select_one(selector) # type:ignore
      if not paragraph_tags:
         raise ValueError("No paragraph tags found in the HTML content.")
      
      if config.get('br_replace'):
         tags = paragraph_tags.find_all('br')
         for br in tags:
            br.replace_with('\n') #type:ignore
      else:
         tags = paragraph_tags.find_all('p') 

      if not tags:
         raise ValueError("No paragraph tags found in the specified selector.")
      

      if self.take_random:
         if self.word_limit:
            text = ' '.join([p.get_text(strip=True, separator=' ') for p in tags])
            words = text.split()
            start_index = random.randint(0, max(0, len(words) - self.word_limit))
            limited_text = ' '.join(words[start_index : start_index + self.word_limit])
            return self._clean_text(limited_text)
         else:
            # Randomly select paragraphs that are next to each other
            start_index = random.randint(0, max(0, len(tags) - self.paragraphs)) # type:ignore
            selected_paragraphs = tags[start_index : start_index + self.paragraphs] # type:ignore
            return self._clean_text('\n'.join([p.get_text(strip=True, separator=' ') for p in selected_paragraphs]))
      
      elif not self.take_random:
         if self.word_limit:
            text = ' '.join([p.get_text(strip=True, separator=' ') for p in tags])
            words = text.split()
            limited_text = ' '.join(words[:self.word_limit])
            return self._clean_text(limited_text)
         elif self.paragraphs:
            # If paragraphs are specified, return the first n paragraphs
            selected_paragraphs = tags[:self.paragraphs]
            return self._clean_text('\n'.join([p.get_text(strip=True, separator=' ') for p in selected_paragraphs]))
      
      else:
         # Default case: return all paragraphs as a single string
         return self._clean_text('\n'.join([p.get_text(strip=True, separator=' ') for p in tags])) if tags else 'No paragraphs found'
   

   def _extract_json_ld(self, *keys, default_value=None) -> Tuple[str, ...]:
    """
    Parse all <script type="application/ld+json"> tags and return the first occurrence
    of one of the requested keys.
    """
    scripts = self.bs.find_all('script', type='application/ld+json') # type:ignore
    results = []
    
    for key in keys:
        found = False
        for script in scripts:
            text = script.string or script.get_text() #type:ignore
            try:
                data = json.loads(text)
            except (json.JSONDecodeError, TypeError):
                continue

            # Normalize to list for unified handling
            items = data if isinstance(data, list) else [data]
            for item in items:
                if key in item:
                    val = item[key]
                    # For nested author object or list
                    if key == "author":
                        if isinstance(val, dict):
                            results.append(val.get("name", default_value))
                        elif isinstance(val, list) and val:
                            results.append(val[0].get("name", default_value))
                        else:
                            results.append(default_value)
                    else:
                        results.append(val)
                    found = True
                    break
            if found:
                break
        
        # If key was not found in any script, append None
        if not found:
            results.append(default_value)
    
    return tuple(results)
   

   def _scrape(self) -> Dict[str, Any]:
      """
      Scrape the HTML content and extract relevant information based on the website type.
      Returns a dictionary with the extracted data.
      """
      source = self.type
      title = self._extract_tag([("property", "og:title")])
      url = self._extract_tag([("property", "og:url")])
      image = self._extract_tag([("property", "og:image")])
      description = self._extract_tag([("property", "og:description")])
      copyright = self._extract_tag([("name", "copyright")])
      language = self._extract_tag([("property", "og:locale"), ("name", "language"), ("itemprop", "inLanguage")], default_value='vi')

      author, date_published, date_modified = self._extract_json_ld('author', 'datePublished', 'dateModified')

      paragraphs = self._extract_paragraphs()

      # Update the result dictionary with the extracted data
      self.result.update({
         'author' : author,
         'copyright' : copyright,
         'date_published' : date_published,
         'date_modified' : date_modified,
         'language' : language,
         'source' : source,
         'title' : title,
         'description' : description,
         'paragraphs' : paragraphs,
         'url' : url,
         'image' : image,
         'label' : '...',  # Placeholder for label
         'type' : 'article' if source in Scrappers.SITE_CONFIG else 'unknown'
      })
      return self.result


   def run_and_write(self, urls: List[str], folder: str = "Data/") -> None:
      """
      Run the scraper for a list of URLs and write the results to JSON files in the specified folder.
      Args:
         urls (List[str]): List of URLs to scrape.
         folder (str): Folder to save the JSON files.
      """
      if urls is None or not isinstance(urls, list):
         print("No URLs provided or invalid format. Please provide a list of URLs.")
      
      if not os.path.exists(folder):
         os.mkdir(folder)

      amount = sum(1 for entry in os.scandir(folder) if entry.is_file() and entry.name.endswith('.json'))
      for link in urls:
         self(link) # this works because __call__ is defined
         file_name = f'{self.type.split('.')[0].upper()}_{amount + 1}'
         self.WriteJSON(folder, file_name)
         amount += 1


   def WriteJSON(self, Path: str, file_name: str) -> None:
      """
      Write the scraped data to a JSON file in the specified path.
      Args:
         Path (str): The directory path where the JSON file will be saved.
         file_name (str): The name of the JSON file (without extension).
      """
      if not self.result:
         print("No data to write. Please run the scraper first.")
         return
      
      if not os.path.exists(Path):
         os.makedirs(Path)
      
      file_path = os.path.join(Path, file_name + ".json")
      with open(file_path, "w", encoding='utf-8') as f:
         json.dump(self.result, f, indent=4, ensure_ascii=False)
         print(f"Data written to {file_path}")

      
   @staticmethod
   def _get(url: str) -> str:
    # Make initial request
    res = Scrappers.session.get(url)
    if res.status_code == 200:
        res.encoding = 'utf-8'
        
        # Check if this is a cookie-setting redirect page
        if 'document.cookie=' in res.text and 'window.location.reload' in res.text:
            # Extract and manually set the cookie
            import re
            cookie_match = re.search(r'document\.cookie="([^"]+)"', res.text)
            if cookie_match:
                cookie_str = cookie_match.group(1)
                # Parse the cookie (format: "name=value; expires=...; path=/")
                cookie_parts = cookie_str.split(';')
                if '=' in cookie_parts[0]:
                    name, value = cookie_parts[0].split('=', 1)
                    Scrappers.session.cookies.set(name, value)
            
            # Wait a moment and make second request
            time.sleep(0.5)
            res = Scrappers.session.get(url)
            if res.status_code == 200:
                res.encoding = 'utf-8'
                return res.text
            else:
                raise Exception(f"Failed to fetch data from {url} on second request, status code: {res.status_code}")
        
        return res.text
    else:
        raise Exception(f"Failed to fetch data from {url}, status code: {res.status_code}")


   @staticmethod
   def _determine_type(url: str) -> str:
      for site in Scrappers.SITE_CONFIG.keys():
          if site in url:
            return site
      raise ValueError(f"Unknown URL type: {url}")
        

   @staticmethod
   def _clean_text(text: str) -> str:
      lines = text.splitlines()
      cleaned_lines = []
      for line in lines:
            # Remove lines starting with 'ẢNH:' or similar tags
            if re.match(r'^\s*ẢNH\s*[:\-]', line, re.IGNORECASE):
               continue
            # Add space around Vietnamese text that might be stuck together
            line = re.sub(r'([a-zA-ZÀ-ỹ])([A-ZÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ])', r'\1 \2', line)
            cleaned_lines.append(line)
      return "\n".join(cleaned_lines).strip()
   

   def __call__(self, url: str | List[str], folder: str = None) -> Any: # type:ignore
      if not url:
            raise ValueError("URL must be a non-empty string or list of strings.")
      
      if isinstance(url, list):
         if folder is None:
               raise ValueError("Folder must be specified when passing a list of URLs.")
         return self.run_and_write(url, folder)
      
      self.type = self._determine_type(url)
      if self.type == 'theanh28.vn':
         # Disable SSL verification for the session
          self.session.verify = False
      else:
          self.session.verify = True

      html = self._get(url)
      self.bs = BeautifulSoup(html, 'lxml')

      return self._scrape()