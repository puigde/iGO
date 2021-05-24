# importa l'API de Telegram
import random
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from staticmap import StaticMap, CircleMarker

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
    context.bot.send_message(chat_id=update.effective_chat.id, text="Fet per Pol Puigdemont Plana i Jan Sallent Bayà")

def where(update, context):
    '''aquesta funció es crida cada cop que arriba una nova localització d'un usuari'''

    # aquí, els missatges són rars: el primer és de debò, els següents són edicions
    message = update.edited_message if update.edited_message else update.message
    # extreu la localització del missatge
    lat, lon = message.location.latitude, message.location.longitude
    # escriu la localització al servidor
    print(lat, lon)
    # envia la localització al xat del client
    context.bot.send_message(chat_id=message.chat_id, text=str((lat, lon)))

# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(MessageHandler(Filters.location, where))

# engega el bot
updater.start_polling()
