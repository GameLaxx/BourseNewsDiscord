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
                description=f"Provider : {_new.provider}.\n**{_new.title}**\nTo learn more, go on {_new.url} !",
                color=discord.Color.from_rgb(navs[nav]["color"][0], navs[nav]["color"][1], navs[nav]["color"][2])  # bar color
            )
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
    await ctx.send(f"{navs[nav]['name']} has been deleted !")

@bot.command()
async def force(ctx):
    await send_news_func()
    print("Send news forced !")

#----------------------------------------------------------------------------------
# Bot launching
#----------------------------------------------------------------------------------

with open("txt/bot_token.txt") as f:
    token = f.readline()
bot.run(token)
