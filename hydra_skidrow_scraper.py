import cloudscraper
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os
from datetime import datetime, timezone

class HydraSkidrowScraper:
    def __init__(self):
        self.base_url = "https://www.skidrowreloaded.com/"
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        self.json_file = "hydra_source.json"

    def load_existing_data(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("downloads", [])
            except Exception: pass
        return []

    def scrape_to_hydra_format(self, pages_to_scrape=5):
        print(f"[*] Iniciando extracción con camuflaje. Revisando {pages_to_scrape} páginas...")
        games_dict = {g["title"]: g for g in self.load_existing_data()}
        
        try:
            for page in range(1, pages_to_scrape + 1):
                url = self.base_url if page == 1 else f"{self.base_url}page/{page}/"
                response = self.scraper.get(url, timeout=20)
                if response.status_code != 200: continue
                    
                articles = BeautifulSoup(response.text, 'html.parser').find_all('article') or BeautifulSoup(response.text, 'html.parser').find_all('div', class_='post')
                if not articles: break

                for article in articles:
                    t_tag = article.find('h2') or article.find('h1') or article.find('h3')
                    if not t_tag or not t_tag.find('a'): continue
                    
                    title = t_tag.find('a').text.strip()
                    g_url = t_tag.find('a')['href']
                    ya_existia = title in games_dict
                    
                    print(f"[*] {'ACTUALIZANDO' if ya_existia else 'NUEVO'} - {title[:50]}...")
                    uris = self.extract_uris(g_url)
                    
                    if uris:
                        games_dict[title] = {"title": title, "uris": uris, "uploadDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"), "fileSize": "Unknown"}
                    
                    time.sleep(random.uniform(3.5, 7.5))
                    
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump({"name": "SkidrowReloaded Custom", "downloads": list(games_dict.values())}, f, indent=4, ensure_ascii=False)
            print("\n[+] Base de datos actualizada con éxito.")
            
        except Exception as e: print(f"[!] Error: {e}")

    def extract_uris(self, g_url):
        try:
            res = self.scraper.get(g_url, timeout=15)
            magnets = re.findall(r'(magnet:\?xt=[^"\'\s<>]+)', res.text)
            return [magnets[0]] if magnets else []
        except Exception: return []

if __name__ == "__main__":
    scraper = HydraSkidrowScraper()
    scraper.scrape_to_hydra_format(pages_to_scrape=40)
