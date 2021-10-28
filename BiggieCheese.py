import datetime
LAUNCH_TIME = datetime.datetime.utcnow()

if __name__ == '__main__':
    import discord
    import os
    import sqlite3
    import traceback

    from discord_components import *
    from dotenv import load_dotenv
    from discord.ext import commands
    from discord.ext.commands import *
    from pathlib import Path

    DIR = os.path.dirname(__file__)
    path = Path(__file__)
    oneup = path.parent.absolute()
    twoup = oneup.parent.absolute()
    databasepath = './bin/Databases/Prefixes.db'
    db = sqlite3.connect(os.path.join(DIR, databasepath))
    SQL = db.cursor()

    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    intents = discord.Intents.default()
    intents.members = True
        
    client = commands.Bot(
        command_prefix='bc!',
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name='bc!help'
        ),
        intents = intents,
        help_command=None,
        case_insensitive=True
    )
    DiscordComponents(client)

    @client.event
    async def on_message(message):
        try:
            SQL.execute(f'select Prefixes from Prefixes where User_ID="{message.author.id}"')
            prefixes = SQL.fetchone()
            prefixlist = prefixes[0].split(', ')
            prefixlist.append('bc!')
        except:
            prefixlist = ['bc!']
        for entry in prefixlist:
            if message.content.lower().startswith(entry.lower()):
                withoutprefix = message.content[len(entry):]
                while withoutprefix.startswith(' '):
                    withoutprefix = withoutprefix.replace(' ', '', 1)
                message.content = 'bc!' + withoutprefix
        await client.process_commands(message)

    @client.command()
    @commands.is_owner()
    async def init(ctx):
        client.load_extension('Init')
        embed = discord.Embed(
            title=f'**:white_check_mark: Initialized!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @init.error
    async def init_error(ctx, error):
        if isinstance(error, CommandInvokeError):
            embed = discord.Embed(
                title='**:x: An error occured whilst trying to initialize.**',
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

    @client.command()
    @commands.is_owner()
    async def deinit(ctx):
        client.unload_extension('Init')
        embed = discord.Embed(
            title=f'**:white_check_mark: Deinitialized!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @deinit.error
    async def deinit_error(ctx, error):
        if isinstance(error, CommandInvokeError):
            embed = discord.Embed(
                title='**:x: An error occured whilst trying to deinitialize.**',
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

    @client.command()
    @commands.is_owner()
    async def reinit(ctx):
        client.reload_extension('Init')
        embed = discord.Embed(
            title=f'**:white_check_mark: Reinitialized!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @reinit.error
    async def reinit_error(ctx, error):
        if isinstance(error, CommandInvokeError):
            embed = discord.Embed(
                title='**:x: An error occured whilst trying to reinitialize.**',
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

    client.load_extension('Init')
            
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            embed = discord.Embed(
                title='**:x: This command does not exist.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    client.run(TOKEN)