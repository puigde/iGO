#falta mrar com fer bé la funció boleana del exists_graph + mirar com es fa lo del plot (aixo ultim ho hauras de mirar tu k
#a mi no em mostra el graph per pantalla)
import fiona 
import osmnx as ox
import pickle as pl

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'

#checks if there is an existent graph file
def exists_graph(GRAPH_FILENAME):
    print ("entro al bolea")
    try:
        open(GRAPH_FILENAME, 'rb')
    except: #if no graph can be opened an error would pop up, we indicate that graph doesn't exist
        return False
    return True

#downloads graph
def download_graph(PLACE):
    print ("entro a download")
    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    di_graph = ox.utils_graph.get_digraph(graph, weight='length') #di_graph separated for plotting issues
    return graph, di_graph

#saves graph using pickle
def save_graph (graph, GRAPH_FILENAME):
    print ("entro a save")
    with open(GRAPH_FILENAME, 'wb') as file:
        pl.dump(graph, file)

#loads graph from files 
def load_graph(GRAPH_FILENAME):
    print ("entro a load")
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pl.load(file)
    return graph

#gives the visual representation of a graph, printed onscreen (default) or saved in a .png file
def plot_graph(graph, onscreen=True): 
    if (onscreen):
        ox.plot_graph(graph, show=True)
    else:
        ox.plot_graph(graph, show= False, save= True, filepath= 'bcn.png')


def test():
    # loads/downloads graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME): 
        graph, di_graph = download_graph(PLACE) #downloads both graph and digraph formats
        save_graph(graph, GRAPH_FILENAME)
    else:
        print("graph already saved, loading...")
        graph = load_graph(GRAPH_FILENAME)

    plot_graph(graph) #prints the graph

#testing
test()
