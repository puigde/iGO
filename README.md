# iGo

No perdeu més el temps: iGo us ensenya el camí més ràpid per córrer com una llebre! 🐰🚘


## Introducció

Aquesta pàgina descriu el projecte iGo, que correspon a la segona pràctica del
curs 2021 d'AP2 al GCED.

La vostra tasca consisteix en implementar en Python un Bot de Telegram que
permeti, dins de la ciutat de Barcelona, guiar els usuaris des de la seva
posició actual fins a la seva destinació pel camí més ràpid en cotxe,
utilitzant el novedós concepte d'*itime* (temps intel·ligent) que té en compte
l'estat del trànsit en temps real en certs trams de la ciutat.

Per fer aquesta pràctica, haureu d'obtenir dades de diferents proveïdors
i entrellaçar-les mutuament. En particular, utilitzareu:

- El mapa de Barcelona d'[Open Street Map](https://www.openstreetmap.org). 🧭

- La [informació sobre l'estat del trànsit als trams](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/trams)  de Barcelona. 🐌

- La [relació de trams de la via pública](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/transit-relacio-trams)  de Barcelona. 🛣

Afortunadament, existeixen algunes llibreries ben documentades que us facilitaran molt la feina:

- Per utilitzar els Open Street Maps utilitzareu la llibreria [OSMnx](https://geoffboeing.com/2016/11/osmnx-python-street-networks/), que funciona
damunt de [NetworkX](https://networkx.github.io/documentation/stable/tutorial.html).

- Per llegir les dades del Servei de dades obertes de l'Ajuntament de Barcelona,
haureu de llegir fitxers en format `csv`, tot utilitzant el mòdul estàndard de Python
[csv](https://docs.python.org/3/library/csv.html).

- Els mapes que mostrareu els generareu amb [`staticmap`](https://github.com/komoot/staticmap), una llibreria de
Python que es connecta a Open Street Maps per generar mapes amb línies i marcadors.

- Per escriure el Bot de Telegram podeu utilitzar
[aquesta lliçó](https://lliçons.jutge.org/python/telegram.html).




## Arquitectura del sistema

Els sistema consta de dos mòduls:

- `igo.py` conté tot el codi i estructures de dades relacionats amb
l'adquisició i l'enmagatzematge de grafs corresponents a mapes, congestions i
càlculs de rutes.  Aquest mòdul no en sap res del bot.

- `bot.py` conté tot el codi relacionat amb el bot de Telegram i utilitza el
  mòdul `igo`. La seva tasca és reaccionar a les comandes dels usuaris per poder-los guiar.

La raó per separar el bot de la resta de funcionalitats és poder adaptar
fàcilment el projecte a noves plataformes en el futur (web, whatsapp…), quan aquest triomfi i
tots plegats ens fem rics! 🤑


## Funcionalitat del mòdul `igo`

Heu de dissenyar el mòdul `igo`  per tal contingui tot el codi relacionat amb
l'adquisició, l'enmagatzematge i la consulta dels grafs de carrers de la
ciutat, dels seus trams, i del trànsit en aquests trams. A més, aquest mòdul
ha de ser capaç de calcular camins mínims entre parells de punts a la ciutat,
tot utilitzant el concepte d'*itime* que més tard es concreta. Aquest mòdul
també ha de ser capaç de generar imatges amb els camins mínims que s'han
calculat.

El programa d'exemple següent us dóna una pauta per dissenyar els tipus i les funcions
d'aquest mòdul, malgrat que no és estrictament necessari que seguiu aquesta interfície, teniu
llibertat completa.

```python
PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

Highway = collections.namedtuple('Highway', '...') # Tram
Congestion = collections.namedtuple('Congestion', '...')

def test():
    # load/download graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME):
        graph = download_graph(PLACE)
        save_graph(graph, GRAPH_FILENAME)
    else:
        graph = load_graph(GRAPH_FILENAME)
    plot_graph(graph)

    # download highways and plot them into a PNG image
    highways = download_highways(HIGHWAYS_URL)
    plot_highways(highways, 'highways.png', SIZE)

    # download congestions and plot them into a PNG image
    congestions = download_congestions(CONGESTIONS_URL)
    plot_congestions(highways, congestions, 'congestions.png', SIZE)

    # get the 'intelligent graph' version of a graph taking into account the congestions of the highways
    igraph = build_igraph(graph, highways, congestions)

    # get 'intelligent path' between two addresses and plot it into a PNG image
    ipath = get_shortest_path_with_ispeeds(igraph, "Campus Nord", "Sagrada Família")
    plot_path(igraph, ipath, SIZE)
```


Per tal de predir el camí més ràpid entre dos punts, iGo utilitza un concepte de
temps intel·ligent anomenat *itime*. Aquest concepte apareix de la integració de
diferents dades disponibles a les dades obertes que el projecte utilitza:

- Velocitat i llargada de cada carrer al graf d'OSMnx: Cada aresta del graf de la ciutat té
un atribut `speed` que indica la velocitat màxima en aquella aresta i un atribut
`length` que indica la seva llargada. Per tant, és fàcil deduir el temps necessari per
recórrer aquella aresta en condicions de circulació òptima.

- La relació de trams de la via pública de la ciutat de Barcelona
defineix un conjunt de trams amb les artèries de circulació més importants de la ciutat.
Cada tram ve definit per una seqüència de segments, dels quals es dónen les coordenades
dels seus extrems. Al codi anterior, els trams es corresponen a les *highways*: malgrat
que no siguin autopistes, solen ser pistes ràpides a la ciutat.

- La informació sobre l'estat del trànsit als trams de la ciutat de Barcelona
dóna la congestió existent a cadascun dels trams. Aquest estat
pot ser: sense dades, molt fluid, fluid, dens, molt dens, congestió, tallat.
Aquesta informació s'actualitza cada cinc minuts.

Malauradament, la informació dels trams que ens proporciona l'ajuntament no quadra
completament amb els carrers d'OSM... I tampoc hi ha informació de la congestió
per a tots els carrers de la ciutat, només per a alguns.
Per tant, cal trobar alguna forma per transportar les dades de congestió dels
trams als carrers d'OSMnx. Aquesta propagació de les congestions s'hauria
d'acabar materialitzant en un nou atribut `itime` a cada aresta del graf "intel·ligent",
sobre el qual es calcularan els camins mínims.

La forma de propagar les congestions és la següent: Per a cada segment de cada
tram pel qual es disposi d'informació sobre congestió, es buscaràn els dos
nodes del graf que siguin més propers als extrems d'aquests segments, i es
trobarà  el camí amb distància mínima per anar entre ambdós en el graf. A tots
els arcs d'aquest camí se'ls imputarà la congestió del tram.

A més, **opcionalment**, també podeu afegir un retard a cada cruïlla de carrers:
Aquest retard hauria de ser petit si la cruïlla s'atravessa del dret (gir de
menys de 15°, diguem) i hauria de ser més gran si cal girar a la cruïlla
(gir de més de 15°). A més, també ho podeu millorat tenint en compte que
girar cap a l'esquerra sol ser més lent que girar cap a la dreta. El grafs
d'OSMnx tenen atributs amb l'angle de les arestes (*bearings*) que us poden
ser útils per això. En aquest cas és probable que us convingui modificar
la topologia (nodes i arcs) del graf.

Evidentment, cada implementació dels *itime* tindrà uns paràmetres associats
que vosaltres haureu de definir i encapsular de forma adient (amb ús de
constants o funcions, per exemple).  Com s'ha vist al programa d'exemple, és
raonable oferir una funció (com ara `build_igraph`) que s'encarregui  de
calcular el graf amb atributs "intel·ligents". És reponsabilitat vostra
proposar, implementar i documentar una bona forma de calcular l'*itime* i els
paràmetres dels quals depengui, basant-vos en les dades disponibles.


## Funcionalitat del mòdul `bot`

El bot de Telegram ha de donar suport a les comandes següents:

- `/start`: inicia la conversa.
- `/help`: ofereix ajuda sobre les comandes disponibles.
- `/author`: mostra el nom dels autors del projecte.
- `/go destí`: mostra a l'usuari un mapa per arribar de la seva posició actual fins al punt de destí escollit
    pel camí més curt segons el concetpe de *ispeed*.
   Exemples:
    - `/go Campus Nord`
    - `/go Sagrada Família`
    - `/go Pla de Palau, 18` (Facultat de Nàutica)
- `/where`: mostra la posició actual de l'usuari.

També hi ha una comanda *secreta* que permet falsejar la posició actual de l'usuari,
de forma que es puguin fer proves facilment sense haver de sortir de casa:

- `/pos`: fixa la posició actual de l'usuari a una posició falsa.
   Exemples:
    - `/pos Campus Nord`
    - `/pos 41.38248 2.18511` (Facultat de Nàutica)


El bot hauria de començar carregant les dades necessàries. A partir d'aquell
moment esperarà connexions de diferents usuaris i els ajudarà a arribar a la
seva destinació tot mostrant la ruta òptima per anar des de la seva posició
actual (real o falsejada amb `/pos`) fins al seu destí. Quan sigui necessari,
el Bot recarregarà les dades sobre la congestió dels trams, per tal
d'adaptar-se al trànsit en temps real.

Totes les comandes han de funcionar per a diferents usuaris alhora i les accions
d'un usuari no han d'interferir amb els altres usuaris.


## Llibreries

Utilitzeu les llibreries de Python següents:

- `csv` per llegir en format CSV.
- `pickle` per llegir/escriure dades en Python de/en fitxers.
- `urllib` per descarregar fitxers des de la web.
- `networkx` per a manipular grafs.
- `osmnx` per a obtenir grafs de llocs.
- `haversine` per a calcular distàncies entre coordenades.
- `staticmap` per pintar mapes.
- `python-telegram-bot` per interactuar amb Telegram.

Les tres primeres són estàndards i no cal que feu res per tenir-les.
Les altres llibreries es poden instal·lar amb `pip3 install` o `sudo pip3 install`, però `osmnx`
porta una mica de feina... En Ubuntu, cal primer fer un `sudo apt install
libspatialindex-dev`. En Mac, cal fer un `brew install spatialindex gdal` i, a
més, posar les darreres versions dels instal·ladors:

1. `pip3 install --upgrade pip setuptools wheel`
2. `pip3 install --upgrade osmnx`
3. `pip3 install --upgrade staticmap`

Podeu utilitzar lliurament altres llibreries estàndards de Python, però si no
són estàndards, heu de demanar permís als vostres professors (que segurament no
us el donaran).



## Indicacions per treballar amb els grafs d'OSMnx

Els grafs d'OSMnx tenen molta informació i triguen molt a carregar. Per aquesta
aplicació, demaneu-los per a cotxe i simplificats i elimineu els arcs múltiples.
A més, descarregeu-los el
primer cop i deseu-los amb Pickle:

```Python
graph = osmnx.graph_from_place(PLACE, network_type='drive', simplify=True)
graph = osmnx.utils_graph.get_digraph(graph, weight='length')
with open(GRAPH_FILENAME, 'wb') as file:
    pickle.dump(graph, file)
```

A partir d'aquest moment els podreu carregar des del fitxer enlloc de des de la xarxa:


```python
with open(GRAPH_FILENAME, 'rb') as file:
    graph = pickle.load(file)
```

Aquesta és la manera de recórrer tots els nodes i les arestes d'un graf:

```python
# for each node and its information...
for node1, info1 in graph.nodes.items():
    print(node1, info1)
    # for each adjacent node and its information...
    for node2, edge in graph.adj[node1].items():
        print('    ', node2)
        print('        ', edge)
```

Compte: a vegades hi ha sorpreses: carrers amb més d'un nom,
valors absents o nuls... Molt divertit!

A banda, segurament haureu d'utilitzar aquestes funcions per treballar amb grafs:

- [`get_nearest_node`](https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=get_nearest_node#osmnx.distance.get_nearest_node)
- [`shortest_path`](https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=shortest_path#osmnx.distance.shortest_path)
- [`geocode`](https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=geocode#osmnx.geocoder.geocode)
- [`plot_graph`](https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=plot_graph#osmnx.plot.plot_graph)
- [`add_edge_bearings`](https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=add_edge_bearings#osmnx.bearing.add_edge_bearings)


Notes: 

- El paquet `networkx` està implementat directament en Python i és bastant lent. Què fi farem...

- Alguns m'heu dit que que `plot_graph` deixa de funcionar amb graf un cop fet el `get_digraph`.

- Els qui teniu Ubuntu sobre Windows,  `plot_graph` no sembla funcionar, potser perquè deu tenir alguna limitació que li impedeix mostrar gràfics per la pantalla. En aquest cas, deseu la imatge en un fitxer:

    ```python
    g = osmnx.graph_from_place('Vic, Catalonia')
    osmnx.plot_graph(g, show=False, save=True, filepath='vic.png')
    ```


## Indicacions per llegirs URLs en CSV

Aquest fragment de codi us pot ajudar per llegir dades en CSV descarregades
d'una web:

```python
with urllib.request.urlopen(HIGHWAYS_URL) as response:
    lines = [l.decode('utf-8') for l in response.readlines()]
    reader = csv.reader(lines, delimiter=',', quotechar='"')
    next(reader)  # ignore first line with description
    for line in reader:
        way_id, description, coordinates = line
        print(way_id, description, coordinates)
```


# Instruccions

## Equips

Podeu fer aquest projecte sols o en equips de dos. En cas de fer-lo en equip,
la càrrega de treball dels dos membres de l'equip ha de ser semblant i el
resultat final és responsabilitat d'ambdós. Cada membre de l'equip ha de saber
què ha fet l'altre membre.

Els qui decidiu fer el segon projecte en un equip de dos estudiants, envieu
abans de les **23:59 del divendres 30 d'abril** un missatge al professor Jordi Petit
amb aquestes característiques:

- des del compte `@estudiantat.upc.edu` del membre més jove de l'equip,
- amb tema (subject) `Equips AP2 2021`,
- amb el nom dels dos estudiants de l'equip al cos del missatge,
- fent còpia (CC) al compte `@estudiantat.upc.edu` de l'altre estudiant.

Si no es reb cap missatge d'equip per aquesta data, es considerarà que feu la
pràctica sols. Si heu enviat aquest missatge, es considerarà que feu la
pràctica junts (i no s'admetràn "divorcis").


## Lliurament

Heu de lliurar la vostra pràctica al Racó. Si heu fet la pràctica en equip,
només el membre més jove ha de fer el lliurament. El termini de lliurament és
el **dilluns 31 de maig a les 23:59**.

Només heu de lliurar un fitxer ZIP que, al descomprimir-se,
generi els fitxers següents:

- `igo.py`,
- `bot.py`,
- `requirements.txt`,
- `README.md` i
- `*.png` si cal adjuntar imatges a la documentació.

Res més. Sense directoris ni subdirectoris. No heu d'incloure el vostre Token de Telegram
(és una informació personal vostra).

Els vostres fitxers de codi en Python han de seguir
[les regles d'estíl PEP8](https://www.python.org/dev/peps/pep-0008/). Podeu
utilitzar el paquet `pep8` o http://pep8online.com/ per assegurar-vos
que seguiu aquestes regles d'estíl.
L'ús de tabuladors en el codi queda
prohibit (zero directe). Si voleu, podeu fer ratlles més llargues que les que dicta PEP8.

El projecte ha de contenir un fitxer `README.md`
que el documenti. Vegeu, per exemple, https://www.makeareadme.com/.
Si us calen imatges al `README.md`, deseu-los com a fitxers PNG.

El projecte també ha de contenir un fitxer `requirements.txt`
amb les llibreries que utilitza el vostre projecte per poder-lo instal·lar.
Vegeu, per exemple, https://www.idkrtm.com/what-is-the-python-requirements-txt/.



## Consells

- Us suggerim seguir aquests passos per a dur a terme el vostre projecte:

    1. Seguiu el [tutorial de networkx](https://networkx.github.io/documentation/stable/tutorial.html).

    1. Seguiu el [tutorial de osmnx](https://geoffboeing.com/2016/11/osmnx-python-street-networks/).

    1. Estudieu el format de la relació de [trams de la via pública](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/transit-relacio-trams) de la ciutat de Barcelona.

    1. Estudieu la informació sobre [l'estat del trànsit als trams](https://opendata-ajuntament.barcelona.cat/data/ca/dataset/trams)  de la ciutat de Barcelona.

    1. Seguiu el
    [tutorial d'`staticmaps`](https://lliçons.jutge.org/python/fitxers-i-formats.html)
    (hi ha altres coses, centreu-vos en la darrera secció).

    1. Dissenyeu el mòdul `igo` tot definint els seus tipus de dades i les capçaleres de les seves funcions públiques.
        Feu-vos un esquema de les diferents funcions i crides entre elles.

    1. Implementeu el mòdul `igo`
       però sense implementar encara el concepte de *itime*. Si seguiu la pauta, implementeu cada funció `load_x`
       i proveu-la amb la corresponent `plot_x`.
       Useu un [*stub*](https://ca.wikipedia.org/wiki/Stub_(software_testing))
       per a `build_igraph` que essencialment no faci res.

    1. Implementareu el concepte d'*itime* en el `build_igraph` real.

    1. Seguiu el [tutorial de telegram](https://lliçons.jutge.org/python/telegram.html).

    1. Implementeu el mòdul `bot` i proveu-lo.

-  Documenteu el codi a mesura que l'escriviu.

- L'enunciat deixa obertes moltes qüestions expressament. Sou els responsables de prendre
  les vostres decisions de disseny i deixar-les reflectides adientment al codi i
  a la documentació.

- Podeu ampliar les capacitats del vostre projecte mentre manteniu les
  funcionalitats mínimes previstes en aquest enunciat. Ara bé, aviseu abans als
  vostres professors i deixeu-ho tot ben documentat.

- Per evitar problemes de còpies, no pengeu el vostre projecte en repositoris
  públics.


## Autors

Jordi Cortadella i Jordi Petit<br>
© Universitat Politècnica de Catalunya, 2021

<br>
