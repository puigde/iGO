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
import pandas as pd #installation with pip3 install pandas
from staticmap import StaticMap, Line, CircleMarker
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


def exists_graph(GRAPH_FILENAME):
    '''Checks wether the graph file has already been downloaded on our directory or not.
    Recieves a parameter with the graph file name and returns a boolean indicating the result of the checking.'''

    try:
        open(GRAPH_FILENAME, 'rb')
    except: #if no graph can be opened an error would pop up, we indicate that graph doesn't exist
        return False
    return True

def download_graph(PLACE):
    '''Downloads a osmnx graph from a certain place recieved as a parameter. It does so trough two separated formats,
    both osmnx graphs but one is a regular graph and the other one is a digraph, for working we will use the digraph
    format as it represents all ways of the edges but we also get the regular one for format issues in the plotting of the graph.'''

    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    di_graph = ox.utils_graph.get_digraph(graph, weight='length') #di_graph separated for plotting issues
    return graph, di_graph

def save_graph (graph, GRAPH_FILENAME):
    '''Saves the downloaded osmnx graph which it recieves using pickle in a indicated filename so we can load it afterwards after
    having downloaded it once.'''

    with open(GRAPH_FILENAME, 'wb') as file:
        pl.dump(graph, file)

def load_graph(GRAPH_FILENAME):
    '''Loads the graph file from our directory, it recieves the filename and returns the graph.'''
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pl.load(file)
    return graph

def plot_graph(graph, onscreen=False):
    '''Plots the graph, in the regular graph osmnx datatype, not the digraph, it recieves as a parameter.
    The onscreen value indicates if the plotting will be done onscreen (only seems to work for mac users) or
    the plotting will be saved in a png image (set as default for avoiding errors).'''

    if onscreen:
        ox.plot_graph(graph, show=True)
    else:
        ox.plot_graph(graph, show= False, save= True, filepath= 'bcn.png')


def adjust_coordinates(highways):
    '''Adjusts coordinates format for each highway from string to pairs of float values. It recieves a vector of highways
    with coordinates in the unwanted string format and adjusts them making the mentioned changes.'''

    for highway in highways:
        highway[1] = highway[1].split(',')
        i=0
        newcoord=[]
        while (i < len(highway[1])):
            x = float (highway[1][i])
            i += 1
            y = float (highway[1][i])
            i += 1
            coord= (x,y)
            newcoord.append(coord)
        highway[1]= newcoord


#When referencing highways we don't mean actual highways but relative high-used streets by cars in Barcelona according to the City Hall's dataset
def download_highways(HIGHWAYS_URL):
    '''Gets, formats and returns highways data from the online Open Data Barcelona dataset, it recieves the URL as a parameter, and stores the data
    into a list of Highways tuples, which contain a 'way_id' parameter that references the id of the highway and a coordinates parameter
    which contains a list of strings (which will be formated into a list of pairs as seen in the adjust coordinates function)
    with the coordinates of the points that compose the highway. We have decided to use this format because it is very simple to work with
    and understand position acesses. When a highway has no data arbitrary values are set there, we include the positions no matter what
    because then it allows us to match the id's with the traffic congestion data. In this way we occupy some extra positions but we investigated
    it with counters and they are only a few, insignificant in comparison to the total size of the list, this insignificant memory sacrifice
    has been done in exchange for format simpliciry and code undestability, made possible because we studied the given data format before deciding.'''

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
    '''Gives a visual representation of the highways data on top of a generated StaticMap of Barcelona, which size is indicated as a parameter.
    It also recieves the highways list andthe filename value for saving the image.'''

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
    '''Gets, formats and returns all the data from traffic congestions in the same way and format as in the highways, it recieves the URL as a parameter
    plus the size of the highways list so the total positions match.'''

    cf= pd.read_csv(CONGESTIONS_URL, sep='#', header= None, usecols = [0, 2]) #reads significant values from the dataset
    congcounter=0
    avg= 0 #average congestion value
    congestions= cf.values.tolist() #formats them into a list
    cong= [Congestion (-1, -1)]*n #creates the list for the congestion namedtuples
    for congestion in congestions: #fills the list
        cong [congestion[0] - 1] = Congestion(congestion[0], congestion[1])
        if (congestion[1]!=0): #skip the no-data case
            avg+=congestion[1]
            congcounter+=1
    return cong, avg/congcounter


#gives a visual representation of the congestion in a static_map painted with lines and saves it into a png file (arbitrary size for tests, SIZE parameter can be added)
#colors correspondece : grey = no data, blue = very fluid, green = fluid, yellow = heavy, orange = very heavy, red = traffic jam, black = blocked
def plot_congestions (highways, congestions, filename,  SIZE):
    '''Saves a png image of a colored representation of the traffic congestions in the Barcelona map. It recieves the lists
    with the data of the highways and congestions and the filename and size for the image.'''
    m = StaticMap (SIZE, SIZE)
    for highway in highways:
       if highway.way_id!=-1: #only highways with existing data must be accessed
        colors= ['grey', 'blue', 'green', 'yellow', 'orange', 'red', 'black']
        congestion_type= congestions[highway.way_id - 1].congestion #id-1 because indexes start at 1 but list positions at 0
        line= Line(highway.coordinates, colors[congestion_type], 1)
        m.add_line(line)
    image = m.render()
    image.save(filename)

def print_graph_info(graph):
    '''Debugging and visualization function which iterates through a graph and prints it's information with clear separations
    to see what is going on and how the data is structured.'''

    for node1, info1 in graph.nodes.items():
        print('NODE INFO: ', node1, info1)

        for node2, edge in graph.adj[node1].items():
            print('NODE 2 ID')
            print(' ', node2)
            print('EDGE INFO BELOW')
            print(' ', edge)

def get_nearest_node(graph, pos, nonreversed=True):
    '''Given a graph and a position in coordinates finds the closest node to those coordinates. It has a reversed
    parameter which indicates positions are given in a (y,x) format instead of (x,y) as some functions work in that way
    but our datatypes respect the nonreversed format, we will usually use this function with geocode so it's order is set
    as default and we will indicate it manually with the parameter otherwise'''
    nearest_node = None
    nearest_dist = INFINIT

    for node, info in graph.nodes.items():
        if nonreversed:
            d = haversine((info['x'], info['y']), pos) #aquí diria que y i x estaven a l'inversa de com ho teniem nosaltres
        else:
            d= haversine((info['y'], info['x']), pos) #pel geocode
        if d < nearest_dist:
            nearest_dist = d
            nearest_node = node
    return nearest_node

def ponderate_congestion (congestion_type):
    '''Given a congestion type from the values given in the Barcelona dataset we assign a ponderation which will allow us to
    calibrate the itime value to take into account traffic congestion to calculate the fastest in a precise way.'''
    factor= [1.25, 1, 1.25, 1.5, 2, 3, INFINIT]
    try:
        return factor[congestion_type]
    except:
        return INFINIT


def build_i_graph(graph, highways, congestions, avg, INFINIT):
    '''Builds an intelligent graph with with an itime parameter in it's edges that takes into account lenght, max speed allowed,
    and traffic congestion in order to then compute the fastest route between two points for our bot users. It recieves the digraph
    (referenced as graph as always except the download function with format separation), the matched lists of highways and congestions,
    a value named avg which is the average congestion from all data collected,  which is the value assigned to fill those congestions that we don't
    have data for in the dataset and finally our INFINITY parameter.'''
    nx.set_edge_attributes(graph, int(round(avg)), name='congestion') #add a parameter for edges with our avg. value

    #THE ALGORITHM:
    #For all highways that we have valid data we will add the respective matched congestion value to the graph's edges that represent the highway.
    #To do so, for each pair of pairs(x,y) of coordinates we get the correspondent nodes and compute the shortest path between them, assuming this is
    #the path that we reference in our highway, and for this path we iterate for each pair of nodes and modify the congestion value of the edges
    #that link them with the respective value from the congestions matching the current highway we are iterating on. The complexity for this part
    #of the algorithm that rules the complexity for the whole algorithm is O(h*l*p) h being the size of the highways list, l being the size of the
    #list of coordinates in a highway and p being the size of the shortest path between two coordinates, we have 3 depth levels of iteration. It could
    #be done faster just by skipping iterations in the second level l and taking just the first and last node but this would be quite imprecise and
    #all the formatting done before would be useless if the edges modified wouldn't match the highways.

    for highway in highways:
        if (highway.way_id>0):
            for i in range(1, len(highway.coordinates)):
                node1= get_nearest_node(graph, highway.coordinates[i-1])
                node2= get_nearest_node(graph, highway.coordinates[i])
                try:
                    path= ox.shortest_path(graph, node1, node2, weight='length')
                    for j in range(1, len(path)):
                        path_node1= path[j-1]
                        path_node2= path[j]
                        graph[path_node1][path_node2]['congestion']= congestions[highway.way_id-1].congestion
                except nx.NetworkXNoPath: #the graph is not connex, sometimes there's no path possible between two nodes
                    pass

        print('loading congestions ', highway.way_id, "/", len(highways))

    #Add the itime attribute, iterate all the edges in the graph and compute the itime value that we will take as a reference
    #to get the fastest paths.
    nx.set_edge_attributes(graph, ARBITRARY, name='itime')
    for node1, node2 in graph.edges():
        length = graph[node1][node2]['length']
        try:
            speed = float(graph[node1][node2]['maxspeed'])
        except: #some edges don't have maxspeed value in them so we add the new normative speed value for the inside cities
            speed= 30
        congestion = ponderate_congestion(graph[node1][node2]['congestion'])
        graph[node1][node2]['itime'] = length*congestion/(speed)
    return graph

def checking_highways_congestions (highways, congestions):
    '''Debugging function that checks highways and congestions list matching given both lists.'''

    if len (highways) != len (congestions):
        print ("len not mathing")
        return
    n = len (highways)
    for i in range (n):
        if highways[i].way_id != i + 1:
            if highways[i].way_id != -1:
                print ("way index not matching position")
                print (i+1)
                print (highways[i].way_id)
        if congestions[i].c_id != i + 1:
            if congestions[i].c_id != -1:
                print ("cong index not matching position")
                print (i+1)
                print (congestions[i].c_id)
        if highways[i].way_id != congestions[i].c_id:
            print ("way index not matching position index")
            print (i+1)
    print ("comprovations completed")


def get_shortest_path_with_itime(igraph, origin, destination):
    '''Gets the shortest path with itime so it is indeed the fastest path, given our igraph that we have previously built
    and origin and destination parameters (origin can either be in coordinate format or string with the name of the place,
    but there is a precondition that destination is a string with the street name for format issues). When the origin and/or
    destination are given in string format with the name of the place we use the geocode function which returns the coordinates
    of the place given so we can then find the nearest node and finally the fastest path.'''
    if type (origin) == str:
        origin += ", Barcelona" #we concatenate Barcelona for precision issues with geocode, seems to work better
        ori = ox.geocode(origin)
        node_ori= get_nearest_node(igraph, ori, False)
    else:
        ori = [(origin[0]), (origin[1])]
        node_ori= get_nearest_node(igraph, ori)
    destination += ", Barcelona"
    dest = ox.geocode(destination)
    node_dest= get_nearest_node(igraph, dest, False)

    return ox.shortest_path(igraph, node_ori, node_dest, weight='itime')

def plot_path(igraph, ipath, SIZE):
    '''Saves a png image of the graphical representation of a given path in a graph at a certain size, all three recieved as parameters.'''

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
    '''Gets fastest path between two adesses and saves it into a png image using the functions seen above.'''

    ipath = get_shortest_path_with_itime(i_graph, origin, destination)
    plot_path(i_graph, ipath, SIZE)

def prepare_i_graph():
    '''Prepares the intelligent graph for work, if necessary it downloads and saves else it loads and then gets and applys
    highways and congestions data to build the intelligent graph with the itime value which it returns.'''
    if not exists_graph(GRAPH_FILENAME) or not exists_graph(PLOT_GRAPH_FILENAME):
        graph, di_graph = download_graph(PLACE) #downloads both graph and digraph formats
        save_graph(di_graph, GRAPH_FILENAME)
    else:
        di_graph = load_graph(GRAPH_FILENAME)
        graph= load_graph(PLOT_GRAPH_FILENAME)
    #downloads and plots into png the highways
    highways, n = download_highways(HIGHWAYS_URL) #n is the biggest way_id of the highways
    #downloads and plots into a png the congestions
    congestions, avg = download_congestions(CONGESTIONS_URL, n)
    #builds the intelligent graph
    i_graph = build_i_graph(di_graph, highways,congestions, avg, INFINIT)

    return i_graph
