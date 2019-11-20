import discord
from discord.ext import commands
import config
from datetime import datetime
import base64
import json
import math
import urllib.parse
import BotUtils
from aioauth_client import TwitterClient
import aiohttp

class APIs(commands.Cog):
    """APIs"""

    def __init__(self, bot):
        self.bot = bot

    # ---
    # FUNCTIONS
    # ---

    # Kinda hacky, sorry. I'll probably have no idea how this works in a couple of months. Anyways just don't touch it thanks
    async def REST(self, url, method="s.get", headers=None, data=None, auth=None, returns="await r.json(content_type=None)"):
        args = [headers, data, auth]
        for n in range(len(args)):
            if args[n]:
                args[n] = f'"{str(args[n])}"'
        func = f'{str(method)}(url="{str(url)}", headers={str(headers)}, data={json.dumps(str(data)) if data else None}, auth={str(auth)})'
        async with aiohttp.ClientSession() as s:
            async with eval(func) as r:
                try:
                    if returns.split(" ")[0] == "await":
                        return await eval(" ".join(returns.split(" ")[1:]))
                    else:
                        return eval(returns)
                except:
                    return None

    def escape(self, url):
        return urllib.parse.quote(url)

    # thanks stackoverflow love ya
    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ("year",        60*60*24*365),
            ("month",       60*60*24*30),
            ("week",        60*60*24*7),
            ("day",         60*60*24),
            ("hour",        60*60),
            ("minute",      60)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = "s" if period_value > 1 else ""
                strings.append("%s %s%s" % (period_value, period_name, has_s))

        return ", ".join(strings)


    async def getMinecraftAge(self, name):
        a = 1263146630 # notch sign-up
        b = math.floor(datetime.utcnow().timestamp())
        last = 0
        for i in range(30):
            if a == b:
                if last == a-1 and await self.REST("https://api.mojang.com/users/profiles/minecraft/" + name + "?at=" + str(a), returns="r.status == 200"):
                    return datetime.utcfromtimestamp(a)
                else:
                    return False
            else:
                mid = a + math.floor((b - a) / 2)
                if await self.REST("https://api.mojang.com/users/profiles/minecraft/" + name + "?at=" + str(mid), returns="r.status == 200"):
                    b = mid
                else:
                    a = mid+1
                    last = mid


    async def getMinecraftUUID(self, name):
        r = await self.REST("https://api.mojang.com/users/profiles/minecraft/" + name)
        if r:
            return r

        r = await self.REST("https://api.mojang.com/users/profiles/minecraft/" + name + "?at=0")
        if r:
            return r
        return None

    async def getMinecraftSkinUrl(self, uuid):
        data = await self.REST("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid)
        try:
            val = data["properties"][0]["value"]
        except:
            return None
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    def getCSStat(self, data, stat):
        return [i for i in data["stats"] if i["name"] == stat][0]["value"]


    # ---
    # GAMES
    # ---

    @commands.command(name="classicube", aliases=["cc"])
    async def classiCubeAPI(self, ctx, *, user=None, server=None):
        """Gets information about ClassiCube, or searches players.
        user = ID or name
        Leave blank for general statistics"""
        if user:
            data = await self.REST("https://www.classicube.net/api/player/"+self.escape(user))
            if not data or data["error"] != "":
                if user.isdigit():
                    data = await self.REST("https://www.classicube.net/api/id/"+self.escape(user))
                if not data or data["error"] != "":
                    raise commands.CommandError(message="%User not found!")

            flags = []
            if "b" in data["flags"]:
                flags.append("'b' - Banned from forums")
            if "d" in data["flags"]:
                flags.append("'d' - Developer")
            if "m" in data["flags"]:
                flags.append("'m' - Forum Moderator")
            if "a" in data["flags"]:
                flags.append("'a' - Site Admin")
            if "e" in data["flags"]:
                flags.append("'e' - Blog editor")
            if "p" in data["flags"]:
                flags.append("'p' - Patreon")
            if "u" in data["flags"]:
                flags.append("'u' - Unverified")
            if "r" in data["flags"]:
                flags.append("'r' - Recovering account")

            if "a" in data["flags"] and data["id"] == 1:
                embed = discord.Embed(title="Founder of Classicube", colour=0x7474A5)
            if "a" in data["flags"]:
                embed = discord.Embed(title="ClassiCube Admin", colour=0xFFD700)
            elif "d" in data["flags"]:
                embed = discord.Embed(title="Classicube Developer", colour=0xFFD700)
            elif "m" in data["flags"]:
                embed = discord.Embed(title="ClassiCube Moderator", colour=0xFFD700)
            elif "p" in data["flags"]:
                embed = discord.Embed(title="ClassiCube Supporter", colour=0xA6A6ED)
            elif "b" in data["flags"]:
                embed = discord.Embed(title="Banned User", colour=0xff0000)
            elif "u" in data["flags"]:
                embed = discord.Embed(title="Unverified ClassiCube Account", colour=0x808080)
            else:
                embed = discord.Embed(title="Regular ClassiCube User", colour=0xE6E6FA)
            
            if "a" in data["flags"] or "m" in data["flags"] or "d" in data["flags"]:
                embed.set_author(name="[Staff] " + data["username"] + " - " + str(data["id"]), icon_url="attachment://head.png")
            elif "p" in data["flags"]:
                embed.set_author(name="[Supporter] " + data["username"] + " - " + str(data["id"]) , icon_url="attachment://head.png")
            elif "b" in data["flags"]:
                embed.set_author(name= data["username"] + " - " + str(data["id"]) + " | [Banned]", icon_url="attachment://head.png")
            elif "r" in data["flags"]:
                embed.set_author(name=data["username"] + " - " + str(data["id"]) + " | [Awaiting Password Reset]", icon_url="attachment://head.png")
            elif "u" in data["flags"]:
                embed.set_author(name=data["username"] + " - " + str(data["id"]) + " | [Unverified]", icon_url="attachment://head.png")
            else:
                embed.set_author(name=data["username"] + " - " + str(data["id"]), icon_url="attachment://head.png")          
            
            
            if await self.REST("https://classicube.s3.amazonaws.com/face/" + str(data["username"]) + ".png", returns="r.status == 200"):
                embed.set_thumbnail(url="https://classicube.s3.amazonaws.com/face/" + str(data["username"]) + ".png")
            else: 
                embed.set_thumbnail(url="https://classicube.s3.amazonaws.com/face/default.png")
            
            
            embed.add_field(name="Avatar Url", value="[Click me](https://classicube.s3.amazonaws.com/face/" + str(data["username"]) + ".png)")
            embed.add_field(name="ID", value=data["id"])
            
            ago = self.td_format(datetime.utcnow() - datetime.utcfromtimestamp(data["registered"]))
            if len(ago) == 0:
                ago = "Under a minute"
            embed.add_field(name="Account created", value="On " + datetime.utcfromtimestamp(data["registered"]).strftime("%c") + "\n" + ago + " ago")
            if flags:
                embed.add_field(name="Flags", value=", ".join(flags))

            if await self.REST("https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png", returns="r.status == 200"):
                embed.add_field(name="Skin URL", value="[Click me](https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png)")
                await BotUtils.skinRenderer2D("https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png", fromFile=False)
                await BotUtils.headRenderer("https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png", fromFile=False)
                file = discord.File("skins/2d/" + str(data["username"]) + ".png", filename="skin.png")
                file2 = discord.File("skins/head/" + str(data["username"]) + ".png", filename="head.png")
            else:
                await BotUtils.skinRenderer2D("https://www.classicube.net/static/default.png")
                await BotUtils.headRenderer("https://www.classicube.net/static/default.png")
                file = discord.File("skins/2d/default.png", filename="skin.png")
                file2 = discord.File("skins/head/default.png", filename="head.png")

            embed.add_field(name="Flag Descriptions: ", value="--------")

            if "a" in data["flags"]:
                embed.add_field(name="'a': ", value="This Account can access the Classicube Admin Panel")
            if "d" in data["flags"]:
                embed.add_field(name="'d': ", value="This Account belongs to an Official Classicube Developer")
            if "m" in data["flags"]:
                embed.add_field(name="'m': ", value="This Account can Moderate the Classicube Forum and view any post (including hidden posts)")
            if "e" in data["flags"]:
                embed.add_field(name="'e': ", value="This Account has Classicube home page blog editing permissions")
            if "p" in data["flags"]:
                embed.add_field(name="'p': ", value="This Account belongs to a player who supports Classicube")
            if "b" in data["flags"]:
                embed.add_field(name="'b': ", value="This Account is banned from the forums thus it does not have access") 
            if "r" in data["flags"]:
                embed.add_field(name="'r': ", value="This Account has a pending password recovery email request")
            if "u" in data["flags"]:
                embed.add_field(name="'u': ", value="This Account hasn't been verified yet")
            if data["id"] == 1:
                embed.add_field(name="Special Status: ", value="This Account belongs to the Classicube Owner")

            embed.set_footer(text="\U00002063", icon_url="https://www.classicube.net/static/img/cc-cube-small.png")
            embed.set_image(url="attachment://skin.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[file, file2], embed=embed)
 
        else:
            data = await self.REST("https://www.classicube.net/api/players/")
            playercount = data["playercount"]
            
            onlinecount = 0
            activemaxcount = 0 
            inactivemaxcount = 0
            maxcount = 0
            servercount = 0
            players = ""

            data = await self.REST("https://www.classicube.net/api/servers/")
            servercount += len(data["servers"])
            serverlist = []
            activeserverlist = []
            servers = ""
            deadservers = len([s for s in data["servers"] if s["players"] == 0])
            superquietservers = len([s for s in data["servers"] if s["players"] >= 1 and s["players"] < 3])
            quietservers = len([s for s in data["servers"] if s["players"] >= 3 and s["players"] < 5])
            typicalservers = len([s for s in data["servers"] if s["players"] >= 5 and s["players"] < 7])
            busyservers = len([s for s in data["servers"] if s["players"] >= 7 and s["players"] < 10])
            popularservers = len([s for s in data["servers"] if s["players"] >= 10 and s["players"] < 20])
            superpopularservers = len([s for s in data["servers"] if s["players"] >= 20])
            #servers = len([s for s in data["servers"] if s["players"] > 1])
            
            activeservers = len([s for s in data["servers"] if s["players"]])
            inactiveservers = len([s for s in data["servers"] if not s["players"]])
            activeserverlist = [s for s in data["servers"] if s["players"]]
                        
            for server in sorted(data["servers"], key=lambda k: k["players"], reverse=True):
                
                # Calculates all servers
                if server["players"] >= 0:
                    maxcount += server["maxplayers"]
                
                # Calculates inactive servers
                if server["players"] == 0:
                    inactivemaxcount += server["maxplayers"]
                
                # Calculates active servers
                if server["players"] > 0:
                    temp = "[" + str(server["country_abbr"]) + "] [" + str(server["name"]) + "](https://www.classicube.net/server/play/" + str(server["hash"]) + ") | " + "Featured: " + str(server["featured"]) + " | " + str(server["players"]) + "/" + str(server["maxplayers"])
                    onlinecount += server["players"]
                    activemaxcount += server["maxplayers"]
                    
                    if len(servers) + len("\n---\n") + len(temp) > 1024:
                        serverlist.append(servers)
                        servers = ""    
                    servers += temp+"\n"
                    
            serverlist.append(servers)                                           	  

            embed = discord.Embed(title="ClassiCube", colour=0x977dab)
            embed.add_field(name="Total Accounts", value=playercount)
            
            embed.add_field(name="Online Players", value=str(onlinecount) + " player(s)")
            
            
            embed.add_field(name="Dead Servers", value=str(deadservers) + " server(s)")
            embed.add_field(name="Active Servers", value= str(activeservers) + " server(s)")
            embed.add_field(name="Very Quiet Servers", value=str(superquietservers) + " server(s)")
            embed.add_field(name="Quiet Servers", value=str(quietservers) + " server(s)")
            embed.add_field(name="Typical Servers", value=str(typicalservers) + " server(s)")
            embed.add_field(name="Busy Servers", value=str(busyservers) + " server(s)")
            embed.add_field(name="Popular Servers", value=str(popularservers) + " server(s)")
            embed.add_field(name="Super Popular Servers", value=str(superpopularservers) + " server(s)")
            embed.add_field(name="Active slots", value=str(activemaxcount) + " slot(s)")
            embed.add_field(name="Inactive Servers", value= str(inactiveservers) + " server(s)")
            embed.add_field(name="Inactive slots", value=str(inactivemaxcount) + " slot(s)")
            embed.add_field(name="Total Servers", value=str(servercount) + " server(s)")
            embed.add_field(name="Total Slots", value=str(maxcount) + " slot(s)")
                 
            
            
            for i in range(len(serverlist)):
                embed.add_field(name="Servers with players\nClick the server names to join!", value=serverlist[i])
            
            embed.add_field(name="Stats: ", value="There are " + str(activeservers) + " out of " + str(servercount) + " servers active with " + str(inactiveservers) + " being inactive. " + str(onlinecount) + " slots are being used from a total of " + str(maxcount) + " available slots." + "The most popular server is " + str(activeserverlist[0]) + " and the least popular server is " + str(activeserverlist[-1]))        
            embed.add_field(name="Player Stats: ", value= str(onlinecount) + " players are currently online.")
                        
            embed.set_footer(text="\U00002063", icon_url="https://www.classicube.net/static/img/cc-cube-small.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

    @commands.command(name="classicubeserver", aliases=["ccserver"])
    async def classiCubeSAPI(self, ctx, *, hash=None):
        """Searches servers"""
        data = await self.REST("https://www.classicube.net/api/server/"+self.escape(hash))
                
        for server in data["servers"]:
            embed = discord.Embed(title="Classicube Server", colour=0x7474A5)
            embed.add_field(name="Server Name", value=server["name"])
            embed.add_field(name="Players", value=server["players"])
            embed.add_field(name="Max Players", value=server["maxplayers"])
            embed.add_field(name="Software", value=server["software"])
            embed.add_field(name="Uptime", value=server["uptime"])

        await ctx.send(embed=embed)
       

    @commands.command(name="minecraft", aliases=["mc"])
    async def minecraftAPI(self, ctx, *, user=None):
        """Gets information about Minecraft, or searches players.
        Leave user as blank for general statistics"""
        if user:
            uuid = await self.getMinecraftUUID(user)
            if not uuid:
                raise commands.CommandError(message="%User not found!")
            history = await self.REST("https://api.mojang.com/user/profiles/" + uuid["id"] + "/names")
            names = []
            for i in range(len(history)):
                names.append(history[i]["name"])
                names[i] = names[i].replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
            names.reverse()
            names[0] += " **[CURRENT]**"
            names[-1] += " **[ORIGINAL]**"
            created = await self.getMinecraftAge(user)
            skin = await self.getMinecraftSkinUrl(uuid["id"])
            if not skin:
                raise commands.CommandOnCooldown(commands.BucketType.default, 10)
            embed = discord.Embed(title="Minecraft User", colour=0x82540f)
            embed.set_author(name=str(history[-1]["name"]) + " originally " + "[" + str(history[0]["name"]) + "]", icon_url="attachment://head.png")
            embed.add_field(name="Name history", value="\n".join(names))
            embed.add_field(name="Name history stats", value="This account has had " + str(len(names) - 1) + " name changes since first registered")
            embed.add_field(name="UUID", value=uuid["id"])
            try:
                skin["textures"]["SKIN"]["url"]
            except:
                # TODO: Try to find a official steve skin in mojang's skin server
                await BotUtils.skinRenderer2D("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                await BotUtils.headRenderer("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                skinFile = discord.File("skins/2d/Steve_skin.png", filename="skin.png")
                headFile = discord.File("skins/head/Steve_skin.png", filename="head.png")
            else:
                embed.add_field(name="Skin URL", value="[Click me]("+skin["textures"]["SKIN"]["url"]+")")
                await BotUtils.skinRenderer2D(skin["textures"]["SKIN"]["url"])
                await BotUtils.headRenderer(skin["textures"]["SKIN"]["url"])
                skinFile = discord.File("skins/2d/" + skin["textures"]["SKIN"]["url"].split("/")[-1] + ".png", filename="skin.png")
                headFile = discord.File("skins/head/" + skin["textures"]["SKIN"]["url"].split("/")[-1] + ".png", filename="head.png")

            if created:
                embed.add_field(name="Account created", value="On " + created.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - created) + " ago")
            else:
                embed.add_field(name="Account created", value="Account may be legacy or name may have been changed - API is not accurate")
            embed.set_footer(text="\U00002063", icon_url="https://minecraft.net/favicon-96x96.png")
            embed.set_image(url="attachment://skin.png")
            embed.set_thumbnail(url="attachment://head.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[skinFile, headFile], embed=embed)
        else:
            sale = await self.REST("https://api.mojang.com/orders/statistics", method="s.post", data='{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}', headers='{"content-type": "application/json"}')
            embed = discord.Embed(title="Minecraft", colour=0x82540f)
            embed.add_field(name="Sold total", value=sale["total"])
            embed.add_field(name="Sold in the last 24h", value=sale["last24h"])
            embed.set_footer(text="\U00002063", icon_url="https://minecraft.net/favicon-96x96.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)


    @commands.command(name="csgo", aliases=["cs"])
    async def CSGOAPI(self, ctx, *, user):
        """Gets information about CSGO players."""
        if not str(user).isdigit():
            data = await self.REST("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + config.apiKeys["steam"] + "&vanityurl=" + self.escape(user))
            user = data["response"]["steamid"]
        data = await self.REST("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + config.apiKeys["steam"] + "&steamids=" + user)
        name = data["response"]["players"][0]["personaname"]
        data = await self.REST("http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=" + config.apiKeys["steam"] + "&steamid=" + user)
        data = data["playerstats"]
        embed = discord.Embed(title="Counter-Strike: Global Offensive", colour=0xadd8e6)
        embed.set_author(name=str(name))
        embed.add_field(name="Kills", value=str(self.getCSStat(data, "total_kills")))
        embed.add_field(name="K/D", value=str(round(self.getCSStat(data, "total_kills")/self.getCSStat(data, "total_deaths"), 2)))
        embed.add_field(name="Time Played", value=str(round(self.getCSStat(data, "total_time_played") / 60 / 60, 1)) + "h")
        embed.add_field(name="Headshot %", value=str(round(self.getCSStat(data, "total_kills_headshot") / self.getCSStat(data, "total_kills") * 100, 1)) + "%")
        embed.add_field(name="Win %", value=str(round(self.getCSStat(data, "total_matches_won") / self.getCSStat(data, "total_matches_played") * 100, 1)) + "%")
        embed.add_field(name="Accuracy", value=str(round(self.getCSStat(data, "total_shots_hit") / self.getCSStat(data, "total_shots_fired") * 100, 1)) + "%")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


    @commands.command(name="osu")
    async def OsuAPI(self, ctx, *, user):
        """Gets information about osu! players."""
        data = await self.REST("https://osu.ppy.sh/api/get_user?u=" + self.escape(user) + "&k=" + config.apiKeys["osu"])
        data = data[0]
        embed = discord.Embed(title="osu! - " + data["username"], color=0xEA68A3)
        embed.set_thumbnail(url="https://a.ppy.sh/" + data["user_id"])
        embed.add_field(name="Level", value=str(round(float(data["level"]), 2)))
        embed.add_field(name="Ranked Score", value=data["ranked_score"])
        embed.add_field(name="Hit Accuracy", value=str(round(float(data["accuracy"]), 2)) + "%")
        embed.add_field(name="Play Count", value=data["playcount"])
        embed.add_field(name="Total Score", value=data["total_score"])
        embed.add_field(name="PP", value=str(round(float(data["pp_raw"]), 2)))
        embed.add_field(name="Playtime", value=str(round(int(data["total_seconds_played"])/60/60, 2)) + "h")
        embed.add_field(name="Ranks", value="Silver SS: " + data["count_rank_ssh"]
                                            + "\nGold SS: " + data["count_rank_ss"]
                                            + "\nSilver S: " + data["count_rank_sh"]
                                            + "\nGold S: " + data["count_rank_s"]
                                            + "\nA: " + data["count_rank_a"])
        embed.add_field(name="Leaderboards", value="**#" + data["pp_rank"] + "** global"
                                                  + "\n**#" + data["pp_country_rank"] + "** in " + data["country"])
        embed.set_footer(text="Account created", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Osu%21Logo_%282015%29.svg/480px-Osu%21Logo_%282015%29.svg.png")
        embed.timestamp = datetime.strptime(data["join_date"], "%Y-%m-%d %H:%M:%S")
        await ctx.send(embed=embed)


    @commands.command(name="wynncraft", aliases=["wc", "wynn"])
    async def WynncraftAPI(self, ctx, *, user=None):
        """Gets information about Wynncraft, or searches players.
        Leave blank for general statistics"""
        if user:
            data = await self.REST("https://api.wynncraft.com/v2/player/"+self.escape(user)+"/stats")
            data = data["data"][0]
            if "error" in data:
                raise commands.CommandError(message="%"+str(data["error"]))

            rankDict = {
                "**" + data["rank"] + "**": data["rank"] != "Player",
                "Veteran": data["meta"]["veteran"],
                data["meta"]["tag"]["value"]: data["meta"]["tag"]["value"]
            }

            ranks = [n for n,r in rankDict.items() if r]
            rank = "\n".join(ranks if ranks else ["Player"])

            stats = []
            stats.append("**Items identified:** " + str(data["global"]["itemsIdentified"]))
            stats.append("**Mobs killed:** " + str(data["global"]["mobsKilled"]))
            stats.append("**PvP kills:** " + str(data["global"]["pvp"]["kills"]))
            stats.append("**PvP deaths:** " + str(data["global"]["pvp"]["deaths"]))
            stats.append("**Chests found:** " + str(data["global"]["chestsFound"]))
            stats.append("**Blocks walked:** " + str(data["global"]["blocksWalked"]))
            stats.append("**Logins:** " + str(data["global"]["logins"]))
            stats.append("**Deaths:** " + str(data["global"]["deaths"]))
            stats.append("**Combat Level:** " + str(data["global"]["totalLevel"]["combat"]))
            stats.append("**Total Level:** " + str(data["global"]["totalLevel"]["combined"]))
            stats.sort(key=lambda x:int(x.split(" ")[-1]))
            stats.reverse()

            classes = []
            for s in data["classes"]:
                classes.append("**" + "".join([i for i in s["name"].title()]) + ":** Level " + str(s["level"]))
            # Why is this a float? Did the api return floats before? Too scared to change
            classes.sort(key=lambda x:float(x.split(" ")[-1]))
            classes.reverse()

            skin = await self.getMinecraftSkinUrl(data["uuid"].replace("-", ""))
            if not skin:
                await ctx.send("Ratelimited! Custom player skin will not be shown.")
            try:
                skin["textures"]["SKIN"]["url"]
            except:
                await self.bot.loop.run_in_executor(None, BotUtils.headRenderer, "https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                headFile = discord.File("skins/head/Steve_skin.png", filename="head.png")
            else:
                await self.bot.loop.run_in_executor(None, BotUtils.headRenderer, skin["textures"]["SKIN"]["url"])
                headFile = discord.File("skins/head/" + skin["textures"]["SKIN"]["url"].split("/")[-1] + ".png", filename="head.png")

            embed = discord.Embed(title="Wynncraft Player", colour=0x7bbf32)
            embed.set_author(name=data["username"],
                    icon_url="attachment://head.png")
            embed.add_field(name="Rank", value=rank)
            embed.add_field(name="Guild", value=str(data["guild"]["name"]))
            embed.add_field(name="Playtime", value=str(round(data["meta"]["playtime"]/12, 2))+"h")
            created = datetime.strptime(data["meta"]["firstJoin"], "%Y-%m-%dT%H:%M:%S.%fZ")
            last = datetime.strptime(data["meta"]["lastJoin"], "%Y-%m-%dT%H:%M:%S.%fZ")
            embed.add_field(name="First joined on", value="On " + created.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - created) + " ago")
            embed.add_field(name="Last joined on", value="On " + last.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - last) + " ago")
            if data["meta"]["location"]["online"]:
                embed.add_field(name="Currently online in", value=data["meta"]["location"]["server"])

            embed.add_field(name="Global stats", value="\n".join(stats))
            embed.add_field(name="Classes", value="\n".join(classes))

            embed.set_footer(text="\U00002063", icon_url="https://cdn.wynncraft.com/img/ico/android-icon-192x192.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[headFile], embed=embed)
        else:
            data = await self.REST("https://api.wynncraft.com/public_api.php?action=onlinePlayersSum")
            embed = discord.Embed(title="Wynncraft", colour=0x7bbf32)
            embed.add_field(name="Players Online", value=data["players_online"])

            embed.set_footer(text="\U00002063", icon_url="https://cdn.wynncraft.com/img/ico/android-icon-192x192.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

    # ---
    # WEBSITES
    # ---

    @commands.command(name="mixer")
    async def MixerAPI(self, ctx, *, user):
        """Gets information about mixer users"""
        data = await self.REST("https://mixer.com/api/v1/channels/" + self.escape(user))

        name = data["token"]
        if data["user"]["username"].lower() != data["token"].lower():
            name = data["token"] + " (" + data["user"]["username"] + ")"

        s = ""
        if data["online"]:
            s = " (Currently Streaming)"

        embed = discord.Embed(title="Mixer user - " + name + s, color=0x002050, url="https://mixer.com/" + data["token"])

        if data["user"]["avatarUrl"]:
            embed.set_thumbnail(url=data["user"]["avatarUrl"])


        typeNames = {
            "Verified": data["user"]["verified"],
            "Suspended": data["suspended"],
            "Featured": data["featured"],
            "Partnered": data["partnered"],
            "Interactive Stream": data["interactive"],
            "VODs": data["vodsEnabled"]
        }
        types = [c for c in typeNames if typeNames[c]]
        groups = []

        try:
            for group in data["user"]["groups"]:
                groups.append(group["name"])
        except:
            pass

        if types:
            embed.add_field(name="Account type", value="\n".join(types))
        if groups:
            embed.add_field(name="Account groups", value="\n".join(groups))

        if data["user"]["bio"]:
            embed.add_field(name="Bio", value=str(data["user"]["bio"]))

        embed.add_field(name="Followers", value=str(data["numFollowers"]))
        embed.add_field(name="Sparks", value=str(data["user"]["sparks"]))

        try:
            if data["thumbnail"]["url"]:
                embed.set_image(url=data["thumbnail"]["url"])
        except:
            pass

        if data["online"]:
            embed.add_field(name="Current viewers", value=str(data["viewersCurrent"]))

        embed.set_footer(icon_url="http://teambeyond.net/wp-content/uploads/2017/05/Mixer-Logo.png", text="LVL " + str(data["user"]["level"]) + " • Account created ")
        embed.timestamp = datetime.strptime(data["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        await ctx.send(embed=embed)


    @commands.command(name="twitch")
    async def TwitchAPI(self, ctx, *, user):
        """Gets information about twitch users"""
        # TODO: Cache tokens
        token = await self.REST("https://id.twitch.tv/oauth2/token?client_id="+config.apiKeys["twitchID"]+"&client_secret="+config.apiKeys["twitchSecret"]+"&grant_type=client_credentials", method="s.post")
        token = token["access_token"]
        data = await self.REST("https://api.twitch.tv/helix/users?login=" + self.escape(user), headers={"Authorization": "Bearer " + token})
        data = data["data"][0]

        name = data["display_name"]
        if data["login"].lower() != data["display_name"].lower():
            name = data["display_name"] + " (" + data["login"] + ")"

        embed = discord.Embed(title="Twitch user - " + name, color=0x6441A4, url="https://twitch.tv/" + data["login"])

        embed.set_thumbnail(url=data["profile_image_url"])

        if data["offline_image_url"]:
            embed.set_image(url=data["offline_image_url"])

        if data["broadcaster_type"]:
            utype = data["broadcaster_type"].title()
            if data["type"]:
                utype += "\n" + data["type"].title()
            embed.add_field(name="User Type", value=utype)

        if data["description"]:
            embed.add_field(name="Description", value=data["description"])
        embed.add_field(name="Views", value=str(data["view_count"]))

        embed.set_footer(icon_url="https://www.stickpng.com/assets/images/580b57fcd9996e24bc43c540.png", text="User id " + data["id"])
        await ctx.send(embed=embed)


    @commands.command(name="imdb", aliases=["movie", "movies"])
    async def IMDbAPI(self, ctx, *, title):
        """Gets information about movies using the IMDb"""
        data = await self.REST("http://www.omdbapi.com/?apikey=" + config.apiKeys["omdb"] + "&t=" + self.escape(title))

        embed = discord.Embed(title=data["Title"] + " (" + data["Year"] + ")", colour=0xf5c518, url="https://www.imdb.com/title/" + data["imdbID"])
        embed.add_field(name="Released", value=data["Released"])
        if "Production" in data:
            embed.add_field(name="Produced by", value=data["Production"])
        embed.add_field(name="Length", value=data["Runtime"])
        embed.add_field(name="Genres", value=data["Genre"])
        embed.add_field(name="Plot", value="||"+data["Plot"]+"||")
        if data["Poster"] != "N/A":
            embed.set_image(url=data["Poster"])

        if data["Ratings"]:
            ratings = ""
            for i in data["Ratings"]:
                ratings += "**" + i["Source"] + "** - `" + i["Value"] + "`\n"
            embed.add_field(name="Ratings", value=ratings)

        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


    @commands.command(name="user")
    async def discordUser(self, ctx, *, user):
        """Gets information about discord users."""
        user = await commands.UserConverter().convert(ctx, user)
        embed = discord.Embed(title="Discord User " + user.name + "#" + str(user.discriminator), colour=0x7289DA)
        embed.set_thumbnail(url=str(user.avatar_url))
        embed.add_field(name="Account created", value="On " + user.created_at.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - user.created_at) + " ago")
        embed.add_field(name="Display Name", value=user.display_name)
        embed.set_footer(text="User ID" + str(user.id))
        await ctx.send(embed=embed)


    @commands.command(name="invite", aliases=["discordinv"])
    async def DiscordAPI(self, ctx, *, invite):
        """Gets information about discord invites"""
        invite = str(invite.split("/")[-1])
        data = await self.REST("https://discordapp.com/api/v6/invite/" +  self.escape(invite) + "?with_counts=true")
        try:
            data["guild"]
        except:
            raise commands.CommandError(message="%"+data["message"])

        embed = discord.Embed(title="Click here to join the server!", colour=0x7289DA, url="https://discord.gg/" + data["code"])
        embed.add_field(name="Guild Name", value=str(data["guild"]["name"]))
        if data["guild"]["description"]:
            embed.add_field(name="Description", value=str(data["guild"]["description"]))
        embed.add_field(name="Members", value=str(data["approximate_member_count"]))
        embed.add_field(name="Online", value=str(data["approximate_presence_count"]))


        flagName = {
            "VERIFIED": "Verified",
            "LURKABLE": "Lurking enabled",
            "INVITE_SPLASH": "Custom invite splash screen",
            "VIP_REGIONS": "VIP Server",
            "FEATURABLE": "Featured server",
            "DISCOVERABLE": "In server discoveries",
            "NEWS": "News channel",
            "BANNER": "Custom banner",
            "VANITY_URL": "Custom vanity url",
            "ANIMATED_ICON": "Animated icon",
            "COMMERCE": "Store",
            "MORE_EMOJI": "More emoji",
            "PUBLIC": "Public server (Lurkable)"
        }

        flags = data["guild"]["features"]

        if flags:
            embed.add_field(name="Special features", value="\n".join([flagName[n] for n in flags]))

        try:
            embed.add_field(name="Invite created by", value=str(data["inviter"]["username"]) + "#" + str(data["inviter"]["discriminator"]) + " (<@" + str(data["inviter"]["id"]) + ">)")
        except KeyError:
            pass

        if "BANNER" in flags and data["guild"]["banner"]:
            embed.set_image(url="https://cdn.discordapp.com/banners/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["banner"]) + ".webp?size=4096")

        if "ANIMATED_ICON" in flags and \
            data["guild"]["icon"] and \
            data["guild"]["icon"].startswith("a_"):
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["icon"] + ".gif?size=4096"))
        elif data["guild"]["icon"]:
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["icon"] + ".webp?size=4096"))

        embed.set_footer(text="Server ID " + str(data["guild"]["id"]))
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


    @commands.command(name="weather")
    async def WeatherAPI(self, ctx, *, city):
        """Gets information about the weather"""
        geocoding = await self.REST("https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=en&q=" + self.escape(city))
        data = await self.REST("https://api.darksky.net/forecast/" +  config.apiKeys["darksky"] + "/" + geocoding[0]["lat"] + "," + geocoding[0]["lon"] + "?exclude=minutely,hourly,daily,flags&units=si")

        embed = discord.Embed(title=geocoding[0]["display_name"], colour=0xffb347)
        embed.set_thumbnail(url="https://darksky.net/images/weather-icons/" + data["currently"]["icon"] + ".png")
        try:
            alerts = []
            for alert in data["alerts"]:
                if len(alerts) > 3:
                    continue
                if alert["title"] not in alerts:
                    embed.add_field(name=alert["title"], value=alert["description"][:1024])
                    alerts.append(alert["title"])
        except:
            pass
        embed.add_field(name="Weather", value=str(round(data["currently"]["temperature"], 2)) + "°C (" + str(round(data["currently"]["temperature"] * (9/5) + 32, 2)) + "°F)\n" \
            + data["currently"]["summary"] + "\n" \
            + "Feels Like: " + str(round(data["currently"]["apparentTemperature"], 2)) + "°C (" + str(round(data["currently"]["apparentTemperature"] * (9/5) + 32, 2)) + "°F)\n" \
            + "Humidity: " + str(round(data["currently"]["humidity"] * 100, 2)) + "%\n" \
            + "Clouds: " + str(round(data["currently"]["cloudCover"] * 100, 2)) + "%\n" \
            + "Wind: " + str(data["currently"]["windSpeed"]) + " m/s (" + str(round(int(data["currently"]["windSpeed"]) * 2.2369362920544, 2)) + " mph)")
        embed.set_footer(text="Powered by Dark Sky and OpenStreetMap")
        embed.timestamp = datetime.utcfromtimestamp(data["currently"]["time"])
        await ctx.send(embed=embed)


    @commands.command(name="twitter")
    async def TwitterAPI(self, ctx, *, user):
        """Gets information about twitter users."""
        twitter = TwitterClient(consumer_key=config.apiKeys["twitterConsKey"],
        consumer_secret=config.apiKeys["twitterConsSecret"],
        oauth_token=config.apiKeys["twitterAccToken"],
        oauth_token_secret=config.apiKeys["twitterAccSecret"])
        data = await twitter.request("GET", "users/search.json", params={"count": 1, "q": self.escape(user)})
        data = data[0]
        embed = discord.Embed(title=data["name"] + " (@" + data["screen_name"] + ")", url="https://twitter.com/"+data["screen_name"], description=data["description"], color=0x1DA1F2)
        embed.set_thumbnail(url=data["profile_image_url_https"])
        embed.add_field(name="Tweets", value=str(data["statuses_count"]))
        embed.add_field(name="Followers", value=str(data["followers_count"]))
        embed.add_field(name="Following", value=str(data["friends_count"]))
        embed.add_field(name="Liked posts", value=str(data["favourites_count"]))
        if data["location"]:
            embed.add_field(name="Location", value=data["location"])
        extra = []
        if data["verified"]:
            extra.append("Verified")
        if data["protected"]:
            extra.append("Private")
        if extra:
            embed.add_field(name="+", value="\n".join(extra))
        embed.set_footer(icon_url="https://about.twitter.com/etc/designs/about-twitter/public/img/favicon-32x32.png", text="Twitter • Account created")
        embed.timestamp = datetime.strptime(data["created_at"], "%a %b %d %H:%M:%S %z %Y")
        await ctx.send(embed=embed)


    @commands.command(name="status", aliases=["statuspage"])
    async def StatusAPI(self, ctx, *, name="None"):
        """Gets information about status pages."""
        for page in config.statusPages:
            if name.lower() == page[0]:
                col = 0x00
                j = await self.REST(page[1] + "/index.json")
                if j["status"]["indicator"] == "none":
                    col = 0x00ff00
                elif j["status"]["indicator"] == "minor":
                    col = 0xffa500
                elif j["status"]["indicator"] == "major":
                    col = 0xff0000

                embed = discord.Embed(title="**" + page[0].title() + " Status** - " + j["status"]["description"], colour=col, url=page[1])
                for comp in j["components"]:
                    embed.add_field(name=comp["name"], value=comp["status"].replace("_", " ").title())
                embed.timestamp = datetime.utcnow()

                await ctx.send(embed=embed)

                for incident in j["incidents"]:
                    if incident["status"] == "resolved" or incident["status"] == "completed":
                        continue
                    firstUpdate = incident["incident_updates"][-1]
                    lastUpdate = incident["incident_updates"][0]
                    if incident["status"] == "scheduled":
                        col = 0xffa500
                    else:
                        col = 0xff0000

                    embed = discord.Embed(title="**" + incident["status"].title() + "** - " + incident["name"], color=col)
                    if firstUpdate["affected_components"]:
                        embed.add_field(name="Affected components", value="\n".join(c["name"] for c in firstUpdate["affected_components"]))
                    if firstUpdate != lastUpdate and len(firstUpdate) + len(lastUpdate) + 5 < 1900:
                        embed.description = "**" + datetime.fromisoformat(lastUpdate["created_at"].rstrip("Z")).strftime("%b %d %H:%M:%S %Y UTC%z") \
                                          + "**: " + lastUpdate["body"] + "\n\n\n**" \
                                          + datetime.fromisoformat(firstUpdate["created_at"].rstrip("Z")).strftime("%b %d %H:%M:%S %Y UTC%z") \
                                          + "**: " + firstUpdate["body"]
                    else:
                        embed.description = firstUpdate["body"]

                    if incident["scheduled_for"]:
                        embed.timestamp = datetime.fromisoformat(incident["scheduled_for"].rstrip("Z"))
                        embed.set_footer(text=incident["impact"].title() + " • Starts")
                    else:
                        embed.timestamp = datetime.fromisoformat(incident["created_at"].rstrip("Z"))
                        embed.set_footer(text=incident["impact"].title() + " • Started")

                    await ctx.send(embed=embed)
                return

        raise commands.CommandError(message="%Invalid page! Currently supported pages: ```\n" + "\n".join([n.title() for n, a in config.statusPages]) + "```")

def setup(bot):
    bot.add_cog(APIs(bot))
