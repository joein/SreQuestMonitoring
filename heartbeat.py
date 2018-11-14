
from telegram.ext import Updater
from datetime import datetime
from config import Config

updater = Updater(Config.TOKEN)
bot = updater.dispatcher.bot
bot.sendMessage(chat_id=Config.CHAT_ID, text=f'---HEARTBEAT---{datetime.now()}')
