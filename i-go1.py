#el programa completa el test actual, falta mirar bé quina és la diferència entre el graph i el digraph
#i quins efectes tindrà en la posterioritat de la implementació, he separat els datatypes com va dir en jordi: https://raco.fib.upc.edu/avisos/veure.jsp?espai=270208&id=118168
import fiona #pel mac
import osmnx as ox
import pickle as pl
import collections
import urllib
import csv
import staticmap

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
SIZE = 800

Highway = collections.namedtuple('Highway', ['way_id', 'description', 'coordinates']) # Tram

#checks if there is an existent graph file
def exists_graph(GRAPH_FILENAME):
    try:
        open(GRAPH_FILENAME, 'rb')
    except: #if no graph can be opened an error would pop up, we indicate that graph doesn't exist
        return False
    return True

#downloads graph
def download_graph(PLACE):
    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    di_graph = ox.utils_graph.get_digraph(graph, weight='length') #di_graph separated for plotting issues
    return graph, di_graph

#saves graph using pickle
def save_graph (graph, GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'wb') as file:
        pl.dump(graph, file)

#loads graph from files
def load_graph(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pl.load(file)
    return graph

#gives the visual representation of a graph, printed onscreen (default) or saved in a .png file
def plot_graph(graph, onscreen=True): #onscreen must be True if MacOS is used and False if WindowsOS is used
    if (onscreen):
        ox.plot_graph(graph, show=True)
    else:
        ox.plot_graph(graph, show= False, save= True, filepath= 'bcn.png')

def download_highways (HIGHWAYS_URL):
    highways = []
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:  
            way_id, description, coordinates = line
            highway = [way_id, description, coordinates]
            highways.append (highway)
        return highways

def plot_highways (highways, SIZE):
    print ("tamos bien")

def test():
    # loads/downloads graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME):
        graph, di_graph = download_graph(PLACE) #downloads both graph and digraph formats
        save_graph(graph, GRAPH_FILENAME)
    else:
        print("graph already saved, loading...")
        graph = load_graph(GRAPH_FILENAME)

    #plot_graph(graph) #prints the graph
    highways = download_highways(HIGHWAYS_URL)
    plot_highways(highways, SIZE)

#testing
test()
