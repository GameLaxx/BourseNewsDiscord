import asyncio
import discord
from discord.ext import commands, tasks
from news import News, get_news, check_nav
from load import set_navs, get_navs, set_memory, get_memory

navs = get_navs()
memory = get_memory()

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
        if nav not in memory:
            memory[nav] = ""
        for _new in news:
            if _new.title == memory[nav]:
                break # stop sending when find same message
            await channel.send(str(_new))
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
    if not (await check_nav(nav)):
        await ctx.send(f"{nav} doesn't lead to a page on Trading View.")
        return
    navs.append(nav)
    set_navs(navs)
    await ctx.send(f"{nav} has been registered !")

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
