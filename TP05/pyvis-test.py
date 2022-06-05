from pyvis.network import Network
import networkx as nx
from faker import Faker
fake = Faker()
n=200
web = nx.random_internet_as_graph(n, seed=0)
print(web)
mapping = { node:fake.url() for node in range(n)}
print(mapping)
H = nx.relabel_nodes(web, mapping)