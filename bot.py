import sqlite3
import discord
from discord.ext import commands
from discord_token import secret_token, secret_api_key, secret_cx_code
from google_images_search import GoogleImagesSearch


class DBConnect:
    def __init__(self, db=':memory:'):
        self.conn = sqlite3.connect(db)
        c = self.conn.cursor()
        # Create table
        try:
            c.execute('''CREATE TABLE links
                         (term text primary key, href text)''')
            self.conn.commit()
        except sqlite3.OperationalError:
            print('Using existing cache of memes')

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        self.conn.close()

db_conn = DBConnect('meme_cache.db')
with db_conn:

    bot = commands.Bot(command_prefix='~')

    quick_react_dict = {
        'notaccident': ('https://i.kym-cdn.com/entries/icons/facebook/000/023/853/accidents.jpg', 'There are no accidents'),
        'bigbrain': ('https://vignette.wikia.nocookie.net/furthestextreme/images/f/f6/Cropped-big-brain.jpg/revision/latest/scale-to-width-down/340?cb=20190929085659', 'Big brains'),
        'bigbrain2': ('https://i.kym-cdn.com/entries/icons/original/000/030/525/cover5.png', 'Markiplier version of big brain'),
        'coffindance': ('https://media0.giphy.com/media/j6ZlX8ghxNFRknObVk/giphy.gif?cid=ecf05e471a1b565aa6951015ad6c9ec2eb2de8a9bed0465d&rid=giphy.gif', 'coffin dance'),
    }

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
        async def gs(self, ctx, *, arg, skip_cache=False):
            '''Searches the phrase given on google'''

            # sanitization
            searchTerm = list(arg)
            for i in searchTerm:
                if not i.isalnum and i not in "'+.:":
                    searchTerm.remove(i)
            searchTerm = ''.join(searchTerm)

            cur = db_conn.conn.cursor()

            if not skip_cache:
                for row in cur.execute('SELECT * FROM links WHERE term="%s"' % (searchTerm,)):
                    url = row[1]
                    if url:
                        embed = discord.Embed()
                        embed.set_image(url=url)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send('Couldn\'t find the searched image.')
                    return

            async with ctx.typing():
                gis = GoogleImagesSearch(secret_api_key, secret_cx_code)

                _search_params = {
                    'q': searchTerm,
                    'num': 10,
                    'safe': 'high',
                }

            gis.search(search_params=_search_params)
            for image in gis.results():
                url = image.url

                try:
                    cur.execute('INSERT INTO links VALUES ("%s", "%s")' % (searchTerm, url))
                    db_conn.conn.commit()
                except sqlite3.IntegrityError:
                    cur.execute('UPDATE links SET href="%s" where term="%s"' % (url, searchTerm))

                embed = discord.Embed()
                embed.set_image(url=url)
                await ctx.send(embed=embed)
                break
            else:
                cur.execute('INSERT INTO links VALUES ("%s", "%s")' % (searchTerm, ""))
                db_conn.conn.commit()

                await ctx.send('Couldn\'t find the searched image.')

        @commands.command()
        async def gsd(self, ctx, *, arg):
            '''Same as gs but deletes the original message'''
            await gs(ctx, arg=arg)
            await ctx.message.delete()

        @commands.command()
        async def gsu(self, ctx, *, arg):
            '''Same as gs but skips any cache check'''
            await gs(ctx, arg=arg, skip_cache=True)

        @commands.command()
        async def gsud(self, ctx, *, arg):
            '''Same as gsu but deletes the original message'''
            await gs(ctx, arg=arg, skip_cache=True)
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

