import discord
import dateutil
from discord.ext import commands
from discord import CategoryChannel, Client, Colour, Embed, Guild, Member, Role, TextChannel, User, VoiceChannel, utils
from discord.ext.commands import Bot, BucketType, Cog, Context, command, group
import typing
import colorsys

class Info(commands.Cog):
    """Info"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="guildinfo", aliases=['gi', 'serverinfo'])
    async def guildinfo(self, ctx: Context) -> None:
        """Returns info about a guild"""
        
        created = ctx.guild.created_at
        features = ", ".join(ctx.guild.features)
        
        id = ctx.guild.id
        owner = ctx.guild.owner
        ownerdn = ctx.guild.owner.display_name
        
        boostlvl = ctx.guild.premium_tier
        boostlen = ctx.guild.premium_subscription_count
       
        #lists of server elements
        rolelist = ctx.guild.roles
        cats = ctx.guild.categories
        chans = ctx.guild.text_channels
        
        #Dictionary of flags
        regionFlag = {
            "amsterdam": ":flag_nl: - Amsterdam",
            "brazil": ":flag_br: -  Brazil",
            "eu_central": ":flag_eu: - Central Europe",
            "eu_west": ":flag_eu: - West Europe",
            "europe": ":flag_eu: - Europe",
            "frankfurt": ":flag_de: - Frankfurt",
            "hongkong": ":flag_ch: - Hong Kong",
            "india": ":flag_in: - India",
            "japan": ":flag_jap: - Japan",
            "london": ":flag_uk: - London",
            "russia": ":flag_ru: - Russia",
            "singapore": ":flag_au: - Singapore",
            "southafrica": ":flag_za: - South Africa",
            "sydney": ":flag_au: - Sydney",
            "us_central": ":flag_us: - US Central",
            "us_east": ":flag_us: - US East",
            "us_south": ":flag_us: - US South",
            "us_west": ":flag_us: - US West"
        }
        
        region = ctx.guild.region
        
        
        # How many of each type of channel?
        roles = len(ctx.guild.roles)
        channels = ctx.guild.channels
        text_channels = 0
        category_channels = 0
        voice_channels = 0
        for channel in channels:
            if type(channel) == TextChannel:
                text_channels += 1
            elif type(channel) == CategoryChannel:
                category_channels += 1
            elif type(channel) == VoiceChannel:
                voice_channels += 1
       
        # How many of each client type status?
        member_count = ctx.guild.member_count
        members = ctx.guild.members
        online = 0
        dnd = 0
        idle = 0
        offline = 0
        mobile = 0
        web = 0
        desktop = 0
        mobileonline = 0
        webonline = 0
        desktoponline = 0
        mobileidle = 0
        webidle = 0
        desktopidle = 0
        mobilednd = 0
        webdnd = 0
        desktopdnd = 0
        
        for member in members:
            if str(member.status) == "online":
                online += 1
            elif str(member.status) == "offline":
                offline += 1
            elif str(member.status) == "idle":
                idle += 1
            elif str(member.status) == "dnd":
                dnd += 1
        
        for member in members:
            if str(member.mobile_status) == "online" or str(member.mobile_status) == "dnd" or str(member.mobile_status) == "idle":
               mobile += 1
            if str(member.web_status) == "online" or str(member.web_status) == "dnd" or str(member.web_status) == "idle":
               web += 1
            if str(member.desktop_status) == "online" or str(member.desktop_status) == "dnd" or str(member.desktop_status) == "idle":
               desktop += 1
            if str(member.mobile_status) == "online":
                mobileonline += 1
            if str(member.web_status) == "online":
                webonline += 1
            if str(member.desktop_status) == "online":
                desktoponline += 1
            if str(member.mobile_status) == "dnd":
                mobilednd += 1
            if str(member.web_status) == "dnd":
                webdnd += 1
            if str(member.desktop_status) == "dnd":
                desktopdnd += 1
            if str(member.mobile_status) == "idle":
                mobileidle += 1
            if str(member.web_status) == "idle":
                webidle += 1
            if str(member.desktop_status) == "idle":
                desktopidle += 1

        embed = discord.Embed(title=str(ctx.guild.name) + "'s information", colour=Colour.blurple())
        embed.add_field(name=":id:", value=id)
        embed.add_field(name=":date: Guild Created On", value=created.strftime("%A %d %B %Y %H:%M"))
        embed.add_field(name=":bust_in_silhouette: Owner", value=str(owner) + " aka " + str(ownerdn))
        embed.add_field(name=":telephone_receiver:  Voice Region", value=" ".join([regionFlag[n] for n in region]))
        embed.add_field(name="Nitro Level", value=str(boostlvl) + "/" + str(3))
        embed.add_field(name="Number of Members currently boosting", value=str(boostlen) + "/" + str(30))
        embed.add_field(name=":busts_in_silhouette: # of Members", value=member_count)
        embed.add_field(name="... of which human", value=len([member for member in ctx.guild.members if not member.bot]))
        embed.add_field(name="... of which bots", value=len([member for member in ctx.guild.members if member.bot]))
        embed.add_field(name="... of Banned Members", value=len(await ctx.guild.bans()))
        embed.add_field(name="... of Roles", value=roles)
        embed.add_field(name="... of Text Channels", value=text_channels)
        embed.add_field(name="... of Voice Channels", value=voice_channels)
        embed.add_field(name="... of Categories", value=category_channels)
        embed.add_field(name=":green_circle: Members Online", value=online)
        embed.add_field(name=":orange_circle: Members Idle", value=idle)
        embed.add_field(name=":red_circle: Members Busy", value=dnd)
        embed.add_field(name=":black_circle: Members Offline/Invisible", value=offline)
        embed.add_field(name=":computer: Members using the Desktop App", value=str(desktop) + " total\n" + str(desktoponline) + " online\n" + str(desktopidle) + " idle\n" + str(desktopdnd) + " busy")
        embed.add_field(name="Members using the Browser App", value=str(web) + " total\n" + str(webonline) + " online\n" + str(webidle) + " idle\n" + str(webdnd) + " busy")
        embed.add_field(name=":iphone: Members using the Mobile App", value=str(mobile) + " total\n" + str(mobileonline) + " online\n" + str(mobileidle) + " idle\n" + str(mobilednd) + " busy")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        
        if boostlen > 30:
            embed.set_footer(text="Max Level", icon_url="")
        else:
            embed.set_footer(text=str(30 - boostlen) + " boosts to go for max boost level", icon_url="")
                   
        await ctx.send(embed=embed)

    
    @commands.command(name="textchannelinfo", aliases=['tci'])
    async def text_channel_info(self, ctx: Context, channel: discord.TextChannel) -> None:
        """Returns info about a channel."""   
    
        name = channel.name
        created = channel.created_at
        id = channel.id
        catid = channel.category_id
        cat = channel.category
        topic = channel.topic
        pos = channel.position
        type = channel.type
        nsfw = channel.is_nsfw()
        croles = channel.changed_roles
    
        embed = discord.Embed(title=channel.name + "'s Information" ,colour=Colour.blurple())
        embed.add_field(name="Created", value=created)
        embed.add_field(name="Name", value=name)
        embed.add_field(name="ID", value=id)
        embed.add_field(name="Category ID", value=catid)
        embed.add_field(name="Category", value=cat)
        embed.add_field(name="Topic", value=topic)
        embed.add_field(name="Position", value=pos)
        embed.add_field(name="Channel Type", value=type)
        embed.add_field(name="is NSFW?", value=nsfw)
        embed.add_field(name="Changed Roles", value=croles) 
        
        await ctx.send(embed=embed)
        
    @commands.command(name="voicechannelinfo", aliases=['vci'])
    async def voice_channel_info(self, ctx: Context, channel: discord.VoiceChannel) -> None:
        """Returns info about a channel."""   
        
        name = channel.name
        created = channel.created_at
        id = channel.id
        catid = channel.category_id
        cat = channel.category
        pos = channel.position
        type = channel.type
        croles = channel.changed_roles
        ulimit = channel.user_limit
        bitrate = channel.bitrate
    
        embed = discord.Embed(title=channel.name + "'s Information" ,colour=Colour.blurple())
        embed.add_field(name="Created", value=created)
        embed.add_field(name="Name", value=name)
        embed.add_field(name="ID", value=id)
        embed.add_field(name="Category ID", value=catid)
        embed.add_field(name="Category", value=cat)
        embed.add_field(name="Position", value=pos)
        embed.add_field(name="User Limit", value=ulimit)
        embed.add_field(name="Bitrate", value=bitrate)
        embed.add_field(name="Channel Type", value=type)
        embed.add_field(name="Changed Roles", value=croles) 
        
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfo", aliases=['ui', 'clientinfo'])
    async def user_info(self, ctx: Context, user: discord.User) -> None:
        """Returns info about a user."""
        
        created = user.created_at
        name = user.name
        avatar = user.avatar_url
        id = user.id
        discrim = user.discriminator
        bot = user.bot
        
        embed = discord.Embed(title=str(user.name) + "'s information", colour=Colour.blurple())
        embed.add_field(name="Account made on", value=created.strftime("%A %d %B %Y %H:%M"))
        embed.add_field(name="Username", value=name)
        embed.add_field(name="Users Discriminator", value=discrim)
        embed.add_field(name="Users ID", value=id)
        embed.add_field(name="Tag", value=str(name) + "#" + str(discrim))
        embed.add_field(name="Bot?", value=bot)
        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="botinfo", aliases=['bi', 'info'])
    async def botinfo(self, ctx: Context) -> None:
        """Returns info about the bot."""
        
        created = ctx.me.created_at
        name = ctx.me.name
        avatar = ctx.me.avatar_url
        id = ctx.me.id
        discrim = ctx.me.discriminator
        guildcount = len(self.bot.guilds)
        
        embed = discord.Embed(title="Bots Information", colour=Colour.blurple())
        embed.add_field(name="Bots Name", value=name)        
        embed.add_field(name="Bots Discriminator", value=discrim)
        embed.add_field(name="Bots ID", value=id)
        embed.add_field(name="Number of guilds bot is in", value=guildcount)
        embed.add_field(name="Bot created on", value=created.strftime("%A %d %B %Y %H:%M"))
        embed.set_thumbnail(url=ctx.me.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="memberinfo", aliases=['mi'])
    async def member_info(self, ctx: Context, user: discord.Member) -> None:
        """Returns info about a member."""
                
        roles = ""
        activities = ""
        joined = user.joined_at
        name = user.name
        gstatus = user.status
        wstatus = user.web_status
        dstatus = user.desktop_status
        mstatus = user.mobile_status
        bot = user.bot
        nick = user.nick
        boostsince = user.premium_since
        mobile = user.is_on_mobile()
        top = user.top_role
        
        #List of users roles
        for i in range(len(user.roles)):
            roles += str(user.roles[i].mention) + ", "
        
        embed = discord.Embed(title=str(user.display_name) + "'s Information", colour=Colour.blurple())
        embed.add_field(name="Member joined on", value=joined.strftime("%A %d %B %Y %H:%M"))
        embed.add_field(name="Members Nickname", value=nick)
        if boostsince == None:
            embed.add_field(name="Boosted server since", value="Never boosted")
        else:
            embed.add_field(name="Boosted server since", value=boostsince.strftime("%A %d %B %Y %H:%M"))
        embed.add_field(name=":robot: Bot?", value=bot)
        embed.add_field(name=":iphone: On Mobile?", value=mobile)
        embed.add_field(name=":computer: Desktop App", value=dstatus)
        embed.add_field(name="Web/Browser App", value=wstatus)
        embed.add_field(name=":iphone: Android/iOS App", value=mstatus)
        embed.add_field(name="Roles Member is in", value=roles)
        embed.add_field(name="Highest role of Member", value=top)
        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)
        
    @commands.command(name="avatar")
    async def avatar(self, ctx: Context, user: discord.Member) -> None:
        """Returns a users avatar"""
        
        avatar = user.avatar_url
        
        embed = discord.Embed(title=user.display_name +"'s avatar", colour=Colour.blurple())
        embed.set_image(url=avatar)
        
        await ctx.send(embed=embed)
        
    @commands.command(name="roleperms")
    async def role_perm_info(self, ctx: Context, role: discord.Role) -> None:
        """Returns info about a members permissions"""
        
        admin = role.permissions.administrator
        
        embed = Embed(
            colour=Colour.blurple(),
            description=f"""
                **Permission information for {role.name}**
                Administrator?: {admin}*
                
                _**Notes:**_
                * This perm overrides all below it making everything else automatically true
            """
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="perms")
    async def perm_info(self, ctx: Context, user: Member) -> None:
        """Returns info about a members permissions"""
        
        admin = user.guild_permissions.administrator
        audit = user.guild_permissions.view_audit_log
        server = user.guild_permissions.manage_guild
        role = user.guild_permissions.manage_roles
        chan = user.guild_permissions.manage_channels
        kick = user.guild_permissions.kick_members
        ban = user.guild_permissions.ban_members
        inv = user.guild_permissions.create_instant_invite
        chnick = user.guild_permissions.change_nickname
        mnick = user.guild_permissions.manage_nicknames
        emoji = user.guild_permissions.manage_emojis
        webh = user.guild_permissions.manage_webhooks
        read = user.guild_permissions.read_messages
        send = user.guild_permissions.send_messages
        sendtts = user.guild_permissions.send_tts_messages
        mmsg = user.guild_permissions.manage_messages
        embedl = user.guild_permissions.embed_links
        files = user.guild_permissions.attach_files
        hist = user.guild_permissions.read_message_history
        eone = user.guild_permissions.mention_everyone
        exemojis = user.guild_permissions.external_emojis
        react = user.guild_permissions.add_reactions
        
        embed = Embed(
            colour=Colour.blurple(),
            description=f"""
                **Permission information for {user.name}**
                Administrator?: {admin}*
                
                **General Permissions**
                View Audit Log?: {audit}
                Manage Server?: {server}
                Manage Roles?: {role}
                Manage Channels?: {chan}
                Kick Members?: {kick}
                Ban Members?: {ban}
                Create Invite?: {inv}
                Change Nickname?: {chnick}
                Manage Nicknames?: {mnick}
                Manage Emojis?: {emoji}
                Manage Webhooks?: {webh}
                Read Text/Voice Channels?: {read}
                **Text Permissions**
                Send Msgs?: {send}
                Send TTS?: {sendtts}
                Manage Msgs?: {mmsg}
                Embed Links?: {embedl}
                Attach Files?: {files}
                Read Msg History?: {hist}
                @everyone?: {eone}
                Use External Emojis?: {exemojis}
                Add Reactions?: {react}
                
                _**Notes:**_
                * This perm overrides all below it making everything else automatically true
            """
        )

        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)
    
    @commands.command(name="roles")
    async def roles_info(self, ctx: Context) -> None:
        """Returns a list of all roles and their corresponding IDs."""
        # Sort the roles by the order as shown in the client's Roles UI
        roles = sorted(ctx.guild.roles, key=lambda role: role.position, reverse=True)
        #roles = [role for role in roles if role.name != "@everyone"]        

        # Build a string
        role_string = ""
        for role in roles:
            role_string += f"{role.position} - {role.mention}\n"
       
        embed = discord.Embed(title="Roles", colour=Colour.blurple(), description=f"""{role_string}""")
        
       
        await ctx.send(embed=embed)        

    @commands.command(name="roleinfo")
    async def role_info(self, ctx: Context, *roles: typing.Union[Role, str]) -> None:
        """
        Return information on a role or list of roles.
        To specify multiple roles just add to the arguments, delimit roles with spaces in them using quotation marks.
        """
        parsed_roles = []

        for role_name in roles:
            if isinstance(role_name, Role):
                # Role conversion has already succeeded
                parsed_roles.append(role_name)
                continue

            role = utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)

            if not role:
                await ctx.send(f":x: Could not convert `{role_name}` to a role")
                continue

            parsed_roles.append(role)

        for role in parsed_roles:
            embed = Embed(
                title=f"{role.name} info",
                colour=role.colour,
            )

            embed.add_field(name="ID", value=role.id, inline=True)

            embed.add_field(name="Colour (RGB)", value=f"#{role.colour.value:0>6x}", inline=True)

            h, s, v = colorsys.rgb_to_hsv(*role.colour.to_rgb())

            embed.add_field(name="Colour (HSV)", value=f"{h:.2f} {s:.2f} {v}", inline=True)

            embed.add_field(name="Member count", value=len(role.members), inline=True)

            embed.add_field(name="Position", value=role.position)

            embed.add_field(name="Permission code", value=role.permissions.value, inline=True)

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))