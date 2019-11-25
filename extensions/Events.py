import discord
from discord.ext import commands
from discord import Colour
import logging
import config

class Events(commands.Cog):   
    bot = commands.Bot(command_prefix=config.get_prefix, description=config.description)
    
    #Fires when a user joins E.P.E.C
    async def on_member_join(self, member):
        discord.Guild.get_role
        role = member.guild.get_role(626460644648026152)
        await member.add_roles(626460644648026152, reason="On join role assign")
        logging.info(f'[Member Role Change] {role.name} was added to {member.name}')
        guild = member.guild
        to_send = 'Welcome {0.mention} to {1.name}, be sure to check rules and verify yourself in 24 hours!. We Hope you enjoy your time here.'.format(member, guild)
        await guild.get_channel(626462887958937610).send(to_send)
        logging.info(f'[Member Join] {member.name} joined {guild.name}')
            
        embed = discord.Embed(title="New Member", colour=Colour.blurple())
        embed.add_field(name="Username", value=str(member.name) + "#" + str(member.discriminator))
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account created", value=member.created_at.strftime("%d/%m/%Y %H:%M"))
        embed.add_field(name="Joined", value=member.joined_at.strftime("%d/%m/%Y %H:%M"))
        
        await guild.get_channel(646722408933359648).send(embed=embed)
        
    #Fires when a user leaves E.P.E.C
    async def on_member_remove(self, member):
        guild = member.guild
        to_send = 'Farewell {0.mention}!'.format(member, guild)
        await guild.get_channel(626462887958937610).send(to_send)    
        logging.info(f'[Member Leave] {member.name} left {guild.name}'.format(member, guild))
            
        embed = discord.Embed(title="Member Left", colour=Colour.blurple())
        embed.add_field(name="Username", value=str(member.name) + "#" + str(member.discriminator))
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account created", value=member.created_at.strftime("%d/%m/%Y %H:%M"))        
        
        await guild.get_channel(646722408933359648).send(embed=embed)

    #Fires when a message is sent in a channel
    async def on_message(self, message):
        #Check if message author is anothor bot if true then return
        if message.author.bot:
            return
        ctx = await bot.get_context(message)
        if ctx.valid:
            await message.add_reaction("\N{HOURGLASS}")
            #Try to process command and if that fails log to console with reason
            try:    
                await bot.process_commands(message)
                logging.info(f'[Command] - {message.content} by {message.author} in {message.guild.name} was fired')
            except:
                logging.debug(f'Bot has errored while processing the command: {message.content} in {message.guild.name}')                  
            try:
                await message.remove_reaction("\N{HOURGLASS}", bot.user)
            except:
                pass

def setup(bot):
    bot.add_cog(Events(bot))