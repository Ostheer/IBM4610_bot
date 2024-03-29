### EDIT THIS LINE
configfile = "/home/>>>USERNAME<<</.config/suremark/config.ini"

import time
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import configparser
from tinydb import TinyDB
import ibmcallbacks as ibm
import ibmcommands as comm
import signal

config = configparser.ConfigParser()
config.read(configfile)
db = TinyDB(config["ADMIN"]["database_file"])

manager = ibm.manager(db, config)
updater = Updater(token=config["ADMIN"]["key"], use_context=True)
dispatcher = updater.dispatcher

commands = {"start":     (comm.start,     0),
            "help":      (comm.help,      0),
            "qr":        (comm.qr,        1),
            "template":  (comm.template,  1),
            "sleep":     (comm.sleep,     2),
            "database":  (comm.database,  2),
            "cancel":    (comm.cancel,    2),
            "register":  (comm.register,  2)}

for command, (handler, clearance) in commands.items():
    dispatcher.add_handler(CommandHandler(command, handler(clearance, manager).do))

for f in (Filters.sticker, Filters.text, Filters.photo, Filters.document):
    dispatcher.add_handler(MessageHandler(f,  manager.handle))

signal.signal(signal.SIGUSR2, lambda x, y: manager.toggle_sleep(None, None, send_messages=False))

for i in range(20):
    try:
        updater.start_polling()
    except telegram.error.NetworkError:
        time.sleep(10)

