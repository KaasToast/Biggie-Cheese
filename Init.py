import discord
import wavelink
import subprocess
import os
import shutil
import traceback
import datetime
import topgg
import sys
import re
import asyncio

from dotenv import load_dotenv
from bin.Cogs.Music import Player
from discord.ext import commands
from discord.ext.commands import *
from pathlib import Path

DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()

load_dotenv()
TOPGG_WEBHOOK_TOKEN = os.getenv('TOPGG_WEBHOOK_TOKEN')
TOPGG_WEBHOOK_PASSWORD = os.getenv('TOPGG_WEBHOOK_PASSWORD')

class Init(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.wavelink = wavelink.Client(bot=client)
        self.client.loop.create_task(self.start_nodes())
        self.topggpy = topgg.DBLClient(self.client, TOPGG_WEBHOOK_TOKEN, autopost=True, post_shard_count=True)
        self.topgg_webhook = topgg.WebhookManager(self.client).dbl_webhook('/webhook', TOPGG_WEBHOOK_PASSWORD)
        self.topgg_webhook.run(5000)

    def cog_unload(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.topgg_webhook.close())        
        for filename in os.listdir('./bin/Cogs'):
            if filename.endswith('.py'):
                try:
                    self.client.unload_extension(f'bin.Cogs.{filename[:-3]}')
                except:
                    pass

    async def start_nodes(self):
        await self.client.wait_until_ready()
        nodes = {
            'MAIN': {
                'host': '10.0.0.14',
                'port': 2333,
                'rest_uri': 'http://10.0.0.14:2333',
                'password': 'password',
                'identifier': 'MAIN',
                'region': 'europe'
            }
        }
        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    async def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.Cog.listener()
    async def on_connect(self):
        print('Bot is starting...')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot started.')

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        try:
            embed = discord.Embed(
                title='**Syncing to dev branch...**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            message = await ctx.send(embed = embed)
            os.system(f'git -C {twoup}/Biggie-Cheese-Dev pull')
            for guild in self.client.guilds:
                player = await self.get_player(guild)
                if player.is_connected:
                    await player.teardown()
            for filename in os.listdir('./bin/Cogs'):
                if filename.endswith('.py'):
                    try:
                        self.client.unload_extension(f'bin.Cogs.{filename[:-3]}')
                    except:
                        pass
            new_cogs = f'{twoup}/Biggie-Cheese-Dev/bin/Cogs'
            old_cogs = './bin/Cogs'
            new_files = os.listdir(new_cogs)
            old_files = os.listdir(old_cogs)
            for file in old_files:
                if file.endswith('.py'):
                    full_path = os.path.join(old_cogs, file)
                    os.remove(full_path)
            for file in new_files:
                if file.endswith('.py'):
                    shutil.copy(os.path.join(new_cogs, file), old_cogs)
            for filename in os.listdir('./bin/Cogs'):
                if filename.endswith('.py'):
                    self.client.load_extension(f'bin.Cogs.{filename[:-3]}')
            os.system(f'git -C {twoup}/Biggie-Cheese add .')
            os.system(f'git -C {twoup}/Biggie-Cheese commit -m "Automated Push"')
            os.system(f'git -C {twoup}/Biggie-Cheese push -u https://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@github.com/KaasToast/Biggie-Cheese main')
            embed = discord.Embed(
                title='**Succesfully synced to dev branch.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await message.edit(embed = embed)
        except:
            traceback.print_exc()

    @sync.error
    async def sync_error(self, ctx, error):
        if isinstance(error, NotOwner):
            embed = discord.Embed(
                title='**:x: This command is only available to the owner of the bot.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        self.client.load_extension(f'bin.Cogs.{extension}')
        embed = discord.Embed(
            title=f'**:white_check_mark: Loaded {extension}!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!load <extension>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, CommandInvokeError):
            embed = discord.Embed(
                title='**:x: An error occured whilst trying to reload extension.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            traceback.print_exc()
        if isinstance(error, NotOwner):
            embed = discord.Embed(
                title='**:x: This command is only available to the owner of the bot.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        if extension == 'Music':
            for guild in self.client.guilds:
                player = await self.get_player(guild)
                if player.is_connected:
                    await player.teardown()
        self.client.unload_extension(f'bin.Cogs.{extension}')
        embed = discord.Embed(
            title=f'**:white_check_mark: Unloaded {extension}!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        
    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!unload <extension>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)        
        if isinstance(error, CommandInvokeError):
            embed = discord.Embed(
                title='**:x: An error occured whilst trying to unload extension.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            traceback.print_exc()
        if isinstance(error, NotOwner):
            embed = discord.Embed(
                title='**:x: This command is only available to the owner of the bot.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        if extension == 'Music':
            for guild in self.client.guilds:
                player = await self.get_player(guild)
                if player.is_connected:
                    await player.teardown()
        self.client.reload_extension(f'bin.Cogs.{extension}')
        embed = discord.Embed(
            title=f'**:white_check_mark: Reloaded {extension}!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        
    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!reload <extension>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)        
        if isinstance(error, CommandInvokeError):
            embed = discord.Embed(
                title='**:x: An error occured whilst trying to reload extension.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            traceback.print_exc()
        if isinstance(error, NotOwner):
            embed = discord.Embed(
                title='**:x: This command is only available to the owner of the bot.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Init(client))
    for filename in os.listdir('./bin/Cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'bin.Cogs.{filename[:-3]}')
