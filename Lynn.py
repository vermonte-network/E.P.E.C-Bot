import discord
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
        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f'Discord.py version: {discord.__version__}')
        
        activity = discord.Game("type %help to get list of commands")
        await bot.change_presence(status=discord.Status.online, activity=activity)


    #Fires when a user joins E.P.E.C
    @bot.event
    async def on_member_join(member):
        guild = member.guild
        to_send = 'Welcome {0.mention} to {1.name}, hope you enjoy your stay!'.format(member, guild)
        await guild.get_channel(626462887958937610).send(to_send)
        logging.info(f'{member.name} joined {guild.name}')
            
        embed = discord.Embed(title="New Member", colour=Colour.blurple())
        embed.add_field(name="Username", value=str(member.name) + "#" + str(member.discriminator))
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account created", value=member.created_at.strftime("%d/%m/%Y %H:%M"))
        embed.add_field(name="Joined", value=member.joined_at.strftime("%d/%m/%Y %H:%M"))
        
        await guild.get_channel(646722408933359648).send(embed=embed)
        
    #Fires when a user leaves E.P.E.C
    @bot.event
    async def on_member_leave(member):
        guild = member.guild
        to_send = 'Farewell {0.mention}!'.format(member, guild)
        await guild.get_channel(626462887958937610).send(to_send)    
        logging.info(f'{member.name} left {guild.name}'.format(member, guild))
            
        embed = discord.Embed(title="Member Left", colour=Colour.blurple())
        embed.add_field(name="Username", value=str(member.name) + "#" + str(member.discriminator))
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account created", value=member.created_at.strftime("%d/%m/%Y %H:%M"))        
        
        await guild.get_channel(646722408933359648).send(embed=embed)

    #Fires when a message is sent in a channel
    @bot.event
    async def on_message(message):
        #Check if message author is anothor bot if true then return
        if message.author.bot:
            return
        ctx = await bot.get_context(message)
        if ctx.valid:
            await message.add_reaction("\N{HOURGLASS}")
            #Try to process command and if that fails log to console with reason
            try:    
                await bot.process_commands(message)
                logging.info(f'[command] - {message.content} by {message.author} in {message.guild.name} was fired')
            except:
                logging.debug(f'Bot has errored while processing the command: {message.content} in {message.guild.name}')                  
            try:
                await message.remove_reaction("\N{HOURGLASS}", bot.user)
            except:
                pass

    bot.run(config.token, bot=True, reconnect=True)
