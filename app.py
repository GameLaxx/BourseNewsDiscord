import discord
from discord.ext import commands, tasks
from news import News, get_news, check_nav
from load import set_navs, get_navs, set_memory, get_memory

navs : dict = get_navs()
memory : dict = get_memory()

#----------------------------------------------------------------------------------
# Bot setup
#----------------------------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#----------------------------------------------------------------------------------
# Bot automation
#----------------------------------------------------------------------------------

async def send_news_func():
    channel = bot.get_channel(1370001423445659699)
    for nav in navs:
        news : list[News] = await get_news(nav)
        fresh = False
        if nav not in memory:
            memory[nav] = ""
            fresh = True
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
            if fresh: # when adding new nav => only first news
                break
        memory[nav] = news[0].title
    set_memory(memory)
        
@tasks.loop(hours=1)
async def send_news_auto():
    await send_news_func()

#----------------------------------------------------------------------------------
# Bot behaviour
#----------------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"Connected as {bot.user} !")
    send_news_auto.start()

@bot.command()
async def test(ctx):
    await ctx.send(f"Salut {ctx.author.name} !")
    
@bot.command()
async def register(ctx, nav):
    ret = await check_nav(nav)
    if ret == None:
        await ctx.send(f"{nav} doesn't lead to a page on Trading View.")
        return
    navs[nav] = ret
    set_navs(navs)
    await ctx.send(f"{navs[nav]['name']} has been registered !")
    
@bot.command()
async def delete(ctx, nav):
    if nav in navs:
        navs.pop(nav)
        set_navs(navs)
    await ctx.send(f"{nav} has been deleted !")

@bot.command()
async def force(ctx):
    await ctx.send("Send news forced !")
    await send_news_func()

@bot.command()
async def list(ctx):
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
    if nav not in navs:
        await ctx.send(f"Symbol {nav} not found..")
        return
    if ctx.author.name in navs[nav]["ping"]:
        await ctx.send(f"User already in ping list of {nav} !")
        return
    navs[nav]["ping"].append(ctx.author.id)
    set_navs(navs)
    await ctx.send(f"User added to ping list of {nav} !")

@bot.command()
async def unping(ctx, nav):
    if nav not in navs:
        await ctx.send(f"Symbol {nav} not found..")
        return
    if ctx.author.name in navs[nav]["ping"]:
        await ctx.send(f"User not in ping list of {nav} !")
        return
    navs[nav]["ping"].remove(ctx.author.id)
    set_navs(navs)
    await ctx.send(f"User removed from ping list of {nav} !")

#----------------------------------------------------------------------------------
# Bot launching
#----------------------------------------------------------------------------------

with open("txt/bot_token.txt") as f:
    token = f.readline()
bot.run(token)
