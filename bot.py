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

    for i in quick_react_dict:
        url, meme = quick_react_dict[i]

        exec('@bot.command()\n\
async def ' + i + '(ctx):\n\
    \'\'\'embeds '+ meme + ' meme\'\'\'\n\
    embed = discord.Embed()\n\
    embed.set_image(url="' + url +'")\n\
    await ctx.send(embed=embed)')

    @bot.command()
    async def gs(ctx, *, arg, skip_cache=False):
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

    @bot.command()
    async def gsd(ctx, *, arg):
        '''Same as gs but deletes the original message'''
        await gs(ctx, arg=arg)
        await ctx.message.delete()

    @bot.command()
    async def gsu(ctx, *, arg):
        '''Same as gs but skips any cache check'''
        await gs(ctx, arg=arg, skip_cache=True)

    @bot.command()
    async def gsud(ctx, *, arg):
        '''Same as gsu but deletes the original message'''
        await gs(ctx, arg=arg, skip_cache=True)
        await ctx.message.delete()

    @bot.command()
    async def ping(ctx):
        '''Gets the latency of the bot'''
        latency = round(bot.latency * 1000)  # Included in the Discord.py library
        await ctx.send(str(latency) + 'ms')

    @bot.command()
    async def lol(ctx):
        '''writes a very witty joke'''
        await ctx.send('fuck you!')

    @bot.command()
    async def version(ctx):
        '''shows the version'''
        await ctx.send('Better than your mom!')

    if __name__ == '__main__':
        bot.run(secret_token)

