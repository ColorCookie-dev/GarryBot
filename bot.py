import discord
from discord.ext import commands
from discord_token import secret_token

bot = commands.Bot(command_prefix='~')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(secret_token)
