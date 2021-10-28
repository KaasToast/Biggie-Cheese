import discord
import datetime
import sqlite3
import os
import asyncio
import googletrans
import random
import re

from humanfriendly import format_timespan
from BiggieCheese import LAUNCH_TIME
from discord_components import *
from iso_language_codes import *
from discord.ext import commands
from discord.ext.commands import *
from pathlib import Path

DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()
threeup = twoup.parent.absolute()
databasepath = f'{twoup}/Databases/Welcomes.db'
db = sqlite3.connect(os.path.join(DIR, databasepath))
SQL = db.cursor()
SQL.execute('create table if not exists Welcomes('
                    '"Server_ID" INTEGER, '
                    '"Channel_ID" INTEGER, '
                    '"Message" TEXT'
                    ')')
databasepath2 = f'{twoup}/Databases/Prefixes.db'
db2 = sqlite3.connect(os.path.join(DIR, databasepath2))
SQL2 = db2.cursor()
SQL2.execute('create table if not exists Prefixes('
                    '"User_ID" INTEGER, '
                    '"Prefixes" TEXT'
                    ')')
databasepath3 = f'{twoup}/Databases/Logging.db'
db3 = sqlite3.connect(os.path.join(DIR, databasepath3))
SQL3 = db3.cursor()
SQL3.execute('create table if not exists Logging('
                    '"Server_ID" INTEGER, '
                    '"ChatLog" TEXT, '
                    '"ModLog" TEXT, '
                    '"JlLog" TEXT, '
                    '"VcLog" TEXT'
                    ')')
databasepath4 = f'{twoup}/Databases/Reminders.db'
db4 = sqlite3.connect(os.path.join(DIR, databasepath4))
SQL4 = db4.cursor()
SQL4.execute('create table if not exists Reminders('
                    '"User_ID" INTEGER, '
                    '"Reason" TEXT, '
                    '"Date" TEXT'
                    ')')
translator = googletrans.Translator()

class Utility(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def about(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - LAUNCH_TIME
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        count = 0
        for filename in os.listdir(f'{twoup}/Cogs'):
            if filename.endswith('.py'):
                count += 1
        def getfiles(dirname):
            allfiles = []
            for entry in os.listdir(dirname):
                fullpath = os.path.join(dirname, entry)
                if os.path.isdir(fullpath):
                    allfiles = allfiles + getfiles(fullpath)
                else:
                    if fullpath.endswith('.py'):
                        allfiles.append(fullpath)
                    else:
                        pass
            return allfiles
        linecount = 0
        commandcount = 0
        for path in getfiles(threeup):
            file = open(path, 'r', encoding='utf8')
            for line in file:
                if 'if cmd.lower() ==' in line:
                    commandcount += 1
                linecount += 1
            file.close()
        charcount = 0
        for path in getfiles(threeup):
            file = open(path, 'r', encoding='utf8')
            data = file.read()
            charcount += len(data)
        embed = discord.Embed(
            title='**About**',
            description=f'Characters in code: {charcount:,}\nCogs: {count:,}\nCommands: {commandcount:,}\nCreator: KaasToast#6969\nCreation date: 07/03/2021\nLanguage: Python\nLines of code: {linecount:,}\nTime since last downtime: {days} days {hours} hours {minutes} minutes {seconds} seconds',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.command()
    async def help(self, ctx, cmd = None):
        if cmd is None:
            title = ['**:tools: Moderation**',
                     '**:upside_down: Fun**',
                     '**:hammer: Utility**',
                     '**:musical_note: Music**',
                     '**:moneybag: Economics**']
            description = ['`ban` `clear` `clearwarns` `kick` `lock` `mute` `mutedrole` `tempban` `tempmute` `unban` `unlock` `unmute` `warn` `warns`\n\nUse bc!help [command] to get info on a specific command.\nUse bc!support to get an invite link to the official support server.',
                           '`biggiecheese` `divorce` `editsnipe` `horny` `jail` `marry` `marriage` `meme` `poll` `ship` `snipe` `topic` `wanted`\n\nUse bc!help [command] to get info on a specific command.\nUse bc!support to get an invite link to the official support server.',
                           '`about` `addprefix` `avatar` `calculator` `help` `invite` `logging` `membercount` `ping` `prefixes` `remind` `removeprefix` `servercount` `support` `translate` `uptime` `welcome` `whois`\n\nUse bc!help [command] to get info on a specific command.\nUse bc!support to get an invite link to the official support server.',
                           '`dj` `djonly` `join` `jump` `leave` `loop` `loopqueue` `makedj` `move` `nowplaying` `pause` `play` `playnext` `playnow` `remove` `shuffle` `skip` `stop` `queue`\n\nUse bc!help [command] to get info on a specific command.\nUse bc!support to get an invite link to the official support server.',
                           '`balance` `daily` `deposit` `give` `top` `vote` `withdraw` `work`\n\nUse bc!help [command] to get info on a specific command.\nUse bc!support to get an invite link to the official support server.']            
            pages = 5
            cur_page = 1
            seed = random.randint(1000000000,2000000000)
            async def callback(interaction):
                nonlocal cur_page
                nonlocal seed
                if interaction.author == ctx.author and interaction.custom_id == f'next{seed}' and cur_page != pages and interaction.message == message:
                    await interaction.respond(type=6)
                    cur_page += 1
                    embed = discord.Embed(
                        title=f'{title[cur_page-1]}',
                        description=f'{description[cur_page-1]}',
                        color=(0xFFFF00)
                    )
                    embed.set_footer(
                        text=f'Page {cur_page}/{pages}',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await message.edit(embed = embed)
                elif interaction.author == ctx.author and interaction.custom_id == f'previous{seed}' and cur_page > 1 and interaction.message == message:
                    await interaction.respond(type=6)
                    cur_page -= 1
                    embed = discord.Embed(
                        title=f'{title[cur_page-1]}',
                        description=f'{description[cur_page-1]}',
                        color=(0xFFFF00)
                    )
                    embed.set_footer(
                        text=f'Page {cur_page}/{pages}',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await message.edit(embed = embed)
                else:
                    embed = discord.Embed(
                        title='**:x: You are not the invoker of this command.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await interaction.respond(embed=embed)
            embed = discord.Embed(
                title=f'{title[cur_page-1]}',
                description=f'{description[cur_page-1]}',
                color=(0xFFFF00)
            )
            embed.set_footer(
                text=f'Page {cur_page}/{pages}',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            message = await ctx.send(embed = embed,
                components=[
                    [
                        self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Previous', custom_id=f'previous{seed}'), callback),
                        self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Next', custom_id=f'next{seed}'), callback),
                    ]
                ]
            )

        if cmd.lower() == 'ban':
            embed = discord.Embed(
                title='**Ban**',
                description='**Description:**\nBan a user from the current server, requires ban permission.\n\n**Usage:**\nbc!ban <@user/id> [reason]\n\n**Examples:**\nbc!ban @KaasToast\nbc!ban @KaasToast for being an idiot\nbc!ban 349159433965928449\nbc!ban 349159433965928449 for being an asshole\n\n<> = required\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'clear' or cmd.lower() == 'purge':
            embed = discord.Embed(
                title='**Clear/Purge**',
                description='**Description:**\nDelete a certain amount of messages from the current channel.\n\n**Usage:**\nbc!clear <amount>\nbc!purge <amount>\n\n**Examples:**\nbc!clear 5\nbc!purge 200\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'clearwarns' or cmd.lower() == 'clearinfractions':
            embed = discord.Embed(
                title='**Clearwarns/Clearinfractions**',
                description='**Description:**\nDelete a users warns, requires kick permission.\n\n**Usage:**\nbc!clearwarns <@user/id>\nbc!clearinfractions <@user/id>\n\n**Examples:**\nbc!clearwarns @KaasToast\nbc!clearinfractions @KaasToast\nbc!clearwarns 349159433965928449\nbc!clearinfractions 349159433965928449\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'kick':
            embed = discord.Embed(
                title='**Kick**',
                description='**Description:**\nKick a user from the current server, requires kick permission.\n\n**Usage:**\nbc!kick <@user/id> [reason]\n\n**Examples:**\nbc!kick @KaasToast\nbc!kick @KaasToast for being an idiot\nbc!kick 349159433965928449\nbc!kick 349159433965928449 for being an asshole\n\n<> = required\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'lock':
            embed = discord.Embed(
                title='**Lock**',
                description='**Description:**\nLock the current channel, this prevents everyone except moderators from typing in the current channel, requires manage channels permission.\n\n**Usage:**\nbc!lock\n\n**Example:**\nbc!lock',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'mute':
            embed = discord.Embed(
                title='**Mute**',
                description='**Description:**\nMute a user from this server, this prevents them from typing anything in any channel and from talking in voice channels, requires kick permission.\n\n**Usage:**\nbc!mute <@user/id> [reason]\n\n**Examples:**\nbc!mute @KaasToast\nbc!mute @KaasToast for being an idiot\nbc!mute 349159433965928449\nbc!mute 349159433965928449 for being an asshole\n\n<> = required\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'mutedrole':
            embed = discord.Embed(
                title='**Mutedrole**',
                description='**Description:**\nCommand to set a mutedrole, requires manage roles permission.\n\n**Usage:**\nbc!mutedrole <create/remove>\n\n**Examples:**\nbc!mutedrole create\nbc!mutedrole remove\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'tempban':
            embed = discord.Embed(
                title='**Tempban**',
                description='**Description:**\nTemporarily ban someone from this server, requires ban permission.\n\n**Usage:**\nbc!tempban <@user/id> <duration> [reason]\n\n**Examples:**\nbc!tempban @KaasToast 10s **|** (10 seconds)\nbc!tempban @KaasToast 10m for being an idiot **|** (10 minutes)\nbc!tempban 349159433965928449 10d12h30m5s **|** (10 days, 12 hours, 30 minutes and 5 seconds)\nbc!tempban 349159433965928449 2w20d5h30m10s for being an asshole **|** (2 weeks, 20 days, 5 hours, 30 minutes and 10 seconds)\n\n<> = required\n[] = optional\n\ns = seconds\nm = minutes\nh = hours\nd = days\nw = weeks',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'tempmute':
            embed = discord.Embed(
                title='**Tempmute**',
                description='**Description:**\nTemporarily mute someone from this server, requires kick permission.\n\n**Usage:**\nbc!tempmute <@user/id> <duration> [reason]\n\n**Examples:**\nbc!tempmute @KaasToast 10s **|** (10 seconds)\nbc!tempmute @KaasToast 10m for being an idiot **|** (10 minutes)\nbc!tempmute 349159433965928449 10d12h30m5s **|** (10 days, 12 hours, 30 minutes and 5 seconds)\nbc!tempmute 349159433965928449 2w20d5h30m10s for being an asshole **|** (2 weeks, 20 days, 5 hours, 30 minutes and 10 seconds)\n\n<> = required\n[] = optional\n\ns = seconds\nm = minutes\nh = hours\nd = days\nw = weeks',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'unban':
            embed = discord.Embed(
                title='**Unban**',
                description='**Description:**\nUnban a banned user from this server, requires ban permission.\n\n**Usage:**\nbc!unban <id>\n\n**Example:**\nbc!unban 349159433965928449\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'unlock':
            embed = discord.Embed(
                title='**Unlock**',
                description='**Description:**\nUnlock a previously locked channel, requires manage channels permission.\n\n**Usage:**\nbc!unlock\n\n**Example:**\nbc!unlock',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'unmute':
            embed = discord.Embed(
                title='**Umute**',
                description='**Description:**\nUnmute a muted user from this server, requires kick permission.\n\n**Usage:**\nbc!unmute <@user/id>\n\n**Examples:**\nbc!unmute @KaasToast\nbc!unmute 349159433965928449\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'warn':
            embed = discord.Embed(
                title='**Warn**',
                description='**Description:**\nWarn a user from this server, requires kick permission.\n\n**Usage:**\nbc!warn <@user/id> [reason]\n\n**Examples:**\nbc!warn @KaasToast\nbc!warn @KaasToast for being an idiot\nbc!warn 349159433965928449\nbc!warn 349159433965928449 for being an asshole\n\n<> = required\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'warns' or cmd.lower() == 'infractions':
            embed = discord.Embed(
                title='**Warns/Infractions**',
                description='**Description:**\nDisplay a users warn history.\n\n**Usage:**\nbc!warns <@user/id>\nbc!infractions <@user/id>\n\n**Examples:**\nbc!warns @KaasToast\nbc!infractions @KaasToast\nbc!warns 349159433965928449\nbc!infractions 349159433965928449\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'biggiecheese' or cmd.lower() == 'bc':
            embed = discord.Embed(
                title='**Biggiecheese/Bc**',
                description='**Description:**\nLiterally send a picture of the one and only biggie cheese!\n\n**Usage:**\nbc!biggiecheese\nbc!bc\n\n**Examples:**\nbc!biggiecheese\nbc!bc',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'divorce':
            embed = discord.Embed(
                title='**Divorce**',
                description='**Description:**\nDivorce the one you are married to.\n\n**Usage:**\nbc!divorce\n\n**Example:**\nbc!divorce',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'editsnipe' or cmd.lower() == 'esnipe':
            embed = discord.Embed(
                title='**Editsnipe/Esnipe**',
                description='**Description:**\nSnipe a message when someone edits it.\n\n**Usage:**\nbc!editsnipe\nbc!esnipe\n\n**Examples:**\nbc!editsnipe\nbc!esnipe',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'horny':
            embed = discord.Embed(
                title='**Horny**',
                description='**Description:**\nShows how horny you are or how horny someone else is.\n\n**Usage:**\nbc!horny [@user/id]\n\n**Examples:**\nbc!horny\nbc!horny @KaasToast\nbc!horny 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return        
        
        if cmd.lower() == 'jail':
            embed = discord.Embed(
                title='**Jail**',
                description='**Description:**\nPlace yourself or someone else in jail.\n\n**Usage:**\nbc!jail [@user/id]\n\n**Examples:**\nbc!jail\nbc!jail @KaasToast\nbc!jail 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'marry' or cmd.lower() == 'propose':
            embed = discord.Embed(
                title='**Marry/Propose**',
                description='**Description:**\nAsk someone to marry you.\n\n**Usage:**\nbc!marry <@user/id>\nbc!propose <@user/id>\n\n**Examples:**\nbc!marry @KaasToast\nbc!marry 349159433965928449\nbc!propose @KaasToast\nbc!propose 349159433965928449\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'marriage':
            embed = discord.Embed(
                title='**Marriage**',
                description='**Description:**\nShow your or someone elses current marriage status.\n\n**Usage:**\nbc!marriage [@user/id]\n\n**Examples:**\nbc!marriage\nbc!marriage @KaasToast\nbc!marriage 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'meme':
            embed = discord.Embed(
                title='**Meme**',
                description='**Description:**\nSend a random meme.\n\n**Usage:**\nbc!meme\n\n**Example:**\nbc!meme',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'poll':
            embed = discord.Embed(
                title='**Poll**',
                description='**Description:**\nCreate a poll.\n\n**Usage:**\nbc!poll <question>\n\n**Example:**\nbc!poll should we praise biggie cheese?\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'ship':
            embed = discord.Embed(
                title='**Ship**',
                description='**Description:**\nShip yourself with someone or 2 people with eachother.\n\n**Usage:**\nbc!ship [@user1/id1] <@user2/id2>\n\n**Examples:**\nbc!ship @Biggie Cheese\nbc!ship @KaasToast @Biggie Cheese\nbc!ship 818200924476014592\nbc!ship 349159433965928449 818200924476014592\n\n<> = required\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'snipe':
            embed = discord.Embed(
                title='**Snipe**',
                description='**Description:**\nSnipe a message when someone deletes it.\n\n**Usage:**\nbc!snipe\n\n**Example:**\nbc!snipe',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'topic':
            embed = discord.Embed(
                title='**Topic**',
                description='**Description:**\nSend a random topic question.\n\n**Usage:**\nbc!topic\n\n**Example:**\nbc!topic',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'translate':
            embed = discord.Embed(
                title='**Translate**',
                description='**Description:**\nTranslate any message to any supported language.\n\n**Usage:**\nbc!translate <language> <message>\n\n**Examples:**\nbc!translate dutch hello\nbc!translate english goedendag\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'wanted':
            embed = discord.Embed(
                title='**Wanted**',
                description='**Description:**\nPlace yourself or someone else on a wanted paper.\n\n**Usage:**\nbc!wanted [@user/id]\n\n**Examples:**\nbc!wanted\nbc!wanted @KaasToast\nbc!wanted 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'avatar' or cmd.lower() == 'av':
            embed = discord.Embed(
                title='**Avatar/Av**',
                description='**Description:**\nGet your or someone elses profile picture.\n\n**Usage:**\nbc!avatar [@user/id]\nbc!av [@user/id]\n\n**Examples:**\nbc!avatar\nbc!avatar @KaasToast\nbc!avatar 349159433965928449\nbc!av\nbc!av @KaasToast\nbc!av 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'calculator':
            embed = discord.Embed(
                title='**Calculator**',
                description='**Description:**\nBrings out a calculator that let\'s you calculate your hard math questions.\n\n**Usage:**\nbc!calculator\n\n**Example:**\nbc!calculator',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'membercount' or cmd.lower() == 'mc':
            embed = discord.Embed(
                title='**Membercount/Mc**',
                description='**Description:**\nShow how many members current server has.\n\n**Usage:**\nbc!membercount\nbc!mc\n\n**Examples:**\nbc!membercount\nbc!mc',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'welcome':
            embed = discord.Embed(
                title='**Welcome**',
                description='**Description:**\nCreate or delete a welcoming channel where the bot will send a custom message everytime a new user joins. Requires manage server permission.\n\n**Usage:**\nbc!welcome\n\n**Example:**\nbc!welcome',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'whois':
            embed = discord.Embed(
                title='**Whois**',
                description='**Description:**\nGet various information about yourself or other members.\n\n**Usage:**\nbc!whois [@user/id]\n\n**Examples:**\nbc!whois\nbc!whois @KaasToast\nbc!whois 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'dj':
            embed = discord.Embed(
                title='**Dj**',
                description='**Description:**\nDisplay the current dj, bot must be connected to a voice channel.\n\n**Usage:**\nbc!dj\n\n**Example:**\nbc!dj',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'djonly':
            embed = discord.Embed(
                title='**Djonly**',
                description='**Description:**\nToggle djonly mode, when enabled only admins and the dj can use music commands.\n\n**Usage:**\nbc!djonly\n\n**Example:**\nbc!djonly',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'join' or cmd.lower() == 'connect':
            embed = discord.Embed(
                title='**Join/Connect**',
                description='**Description:**\nLet the bot join your voice channel to play music.\n\n**Usage:**\nbc!join\nbc!connect\n\n**Examples:**\nbc!join\nbc!connect',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'jump':
            embed = discord.Embed(
                title='**Jump**',
                description='**Description:**\nJump to a position in the queue.\n\n**Usage:**\nbc!jump <number>\n\n**Examples:**\nbc!jump 5\nbc!jump 100\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'leave' or cmd.lower() == 'disconnect' or cmd.lower() == 'dc':
            embed = discord.Embed(
                title='**Leave/Disconnect/Dc**',
                description='**Description:**\nDisconnects the bot from your current voice channel if it\'s connected, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!leave\nbc!disconnect\nbc!dc\n\n**Examples:**\nbc!leave\nbc!disconnect\nbc!dc',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'loop' or cmd.lower() == 'repeat':
            embed = discord.Embed(
                title='**Loop/Repeat**',
                description='**Description:**\nLoop the currently playing song or disable looping if it\'s already enabled, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!loop\nbc!repeat\n\n**Examples:**\nbc!loop\nbc!repeat',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'loopqueue' or cmd.lower() == 'repeatqueue':
            embed = discord.Embed(
                title='**Loopqueue/Repeatqueue**',
                description='**Description:**\nLoop the entire queue or disable looping if it\'s already enabled, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!loopqueue\nbc!repeatqueue\n\n**Examples:**\nbc!loopqueue\nbc!repeatqueue',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'makedj':
            embed = discord.Embed(
                title='**Makedj**',
                description='**Description:**\nMake someone else dj if you\'re the dj.\n\n**Usage:**\nbc!makedj <@user/id>\n\n**Examples:**\nbc!makedj @KaasToast\nbc!makedj 349159433965928449\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'move':
            embed = discord.Embed(
                title='**Move**',
                description='**Description:**\nMove a song to a specific position in the queue, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!move <old-position> <new-position>\n\n**Examples:**\nbc!move 1 30\nbc!move 400 3\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'nowplaying' or cmd.lower() == 'np':
            embed = discord.Embed(
                title='**Nowplaying/Np**',
                description='**Description:**\nShow the currenty playing song.\n\n**Usage:**\nbc!nowplaying\nbc!np\n\n**Examples:**\nbc!nowplaying\nbc!np',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'pause':
            embed = discord.Embed(
                title='**Pause**',
                description='**Description:**\nPause the currently playing song, you must be in the same voice channel as the bot.\n\n**Usage**:\nbc!pause\n\n**Example:**\nbc!pause',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'play' or cmd.lower() == 'p':
            embed = discord.Embed(
                title='**Play/P**',
                description='**Description:**\nPlay a song from YouTube, Spotify, any http stream or a local file into your voice channel or resume paused music, bot must be connected to the voice channel using bc!join first and you must be in the same voice channel as the bot. If you want to play a local file use bc!play with an attached file, supported filetypes are: webm, mkv, ogg, mov, mp4, aac, flac, mp3 and wav\n\n**Usage:**\nbc!play\nbc!play [url/search]\n\n**Examples:**\nbc!play\nbc!play https://www.youtube.com/watch?v=dQw4w9WgXcQ\nbc!play https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=8705f44d07d24dff\nbc!play epic music\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'playnext' or cmd.lower() == 'pnext' or cmd.lower() == 'playtop' or cmd.lower() == 'ptop':
            embed = discord.Embed(
                title='**Playnext/Pnext/Playtop/Ptop**',
                description='**Description:**\nPlay a song from YouTube, Spotify, any http stream or local file into your voice channel at the top of the queue, bot must be connected to the voice channel using bc!join first and you must be in the same voice channel as the bot. If you want to play a local file use bc!playnext with an attached file, supported filetypes are: webm, mkv, ogg, mov, mp4, aac, flac, mp3 and wav\n\n**Usage:**\nbc!playnext [url/search]\nbc!pnext [url/search]\nbc!playtop [url/search]\nbc!ptop [url/search]\n\n**Examples:**\nbc!playnext https://www.youtube.com/watch?v=dQw4w9WgXcQ\nbc!playnext epic music\nbc!playtop https://www.youtube.com/watch?v=dQw4w9WgXcQ\nbc!playtop epic music\nbc!pnext https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=ec20ddb6b5944072\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'playnow' or cmd.lower() == 'pnow':
            embed = discord.Embed(
                title='**Playnow/Pnow**',
                description='**Description:**\nPlay a song from YouTube, Spotify, any http stream or local file into your voice channel at the top of the queue and skips current song, bot must be connected to the voice channel using bc!join first and you must be in the same voice channel as the bot. If you want to play a local file use bc!playnow with an attached file, supported filetypes are: webm, mkv, ogg, mov, mp4, aac, flac, mp3 and wav\n\n**Usage:**\nbc!playnow [url/search]\nbc!pnow [url/search]\n\n**Examples:**\nbc!playnow https://www.youtube.com/watch?v=dQw4w9WgXcQ\nbc!playnow epic music\nbc!pnow https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=eb6cf98eb97a44da\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'remove':
            embed = discord.Embed(
                title='**Remove**',
                description='**Description:**\nRemove a song from the queue, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!remove <position>\n\n**Examples:**\nbc!remove 3\nbc!remove 200\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'shuffle':
            embed = discord.Embed(
                title='**Shuffle**',
                description='**Description:**\nShuffle the queue.\n\n**Usage:**bc!shuffle\n\n**Example:**\nbc!shuffle',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'skip' or cmd.lower() == 'next':
            embed = discord.Embed(
                title='**Skip/Next**',
                description='**Description:**\nSkip a number of tracks in the queue, defaults to 1, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!skip [amount]\nbc!next [amount]\n\n**Examples:**\nbc!skip\nbc!next\nbc!skip 2\nbc!next 100\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'stop':
            embed = discord.Embed(
                title='**Stop**',
                description='**Description:**\nStop playing music and clear the queue, you must be in the same voice channel as the bot.\n\n**Usage:**\nbc!stop\n\n**Example:**\nbc!stop',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'queue' or cmd.lower() == 'q':
            embed = discord.Embed(
                title='**Queue/Q**',
                description='**Description:**\nDisplay the queue.\n\n**Usage:**\nbc!queue\n\n**Example:**\nbc!queue',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'balance' or cmd.lower() == 'bal':
            embed = discord.Embed(
                title='**Balance/Bal**',
                description='**Description:**\nShow your own or someone elses balance.\n\n**Usage:**\nbc!balance [@user/id]\nbc!bal [@user/id]\n\n**Examples:**\nbc!balance\nbc!balance @KaasToast\nbc!balance 349159433965928449\nbc!bal\nbc!bal @KaasToast\nbc!bal 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'give' or cmd.lower() == 'pay':
            embed = discord.Embed(
                title='**Give/Pay**',
                description='**Description:**\nGive someone money.\n\n**Usage:**\nbc!give <@user/id> <amount>\n\n**Examples:**\nbc!give @KaasToast 100\nbc!give 349159433965928449 100\nbc!pay @KaasToast 100\nbc!pay 349159433965928449 100\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'top':
            embed = discord.Embed(
                title='**Top**',
                description='**Description:**\nShow different types of economy-related leaderboards.\n\n**Usage:**\nbc!top\n\n**Example:**\nbc!leaderboard',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'vote':
            embed = discord.Embed(
                title='**Vote**',
                description='**Description:**\nGet a link to vote for the bot, you will receive a stacking reward for each time you vote.\n\n**Usage:**\nbc!vote\n\n**Example:**\nbc!vote',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'about':
            embed = discord.Embed(
                title='**About**',
                description='**Description:**\nShows information about Biggie Cheese.\n\n**Usage:**\nbc!about\n\n**Example:**\nbc!about',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'addprefix':
            embed = discord.Embed(
                title='**Addprefix**',
                description='**Description:**\nAdd a custom prefixes to your custom prefixes, you can have up to 10 custom prefixes.\n\n**Usage:**\nbc!addprefix <prefix>\n\n**Example:**\nbc!addprefix epic custom prefix\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'help':
            embed = discord.Embed(
                title='**Help**',
                description='**Description:**\nShows all available commands or information about a specific command.\n\n**Usage:**\nbc!help [command]\n\n**Examples:**\nbc!help\nbc!help ban\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'invite':
            embed = discord.Embed(
                title='**Invite**',
                description='**Description:**\nSends an invite link so you can invite Biggie Cheese to your own server.\n\n**Usage:**\nbc!invite\n\n**Examples:**\nbc!invite',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'logging':
            embed = discord.Embed(
                title='**Logging**',
                description='**Description:**\nCommand for showing logging channel status as well as info on how to set it up. Requires manage server permission\n\n**Usage:**\nbc!logging\n\n**Example:**\nbc!logging',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'ping':
            embed = discord.Embed(
                title='**Ping**',
                description='**Description:**\nShows the bot latency\n\n**Usage:**\nbc!ping\n\n**Example:**\nbc!ping',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'prefixes':
            embed = discord.Embed(
                title='**Prefixes**',
                description='**Description:**\nList your or someone elses custom prefixes, you can create up to 10.\n\n**Usage:**\nbc!prefixes [@user/id]\n\n**Examples:**\n\nbc!prefixes\nbc!prefixes @KaasToast\nbc!prefixes 349159433965928449\n\n[] = optional',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'remind':
            embed = discord.Embed(
                title='**Remind**',
                description='**Description:**\nSet a reminder.\n\n**Usage:**\nbc!remind <duration> <message>\n\n**Examples:**\nbc!remind 10s wake up **|** (10 seconds)\nbc!remind 10m wake up again **|** (10 minutes)\nbc!remind 10d12h30m5s listen to biggie cheese **|** (10 days, 12 hours, 30 minutes and 5 seconds)\nbc!remind 2w20d5h30m10s listen to biggie cheese again **|** (2 weeks, 20 days, 5 hours, 30 minutes and 10 seconds)\n\n<> = required\n[] = optional\n\ns = seconds\nm = minutes\nh = hours\nd = days\nw = weeks',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'removeprefix':
            embed = discord.Embed(
                title='**Removeprefix**',
                description='**Description:**\nRemove a custom prefix from your custom prefixes\n\n**Usage:**\nbc!removeprefix <prefix>\n\n**Example:**\nbc!removeprefix stinkyprefix\n\n<> = required',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'servercount' or cmd.lower() == 'sc':
            embed = discord.Embed(
                title='**Servercount/Sc**',
                description='**Description:**\nShows how many servers the bot is in and how many users it\'s serving.\n\n**Usage:**\nbc!servercount\nbc!sc\n\n**Examples:**\nbc!servercount\nbc!sc',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return

        if cmd.lower() == 'support':
            embed = discord.Embed(
                title='**Support**',
                description='**Description:**\nSends an invite link to the official Biggie Cheese support server.\n\n**Usage:**\nbc!support\n\n**Example:**\nbc!support',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        
        if cmd.lower() == 'uptime':
            embed = discord.Embed(
                title='**Uptime**',
                description='**Description:**\nShows how long the bot is online.\n\n**Usage:**\nbc!uptime\n\n**Example:**\nbc!uptime',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return   

        else:
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
            return

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(
            title='**To invite me to join your server use the following link:**',
            description='[Invite](https://biggiecheese.xyz/invite)',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            title=f'**Pong! `{round(self.client.latency * 1000)}ms.`**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.command(aliases=['sc'])
    async def servercount(self, ctx):
        usercount = 0        
        for s in self.client.guilds:
            usercount += len(s.members)        
        embed = discord.Embed(
            title=f'**Biggie Cheese is currently in {str(len(self.client.guilds))} servers serving {usercount} users.**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.command()
    async def prefixes(self, ctx, member : discord.Member=None):
        if member is None:
            member_id = ctx.author.id
            member_name = ctx.author.name
        else:
            member_id = member.id
            member_name = member.name
        SQL2.execute(f'select Prefixes from Prefixes where User_ID="{member_id}"')
        table_exists = SQL2.fetchone()
        if table_exists is None:
            if member is None:
                embed = discord.Embed(
                    title='**:x: You don\'t have any custom prefixes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**:x: This user doesn\'t have any custom prefixes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            SQL2.execute(f'select Prefixes from Prefixes where User_ID="{member_id}"')
            prefixes = SQL2.fetchone()
            prefixlist = prefixes[0].split(', ')
            embed = discord.Embed(
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(
                name=f'**{member_name}\'s custom prefixes:\n**',
                value='\n'.join(prefixlist)
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def addprefix(self, ctx, *, prefix : str):
        author_id = ctx.message.author.id
        try:
            prefix.replace(',', '')
        except:
            pass
        prefix = prefix.lower()
        if len(prefix) >= 32:
            embed = discord.Embed(
                title='**:x: Custom prefix cannot be longer than 32 characters.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if len(prefix) == 0:
            embed = discord.Embed(
                title='**:x: Use: bc!addprefix <prefix> or bc!help addprefix for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        SQL2.execute(f'select Prefixes from Prefixes where User_ID="{author_id}"')
        table_exists = SQL2.fetchone()
        if table_exists is None:
            SQL2.execute(f'insert into Prefixes(User_ID, Prefixes) values(?,?)',
                        (author_id, prefix))
            db2.commit()
            embed = discord.Embed(
                title=f'**:white_check_mark: Added "{prefix}" to custom prefixes.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            SQL2.execute(f'select Prefixes from Prefixes where User_ID="{author_id}"')
            prefixes = SQL2.fetchone()
            prefixlist = prefixes[0].split(', ')
            if prefix in prefixlist:
                embed = discord.Embed(
                    title='**:x: You already have this custom prefix.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            if len(prefixlist) >= 10:
                embed = discord.Embed(
                    title='**:x: You already have 10 custom prefixes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                SQL2.execute(f'select Prefixes from Prefixes where User_ID="{author_id}"')
                prefixes = SQL2.fetchone()
                newprefixes = prefixes[0] + f', {prefix}'
                SQL2.execute(f"update Prefixes set Prefixes='{newprefixes}' where User_ID='{author_id}'")
                db2.commit()
                embed = discord.Embed(
                    title=f'**:white_check_mark: Added "{prefix}" to custom prefixes.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @addprefix.error
    async def addprefix_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!addprefix <prefix> or bc!help addprefix for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def removeprefix(self, ctx, *, prefix : str):
        author_id = ctx.message.author.id
        try:
            prefix.replace(',', '')
        except:
            pass
        prefix = prefix.lower()
        SQL2.execute(f'select Prefixes from Prefixes where User_ID="{author_id}"')
        table_exists = SQL2.fetchone()
        if table_exists is None:
            embed = discord.Embed(
                title='**:x: Prefix not found.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            SQL2.execute(f'select Prefixes from Prefixes where User_ID="{author_id}"')
            prefixes = SQL2.fetchone()
            prefixlist = prefixes[0].split(', ')
            try:
                prefixlist.remove(prefix)
            except:
                embed = discord.Embed(
                    title=f'**:x: Prefix not found.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            if len(prefixlist) == 0:
                SQL2.execute(f'delete from Prefixes where User_ID="{author_id}"')
                db2.commit()
            elif len(prefixlist) == 1:
                SQL2.execute(f'update Prefixes set Prefixes="{prefixlist[0]}" where User_ID="{author_id}"')
                db2.commit()
            else:
                commaseperated = ", ".join(prefixlist)
                SQL2.execute(f'update Prefixes set Prefixes="{commaseperated}" where User_ID="{author_id}"')
                db2.commit()
            embed = discord.Embed(
                title=f'**:white_check_mark: Removed "{prefix}" from custom prefixes.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @removeprefix.error
    async def removeprefix_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!removeprefix <prefix> or bc!help removeprefix for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def support(self, ctx):
        embed = discord.Embed(
            title='**To join the official Biggie Cheese support server use the following link:**',
            description='[Support](https://biggiecheese.xyz/support)',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.command()
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - LAUNCH_TIME
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(
            title='**Current uptime:**',
            description=f'**{days} days {hours} hours {minutes} minutes {seconds} seconds**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        
    @commands.command(aliases=['av'])
    async def avatar(self, ctx, member : discord.Member=None):
        if member is None:
            member = ctx.message.author
        embed = discord.Embed(
            title=f"{member.name}'s avatar:",
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_image(
            url=member.avatar_url_as(format='png')
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        
    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, MemberNotFound):
            embed = discord.Embed(
                title='**:x: User not found!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command(aliases = ['mc'])
    async def membercount(self, ctx):
        embed = discord.Embed(
            title='Total Members:',
            description=f'**{ctx.guild.member_count}**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.command()
    async def whois(self, ctx, member : discord.Member=None):
        if member is None:
            member = ctx.message.author        
        embed = discord.Embed(
            title='User information',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(
            url=member.avatar_url
        )
        embed.add_field(
            name='Name',
            value=str(member)
        )
        embed.add_field(
            name='ID',
            value=member.id
        )
        embed.add_field(
            name='Highest Role',
            value=member.top_role.mention
        )
        embed.add_field(
            name='Joined at',
            value=member.joined_at.strftime('%d/%m/%Y %H:%M:%S')
        )
        embed.add_field(
            name='Created at',
            value=member.created_at.strftime('%d/%m/%Y %H:%M:%S')
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        
    @whois.error
    async def whois_error(self, ctx, error):
        if isinstance(error, MemberNotFound):
            embed = discord.Embed(
                title='**:x: User not found!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    async def selectchannel(self, ctx):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.message.author
        try:
            answer = await self.client.wait_for('message', check=check, timeout=600)
        except asyncio.TimeoutError:
            return
        channel = answer.content
        if str(channel).lower() == 'stop':
            embed = discord.Embed(
                title='**Setup cancelled.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        elif channel.isdigit():
            try:
                channel = discord.utils.get(ctx.guild.channels, id=int(channel))
                embed = discord.Embed(
                    title=f'**:white_check_mark: Channel with name `{channel.name}` selected.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            except:
                embed = discord.Embed(
                    title='**:x: Invalid channel.**',
                    description='Try again or reply with `stop` to cancel at any time.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return 'Failed'
        else:
            try:
                channel = channel.replace('<', '')
                channel = channel.replace('>', '')
                channel = channel.replace('#', '')
                channel = discord.utils.get(ctx.guild.channels, id=int(channel))
                embed = discord.Embed(
                    title=f'**:white_check_mark: Channel with name `{channel.name}` selected.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            except:
                embed = discord.Embed(
                    title='**:x: Invalid channel.**',
                    description='Try again or reply with `stop` to cancel at any time.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return 'Failed'
        return channel

    async def selectmessage(self, ctx):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.message.author
        try:
            answer = await self.client.wait_for('message', check=check, timeout=600)
        except asyncio.TimeoutError:
            return
        message = answer.content
        if str(message).lower() == 'stop':
            embed = discord.Embed(
                title='**Setup cancelled.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        embed = discord.Embed(
            title='**Are you sure you want to select the welcome message:**',
            description=f'{message}\n\nReply with `yes` or `no` or reply with `stop` to cancel at any time.',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        def confirmcheck(m):
            return m.channel == ctx.channel and m.author == ctx.message.author
        try:
            answer2 = await self.client.wait_for('message', check=confirmcheck, timeout=600)
        except asyncio.TimeoutError:
            return
        confirmation = answer2.content
        if str(confirmation).lower() == 'stop':
            embed = discord.Embed(
                title='**Setup cancelled.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        elif str(confirmation).lower() == 'yes':
            return str(message)
        else:
            embed = discord.Embed(
                title='**Enter the text you want to send as a welcome message.**',
                description='Use `{mention}` to mention the joined member. Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return 'Failed'

    @commands.command()
    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        SQL.execute(f'select Channel_ID from Welcomes where Server_ID="{ctx.guild.id}"')
        table_exists = SQL.fetchone()
        if table_exists is not None:
            embed = discord.Embed(
                title='**Are you sure you want to remove the welcoming channel?**',
                description='Reply with `yes` or `no`',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.message.author
            try:
                answer = await self.client.wait_for('message', check=check, timeout=600)
            except asyncio.TimeoutError:
                return
            confirmation = answer.content
            if str(confirmation).lower() == 'yes':
                SQL.execute(f'delete from Welcomes where Server_ID="{ctx.guild.id}"')
                db.commit()
                embed = discord.Embed(
                    title='**:white_check_mark: Removed the welcoming channel.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**No changes were made.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title='**Enter the channel id or tag the channel you want to send the welcome messages.**',
                description='Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            selectedchannel = await self.selectchannel(ctx)
            if selectedchannel is None:
                return
            while selectedchannel == 'Failed':
                selectedchannel = await self.selectchannel(ctx)
                if selectedchannel is None:
                    return
            embed = discord.Embed(
                title='**Enter the text you want to send as a welcome message.**',
                description='Use `{mention}` to mention the joined member. Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            selectedtext = await self.selectmessage(ctx)
            if selectedtext is None:
                return
            while selectedtext == 'Failed':
                selectedtext = await self.selectmessage(ctx)
                if selectedtext is None:
                    return
            SQL.execute(f'insert into Welcomes(Server_ID, Channel_ID, Message) values(?,?,?)',
                        (ctx.guild.id, selectedchannel.id, selectedtext))
            db.commit()
            embed = discord.Embed(
                title='**:white_check_mark: Selected the text:**',
                description=f'{selectedtext}',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @welcome.error
    async def welcome_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(
                title='**:x: You do not have permission to execute that command!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MaxConcurrencyReached):
            embed = discord.Embed(
                title='**:x: A welcome channel setup is already running in this server.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        SQL.execute(f'select Channel_ID from Welcomes where Server_ID="{member.guild.id}"')
        channel_id = SQL.fetchone()
        if channel_id is None:
            return
        else:
            channel = self.client.get_channel(int(channel_id[0]))
            SQL.execute(f'select Message from Welcomes where Server_ID="{member.guild.id}"')
            message = SQL.fetchone()
            try:
                message = message[0].replace('{mention}', member.mention)
            except:
                message = message[0]
            await channel.send(message)

    @commands.command()
    async def translate(self, ctx, to_language, *, msg):
        try:
            translation = translator.translate(msg, dest=to_language)
            srclangname = language_name(translation.src)
            destlangname = language_name(translation.dest)
            embed = discord.Embed(
                title='**Translation**',
                description=f'**{srclangname}:**\n{translation.origin}\n\n**{destlangname}:**\n{translation.text}',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        except:
            embed = discord.Embed(
                title='**:x: This language is not supported.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @translate.error
    async def translate_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!translate <language> <message> or bc!help translate for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def calculator(self, ctx):
        seed = random.randint(1000000000,2000000000)
        string = '\>'
        async def callback(interaction):
            nonlocal seed
            nonlocal string
            if interaction.author == ctx.author and interaction.custom_id == f'7-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 7'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '7'
                else:
                    string += ' 7'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'8-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 8'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '8'
                else:
                    string += ' 8'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'9-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 9'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '9'
                else:
                    string += ' 9'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'⌫-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\>'
                elif len(string) == 2:
                    return
                elif not string[-1].isdigit():
                    string = string[:-2]
                else:
                    string = string[:-1]
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'C-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                string = '\>'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'4-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 4'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '4'
                else:
                    string += ' 4'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'5-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 5'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '5'
                else:
                    string += ' 5'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'6-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 6'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '6'
                else:
                    string += ' 6'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'*-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if len(string) == 2:
                    return
                elif string == 'Error':
                    string = '\>'
                elif string[-1].isdigit() or string[-1] == ')':
                    string += ' *'
                else:
                    return
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'/-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if len(string) == 2:
                    return
                elif string == 'Error':
                    string = '\>'
                elif string[-1].isdigit() or string[-1] == ')':
                    string += ' /'
                else:
                    return
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'1-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 1'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '1'
                else:
                    string += ' 1'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'2-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 2'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '2'
                else:
                    string += ' 2'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'3-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 3'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '3'
                else:
                    string += ' 3'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'+-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if len(string) == 2:
                    return
                elif string == 'Error':
                    string = '\>'
                elif string[-1].isdigit() or string[-1] == ')':
                    string += ' +'
                else:
                    return
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'--{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if len(string) == 2:
                    return
                elif string == 'Error':
                    string = '\>'
                elif string[-1].isdigit() or string[-1] == ')':
                    string += ' -'
                else:
                    return
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'.-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if len(string) == 2:
                    return
                elif string == 'Error':
                    string = '\>'
                elif string[-1].isdigit():
                    string += '.'
                else:
                    return
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'0-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> 0'
                elif string[-1].isdigit() or string[-1] == '(' or string[-1] == '.':
                    string += '0'
                else:
                    string += ' 0'
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'=-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                try:
                    answer = str(eval(string[2:]))
                    string = f'\> {answer}'
                    await message.edit(content=string)
                except:
                    string = 'Error'
                    await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f'(-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if string == 'Error':
                    string = '\> ('
                elif not string[-1].isdigit():
                    string += ' ('
                else:
                    return
                await message.edit(content=string)
            elif interaction.author == ctx.author and interaction.custom_id == f')-{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                if len(string) == 2:
                    return
                elif string == 'Error':
                    string = '\>'
                elif string[-1].isdigit():
                    string += ')'
                else:
                    return
                await message.edit(content=string)
            else:
                embed = discord.Embed(
                    title='**:x: You are not the invoker of this command.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await interaction.respond(embed=embed)
        message = await ctx.send(string,
            components=[
                [
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='7', custom_id=f'7-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='8', custom_id=f'8-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='9', custom_id=f'9-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='⌫', custom_id=f'⌫-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='C', custom_id=f'C-{seed}'), callback)
                ],
                [
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='4', custom_id=f'4-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='5', custom_id=f'5-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='6', custom_id=f'6-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='*', custom_id=f'*-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='/', custom_id=f'/-{seed}'), callback)
                ],
                [
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='1', custom_id=f'1-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='2', custom_id=f'2-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='3', custom_id=f'3-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='+', custom_id=f'+-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='-', custom_id=f'--{seed}'), callback)
                ],
                [
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='.', custom_id=f'.-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='0', custom_id=f'0-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='=', custom_id=f'=-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='(', custom_id=f'(-{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label=')', custom_id=f')-{seed}'), callback)
                ]
            ]
        )

    @commands.command()
    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @commands.has_permissions(manage_guild=True)
    async def chatlog(self, ctx):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{ctx.guild.id}"')
        table_exists = SQL3.fetchone()
        if table_exists is None:
            value = str(None)
            SQL3.execute('insert into Logging(Server_ID, ChatLog, ModLog, JlLog, VcLog) values(?,?,?,?,?)',
                            (ctx.guild.id, value, value, value, value))
            db3.commit()
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{ctx.guild.id}"')
        chatlog = SQL3.fetchone()
        if chatlog[0] == 'None':
            embed = discord.Embed(
                title='**Enter the channel id or tag the channel you want to send chat logs to.**',
                description='Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            selectedchannel = await self.selectchannel(ctx)
            if selectedchannel is None:
                return
            while selectedchannel == 'Failed':
                selectedchannel = await self.selectchannel(ctx)
                if selectedchannel is None:
                    return
            SQL3.execute(f'update Logging set ChatLog="{selectedchannel.id}" where Server_ID="{ctx.guild.id}"')
            db3.commit()
        else:
            embed = discord.Embed(
                title='**Are you sure you want to remove the chat log channel?**',
                description='Reply with `yes` or `no`',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.message.author
            try:
                answer = await self.client.wait_for('message', check=check, timeout=600)
            except asyncio.TimeoutError:
                return
            confirmation = answer.content
            if str(confirmation).lower() == 'yes':
                SQL3.execute(f'update Logging set ChatLog="{str(None)}" where Server_ID="{ctx.guild.id}"')
                db3.commit()
                embed = discord.Embed(
                    title='**:white_check_mark: Removed chat log channel.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**No changes were made.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @chatlog.error
    async def chatlog_error(self, ctx, error):
        if isinstance(error, MaxConcurrencyReached):
            embed = discord.Embed(
                title='**:x: A chat logging setup is already running in this server.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(
                title='**:x: You do not have permission to execute that command!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @commands.has_permissions(manage_guild=True)
    async def modlog(self, ctx):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{ctx.guild.id}"')
        table_exists = SQL3.fetchone()
        if table_exists is None:
            value = str(None)
            SQL3.execute('insert into Logging(Server_ID, ChatLog, ModLog, JlLog, VcLog) values(?,?,?,?,?)',
                            (ctx.guild.id, value, value, value, value))
            db3.commit()
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog[0] == 'None':
            embed = discord.Embed(
                title='**Enter the channel id or tag the channel you want to send mod logs to.**',
                description='Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            selectedchannel = await self.selectchannel(ctx)
            if selectedchannel is None:
                return
            while selectedchannel == 'Failed':
                selectedchannel = await self.selectchannel(ctx)
                if selectedchannel is None:
                    return
            SQL3.execute(f'update Logging set ModLog="{selectedchannel.id}" where Server_ID="{ctx.guild.id}"')
            db3.commit()
        else:
            embed = discord.Embed(
                title='**Are you sure you want to remove the mod log channel?**',
                description='Reply with `yes` or `no`',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.message.author
            try:
                answer = await self.client.wait_for('message', check=check, timeout=600)
            except asyncio.TimeoutError:
                return
            confirmation = answer.content
            if str(confirmation).lower() == 'yes':
                SQL3.execute(f'update Logging set ModLog="{str(None)}" where Server_ID="{ctx.guild.id}"')
                db3.commit()
                embed = discord.Embed(
                    title='**:white_check_mark: Removed mod log channel.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**No changes were made.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @modlog.error
    async def modlog_error(self, ctx, error):
        if isinstance(error, MaxConcurrencyReached):
            embed = discord.Embed(
                title='**:x: A mod logging setup is already running in this server.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(
                title='**:x: You do not have permission to execute that command!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
    
    @commands.command()
    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @commands.has_permissions(manage_guild=True)
    async def joinleavelog(self, ctx):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{ctx.guild.id}"')
        table_exists = SQL3.fetchone()
        if table_exists is None:
            value = str(None)
            SQL3.execute('insert into Logging(Server_ID, ChatLog, ModLog, JlLog, VcLog) values(?,?,?,?,?)',
                            (ctx.guild.id, value, value, value, value))
            db3.commit()
        SQL3.execute(f'select JlLog from Logging where Server_ID="{ctx.guild.id}"')
        jllog = SQL3.fetchone()
        if jllog[0] == 'None':
            embed = discord.Embed(
                title='**Enter the channel id or tag the channel you want to send join/leave logs to.**',
                description='Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            selectedchannel = await self.selectchannel(ctx)
            if selectedchannel is None:
                return
            while selectedchannel == 'Failed':
                selectedchannel = await self.selectchannel(ctx)
                if selectedchannel is None:
                    return
            SQL3.execute(f'update Logging set JlLog="{selectedchannel.id}" where Server_ID="{ctx.guild.id}"')
            db3.commit()
        else:
            embed = discord.Embed(
                title='**Are you sure you want to remove the join/leave log channel?**',
                description='Reply with `yes` or `no`',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.message.author
            try:
                answer = await self.client.wait_for('message', check=check, timeout=600)
            except asyncio.TimeoutError:
                return
            confirmation = answer.content
            if str(confirmation).lower() == 'yes':
                SQL3.execute(f'update Logging set JlLog="{str(None)}" where Server_ID="{ctx.guild.id}"')
                db3.commit()
                embed = discord.Embed(
                    title='**:white_check_mark: Removed join/leave log channel.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**No changes were made.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @joinleavelog.error
    async def joinleavelog_error(self, ctx, error):
        if isinstance(error, MaxConcurrencyReached):
            embed = discord.Embed(
                title='**:x: A join/leave logging setup is already running in this server.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(
                title='**:x: You do not have permission to execute that command!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @commands.has_permissions(manage_guild=True)
    async def vclog(self, ctx):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{ctx.guild.id}"')
        table_exists = SQL3.fetchone()
        if table_exists is None:
            value = str(None)
            SQL3.execute('insert into Logging(Server_ID, ChatLog, ModLog, JlLog, VcLog) values(?,?,?,?,?)',
                            (ctx.guild.id, value, value, value, value))
            db3.commit()
        SQL3.execute(f'select VcLog from Logging where Server_ID="{ctx.guild.id}"')
        vclog = SQL3.fetchone()
        if vclog[0] == 'None':
            embed = discord.Embed(
                title='**Enter the channel id or tag the channel you want to send voice channel logs to.**',
                description='Reply with `stop` to cancel at any time.',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            selectedchannel = await self.selectchannel(ctx)
            if selectedchannel is None:
                return
            while selectedchannel == 'Failed':
                selectedchannel = await self.selectchannel(ctx)
                if selectedchannel is None:
                    return
            SQL3.execute(f'update Logging set VcLog="{selectedchannel.id}" where Server_ID="{ctx.guild.id}"')
            db3.commit()
        else:
            embed = discord.Embed(
                title='**Are you sure you want to remove the voice channel log channel?**',
                description='Reply with `yes` or `no`',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.message.author
            try:
                answer = await self.client.wait_for('message', check=check, timeout=600)
            except asyncio.TimeoutError:
                return
            confirmation = answer.content
            if str(confirmation).lower() == 'yes':
                SQL3.execute(f'update Logging set VcLog="{str(None)}" where Server_ID="{ctx.guild.id}"')
                db3.commit()
                embed = discord.Embed(
                    title='**:white_check_mark: Removed voice channel log channel.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title='**No changes were made.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @vclog.error
    async def vclog_error(self, ctx, error):
        if isinstance(error, MaxConcurrencyReached):
            embed = discord.Embed(
                title='**:x: A voice channel logging setup is already running in this server.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, MissingPermissions):
            embed = discord.Embed(
                title='**:x: You do not have permission to execute that command!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{ctx.guild.id}"')
        chatlog = SQL3.fetchone()
        if not chatlog:
            embed = discord.Embed(
                title='Logging',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            embed.add_field(
                name='Type',
                value='Chat-logging\nMod-logging\nJoin/leave-logging\nVoice-logging'
            )
            embed.add_field(
                name='Command',
                value='bc!chatlog\nbc!modlog\nbc!joinleavelog\nbc!vclog'
            )
            embed.add_field(
                name='Channel',
                value='Unset\nUnset\nUnset\nUnset'
            )
            await ctx.send(embed = embed)
            return
        elif chatlog[0] == 'None':
            chatlog = 'Unset'
        else:
            chatlog = self.client.get_channel(int(chatlog[0])).mention
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog[0] == 'None':
            modlog = 'Unset'
        else:
            modlog = self.client.get_channel(int(modlog[0])).mention
        SQL3.execute(f'select JlLog from Logging where Server_ID="{ctx.guild.id}"')
        jllog = SQL3.fetchone()
        if jllog[0] == 'None':
            jllog = 'Unset'
        else:
            jllog = self.client.get_channel(int(jllog[0])).mention
        SQL3.execute(f'select VcLog from Logging where Server_ID="{ctx.guild.id}"')
        vclog = SQL3.fetchone()
        if vclog[0] == 'None':
            vclog = 'Unset'
        else:
            vclog = self.client.get_channel(int(vclog[0])).mention
        embed = discord.Embed(
            title='Logging',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        embed.add_field(
            name='Type',
            value='Chat-logging\nMod-logging\nJoin/leave-logging\nVoice-logging'
        )
        embed.add_field(
            name='Command',
            value='bc!chatlog\nbc!modlog\nbc!joinleavelog\nbc!vclog'
        )
        embed.add_field(
            name='Channel',
            value=f'{chatlog}\n{modlog}\n{jllog}\n{vclog}'
        )
        await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        SQL3.execute(f'select JlLog from Logging where Server_ID="{member.guild.id}"')
        jllog = SQL3.fetchone()
        if jllog is not None:
            if jllog[0] != 'None':
                channel = self.client.get_channel(int(jllog[0]))
                createdate = member.created_at.strftime('%d/%m/%Y %H:%M:%S')
                embed = discord.Embed(
                    title='**User joined**',
                    description=f'User: {member.mention}\nID: {member.id}\nCreated at: {createdate}',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(
                    url=member.avatar_url
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            await member.guild.fetch_ban(member)
        except discord.NotFound:
            SQL3.execute(f'select JlLog from Logging where Server_ID="{member.guild.id}"')
            jllog = SQL3.fetchone()
            if jllog is not None:
                if jllog[0] != 'None':
                    channel = self.client.get_channel(int(jllog[0]))
                    createdate = member.created_at.strftime('%d/%m/%Y %H:%M:%S')
                    embed = discord.Embed(
                        title='**User left**',
                        description=f'User: {member.mention}\nID: {member.id}\nCreated at: {createdate}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=member.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        SQL3.execute(f'select VcLog from Logging where Server_ID="{member.guild.id}"')
        vclog = SQL3.fetchone()
        if vclog is not None:
            if vclog[0] != 'None':
                channel = self.client.get_channel(int(vclog[0]))
                if after.channel is None:
                    embed = discord.Embed(
                        title='**User left voice channel**',
                        description=f'User: {member.mention}\nID: {member.id}\nChannel: {before.channel.mention}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=member.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)
                elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                    embed = discord.Embed(
                        title='**User switched voice channels**',
                        description=f'User: {member.mention}\nID: {member.id}\nPrevious channel: {before.channel.mention}\nNew channel: {after.channel.mention}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=member.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)
                elif before.channel is None and after.channel is not None:
                    embed = discord.Embed(
                        title='**User joined voice channel**',
                        description=f'User: {member.mention}\nID: {member.id}\nChannel: {after.channel.mention}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=member.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{message.guild.id}"')
        chatlog = SQL3.fetchone()
        if chatlog is not None:
            if chatlog[0] != 'None':
                channel = self.client.get_channel(int(chatlog[0]))
                embed = discord.Embed(
                    title='**Message deleted**',
                    description=f'User: {message.author.mention}\nID: {message.author.id}\nMessage ID: {message.id}\nChannel: {message.channel.mention}\n\n**Message:**\n{message.content}',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(
                    url=message.author.avatar_url
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        SQL3.execute(f'select ChatLog from Logging where Server_ID="{before.guild.id}"')
        chatlog = SQL3.fetchone()
        if chatlog is not None:
            if chatlog[0] != 'None':
                channel = self.client.get_channel(int(chatlog[0]))
                embed = discord.Embed(
                    title='**Message edited**',
                    description=f'User: {before.author.mention}\nID: {before.author.id}\nMessage ID: {before.id}\nChannel: {before.channel.mention}\n\n**Previous message:**\n{before.content}\n\n**New message:**\n{after.content}',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(
                    url=before.author.avatar_url
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await channel.send(embed = embed)

    @commands.command()
    async def remind(self, ctx, duration, *, reason):
        conv_dict = {
            'w': 'weeks',
            'd': 'days',
            'h': 'hours',
            'm': 'minutes',
            's': 'seconds'
        }
        pat = r'[0-9]+[s|m|h|d|w]{1}'
        def timestr_to_dict(tstr):
            return {conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, duration)}
        def timestr_to_seconds(tstr):
            return int(datetime.timedelta(**timestr_to_dict(tstr)).total_seconds())
        reminddate = datetime.datetime.utcnow() + datetime.timedelta(seconds = timestr_to_seconds(duration))
        if timestr_to_seconds(duration) == 0:
            embed = discord.Embed(
                title='**:x: Use: bc!remind <duration> <message> or bc!help remind for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        elif timestr_to_seconds(duration) > 3150000000:
            embed = discord.Embed(
                title='**:x: Cannot set a reminder for over more than 100 years.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            SQL4.execute(f'insert into Reminders(User_ID, Reason, Date) values(?,?,?)',
                        (ctx.author.id, reason, reminddate))
            db4.commit()
            formattedtime = format_timespan(timestr_to_seconds(duration))
            embed = discord.Embed(
                title=f'**:white_check_mark: Reminding you in {formattedtime}!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @remind.error
    async def remind_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!remind <duration> <message> or bc!help remind for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            
def setup(client):
    client.add_cog(Utility(client))