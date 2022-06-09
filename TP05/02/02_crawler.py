import sys
from bs4 import BeautifulSoup
import requests
import queue
import networkx as nx
from pyvis.network import Network

class Crawler:

    def __init__(self):
        self.MAX_SITE_PAGES = 30
        self.MAX_PAGES_DEPTH = 3
        self.CRAWL_LIMIT = 500

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
            html_page = requests.get(url, timeout=5)
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

    def crawl(self, initial_seed):
        q = queue.Queue()
        todo_list = {}      # Only to simplify link lookup

        result = []        
        
        site_pages_amt = {}

        id = 0
        for url in initial_seed:
            page = {"id": id,"url": url, "outlinks": [], "depth": 0}
            todo_list[url] = id
            q.put(page)
            id += 1
            protocol, host, path = self.__split_url__(url)
            site_pages_amt[host] = 0

        done_list = {}
        
        
        while (not q.empty()) and (id <= self.CRAWL_LIMIT):
            # Get next page from queue
            page = q.get()
            # Remove page from todo list
            del todo_list[page["url"]]
            # Append page to done list
            done_list[page["url"]] = page["id"]
            
            try:
                if page["depth"] < self.MAX_PAGES_DEPTH:
                    # Get links from page
                    links = self.__retrieve_links__(page["url"], False)
                    for link in links:
                        if link in done_list:
                            page["outlinks"].append(done_list[link])
                        elif link in todo_list:
                            page["outlinks"].append(todo_list[link])
                        elif id < self.CRAWL_LIMIT:
                            # If the link is not done nor todo, add it to todo (will add param checks in here)
                            protocol, host, path = self.__split_url__(link)
                            if host not in site_pages_amt:
                                site_pages_amt[host] = 0                        
                            if site_pages_amt[host] < self.MAX_SITE_PAGES and self.__is_physical_length_ok__(path):
                                new_page = {"id": id, "url": link, "outlinks": [], "depth": page["depth"] + 1}                    
                                id += 1
                                q.put(new_page)
                                todo_list[link] = new_page["id"]
                                page["outlinks"].append(new_page["id"])
                                # Count page in this host
                                site_pages_amt[host] += 1
                
                result.append(page)
                #print(result)
            except Exception as e:
                print(e)
                print(page)
        return result

def read_seed(path):
    seed = []
    with open(path, "r") as file:
        for line in file.readlines():
            seed.append(line.strip())
    return seed

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("El programa espera un archivo con la semilla")
        sys.exit(0)
    crawler = Crawler()
    seed_path = sys.argv[1]
    initial_seed = read_seed(seed_path)
        
    pages = crawler.crawl(initial_seed)
    
    
    nodes = []
    node_mappings = {}
    edges = []
    for page in pages:
        url = page["url"]
        id = page["id"]
        outlinks = page["outlinks"]
        nodes.append(id)
        node_mappings[id] = url
        for outlink in outlinks:
            edges.append((id, outlink))

    print(f"Total crawled pages: {len(pages)}")
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    H = nx.relabel_nodes(G, node_mappings)
    nt = Network('720px', '1280px')

    nt.from_nx(H)
    nt.show('graph.html')

