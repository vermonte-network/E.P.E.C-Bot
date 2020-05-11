import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Bot, Greedy, Context
from typing import Optional

class EPEC(commands.Cog):
    """E.P.E.C Server Tasks"""

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="iamfrom")
    @commands.guild_only()
    async def countryassign(self, ctx: Context, continent: discord.Role, *, country=""):
        """Assign yourself to your country"""
        try:
            await ctx.author.add_roles(continent, reason="Auto Verified User")
        except discord.InvalidArgument:
            ctx.send("Could not change " + str(ctx.author.name) +"'s role")
        
        try:
            role = ctx.guild.get_role(626460644648026152)
            await ctx.author.remove_roles(role, reason="Removal of Unverified Role")
        except discord.InvalidArgument:
            ctx.send("Could not remove default role from " + str(ctx.author.name))
        
        try:
            await ctx.author.edit(nick=country+" | "+ctx.author.display_name)
        except discord.InvalidArgument:
            ctx.send("Could not change " + str(ctx.author.name) +"'s role")

        await ctx.send("Welcome "+ str(ctx.author.name)+" from "+ str(country)+", you've been assigned to the "+str(continent)+" role")


    # Message filter system
    @commands.Cog.listener()
    async def on_message(self, ctx: Context, message: discord.Message):
        if message.mention_everyone == True:
            await ctx.send(str(message.author) + "is it wise to ping the whole server, it can be annoying to some")
        

def setup(bot):
    bot.add_cog(EPEC(bot))        