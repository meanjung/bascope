import requests
from bs4 import BeautifulSoup as bsoup
from kakaotrans import Translator

def crawl(attackName):
    url = f"https://nvd.nist.gov/vuln/detail/{attackName}"

    response = requests.get(url)
    try:
        if response.status_code==200:
            html = response.text
            soup = bsoup(html, 'html.parser')
            en_description = soup.find("p", {"data-testid":"vuln-description"}).get_text()

            translator = Translator()
            ko_description = translator.translate(en_description, separate_lines=True, tgt="kr")
            ko_description = ''.join(ko_description)
            return {
                "en_description":en_description,
                "ko_description":ko_description
            }
        else:
            print(f'crawling response status : {response.status_code}')
            return None
            
    except Exception as e:
        print('crawler Error : ', e)
        return None
