import discord
import typing
from discord.ext import commands
from discord_token import secret_token, secret_api_key, secret_cx_code
from google_images_search import GoogleImagesSearch


bot = commands.Bot(command_prefix='~')

quick_react_dict = {
    'notaccident': ('https://i.kym-cdn.com/entries/icons/facebook/000/023/853/accidents.jpg', 'There are no accidents'),
    'bigbrain': ('https://vignette.wikia.nocookie.net/furthestextreme/images/f/f6/Cropped-big-brain.jpg/revision/latest/scale-to-width-down/340?cb=20190929085659', 'Big brains'),
    'bigbrain2': ('https://i.kym-cdn.com/entries/icons/original/000/030/525/cover5.png', 'Markiplier version of big brain'),
    'coffindance': ('https://media0.giphy.com/media/j6ZlX8ghxNFRknObVk/giphy.gif?cid=ecf05e471a1b565aa6951015ad6c9ec2eb2de8a9bed0465d&rid=giphy.gif', 'coffin dance'),
}

# Just for the intellisense
class Quick_Reactions(commands.Cog):
    pass

dyn_quick_functions_code = "\
class Quick_Reactions(commands.Cog, name='Quick'):\n\
    '''For Quick Reactions to memes'''\n"

for i in quick_react_dict:
    url, meme = quick_react_dict[i]

    dyn_quick_functions_code += f"\
    @commands.command()\n\
    async def {i}(self, ctx):\n\
        '''embeds {meme} meme'''\n\
        embed = discord.Embed()\n\
        embed.set_image(url='{url}')\n\
        await ctx.send(embed=embed)\n"

exec(dyn_quick_functions_code)

class Searching_Commands(commands.Cog, name="Search"):
    '''Commands which search on the web'''

    @commands.command()
    async def gs(self, ctx, ind: typing.Optional[int] = 1, *, searchTerm):
        '''Searches the phrase given on google'''

        ind -= 1
        if not ind >= 0:
            await ctx.send('Index not in bound')
            return

        gis = GoogleImagesSearch(secret_api_key, secret_cx_code)

        _search_params = {
            'q': searchTerm,
            'num': ind+1,
            'safe': 'high',
        }

        gis.search(search_params=_search_params)
        results = gis.results()
        url = results[ind] if len(results) >= ind else None
        if url:
            embed = discord.Embed()
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Couldn\'t find the searched image.')

    @commands.command()
    async def gsd(self, ctx, ind: typing.Optional[int] = 1, *, arg):
        '''Same as gs but deletes the original message'''
        await self.gs(ctx, ind=ind, searchTerm=arg)
        await ctx.message.delete()

class Bot_Commands(commands.Cog, name="Normal"):
    '''Normal Bot commands'''

    @commands.command()
    async def ping(self, ctx):
        '''Gets the latency of the bot'''
        latency = round(bot.latency * 1000)  # Included in the Discord.py library
        await ctx.send(str(latency) + 'ms')

    @commands.command()
    async def lol(self, ctx):
        '''writes a very witty joke'''
        await ctx.send('fuck you!')

    @commands.command()
    async def version(self, ctx):
        '''shows the version'''
        await ctx.send('Better than your mom!')

bot.add_cog(Quick_Reactions(bot))
bot.add_cog(Searching_Commands(bot))
bot.add_cog(Bot_Commands(bot))

if __name__ == '__main__':
    bot.run(secret_token)

