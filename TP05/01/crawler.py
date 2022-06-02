import sys
from bs4 import BeautifulSoup
import requests
 
'''proxies = {
   "http"  : "http://proxy.unlu.edu.ar",
   "https" : "https://proxy.unlu.edu.ar",
}'''
 
class Crawler:

    def __init__(self):
        pass



    def __normalize_base_url__(self, url):
        output_link = url
        if not url.startswith("http") and not url.startswith("https"):
            output_link = "http://" + url
        if not output_link.endswith("/"):
            output_link += "/"
        return output_link

    def __normalize_link__(self, base_url, link):
        output_link = link
        # Check if it's relative
        if not link.startswith("http") and not link.startswith("https"):
            output_link = base_url + link
        # Remove URL "Fragment" (# section indicator)
        output_link = output_link.split("#")[0]
        return output_link
        
    def retrieve_links(self, url, allow_repetitions):        
        base_url = self.__normalize_base_url__(url)
        html_page = requests.get(url)
        soup = BeautifulSoup(html_page.text, "html5lib")
        if (allow_repetitions):
            links = []
        else:
            links = set()
        
        for a_tag in soup.findAll('a'):
            if a_tag.has_attr("href"):
                possible_link = str(a_tag.get('href')).strip()                
                if len(possible_link) > 0:
                    link = self.__normalize_link__(base_url, possible_link) 
                    if (allow_repetitions):
                        links.append(link) 
                    else:
                        links.add(link)                   
        return links

def print_links(links):
    for link in links:
        print(link)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("El programa espera una URL para crawlear")
        sys.exit(0)
    crawler = Crawler()
    allow_repetitions = False
    if len(sys.argv) == 3:  
        if sys.argv[2].lower() == "true":
            allow_repetitions = True

    links = crawler.retrieve_links(sys.argv[1], allow_repetitions)
    print_links(links)