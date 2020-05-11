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
    for extension in [f.replace('.py', '') for f in os.listdir("extensions") if
                      os.path.isfile(os.path.join("extensions", f))]:
        try:
            bot.load_extension(config.cogDir + '.' + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.', exc_info=True)


    # Fires when bot is in ready state
    @bot.event
    async def on_ready():
        info = await bot.application_info()
        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f'Bots Team: {info.name}')
        logging.info(f'Team Owned by: {info.owner}')
        logging.info(f'Discord.py version: {discord.__version__}')

        activity = discord.Game("type %help to get list of commands")
        await bot.change_presence(status=discord.Status.online, activity=activity)


    # Fires when a user joins E.P.E.C
    @bot.event
    async def on_member_join(member):
        role = member.guild.get_role(626460644648026152)
        await member.add_roles(role, reason="On join role assign")
        logging.info(f'[Member Role Change] {role.name} was added to {member.name}')
        guild = member.guild
        wembed = discord.Embed(title="Member #"+str(len(guild.members)),
                               description=f"""Welcome {member.mention} to {guild.name}, be sure to check the rules and verify yourself in 24 hours!. 
                               We hope you enjoy your time here.""")

        wembed.set_footer(text="Members: "+str(len(guild.members)))

        await guild.get_channel(626462887958937610).send(embed=wembed)

        logging.info(f'[Member Join] {member.name} joined {guild.name}')

        embed = discord.Embed(title="New Member", colour=Colour.green())
        embed.add_field(name="Username", value=str(member.name) + "#" + str(member.discriminator))
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account created", value=member.created_at.strftime("%d/%m/%Y %H:%M"))
        embed.add_field(name="Joined", value=member.joined_at.strftime("%d/%m/%Y %H:%M"))

        await guild.get_channel(649677778014437378).send(embed=embed)
        await bot.get_guild(647218684095365139).get_channel(653687223266443264).send(embed=embed)

        dmembed = discord.Embed(
            colour=Colour.blurple(),
            description=f"""
                {member.name},
                Thanks for joining Every Person Every Country, 
                be sure to check the rules and verify yourself within 24 hours!
                If you fail to do this you'll be kicked.   
                
                The Staff at E.P.E.C hopes you have a nice time with us.           
            """
        )

        await member.send(embed=dmembed)


    # Fires when a user leaves or is kicked from E.P.E.C
    @bot.event
    async def on_member_remove(member):
        guild = member.guild
        gembed = discord.Embed(title="",
                               description=f"""Goodbye to {member.mention} from all at {guild.name}, we hope they come back soon.""")
        gembed.set_footer(text="Members: "+str(len(guild.members)))
        
        await guild.get_channel(626462887958937610).send(embed=gembed)
        logging.info(f'[Member Leave] {member.name} left {guild.name}')

        embed = discord.Embed(title="Member Left", colour=Colour.blue())
        embed.add_field(name="Username", value=str(member.name) + "#" + str(member.discriminator))
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account created", value=member.created_at.strftime("%d/%m/%Y %H:%M"))

        await guild.get_channel(649677778014437378).send(embed=embed)
        await bot.get_guild(647218684095365139).get_channel(653687223266443264).send(embed=embed)


    # Fires when a message is sent in a channel
    @bot.event
    async def on_message(message):
        # Check if message author is anothor bot if true then return
        if message.author.bot:
            f = open("logs/discord"+datetime.now().strftime('%Y-%m-%d')+".log" ,"w+")
            f.write('%(asctime)s' "|" + message.author.name)
            f.close()
            return
        ctx = await bot.get_context(message)
        if ctx.valid:
            await message.add_reaction("\N{HOURGLASS}")
            # Try to process command and if that fails log to console with reason
            try:
                await bot.process_commands(message)
                logging.info(f'[Command] - {message.content} by {message.author} in {message.guild.name} was fired')
            except:
                logging.debug(
                    f'Bot has errored while processing the command: {message.content} in {message.guild.name}')
            try:
                await message.remove_reaction("\N{HOURGLASS}", bot.user)
            except:
                pass


    # Fires when a member is banned from E.P.E.C
    @bot.event
    async def on_member_ban(guild, user):
        logging.info(f'[Member Ban] {user.name} was banned from {guild.name}')

        embed = discord.Embed(title="Member Banned", colour=Colour.red())
        embed.add_field(name="Username", value=str(user.name) + "#" + str(user.discriminator))
        embed.add_field(name="ID", value=user.id)

        await guild.get_channel(649677778014437378).send(embed=embed)
        await bot.get_guild(647218684095365139).get_channel(653687223266443264).send(embed=embed)


    # Fires when a member is edited
    @bot.event
    async def on_member_update(before, after):
        broles = ""
        aroles = ""

        for i in range(len(before.roles)):
            broles += str(before.roles[i].mention) + ", "

        for i in range(len(after.roles)):
            aroles += str(after.roles[i].mention) + ", "

        if before.roles != after.roles:
            embed = discord.Embed(title=str(before.name) + "'s Roles Changed", colour=Colour.teal())
            embed.add_field(name="Old Roles", value=broles)
            embed.add_field(name="New Roles", value=aroles)

            guild = before.guild
            await guild.get_channel(649677778014437378).send(embed=embed)
            await bot.get_guild(647218684095365139).get_channel(653687223266443264).send(embed=embed)

        # async for entry in after.guild.audit_logs(limit=1, after=datetime.utcnow, action=discord.AuditLogAction.member_update):
        #    await before.guild.get_channel(649677778014437378).send('{0.user} updated {0.target}s role(s)'.format(entry))

        if before.nick != after.nick:
            embed = discord.Embed(title="Member changed Nick", colour=Colour.teal())
            embed.add_field(name="Old Username", value=str(before.nick))
            embed.add_field(name="New Nick", value=after.nick)

            guild = before.guild
            await guild.get_channel(649677778014437378).send(embed=embed)
            await bot.get_guild(647218684095365139).get_channel(653687223266443264).send(embed=embed)

            f = open("logs/discord/member_update/"+datetime.now().strftime('%Y-%m-%d')+".log" ,"a+")
            f.write(datetime.now().strftime('%Y-%m-%d - %I:%M %p')+" | "+str(before.name)+"'s nick was changed from "+str(before.nick)+" to "+str(after.nick)+"\n")
            f.close()

        # async for entry in after.guild.audit_logs(limit=1, after=datetime.utcnow, action=discord.AuditLogAction.member_update):
        #    await before.guild.get_channel(649677778014437378).send('{0.user} updated {0.target}s nick'.format(entry))


    bot.run(config.token, bot=True, reconnect=True)
