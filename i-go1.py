#he estat llegint i investigant com tenim disposat el graf de bcn en sí, és interessant l'enllaç https://networkx.org/documentation/stable/tutorial.html#examining-elements-of-a-graph
#per l'apartat concret i tot l'article en general, parla de com funciona un graf de osmnx com el que tenim creat

#A les funcion plot_highways i plot_congestions hi ha el parametre congestions.png / highways.png k em dona error si el poso, l'he tret i tot forula
#mira si a tu et va be sense o és alló de que o ho he de fer de una forma i tu d'una altre

from typing import NoReturn
from networkx.algorithms.bipartite.matching import INFINITY
from networkx.generators.classic import path_graph
import fiona #pel mac
import osmnx as ox
import pickle as pl
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
        newcord=[]
        while (i < len(highway[1])): #highway[1] are the coordinates
            x = float (highway[1][i])
            i += 1
            y = float (highway[1][i])
            i += 1
            pair= (x,y)
            newcord.append(pair)
        highway[1]= newcord
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
    hw = [Highway(-1, (-1, -1))] * n #list of namedtuple highways
    for highway in highways: #reoorder highways so they're sorted with way_id
        hw [highway[0] - 1] = Highway(highway[0], highway[1])
    print (hw[1].coordinates) #xivato per veure el format 
    return hw, n

#gives a visual representation of the highways in a static_map painted with lines and saves it into a png file (arbitrary size for tests, SIZE parameter can be added)
def plot_highways(highways, filename, SIZE):
    #ploting the data
    m = StaticMap (SIZE, SIZE) #test values
    for highway in highways:
        if highway.way_id != -1: #only existing higways must be painted
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
        #only existing higways must be painted
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


#FIRST VERSION, HIGHWAY COORDINATE FORMAT NEEDS TO BE ADJUSTED FOR THIS IMPLEMENTATION TO RUN, ALSO NEEDS TESTING AND TALKING THE EXACT FORMAT
#BUT I THINK THAT THE MAIN IDEA IS THERE
def build_i_graph(graph, highways, congestions, ARBITRARY, INFINIT):
    #adding a congestion parameter to edges at an arbitrary value arb
    nx.set_edge_attributes(graph, ARBITRARY, name='congestion')
    #print_graph_info(graph) #interesting to see graph's structure
    i=2
    first= True
    highway_id_counter=0
    for highway in highways:
        #taking into account prec. minimum of 4 coordinates for a highway
        if (len(highway.coordinates)>0):
            start= highway.coordinates[0]
        while i< len(highway.coordinates): #JAN, ACTUALMENT AQUEST PARÀMETRE ESTÀ EN PARELLS DE DOUBLES SI HO VOLS PASSAR A
            #UNA LLISTA DE STRINGS, AQUÍ ESTÀ PROGRAMAT PER FER-HO AIXÍ, FIXA'T QUE AGAFO PRIMER UNA DESPRÉS L'ALTRA I DESPRÉS LES PASSO
            #A GEOCODE PER CADASCUNA DE LES PARELLES PERÒ SEMPRE ES POT REFORMATEJAR COM HO VEGIS, SINÓ TRUCA'M I HO COMENTEM QUAN ET VAGI BÉ
            #LLAVORS PODRÍEM ELIMITAR TOT EL CODI DE FORMATEIG AL UTILITZAR GEOCODE
               #això estaria construint l'string amb la coma per si     ho haguessim separat
                #al formatejar però si no hagués estat així i haguessim pescat cada dos posicions pel vector es fa una petita mod i com nou
            end=  highway.coordinates[i]

            #once we have start and end we geolocalize them
            if (first):
                start_posnode= ox.geocode(start)
                end_posnode= ox.geocode(end)
            else:
                end_posnode= ox.geocode(end)

            #NOTA IMPORTANT, SI POSÉSSIM TOTS ELS VALORS X PER CADA NODE EN UNA LLISTA X I ÍDEM PELS Y PODRÍEM OBTENIR TOTS ELS NODES D1
            #PERO CREC QUE 1 A 1 POTSER ÉS MÉS FÀCIL DE TREBALLAR, VEURE FUNC.: https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=nearest_nodes#osmnx.distance.nearest_nodes

            #TROBEM ELS ID'S DELS NODES INICI I FINAL EN ELS QUE ENS TROBEM
            if (first):
                id_start= ox.nearest_nodes(graph, start_posnode[0], start_posnode[1]) #check if float() indicator is needed
                first= False
            else:
                id_start=id_end

            id_end= ox.nearest_nodes(graph, end_posnode[0], end_postnode[1])

            #ONCE WE HAVE NODES GEOLOCALIZED WE GET THE PATH BETWEEN THEM AND ASSUME IT'S THE HIGHWAY
            try:
                path= ox.shortest_path(id_start, id_end) #returns a list of node id's that form the shortest path between start node and finish node

                #we now want to iterate through the edges that link this nodes and add the respective congestion parameter related to the highway
                path_start= path[0]
                first=True
                j=1
                while (j<len(path)): #actualitza congestió per cada parells de nodes consecutiva del camí més curt
                    if (not first):
                        path_start=path_end
                    path_end= path[j]
                    for i in range (len(graph[path_start][path_end])): #needs this kind of iteration because of the digraph format
                        graph[path_start][path_end][i]['congestion']= congestions[highway_id_counter] #add the congestion parameter of the whole highway
                    first=False
                    j+=1
            except:
                "there is no path between those two nodes, skip"

        highway_id_counter+=1

    #HERE, THE CONGESTION VALUES THAT WE KNOW SHOULD BE SET IN THE RESPECTIVE PATHS OF ALL EDGES THAT ARE CONTAINED IN ALL OUR HIGHWAYS
    #I THINK THAT WE COULD COMPUTE THE AVERAGE CONGESTION WHEN READING AND SET IT AS THE VALUE OF THE ARBITRARY CONSTANT IF WE DON'T
    #WANT TO OVERCOMPLICATE IT, ONCE ALL EDGES HAVE A CONGESTION VALUE WE CAN PROCEED AND ADD THE ITIME CONCEPT WHICH WILL BE ANOTHER PARAMETER
    #OF EVERY EDGE THAT THE SHORTEST PATH FUNCTION WILL TAKE IN CONSIDERATION FOR COMPUTING THE SORTEST PATH, FOR EXAMPLE

        #adding itime value
    nx.set_edge_attributes(graph, INFINIT, name='itime')

    #iterating and modifiying itime for all edges
    for n1, n2 in graph.edges():
        for i in range(len(graph[n1][n2])):
            length= graph[n1][n2][i]['lenght']
            speed_max= float(graph[n1][n2][i]['speed'])
            congestion= graph[n1][n2][i]['congestion']
            itime= (length/speed)* congestion #arbitrary, after testing we calibrate it

    #HERE THE INTELLIGENT GRAPH IS BUILT AND NOW WE CAN COMPUTE THE SHORTEST PATH BETWEEN TWO NODES USING THE SHORTEST PATH FUNCTION, SEE BELOW:
    #sp= ox.shortest_path(starting_point, finishing_point, weight='itime')



def test():
    # loads/downloads graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME) or not exists_graph(PLOT_GRAPH_FILENAME):
        graph, di_graph = download_graph(PLACE) #downloads both graph and digraph formats
        save_graph(di_graph, GRAPH_FILENAME)
        save_graph(graph, PLOT_GRAPH_FILENAME)
    else:
        print("graph already saved, loading...")
        di_graph = load_graph(GRAPH_FILENAME)
        graph= load_graph(PLOT_GRAPH_FILENAME) #for printing issues

    #plot_graph(graph) #prints the graph

    #downloads and prints highways
    highways, n = download_highways(HIGHWAYS_URL) #n is the biggest way_id of the highways
    plot_highways(highways, 'highways.png', SIZE)

    #downloads and prints congestions
    congestions = download_congestions(CONGESTIONS_URL, n)
    plot_congestions(highways, congestions, 'congestions.png', SIZE)

    i_graph= build_i_graph(di_graph, highways,congestions, ARBITRARY, INFINIT)


test()
