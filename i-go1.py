#falta mrar com fer bé la funció boleana del exists_graph + mirar com es fa lo del plot (aixo ultim ho hauras de mirar tu k
#a mi no em mostra el graph per pantalla)

import osmnx as ox
import pickle as pl

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'

def exists_graph(GRAPH_FILENAME):
    print ("entro al bolea")
    if open(GRAPH_FILENAME, 'rb'):
        return True
    else:
        return False

def download_graph(PLACE):
    print ("entro a download")
    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    graph = ox.utils_graph.get_digraph(graph, weight='length')
    ox.plot_graph(g, show=False, save=True, filepath='bcn.png')
    return graph

def save_graph (graph, GRAPH_FILENAME):
    print ("entro a save")
    with open(GRAPH_FILENAME, 'wb') as file:
        pl.dump(graph, file)

def load_graph(GRAPH_FILENAME):
    print ("entro a load")
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pl.load(file)

#def plot_graph (graph):


def test():
    # load/download graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME):
        graph = download_graph(PLACE)
        save_graph(graph, GRAPH_FILENAME)
    else:
        graph = load_graph(GRAPH_FILENAME)
    plot_graph(graph)

test()
