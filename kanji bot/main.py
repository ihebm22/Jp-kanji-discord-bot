import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from japanese_utils import lookup_word

load_dotenv()

# Create bot instance with command prefix '!' and specific permissions
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    application_id=1126312224213056
    
)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is now running!')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

@bot.command()
async def jisho(ctx, *, word: str):
    """Look up a Japanese word"""
    try:
        await ctx.send("Searching... 🔍")
        result, _ = lookup_word(word)
        
        embed = discord.Embed(
            title=f"Dictionary lookup: {word}", 
            description=result,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
                
    except Exception as e:
        print(f"Error in jisho command: {str(e)}")
        await ctx.send(f"Error occurred: {str(e)}")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
