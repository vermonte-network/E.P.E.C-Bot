import discord
import pickle
from discord import Colour
from discord.ext import commands
import traceback
import config
import os
import logging
from datetime import datetime

errors = ""
bot = commands.Bot(command_prefix=config.get_prefix, description=config.description)

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir("extensions") if os.path.isfile(os.path.join("extensions", f))]:
        try:
            bot.load_extension(config.cogDir + '.' + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.', exc_info=True)

    #Fires when bot is in ready state
    @bot.event
    async def on_ready():
        info = await bot.application_info()

        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f'Owned by: {info.owner}')
        logging.info(f'Discord.py version: {discord.__version__}')
        
        activity = discord.Game("type %help to get list of commands")
        await bot.change_presence(status=discord.Status.online, activity=activity)

    bot.run(config.token, bot=True, reconnect=True)
