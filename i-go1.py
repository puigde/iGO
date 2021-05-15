#el programa completa el test actual, falta mirar bé quina és la diferència entre el graph i el digraph
#i quins efectes tindrà en la posterioritat de la implementació, he separat els datatypes com va dir en jordi: https://raco.fib.upc.edu/avisos/veure.jsp?espai=270208&id=118168

#A les funcion plot_highways i plot_congestions hi ha el parametre congestions.png / highways.png k em dona error si el poso, l'he tret i tot forula
#mira si a tu et va be sense o és alló de que o ho he de fer de una forma i tu d'una altre
import fiona #pel mac
import osmnx as ox
import pickle as pl
import collections
import urllib
import csv
from staticmap import StaticMap, Line

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'
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

#returns every coordinate as a float
def string_to_float (coordinates, i):
    new_coordinate = 0
    dot = False
    j = 1
    while (i < len (coordinates) and coordinates[i] != ',' ):
        if (coordinates[i] == '.'):
            dot = True
        elif (coordinates[i] != ' '):
            if dot:
                new_coordinate = new_coordinate + float (coordinates[i]) * pow (10, -j)
                j += 1
            else:
                new_coordinate = new_coordinate * 10 + float (coordinates[i])
        i += 1
    i += 1 #i doesn't have to stay at position with ,
    return new_coordinate, i

#returns a list of every highway
def download_highways (HIGHWAYS_URL):
    highways = []
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:
            way_id, description, coordinates = line
            #coordinates are read as strings but must be put as pairs x, y of floats
            new_coordinates = []
            i = 0
            while (i < len (coordinates)):
                x, i = string_to_float(coordinates, i)
                y, i = string_to_float(coordinates, i)
                pair = (x, y)
                new_coordinates.append (pair)
            highway = [int (way_id), description, new_coordinates]
            highways.append (highway)
        return highways

#gives a .png file of all the highways printed on a map
def plot_highways( highways ,SIZE):
    m = StaticMap (SIZE, SIZE)
    for highway in highways:
        line = Line(highway[2], 'red', 1) #highway[2] is the list of coordinates
        m.add_line(line)
    image = m.render()
    image.save('highways.png')

#returns the number which defines the congestion of the stretch
def read_congestion (all):
    n = len (all)
    return all [0][n - 2]

#returns a list of all the congestion of every stretch
def download_congestions (CONGESTIONS_URL):
    congestions = [-1]*533
    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:
            all = line
            print (line)
            congestions.append (read_congestion (all))

    return congestions

def plot_congestions (highways, congestions, SIZE):
    m = StaticMap (SIZE, SIZE)
    for highway in highways:
        congestion_type = congestions[highway[0] - 1]
        if congestion_type == 0:
            line = Line(highway[2], 'blue', 1)
            m.add_line(line)
        elif congestion_type == 1:
            line = Line(highway[2], 'green', 1)
            m.add_line(line)
        elif congestion_type == 2:
            line = Line(highway[2], 'yellow', 1)
            m.add_line(line)
        elif congestion_type == 3:
            line = Line(highway[2], 'orange', 1)
            m.add_line(line)
        elif congestion_type == 4:
            line = Line(highway[2], 'red', 1)
            m.add_line(line)
        elif congestion_type == 5:
            line = Line(highway[2], 'grey', 1)
            m.add_line(line)
        elif congestion_type == 6:
            line = Line(highway[2], 'black', 1)
            m.add_line(line)

    image = m.render()
    image.save('congestions.png')

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
    plot_highways( highways, SIZE)

    congestions = download_congestions(CONGESTIONS_URL)
    plot_congestions(highways, congestions, SIZE)

#testing
test()
