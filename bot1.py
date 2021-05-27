# importa l'API de Telegram
import random
import os
import i_go1 as i_go
import osmnx as ox
import collections

#Street = collections.namedtuple('Street', ['coor_x', 'coord_y', 'name']) # Tram

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from staticmap import StaticMap, CircleMarker

SIZE = 800
INFINITY = 999999


Origin = collections.namedtuple ('Origin', ['coord', 'name'])
graph = i_go.prepare_i_graph()


def pos(update, context):
    origin = Origin([INFINITY, INFINITY], ' ')
    try:
        origin.coord[0] = float (context.args [1])
        origin.coord[1] = float (context.args [0])

    except:
        street = context.args [0]
        for i in range (1, len(context.args)):
            street += ' '
            street += context.args[i]
        coord = ox.geocode (street)
        origin.coord[0] = coord [1] #lat i lon estan canviats en el geocode
        origin.coord[1] = coord [0]
        origin.name = street
    key = update.effective_chat.username
    value = origin
    context.user_data[key] = value

# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Soc el bot i-go. Introdueix la comanda que desitgis. Si no saps quines comandes fer servir, escrivint /help al xat et podré ajudar")

def text_help():
    help = "Escrivint /author obtindràs el nom dels autors d'aquest bot.\n \n"
    help += "Escrivint /go destí (exemple: /go Sagrada Família) se't mostrarà un mapa indicant la ruta més curta des de la teva posició actual.\n \n"
    help += "Escrivint /where obtindràs la posició on et trobes ara mateix."
    return help


def help (update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_help())

def author (update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text= "Fet per Pol Puigdemont Plana i Jan Sallent Bayà")

def your_location (update, context):
    origin = Origin([INFINITY, INFINITY], ' ')
    try:
        origin.coord[1], origin.coord[0] = update.message.location.latitude, update.message.location.longitude #tmb ta canviat
        origin.name = ' '
        key = update.effective_chat.username
        value = origin
        context.user_data[key] = value
    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="La localització no s'ha compartit correctement")

def where (update, context):

    key = update.effective_chat.username
    try:
        origin = context.user_data [key]
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text ='Necessito que em comparteixis la teva localització')

    #if (origin.coord[0] != INFINITY and origin.coord[1] != INFINITY):
    fitxer = "%d.png" % random.randint(1000000, 9999999)
    mapa = StaticMap(500, 500)
    mapa.add_marker(CircleMarker((origin[0], origin[1]), 'blue', 10))
    imatge = mapa.render()
    imatge.save(fitxer)
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(fitxer, 'rb'))
    os.remove(fitxer)
    #else :
    #    context.bot.send_message(chat_id=update.effective_chat.id, text ='Necessito que em comparteixis la teva localització')

def go (update, context):
    key = update.effective_chat.username
    origin = context.user_data [key]
    if (origin.coord[0]!= INFINITY and origin.coord[1] != INFINITY):
        street = context.args [0]
        for i in range (1, len(context.args)):
            street += ' '
            street += context.args[i]
        destination = street
        fitxer = "your_path.png"
        if (origin.street == ' '):
            i_go.make_path(origin.coord, destination, graph)
        else:
            i_go.make_path(origin.name, destination, graph)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(fitxer, 'rb'))
        os.remove(fitxer)

    else :
        context.bot.send_message(chat_id=update.effective_chat.id, text ='Necessito que em comparteixis la teva localització')

# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('pos', pos))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(MessageHandler(Filters.location, your_location))

# engega el bot
updater.start_polling()
