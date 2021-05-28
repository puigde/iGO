import random
import os
import i_go as i_go
import osmnx as ox
from datetime import datetime, date, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from staticmap import StaticMap, CircleMarker

SIZE = 800
INFINITY = 999999

#keys of the map necessary to store our igraph and the time it has been made
key_time = random.randint(1000000, 9999999)
key_graph = random.randint(1000000, 9999999)

#Sends a message introducing our bot
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Soc el bot i-go. Introdueix la comanda que desitgis. Si no saps quines comandes fer servir, escrivint /help al xat et podré ajudar")

#Returns the text necessary for the function help
def text_help():
    help = "Escrivint /author obtindràs el nom dels autors d'aquest bot.\n \n"
    help += "Escrivint /go destí (exemple: /go Sagrada Família) se't mostrarà un mapa indicant la ruta més curta des de la teva posició actual.\n \n"
    help += "Escrivint /where obtindràs la posició on et trobes ara mateix."
    return help

#Sends a message with all the possible commands
def help (update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_help())

#Sends a message with the name of the authors of the bot
def author (update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text= "Fet per Pol Puigdemont Plana i Jan Sallent Bayà")

#Stores the location of the user
def your_location (update, context):
    #stores in a map the location of the user using the id of the user as the key
    try:
        key = update.effective_chat.id
        context.user_data[key] = [update.message.location.longitude, update.message.location.latitude]
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="La localització no s'ha compartit correctement")

#Private function that stores the location of a user without sharing the location
#Precondition: if the location is send in coordinates, first parameter must be the latitude and the second one must be longitude
def _pos_ (update, context):
    try:
        origin = [float(context.args [1]), float(context.args [0])]
        #latitude and longitude are changed because in this program longitude is the first parameter and latitude the second one
    except:
        street = context.args
        #for i in range (1, len(context.args)):
        #    street += ' '
        #    street += context.args[i]
        street += ", Barcelona"
        coord = ox.geocode (street)
        origin = [coord[1], coord[0]]
    key = update.effective_chat.id
    context.user_data[key] = origin
    #latitude and longitude are changed because in this program longitude is the first parameter and latitude the second one

#Sends a photo of the location of the user
#Precondition: location has to be send previously or function /pos has to be used
def where (update, context):
    key = update.effective_chat.id #we use the id of the user as the key of the map
    try:
        origin = context.user_data [key]
        fitxer = "%d.png" % random.randint(1000000, 9999999) #generate a random name for the photo
        #photo is made, send and then removed
        mapa = StaticMap(500, 500)
        mapa.add_marker(CircleMarker((origin[0], origin[1]), 'blue', 10))
        imatge = mapa.render()
        imatge.save(fitxer)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(fitxer, 'rb'))
        os.remove(fitxer)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text = 'Necessito que em comparteixis la teva localització')


def go (update, context):
    key = update.effective_chat.id
    origin = context.user_data [key]
    if (origin[0]!= INFINITY and origin[1] != INFINITY):
        try:
            new_time = datetime.now()
            if new_time - context.user_data[key_time] < timedelta (minutes = 5):
                context.bot.send_message(chat_id=update.effective_chat.id, text="Estem recalculant les congestions, espera uns segons")
                context.user_data[key_time] = datetime.now()
                context.user_data[key_graph] =  i_go.prepare_i_graph()
        except:
                context.user_data[key_time] = datetime.now()
                context.user_data[key_graph] =  i_go.prepare_i_graph()
        street = context.args [0]
        for i in range (1, len(context.args)):
            street += ' '
            street += context.args[i]
        destination = street
        fitxer = "your_path.png"
        i_go.make_path(origin, destination, context.user_data[key_graph])
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

updater.start_polling()
updater.idle()
