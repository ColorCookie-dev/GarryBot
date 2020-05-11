import discord
import typing
from discord.ext import commands
from discord_token import secret_token, secret_api_key, secret_cx_code
from google_images_search import GoogleImagesSearch


bot = commands.Bot(command_prefix='~')

class Searching_Commands(commands.Cog, name="Search"):
    '''Commands which search on the web'''

    @commands.command()
    async def gs(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *,
            searchTerm,
            delete=False):
        '''Searches the phrase given on google'''

        if not (start >= 1 and start <= 200 and num >= 1 and num <= 10):
            await ctx.send('Numbers not in bound')
            return

        gis = GoogleImagesSearch(secret_api_key, secret_cx_code)

        _search_params = {
            'q': searchTerm,
            'start': start,
            'num': num,
            'safe': 'high',
        }

        webhook = None
        webhooks = await ctx.channel.webhooks()
        if len(webhooks):
            webhook = webhooks[0]
        else:
            webhook = await ctx.channel.create_webhook(name='LOLBot')

        gis.search(search_params=_search_params)
        embeds = []
        for img in gis.results():
            if img.url:
                embed_data = {
                    'type': 'image',
                    'image': {
                        'url': img.url,
                    },
                }
                embeds.append(discord.Embed.from_dict(embed_data))
        await ctx.message.delete()
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

    @commands.command()
    async def gsd(self, ctx, start: typing.Optional[int] = 1, num: typing.Optional[int] = 1, *, arg):
        '''Same as gs but deletes the original message'''
        await self.gs(ctx, start=start, num=num, searchTerm=arg, delete=True)

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

