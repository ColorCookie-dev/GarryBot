import sqlite3
import discord
import typing
from discord.ext import commands
from discord_token import secret_token, secret_api_key, secret_cx_code
from google_images_search import GoogleImagesSearch

class DBConnection:
    insert_query = 'INSERT INTO links (term, ind, href) VALUES ("%s", "%d", "%s")'
    select_query = 'SELECT href FROM links WHERE term="%s" and ind="%d"'
    update_query = 'UPDATE links SET href="%s" where term="%s"'

    def __init__(self, db=':memory:'):
        self.conn = sqlite3.connect(db)
        c = self.conn.cursor()
        # Create table command
        try:
            c.execute('''CREATE TABLE links
                         (id int primary key autoincrement, term text not null, ind int, href text)''')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.conn.close()

bot = commands.Bot(command_prefix='~')

class Searching_Commands(commands.Cog, name="Search"):
    '''Commands which search on the web'''

    @commands.command()
    async def gs(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *, arg,
            skip_cache=False,
            delete=False):
        '''Searches the phrase given on google'''
        if not (start >= 1 and start <= 200
                and num >= 1 and num <= 10):
            await ctx.send('Numbers not in bound')
            return

        # sanitization
        searchTerm = ''
        for i in arg:
            if i.isalnum or i in "'+.:":
                searchTerm += i
        searchTerm = ''.join(searchTerm)

        webhook = None
        webhooks = await ctx.channel.webhooks()
        if len(webhooks):
            webhook = webhooks[0]
        else:
            webhook = await ctx.channel.create_webhook(name='LOLBot')

        with DBConnection('meme_cache.db') as db_conn:
            cur = db_conn.conn.cursor()

            if (not skip_cache) or (num != 1):
                for row in cur.execute(db_conn.select_query % (searchTerm, start)):
                    url = row[0]
                    if url:
                        embed = discord.Embed()
                        embed.set_image(url=url)
                        if not delete:
                            await webhook.send(content=ctx.message.content,
                                    embed=embed,
                                    username=ctx.message.author.nick,
                                    avatar_url=ctx.message.author.avatar_url)
                        else:
                            await webhook.send(
                                    embed=embed,
                                    username=ctx.message.author.nick,
                                    avatar_url=ctx.message.author.avatar_url)
                        await ctx.message.delete()
                    else:
                        await ctx.send('Couldn\'t find the searched image.')
                    return

            gis = GoogleImagesSearch(secret_api_key, secret_cx_code)

            _search_params = {
                'q': searchTerm,
                'start': start,
                'num': num,
                'safe': 'high',
            }

            gis.search(search_params=_search_params)
            embeds = []
            for i, img in enumerate(gis.results()):
                if img.url:
                    embed_data = {
                        'type': 'image',
                        'image': {
                            'url': img.url,
                        },
                    }
                    embeds.append(discord.Embed.from_dict(embed_data))

                    try:
                        cur.execute(db_conn.insert_query % (searchTerm, start+i, img.url))
                        db_conn.conn.commit()
                    except sqlite3.IntegrityError:
                        cur.execute(db_conn.update_query % (img.url, start+i, searchTerm))
                else:
                    await ctx.send('Couldn\'t find the searched image.')
                    cur.execute(db_conn.insert_query % (searchTerm, start+i, ""))
                    db_conn.conn.commit()

            if not delete:
                cont = ctx.message.content
                await webhook.send(content=cont,
                        embeds=embeds,
                        username=ctx.message.author.nick,
                        avatar_url=ctx.message.author.avatar_url)
            else:
                await webhook.send(
                        embeds=embeds,
                        username=ctx.message.author.nick,
                        avatar_url=ctx.message.author.avatar_url)
            await ctx.message.delete()

    @commands.command()
    async def gsd(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *, arg):
        '''Same as gs but deletes the original message'''
        await self.gs(ctx, start=start, num=num, arg=arg, delete=True)

    @commands.command()
    async def gsu(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *, arg):
        '''Same as gs but skips any cache check'''
        await self.gs(ctx, start=start, num=num, arg=arg, skip_cache=True)

    @commands.command()
    async def gsu(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *, arg):
        '''Same as gsu but deletes the original message'''
        await self.gs(ctx, start=start, num=num, arg=arg, skip_cache=True, delete=True)

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

bot.add_cog(Searching_Commands(bot))
bot.add_cog(Bot_Commands(bot))

if __name__ == '__main__':
    bot.run(secret_token)

