#he estat llegint i investigant com tenim disposat el graf de bcn en sí, és interessant l'enllaç https://networkx.org/documentation/stable/tutorial.html#examining-elements-of-a-graph
#per l'apartat concret i tot l'article en general, parla de com funciona un graf de osmnx com el que tenim creat

#A les funcion plot_highways i plot_congestions hi ha el parametre congestions.png / highways.png k em dona error si el poso, l'he tret i tot forula
#mira si a tu et va be sense o és alló de que o ho he de fer de una forma i tu d'una altre

from typing import NoReturn
import fiona #pel mac
import osmnx as ox
import pickle as pl
import collections
import urllib
import csv
import pandas as pd #installation with pip3 install pandas
from staticmap import StaticMap, Line
import networkx as nx #potser caldrà instalar l'scipy, jo he fet brew install scipy pq me'l demanava però per wdws no se quina cmmd és

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'
SIZE = 800


Highway = collections.namedtuple('Highway', ['way_id', 'description', 'coordinates']) # Tram
Congestion= collections.namedtuple('Congestion',['c_id', 'date', 'current', 'future']) #Trànsit

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

#adjust coordinates from panda lecture to a list of pairs
def adjust_coordinates(highways):
    for highway in highways:
        i=0
        newcord=[]
        while (i<len(highway[2])):
            x,i = string_to_float(highway[2],i)
            y,i = string_to_float(highway[2],i)
            pair= (x,y)
            newcord.append(pair)
        highway[2]= newcord

#downloads highways info and stores it in a tuple
def download_highways(HIGHWAYS_URL): #versió utilitzant panda, trobo que queda més net

    df= pd.read_csv(HIGHWAYS_URL) #reads the csv file
    highways= df.values.tolist() #adjusts to list format
    adjust_coordinates(highways) #adjusts coordinates to float values
    n = -1
    for highway in highways:
        if (n < highway [0]):
            n = highway[0]
    hw = [Highway(-1, "VOID", (-1, -1))] * n #list of namedtuple highways
    for highway in highways:
        hw [highway[0] - 1] = Highway(highway[0], highway[1], highway[2])
    return hw, n

#gives a visual representation of the highways in a static_map painted with lines and saves it into a png file (arbitrary size for tests, SIZE parameter can be added)
def plot_highways(highways, SIZE):
    #ploting the data
    m = StaticMap (SIZE, SIZE) #test values
    for highway in highways:
        if highway.way_id != -1: #only existing higways must be painted
            line = Line(highway.coordinates, 'red', 1) #highway[2] has to be the list of coordinates in pairs
            m.add_line(line)

    print('checkpoint_succesful')

    #saving the image
    image = m.render()
    image.save('highways.png')

#gets all the congestions values and stores them in a list of the defined tuple congestions with the indicated parameters
def pandas_download_congestions(CONGESTIONS_URL, n):
    cf= pd.read_csv(CONGESTIONS_URL, sep='#', header= None)
    #creates a list of lists with the parameters id, date, value1, value 2 read from the dataset
    #de cares al plotting seria interessant veure quin dels dos valors és el que indica la congestió o com va
    congestions= cf.values.tolist()
    cong= [Congestion (-1, "void", -1, -1)]*n
    for congestion in congestions:
        cong [congestion[0] - 1]= Congestion(congestion[0], congestion[1], congestion[2], congestion[3])
    return cong


#gives a visual representation of the congestion in a static_map painted with lines and saves it into a png file (arbitrary size for tests, SIZE parameter can be added)
#colors correspondece : grey = no data, blue = very fluid, green = fluid, yellow = heavy, orange = very heavy, red = traffic jam, black = blocked
def plot_congestions (highways, congestions, SIZE):
    m = StaticMap (SIZE, SIZE)
    for highway in highways:
        #only existing higways must be painted
        if highway.way_id != -1:
            congestion_type = congestions[highway.way_id - 1].current
            if congestion_type == 0:
                line = Line(highway.coordinates, 'grey', 1)
                m.add_line(line)
            elif congestion_type == 1:
                line = Line(highway.coordinates, 'blue', 1)
                m.add_line(line)
            elif congestion_type == 2:
                line = Line(highway.coordinates, 'green', 1)
                m.add_line(line)
            elif congestion_type == 3:
                line = Line(highway.coordinates, 'yellow', 1)
                m.add_line(line)
            elif congestion_type == 4:
                line = Line(highway.coordinates, 'orange', 1)
                m.add_line(line)
            elif congestion_type == 5:
                line = Line(highway.coordinates, 'red', 1)
                m.add_line(line)
            else:
                line = Line(highway.coordinates, 'black', 1)
                m.add_line(line)
    image = m.render()
    image.save('congestions.png')



#SEMBLA QUE EL QUE HEM DE BAIXAR JA ES BAIXA, ARA A PER LA PART DEL GRAF EN SI, aka 'lu divertit':
#llegir al README les indicacions per treballar amb els grafs: https://github.com/puigde/ap2-igo#indicacions-per-treballar-amb-els-grafs-dosmnx
#funcions per a treballar amb NetworkX: https://networkx.org/documentation/stable/reference/functions.html
#funcions per a treballar amb Osmnx: https://osmnx.readthedocs.io/en/stable/

#passos a seguir:
#get_nearest_node() a partir d'unes coordenades troba el node del graf més proper - no tinc clar com serà l'input i com passar-lo a coordenades

#de cares a fer el  graf intel·ligent, obtenir nodes més propers al graf a partir dels extrems de les highways (o potser més precisió que els extrems) generar paths i per cada path, afegir la congestió corresponent a la highway que ja tenim emparellada
#es pot utilitzar geocode() per convertir strings de coordenades a coordenades per treballar(EXACTE, podria ser que el conversor que et vas cascar no fos necessari)
#d'aquesta manera transferir el paràmetre de les congestions al pes de les arestes amb la funció add_edge_bearings() (veure exemple codi Biosca)

#s'ha de llegir i pair el format, jo aprofitaria demà dijous per fer preguntes perquè hi ha coses encara que ballen

#NOTA: per treballar amb el graph en si haurem d'utilitzar l'objecte di_graph()



def test():
    # loads/downloads graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME):
        graph, di_graph = download_graph(PLACE) #downloads both graph and digraph formats
        save_graph(graph, GRAPH_FILENAME)
    else:
        print("graph already saved, loading...")
        graph = load_graph(GRAPH_FILENAME)

    plot_graph(graph) #prints the graph

    #downloads and prints highways
    highways, n = download_highways(HIGHWAYS_URL)
    plot_highways( highways, SIZE)

    #downloads and prints congestions
    congestions = pandas_download_congestions(CONGESTIONS_URL, n)
    plot_congestions(highways, congestions, SIZE)

#testing
test()
