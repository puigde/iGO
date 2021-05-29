import random
import os
import i_go
import osmnx as ox
from datetime import datetime, date, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from staticmap import StaticMap, CircleMarker

TOKEN = open('token.txt').read().strip() #constant which uses telegram to recognize the bot

# Keys of the dictionary necessary to store igraph and the time in the dictionary graph_info
key_time = random.randint(1000000, 9999999)
key_graph = random.randint(1000000, 9999999)

#i_graph and the time when it has been made are stored in a dictionary called graph_info
graph_info = {
        key_graph : i_go.prepare_i_graph(),
        key_time : datetime.now()
    }

def start(update, context):
    '''Sends a message introducing the bot.
    Complexity O(1).'''

    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am the iGo bot. Type the command you desire. If you don't know which commands to use, write /help in the chat and I'll give you some possible instructions")

def text_help():
    '''Returns the text necessary for the function help.
    Complexity O(1).'''

    help = "By writing /author you will obtain the names of the authors of the bot.\n \n"
    help += "By writing /go destination (for example: /go Sagrada Família) a map indicating the fastest route from your current position to Sagrada Família will be shown)\n \n"
    help += "By writing /where you will obtain an image with your current position indicated"
    return help

def help (update, context):
    '''Sends a message with all the possible commands.
    Complexity O(1).'''

    context.bot.send_message(chat_id=update.effective_chat.id, text=text_help())

def author (update, context):
    '''Sends a message with the name of the authors of the bot.
    Complexity O(1).'''

    context.bot.send_message(chat_id=update.effective_chat.id, text= "Made by Pol Puigdemont Plana and Jan Sallent Bayà")

def your_location (update, context):
    '''Stores the location of the user.
    Complexity O(1).'''

    #stores in a map the location of the user using the id of the user as the key
    try:
        key = update.effective_chat.id
        context.user_data[key] = [update.message.location.longitude, update.message.location.latitude]
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your location wasn't shared succesfully")

def pos (update, context):
    '''Stores the location of a user without sharing the location
    Precondition: if the location is send in coordinates, first parameter must be the latitude and the second one must be longitude.
    Complexity O(l) l being the lenght of context.args list.'''

    try:
        origin = [float(context.args [1]), float(context.args [0])]
        #latitude and longitude are changed because in i_go module, longitude is the first parameter and latitude is the second one
    except:
        street = context.args [0]
        for i in range (1, len(context.args)):
            street += ' '
            street += context.args[i]
        street += ", Barcelona" #if we add ", Barcelona" at the end, geocode function becomes much more accurate
        coord = ox.geocode (street)
        origin = [coord[1], coord[0]]
        #latitude and longitude are changed because in i_go module, longitude is the first parameter and latitude is the second one
    key = update.effective_chat.id
    context.user_data[key] = origin

def where (update, context):
    '''Sends a photo of the location of the user
    Precondition: location has to be send previously or function /pos has to be used.
    Complexity O(1).'''

    key = update.effective_chat.id #we use the id of the user as the key of the map
    try:
        location = context.user_data [key]
        fitxer = "%d.png" % random.randint(1000000, 9999999) #generate a random name for the photo

        mapa = StaticMap(500, 500)
        mapa.add_marker(CircleMarker((location[0], location[1]), 'blue', 10))
        imatge = mapa.render()
        imatge.save(fitxer)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(fitxer, 'rb'))
        os.remove(fitxer)
        #photo is made, send, and then removed

    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text = "Your location must be sent")

def go (update, context):
    '''Sends a photo showing the shortest path.
    Precondition: location has to be send previously or function /pos has to be used.
    Complexity of the shortest_path osmnx function.'''
    
    try:
        key = update.effective_chat.id
        origin = context.user_data [key]
        new_time = datetime.now()
    
        #if more than 5 minutes have been passed since congestions were added, we need to remake the graph and add new congestions
        if new_time - graph_info [key_time] > timedelta (minutes = 5):
            context.bot.send_message(chat_id=update.effective_chat.id, text="Your graph data needs an update, recalculating congestions, please wait a few seconds")
            graph_info[key_time] = datetime.now()
            graph_info[key_graph] = i_go.prepare_i_graph()

        destination = context.args [0]
        for i in range (1, len(context.args)):
            destination += ' '
            destination += context.args[i]
        destination += ", Barcelona" #if we add ", Barcelona" at the end, geocode function becomes much more accurate

        fitxer = "your_path.png"
        result= i_go.make_path(origin, destination, graph_info[key_graph])
        if (result==-1): #function returns -1 if path could not be found
            context.bot.send_message(chat_id=update.effective_chat.id, text = "Path could not be found")
        else: #there's only file if the path was existant
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(fitxer, 'rb'))
            os.remove(fitxer)
            #photo is made, send, and then removed
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text = "Your location must be sent")

# creates objects to work with Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# When bot recieves the command (eg: start), function /start is executed
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('pos',    pos))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(MessageHandler(Filters.location, your_location))

# bot is started
updater.start_polling()

# command necessary if MacOS is used
updater.idle()
