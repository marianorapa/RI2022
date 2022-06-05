import sys
from bs4 import BeautifulSoup
import requests
import queue
import networkx as nx
from pyvis.network import Network
import os


class Crawler:

    def __init__(self):
        self.MAX_SITE_PAGES = 500
        self.MAX_PAGES_DEPTH = 5
        self.MAX_PHYSICAL_DEPTH = 5
        self.CRAWL_LIMIT = 500
        self.headers = {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

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
        
    def __retrieve_links__(self, url, allow_repetitions):        
        base_url = self.__normalize_base_url__(url)
        try:
            html_page = requests.get(url, timeout=5, headers=self.headers)            
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
        except:
            return []
    
    def __split_url__(self, url):        
        protocol, host_and_path = url.split("://", 1)
        try:        
            host, relative_path = host_and_path.split("/", 1)
        except ValueError:
            host = host_and_path
            relative_path = ""
        return protocol, host, relative_path

    def __is_physical_length_ok__(self, path):
        return path.count("/") < 3

    def __is_dynamic__(self, link):
        return any(character in link for character in ["?", "=", "&", "%"])        

    def __get_p_depth__(self, link):
        return link.count("/")

    def crawl(self, url):
        q = queue.Queue()
        todo_list = {}      # Only to simplify link lookup

        result = []        
        
        site_pages_amt = {}

        id = 0

        protocol, wanted_host, path = self.__split_url__(url)

        q.put({"id": id, "url": url, "depth": 0, "p_depth": self.__get_p_depth__(url),"outlinks": [], "dynamic": False})
        todo_list[url] = id
        done_list = {}
        id += 1

        crawled_pages = 0
        while not q.empty() and crawled_pages < self.CRAWL_LIMIT:
            # Get next page from queue
            page = q.get()
            os.system('clear')
            print(crawled_pages)
            # Remove page from todo list
            del todo_list[page["url"]]
            # Append page to done list
            done_list[page["url"]] = page["id"]
            
            try:
                if page["depth"] < self.MAX_PAGES_DEPTH:
                    # Get links from page
                    links = self.__retrieve_links__(page["url"], False)
                    for link in links:
                        protocol, host, path = self.__split_url__(link)
                        if host == wanted_host:
                            if link in done_list:
                                page["outlinks"].append(done_list[link])
                            elif link in todo_list:
                                page["outlinks"].append(todo_list[link])
                            else:
                                # If the link is not done nor todo, add it to todo (will add param checks in here)                            
                                if host not in site_pages_amt:
                                    site_pages_amt[host] = 0                  
                                links_p_depth = self.__get_p_depth__(link)      
                                if site_pages_amt[host] < self.MAX_SITE_PAGES and links_p_depth < self.MAX_PHYSICAL_DEPTH:
                                    new_page = {"id": id, "url": link, "outlinks": [], "depth": page["depth"] + 1, "p_depth": links_p_depth, "dynamic": self.__is_dynamic__(link)}
                                    id += 1
                                    q.put(new_page)
                                    todo_list[link] = new_page["id"]
                                    page["outlinks"].append(new_page["id"])
                                    # Count page in this host
                                    site_pages_amt[host] += 1
                crawled_pages += 1
                result.append(page)
                #print(result)
            except Exception as e:
                print(e)
                print(page)
        return result

def save_pages_to_file(pages):
    with open("crawled_pages.txt", "w") as file:
        file.write("\"id\";\"url\";\"l_depth\";\"p_depth\";\"dynamic\"\n")
        for page in pages:            
            file.write(f"\"{page['id']}\";\"{page['url']}\";\"{page['depth']}\";\"{page['p_depth']}\";\"{page['dynamic']}\"\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("El programa espera una URL base para crawlear")
        sys.exit(0)
    crawler = Crawler()
    base_url = sys.argv[1]
        
    pages = crawler.crawl(base_url)    
    save_pages_to_file(pages)
    #nodes = []
    #node_mappings = {}
    #edges = []
    #for page in pages:
    #    url = page["url"]
    #    id = page["id"]
    #    outlinks = page["outlinks"]
    #    nodes.append(id)
    #    node_mappings[id] = url
    #    for outlink in outlinks:
    #        edges.append((id, outlink))

    #print(f"Total crawled pages: {len(pages)}")
    #G = nx.DiGraph()
    #G.add_nodes_from(nodes)
    #G.add_edges_from(edges)
    #H = nx.relabel_nodes(G, node_mappings)
    #nt = Network('720px', '1280px')

    #nt.from_nx(H)
    #nt.show('graph.html')

