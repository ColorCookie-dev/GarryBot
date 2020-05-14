import asyncio
import datetime
import discord
import typing
from discord.ext import commands
from discord_token import secret_token, secret_api_key, secret_cx_code
from google_images_search import GoogleImagesSearch


bot = commands.Bot(command_prefix='~')

async def get_web_hook(channel: discord.TextChannel):
    webhooks = await channel.webhooks()
    if len(webhooks):
        return webhooks[0]
    else:
        return await channel.create_webhook(name='LOLBot')

class Searching_Commands(commands.Cog, name="Search"):
    '''Commands which search on the web'''

    @commands.command()
    async def gs(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *, searchTerm,
            delete=False):
        '''Searches the phrase given on google'''

        if not (start >= 1 and start <= 200
                and num >= 1 and num <= 10):
            await ctx.send('Numbers not in bound')
            return

        gis = GoogleImagesSearch(secret_api_key, secret_cx_code)

        _search_params = {
            'q': searchTerm,
            'start': start,
            'num': num,
            'safe': 'high',
        }

        webhook = await get_web_hook(ctx.channel)

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

        if not delete:
            cont = ctx.message.content
            await webhook.send(content=cont,
                    embeds=embeds,
                    username=ctx.message.author.display_name,
                    avatar_url=ctx.message.author.avatar_url)
        else:
            await webhook.send(
                    embeds=embeds,
                    username=ctx.message.author.display_name,
                    avatar_url=ctx.message.author.avatar_url)
        await ctx.message.delete()

    @commands.command()
    async def gsd(self,
            ctx,
            start: typing.Optional[int] = 1,
            num: typing.Optional[int] = 1,
            *, searchTerm):
        '''Same as gs but deletes the original message'''
        await self.gs(ctx, start=start, num=num, searchTerm=searchTerm, delete=True)

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

    @commands.command()
    async def secret(self, ctx, sec: typing.Optional[float] = 10.0, *, content: str = ""):
        '''deletes the secret after some time'''
        if sec < 1 or sec > 60:
            await ctx.send('Time is out of bound [1, 60]')
            return
        webhook = await get_web_hook(ctx.channel)
        secr_msg = await webhook.send(content=f"The secret message will be deleted in {sec} seconds",
                wait=True,
                username=ctx.message.author.display_name,
                avatar_url=ctx.message.author.avatar_url,
                embeds=ctx.message.embeds)
        await asyncio.sleep(sec)
        await secr_msg.delete()
        await ctx.message.delete()

    @commands.command()
    async def say(self, ctx, *, content):
        '''makes the bot say anything'''
        await ctx.send(content)
        await ctx.message.delete()

class ChatPattern:
    def __init__(self, arg):
        if arg in ['before', 'after', 'around']: 
            self.option = arg
        else:
            raise TypeError('NonExistent Pattern Found')

class ManagementCmds(commands.Cog, name='Management'):
    '''Server and chat management commands'''

    @commands.has_permissions(manage_messages=True)
    @commands.command(name='del')
    async def _del(self, ctx,
            till: typing.Union[int, discord.Message] = int(1),
            option: typing.Optional[ChatPattern] = ChatPattern('after')):
        '''deletes message relative to the latest msg'''
        await ctx.message.delete()
        if isinstance(till, int):
            if till < 0 or till > 60:
                await ctx.send('Given index is out of bound')
                return
            deleted = await ctx.channel.purge(limit=till)
        else:
            _params = {
                option.option: till,
                'limit': 60
            }
            deleted = await ctx.channel.purge(**_params)
        webhook = await get_web_hook(ctx.channel)
        await webhook.send(content='Deleted {} message(s)'.format(len(deleted)),
                username=ctx.message.author.display_name,
                avatar_url=ctx.message.author.avatar_url)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def move(self, ctx,
            to_channel: discord.TextChannel,
            till: typing.Union[int, discord.Message, datetime.datetime] = int(1),
            option: typing.Optional[ChatPattern] = ChatPattern('after')):
        '''Moves msgs with respect to latest msg'''
        if not ctx.message.author.permissions_in(to_channel).send_messages:
            await ctx.send('You do not have permission to move messages to the said channel')
            return

        await ctx.message.delete()

        _params = {}
        if isinstance(till, int):
            if till < 0 or till > 60:
                await ctx.send('Given index is out of bound')
                return
            _params['limit'] = till
        else:
            _params[option.option] = till
            _params['limit'] = 60

        webhook = await get_web_hook(to_channel)

        if not _params.get('after', None):
            history = reversed(await ctx.channel.history(**_params).flatten())
        else:
            history = await ctx.channel.history(**_params).flatten()

        for msg in history:
            files = []
            for att in msg.attachments:
                files.append(await att.to_file())
            new_msg = {
                'content': msg.content,
                'tts': msg.tts,
                'files': files,
                'embeds': msg.embeds,
                'username': msg.author.display_name,
                'avatar_url': msg.author.avatar_url
            }
            await webhook.send(**new_msg)
            await msg.delete()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delfrom(self, ctx,
            start: discord.Message,
            till: discord.Message):
        '''deletes messages between 2 msgs'''

        _params = {
            'before': start,
            'after': till,
        }

        if start.created_at <= till.created_at:
            _params = {
                'after': start,
                'before': till,
            }

        await ctx.message.delete()

        deleted = await ctx.channel.purge(**_params)
        webhook = await get_web_hook(ctx.channel)
        await webhook.send(content='Deleted {} message(s)'.format(len(deleted)),
                username=ctx.message.author.display_name,
                avatar_url=ctx.message.author.avatar_url)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def movefrom(self, ctx,
            to_channel: discord.TextChannel,
            start: discord.Message,
            till: discord.Message):
        '''moves messages from between 2 msgs to a certain channel'''
        if not ctx.message.author.permissions_in(to_channel).send_messages:
            await ctx.send('You do not have permission to move messages to the said channel')
            return

        _params = {
            'before': start,
            'after': till,
        }

        if start.created_at <= till.created_at:
            _params['after'] = start
            _params['before'] = till

        await ctx.message.delete()

        webhook = await get_web_hook(to_channel)

        history = await ctx.channel.history(**_params).flatten()
        for msg in history:
            files = []
            for att in msg.attachments:
                files.append(await att.to_file())
            new_msg = {
                'content': msg.content,
                'tts': msg.tts,
                'files': files,
                'embeds': msg.embeds,
                'username': msg.author.display_name,
                'avatar_url': msg.author.avatar_url
            }
            await webhook.send(**new_msg)
            await msg.delete()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def spam(self, ctx, num: int = 5):
        '''Spams channel with numbers'''
        webhook = await get_web_hook(ctx.channel)
        if num < 1 or num > 60:
            ctx.send('Index is not in bound')
            return
        await ctx.message.delete()
        for i in range(num, 0, -1):
            await webhook.send(content=i,
                    username=ctx.message.author.display_name,
                    avatar_url=ctx.message.author.avatar_url)

bot.add_cog(Searching_Commands(bot))
bot.add_cog(Bot_Commands(bot))
bot.add_cog(ManagementCmds(bot))

if __name__ == '__main__':
    bot.run(secret_token)

