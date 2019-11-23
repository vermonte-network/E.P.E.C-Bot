import discord
from discord import Member as DiscordMember
from discord.ext import commands
from discord.ext.commands import Bot, Greedy
from typing import Optional

class Mod(commands.Cog):
    """Mod"""

    def __init__(self, bot):
        self.bot = bot
    
    class get:
        def superior(Member1, Member2):
            if Member1.top_role.position > Member2.top_role.position:
                return Member1
            elif Member1.top_role.position < Member2.top_role.position:
                return Member2
            return 
    
    class BannedMember(commands.Converter):
        async def convert(self, ctx, argument):
            ban_list = await ctx.guild.bans()
            try:
                member_id = int(argument, base=10)
                entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
            except ValueError:
                entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

            if entity is None:
                raise commands.BadArgument("%Not a valid previously-banned member.")
            return entity

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, *, user: discord.Member):
        """Bans a user"""
        try:
            await ctx.guild.ban(user, reason="Banned by " + ctx.author.name)
        except discord.Forbidden:
            await ctx.send("Could not ban " + user.name)
        else:
            await ctx.send(user.name + " was banned.")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, user: BannedMember):
        """Unbans a user"""
        try:
            await ctx.guild.unban(user.user, reason="Unbanned by " + ctx.author.name)
        except discord.Forbidden:
            await ctx.send("Could not unban " + user.name)
        else:
            await ctx.send(user.name + " was unbanned.")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, *, member: discord.Member):
        """Kicks a user"""
        try:
            await ctx.guild.kick(user, reason="Kicked by " + ctx.author.name)
        except discord.Forbidden:
            await ctx.send("Could not kick " + user.name)
        else:
            await ctx.send(user.name + " was kicked.")
    
    @commands.command(name="nick", aliases=["nickname"])
    @commands.has_permissions(change_nickname=True)
    @commands.guild_only()
    async def nick(self, ctx, user: discord.Member, *, nick=""):
        """Changes user's nickname"""
        try:
            await user.edit(nick=nick)
        except discord.Forbidden:
            await ctx.send("Could not change " + user.name + "'s nickname")
        else:
            await ctx.send(user.name + "'s nickname was changed to `"+nick+"`")

    @commands.command(name="role")
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def role(self, ctx, user: discord.Member, *, role: discord.Role):
        """Add or remove role from user"""
        if role in user.roles:
            try:
                await ctx.guild.remove_roles(role)
            except discord.Forbidden:
                await ctx.send("Could not remove " + user.name + "'s role")
            else:
                await ctx.send(user.name + " was removed from the role " + role.name)
        else:
            try:
                await ctx.guild.add_roles(role)
            except discord.Forbidden:
                await ctx.send("Could not add a role to " + user.name)
            else:
                await ctx.send(user.name + " was given the role " + role.name)

    @commands.command(name="createinvite", aliases=["makeinv"])
    @commands.has_permissions(create_instant_invite=True)
    @commands.guild_only()
    async def createinvite(self, ctx, limit=0, duration_minutes=0):
        inv = await ctx.channel.create_invite(max_age=duration_minutes*60, max_uses=limit)
        info = "Invite lasts for `"+ (str(inv.max_age // 60) if inv.max_age else "8") + "` minutes.\n" \
        + "Invite can be used `"+ (str(inv.max_uses) if inv.max_uses else "8") + "` times."
        await ctx.send("Invite created: https://discord.gg/" + inv.code + "\n" + info)

    @commands.command(name="masskick")
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def mass_kick_members(self, ctx, targets:[discord.Member], *, reason:Optional[str]=""):
        """Kicks mentioned Members"""
        for Target in targets:
            if ctx.author is get.superior(ctx.author, Target):
                await Target.kick(reason=reason)
                await ctx.send("Done.")
            else: 
            	  await ctx.send("Cannot Kick")          
        return
    
    @commands.command(name="massban")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def mass_ban_members(self, ctx, targets:Greedy[discord.Member], *, reason:Optional[str]=""):
        """Bans mentioned Members"""
        for Target in targets:
            if ctx.author is get.superior(ctx.author, Target):
                await Target.ban(reason=reason, days_to_delete=7)            
                await ctx.send("Done.")
            else:
                await ctx.send("Cannot Ban")

        return
    
    @commands.command(name="hackban")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def hackban(self, ctx, *, uId):
        """Bans an user that's not in the server"""
        try:
            await ctx.guild.ban(discord.Object(id=uId), reason="Hackbanned by " + ctx.author.name)
        except discord.Forbidden:
            await ctx.send("Could not hackban " + uId)
        else:
            await ctx.send(uId + " was hackbanned.")
    
    @commands.command(name='purge', aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int=None):
        """Purge an amount of messages in a channel"""
        if amount>500 or amount<0:
            raise commands.CommandError(message="Invalid amount")
        await ctx.message.delete()
        await ctx.message.channel.purge(limit=amount)
        await ctx.send(f'Sucesfully deleted **{int(amount)}** messages!', delete_after=5)

    @commands.command(name='echo', aliases=['say', 'repeat'])
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, message):
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Mod(bot))