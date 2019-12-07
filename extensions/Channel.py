import discord
from discord.ext import commands
from discord import CategoryChannel, Client, Colour, Embed, Guild, Member, Role, TextChannel, User, VoiceChannel, utils
from discord.ext.commands import Bot, BucketType, Cog, Context, command, group
import typing
from typing import Optional
import colorsys
from Lynn import errors
import traceback
import math
import sys


class Channel(commands.Cog):
    """Commands for channel related tasks"""

    def __init__(self, bot):
        self.bot = bot
       
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        global errors
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        try:
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
        except:
            pass

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send('This command has been disabled.')
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.UserInputError):
            await ctx.send("Invalid input. Usage:")
            await ctx.send_help(ctx.command)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
            return

        try:
            if hasattr(error, "args") and len(error.args) != 0 and error.args[0][0] == "%":
                await ctx.send(error.args[0][1:])
        except:
            pass

        print("Ignoring exception in " + str(ctx.command), file=sys.stderr)
        errors = "\n".join(traceback.format_exception(type(error), error, error.__traceback__))
        
    @commands.command("slowmode", aliases=["slow"])
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def slow_mode(self, ctx: Context, *, channel: discord.TextChannel, delay: Optional[int]=""):
        """Toggles slowmode"""
        try:        
            if channel.slowmode_delay == 0:
                await channel.edit(slowmode_delay=delay)
                await ctx.send(f"""Set slowmode delay to {delay} seconds""")
            else:
                await channel.edit(slowmode_delay=0)
                await ctx.send(f"Disabled slowmode")
        except:
            global errors
            for msg in [errors[i:i+1990] for i in range(0, len(errors), 1990)]:
                await ctx.send("```py\n" + msg + "```")
            
        
        
def setup(bot):
    bot.add_cog(Channel(bot))