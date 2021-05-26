#he estat llegint i investigant com tenim disposat el graf de bcn en sí, és interessant l'enllaç https://networkx.org/documentation/stable/tutorial.html#examining-elements-of-a-graph
#per l'apartat concret i tot l'article en general, parla de com funciona un graf de osmnx com el que tenim creat

#A les funcion plot_highways i plot_congestions hi ha el parametre congestions.png / highways.png k em dona error si el poso, l'he tret i tot forula
#mira si a tu et va be sense o és alló de que o ho he de fer de una forma i tu d'una altre

from typing import NoReturn
from networkx.algorithms.bipartite.matching import INFINITY
from networkx.classes import digraph
from networkx.generators.classic import path_graph
from networkx.generators.duplication import partial_duplication_graph
import fiona #pel mac
import osmnx as ox
import pickle as pl
from haversine import haversine
import collections
import urllib
import csv
import pandas as pd #installation with pip3 install pandas
from staticmap import StaticMap, Line
import networkx as nx #potser caldrà instalar l'scipy, jo he fet brew install scipy pq me'l demanava però per wdws no se quina cmmd és
#import sklearn

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'
SIZE = 800
PLOT_GRAPH_FILENAME= 'plot_bcn.graph'
ARBITRARY= 1
INFINIT= 10000000000

Highway = collections.namedtuple('Highway', ['way_id', 'coordinates']) # Tram
Congestion= collections.namedtuple('Congestion',['c_id', 'congestion']) #Trànsit

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
def plot_graph(graph, onscreen=False): #onscreen must be True if MacOS is used and False if WindowsOS is used
    if (onscreen):
        ox.plot_graph(graph, show=True)
    else:
        ox.plot_graph(graph, show= False, save= True, filepath= 'bcn.png')

#adjust coordinates from panda lecture to a list of pairs
def adjust_coordinates(highways):
    for highway in highways:
        highway[1] = highway[1].split(',')
        i=0
        newcoord=[]
        while (i < len(highway[1])): #highway[1] are the coordinates
            x = float (highway[1][i])
            i += 1
            y = float (highway[1][i])
            i += 1
            coord= (x,y)
            newcoord.append(coord)
        highway[1]= newcoord
    return


#downloads highways info and stores it in a tuple
def download_highways(HIGHWAYS_URL): #versió utilitzant panda, trobo que queda més net
    df = pd.read_csv(HIGHWAYS_URL, usecols = ['Tram', 'Coordenades']) #reads the csv file
    highways= df.values.tolist() #adjusts to list format
    adjust_coordinates(highways) #adjusts coordinates to float
    n = -1
    for highway in highways:
        if (n < highway [0]):
            n = highway[0]
    hw = [Highway(-1, (INFINIT, INFINIT))] * n #list of namedtuple highways
    for highway in highways: #reoorder highways so they're sorted with way_id
        hw [highway[0] - 1] = Highway(highway[0], highway[1])
    return hw, n

#gives a visual representation of the highways in a static_map painted with lines and saves it into a png file (arbitrary size for tests, SIZE parameter can be added)
def plot_highways(highways, filename, SIZE):
    #ploting the data
    m = StaticMap (SIZE, SIZE) #test values
    for highway in highways:
        if highway.way_id != -1: #only existing highways must be painted
            line = Line(highway.coordinates, 'red', 1) #highway[2] has to be the list of coordinates in pairs
            m.add_line(line)

    #saving the image
    image = m.render()
    image.save(filename)

#gets all the congestions values and stores them in a list of the defined tuple congestions with the indicated parameters
def download_congestions(CONGESTIONS_URL, n):
    cf= pd.read_csv(CONGESTIONS_URL, sep='#', header= None, usecols = [0, 2])
    #creates a list of lists with the parameters id, congestion read from the dataset
    congestions= cf.values.tolist()
    cong= [Congestion (-1, -1)]*n
    for congestion in congestions:
        cong [congestion[0] - 1] = Congestion(congestion[0], congestion[1])
    return cong


#gives a visual representation of the congestion in a static_map painted with lines and saves it into a png file (arbitrary size for tests, SIZE parameter can be added)
#colors correspondece : grey = no data, blue = very fluid, green = fluid, yellow = heavy, orange = very heavy, red = traffic jam, black = blocked
def plot_congestions (highways, congestions, filename,  SIZE):
    m = StaticMap (SIZE, SIZE)
    for highway in highways:
        #only existing highways must be painted
        if highway.way_id != -1:
            congestion_type = congestions[highway.way_id - 1].congestion
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
    image.save(filename)



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

#it iterates trough the graph and prints information
def print_graph_info(graph):
    for node1, info1 in graph.nodes.items():
        print('NODE INFO: ', node1, info1)

        for node2, edge in graph.adj[node1].items():
            print('NODE 2 ID')
            print(' ', node2)
            print('EDGE INFO BELOW')
            print(' ', edge)

#prova a funció alternativa a la que ve per defecte i utilitza el modul aquell dels collons que hem comentat amb en jordi
#donat un graph i una posició retorna el node del graph més proper a la posició
def get_nearest_node(graph, pos, reversed=True):

    nearest_node = None
    nearest_dist = 99999 # km

    for node, info in graph.nodes.items():
        if reversed:
            d = haversine((info['x'], info['y']), pos) #aquí diria que y i x estaven a l'inversa de com ho teniem nosaltres
        else:
            d= haversine((info['y'], info['x']), pos)
        if d < nearest_dist:
            nearest_dist = d
            nearest_node = node
    return nearest_node

def ponderate_congestion (congestion_type):
    if congestion_type == 0:
        return 1.25 #aixo vol dir k no te info llavors quin valor li donem??
    elif congestion_type == 1:
        return 1
    elif congestion_type == 2:
        return 1.25
    elif congestion_type == 3:
        return 1.5
    elif congestion_type == 4:
        return 2
    elif congestion_type == 5:
        return 3
    else:
        return INFINIT

#seems to be working, we could add a delay for <15 degree turns as suggested in the README and discuss the calibration of the itime factors
def build_i_graph(graph, highways, congestions, ARBITRARY, INFINIT): #intento fer una altra funció perquè he provat de deubgar la principal però no se que collons l'hi passa
    nx.set_edge_attributes(graph, ARBITRARY, name='congestion')
    #print_graph_info(graph)
    nopath_counter=0
    no_speed_data_counter=0
    edges_with_speed_data_in=0
    zerospeed=0
    zerocongestion=0
    counter2=0
    for highway in highways:
        if (highway.way_id>0):
            for i in range(1, len(highway.coordinates)):
                #alerta aquí abans teníem
                node1= get_nearest_node(graph, highway.coordinates[i-1])
                node2= get_nearest_node(graph, highway.coordinates[i])
                try:
                    path= ox.shortest_path(graph, node1, node2, weight='length')
                    #print(path)
                    #print('path found')
                    for j in range(1, len(path)):
                        path_node1= path[j-1]
                        path_node2= path[j]
                        #print('aquí bé')
                        #algún dels accessos d'aquí sota és incorrecte, no semblo entendre perquè
                        graph[path_node1][path_node2]['congestion']= congestions[highway.way_id-1].congestion
                        if (congestions[highway.way_id-1].congestion==0):
                            zerocongestion+=1
                except nx.NetworkXNoPath:
                    #print('nopath')
                    nopath_counter+=1
                    pass
        print('loading congestions ', highway.way_id, "/", len(highways))

    #adding the itime atribute for all edges in the graph
    nx.set_edge_attributes(graph, ARBITRARY, name='itime')
    for node1, node2 in graph.edges():
        length = graph[node1][node2]['length']
        try:
            speed = float(graph[node1][node2]['maxspeed'])
            edges_with_speed_data_in+=1
        except: #some edges don't have maxspeed value in them so we add the new normative speed value for the inside cities
            speed= 30
        congestion = ponderate_congestion(graph[node1][node2]['congestion'])
        graph[node1][node2]['itime'] = length*congestion/(speed)

    #print_graph_info(graph)
    return graph



def checking_highways_congestions (highways, congestions):
    if len (highways) != len (congestions):
        print ("la primera en la frente")
        return
    n = len (highways)
    for i in range (n):
        if highways[i].way_id != i + 1:
            if highways[i].way_id != -1:
                print ("index de la highway no coincideix amb la posicio")
                print (i+1)
                print (highways[i].way_id)
        if congestions[i].c_id != i + 1:
            if congestions[i].c_id != -1:
                print ("index del congestion no coincideix amb la posicio")
                print (i+1)
                print (congestions[i].c_id)
        if highways[i].way_id != congestions[i].c_id:
            print ("index de la highway no coincideix amb el de congestion")
            print (i+1)
    print ("pol puto subnormal")

#crec que el geocode no funciona tan màgicament amb el nom del lloc directament o almenys salta un error per aquest cas
#efectivament no chuta, la funcio aquesta  si que ho hauria de fer pero no va, l'he treta d'aqui https://geopandas.org/docs/user_guide/data_structures.html
def get_shortest_path_with_itime(igraph, origin, destination):
    if type (origin) == str:
        origin += ", Barcelona"
        ori = ox.geocode(origin)
        node_ori= get_nearest_node(igraph, ori, False)
    else:
        ori = [(origin[0]), (origin[1])]
        node_ori= get_nearest_node(igraph, ori, True)
    destination += ", Barcelona"
    dest = ox.geocode(destination)
    node_dest= get_nearest_node(igraph, dest, False)
    return ox.shortest_path(igraph, node_ori, node_dest, weight='itime')

def plot_path(igraph, ipath, SIZE):
    #ploting the data
    iplot = []
    for i in range (len(ipath)):
        iplot.append ((igraph.nodes[ipath[i]]['x'], igraph.nodes[ipath[i]]['y']))
    m = StaticMap (SIZE, SIZE) #test values
    line = Line(iplot, 'red', 2)
    m.add_line(line)
    #saving the image
    image = m.render()
    image.save("your_path.png")


def make_path(origin, destination, i_graph):
    # get 'intelligent path' between two addresses and plot it into a PNG image
    ipath = get_shortest_path_with_itime(i_graph, origin, destination)
    plot_path(i_graph, ipath, SIZE)

def prepare_i_graph():
    if not exists_graph(GRAPH_FILENAME) or not exists_graph(PLOT_GRAPH_FILENAME):
        graph, di_graph = download_graph(PLACE) #downloads both graph and digraph formats
        save_graph(di_graph, GRAPH_FILENAME)
    else:
        di_graph = load_graph(GRAPH_FILENAME)

    highways, n = download_highways(HIGHWAYS_URL) #n is the biggest way_id of the highways
    #downloads and prints congestions
    congestions = download_congestions(CONGESTIONS_URL, n)

    #checking_highways_congestions (highways, congestions)
    i_graph = build_i_graph(di_graph, highways,congestions, ARBITRARY, INFINIT)

    return i_graph
