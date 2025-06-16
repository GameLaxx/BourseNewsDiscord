import discord
from datetime import timedelta
from discord.ext import commands, tasks
from news import News, get_news, check_nav
from load import set_navs, get_navs, set_memory, get_memory, set_settings, get_settings

navs : dict[str] = get_navs()
memory : dict = get_memory()
settings : dict = get_settings()

send_news_auto = None

def word_to_nav(word : str):
    word = word.lower()
    for nav in navs:
        if word in nav.lower():
            return nav
        if word in navs[nav]["name"].lower():
            return nav
    return None

#----------------------------------------------------------------------------------
# Bot setup
#----------------------------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

#----------------------------------------------------------------------------------
# Bot automation
#----------------------------------------------------------------------------------

async def send_news_func():
    channel = bot.get_channel(1370001423445659699)
    for nav in navs:
        news : list[News] = await get_news(nav)
        news[0].title += " (actualisé)"
        break_first = False
        if "(actualisé)" in news[0].title:
            break_first = True
        if nav not in memory:
            memory[nav] = ""
            break_first = True
        for _new in news:
            if _new.title == memory[nav]:
                break # stop sending when find same message
            embed = discord.Embed(
                title=navs[nav]["name"],
                description=f"Provider : {_new.provider}.\n**{_new.title}**\nTo learn more, go on {_new.url} !\n",
                color=discord.Color.from_rgb(navs[nav]["color"][0], navs[nav]["color"][1], navs[nav]["color"][2])  # bar color
            )
            for ping in navs[nav]["ping"]:
                embed.description += f"<@{ping}>"
            embed.set_footer(text="BourseNewsBot • TradingView")
            await channel.send(embed=embed)
            if break_first: # when adding new nav or updated news => only first news
                break
        memory[nav] = news[0].title
    set_memory(memory)
        
def create_send_news_loop(time : str):
    time = time.split(":")
    if len(time) != 3:
        return None
    try:
        interval = timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
    except:
        return None
    @tasks.loop(seconds=interval.total_seconds())
    async def send_news_auto():
        await send_news_func()
    return send_news_auto

#----------------------------------------------------------------------------------
# Bot behaviour
#----------------------------------------------------------------------------------

@bot.event
async def on_ready():
    global send_news_auto
    print(f"Connected as {bot.user} !") 
    send_news_auto = create_send_news_loop(settings["news_auto"])
    if send_news_auto == None:
        settings["news_auto"] = "1:0:0"
        send_news_auto = create_send_news_loop("1:0:0")
        set_settings(settings)
    send_news_auto.start()

@bot.command()
async def test(ctx):
    await ctx.send(f"Salut {ctx.author.name} !")
    
@bot.command()
async def register(ctx, nav):
    ret = await check_nav(nav)
    if ret == None:
        await ctx.send(f"https://fr.tradingview.com/symbols/{nav}/news/ doesn't lead to a page on Trading View.")
        return
    navs[nav] = ret
    set_navs(navs)
    await ctx.send(f"{navs[nav]['name']} has been registered !")
    
@bot.command()
async def delete(ctx, nav):
    w_nav = word_to_nav(nav)
    if w_nav != None:
        navs.pop(w_nav)
        set_navs(navs)
    await ctx.send(f"{w_nav} has been deleted !")

@bot.command()
async def force(ctx):
    await ctx.send("Send news forced !")
    await send_news_func()

@bot.command()
async def show(ctx):
    ret = "Here is a list of all registered items :\n"
    for nav in navs:
        ret += f"{navs[nav]['name']} (__symbol__ : {nav})"
        if navs[nav]['ping'] != []:
            ret += " [**ping**:"
            for ping in navs[nav]['ping']:
                ret += " " + (await bot.fetch_user(ping)).name
            ret += "]"
        ret += "\n"
    await ctx.send(ret)

@bot.command()
async def ping(ctx, nav):
    w_nav = word_to_nav(nav)
    if w_nav == None:
        await ctx.send(f"Symbol {nav} not found..")
        return
    if ctx.author.name in navs[w_nav]["ping"]:
        await ctx.send(f"User already in ping list of {w_nav} !")
        return
    navs[w_nav]["ping"].append(ctx.author.id)
    set_navs(navs)
    await ctx.send(f"User added to ping list of {w_nav} !")

@bot.command()
async def unping(ctx, nav):
    w_nav = word_to_nav(nav)
    if w_nav == None:
        await ctx.send(f"Symbol {nav} not found..")
        return
    if ctx.author.name in navs[w_nav]["ping"]:
        await ctx.send(f"User not in ping list of {w_nav} !")
        return
    navs[w_nav]["ping"].remove(ctx.author.id)
    set_navs(navs)
    await ctx.send(f"User removed from ping list of {w_nav} !")

@bot.command()
async def get(ctx, nav):
    w_nav = word_to_nav(nav)
    if w_nav == None:
        await ctx.send(f"Symbol {nav} not found..")
        return
    await ctx.send(f"You can see all the news about {navs[w_nav]['name']} here : https://fr.tradingview.com/symbols/{w_nav}/news/")

@bot.command()
async def params(ctx, setting = ""):
    if setting == "":
        ret = "Here are the current settings :\n"
        for key in settings:
            ret += f"{key} : {settings[key]}"
        await ctx.send(ret)
        return
    if create_send_news_loop(setting) == None:
        await ctx.send("Problem occured : News auto setting should be in format 'H:M:S'.")
    global send_news_auto
    if send_news_auto.is_running():
        send_news_auto.cancel()
    send_news_auto = create_send_news_loop(setting)
    send_news_auto.start()
    settings["news_auto"] = setting
    set_settings(settings)
    await ctx.send(f"News auto setting has been set to : '{setting}'.")

@bot.command()
async def help(ctx):
    ret = "**Here are all the commands for this bot !**\n"
    ret += "'!register SYMBOL' allows to make the bot listen to a news page on Trading View.\n"
    ret += "'!delete SYMBOL' stops the bot from listening to a news page on Trading View.\n"
    ret += "'!show' shows all symbols, their equivalent name and the list of pinged people.\n"
    ret += "'!ping SYMBOL' allows the author to be pinged when a news about this symbol comes out.\n"
    ret += "'!unping SYMBOL' stops the author from being pinged when a news about this symbol comes out.\n"
    ret += "'!force' forces the bot to check for news. This command is automatically called every hour.\n"
    await ctx.send(ret)

#----------------------------------------------------------------------------------
# Bot launching
#----------------------------------------------------------------------------------

with open("txt/bot_token.txt") as f:
    token = f.readline()
bot.run(token)
