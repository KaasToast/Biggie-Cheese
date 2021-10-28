import discord
import traceback
import datetime
import sqlite3
import os
import asyncio

from discord.ext import commands
from discord.ext.commands import *
from pathlib import Path

DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()
databasepath = f'{twoup}/Databases/Economics.db'
db = sqlite3.connect(os.path.join(DIR, databasepath))
SQL = db.cursor()
SQL.execute('create table if not exists Economy('
                    '"User_ID" INTEGER, '
                    '"Wallet" INTEGER, '
                    '"Bank" INTEGER, '
                    '"DailyStreak" INTEGER, '
                    '"DailyStreakExpiration" TEXT, '
                    '"DailyStreakHS" INTEGER, '
                    '"VoteStreak" INTEGER, '
                    '"VoteStreakExpiration" TEXT, '
                    '"VoteStreakHS" INTEGER'
                    ')')

class Dev(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def run(self, ctx, *, code):
        try:
            code = code.replace('\\n', '\n      ')
            exec(f'async def command(self, ctx):\n      {code}')
            return await locals()['command'](self, ctx)
        except:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @run.error
    async def run_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: dev run <code>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def addwallet(self, ctx, member : discord.Member, money):
        if money.isdigit() == False:
            embed = discord.Embed(
                title='**:x: Amount must be a number.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            user_id = member.id
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, Streak, StreakExpiration) values(?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            wallet = SQL.fetchone()
            newwallet = int(wallet[0]) + int(money)
            SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{user_id}"')
            db.commit()
            embed = discord.Embed(
                title=f'**Added {int(money):,} :cheese: to {member.name}\'s wallet.**',
                description=f'{member.name}\'s new wallet balance: {newwallet:,} :cheese:',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @addwallet.error
    async def addwallet_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!addwallet <@user/id> <amount>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def addbank(self, ctx, member : discord.Member, money):
        if money.isdigit() == False:
            embed = discord.Embed(
                title='**:x: Amount must be a number.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            user_id = member.id
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, Streak, StreakExpiration) values(?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Bank from Economy where User_ID="{user_id}"')
            bank = SQL.fetchone()
            newbank = int(bank[0]) + int(money)
            SQL.execute(f'update Economy set Bank="{int(newbank)}" where User_ID="{user_id}"')
            db.commit()
            embed = discord.Embed(
                title=f'**Added {int(money):,} :cheese: to {member.name}\'s bank.**',
                description=f'{member.name}\'s new bank balance: {newbank:,} :cheese:',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @addbank.error
    async def addbank_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!addbank <@user/id> <amount>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def removewallet(self, ctx, member : discord.Member, money):
        if money.isdigit() == False:
            embed = discord.Embed(
                title='**:x: Amount must be a number.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            user_id = member.id
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, Streak, StreakExpiration) values(?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            wallet = SQL.fetchone()
            newwallet = int(wallet[0]) - int(money)
            if newwallet < 0:
                embed = discord.Embed(
                    title='**:x: New balance must be higher than 0.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{user_id}"')
                db.commit()
                embed = discord.Embed(
                    title=f'**Removed {int(money):,} :cheese: from {member.name}\'s wallet.**',
                    description=f'{member.name}\'s new wallet balance: {newwallet:,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @removewallet.error
    async def removewallet_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!removewallet <@user/id> <amount>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def removebank(self, ctx, member : discord.Member, money):
        if money.isdigit() == False:
            embed = discord.Embed(
                title='**:x: Amount must be a number.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            user_id = member.id
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, Streak, StreakExpiration) values(?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Bank from Economy where User_ID="{user_id}"')
            bank = SQL.fetchone()
            newbank = int(bank[0]) - int(money)
            if newbank < 0:
                embed = discord.Embed(
                    title='**:x: New balance must be higher than 0.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                SQL.execute(f'update Economy set Bank="{int(newbank)}" where User_ID="{user_id}"')
                db.commit()
                embed = discord.Embed(
                    title=f'**Removed {int(money):,} :cheese: from {member.name}\'s bank.**',
                    description=f'{member.name}\'s new bank balance: {newbank:,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @removebank.error
    async def removebank_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!removebank <@user/id> <amount>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def setwallet(self, ctx, member : discord.Member, money):
        if money.isdigit() == False:
            embed = discord.Embed(
                title='**:x: Amount must be a number.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            user_id = member.id
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, Streak, StreakExpiration) values(?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'update Economy set Wallet="{int(money)}" where User_ID="{user_id}"')
            db.commit()
            embed = discord.Embed(
                title=f'**:white_check_mark: Set {member.name}\'s wallet balance to: {int(money):,} :cheese:**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @setwallet.error
    async def setwallet_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!setwallet <@user/id> <amount>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def setbank(self, ctx, member : discord.Member, money):
        if money.isdigit() == False:
            embed = discord.Embed(
                title='**:x: Amount must be a number.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            user_id = member.id
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, Streak, StreakExpiration) values(?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'update Economy set Bank="{int(money)}" where User_ID="{user_id}"')
            db.commit()
            embed = discord.Embed(
                title=f'**:white_check_mark: Set {member.name}\'s bank balance to: {int(money):,} :cheese:**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @setbank.error
    async def setbank_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!setbank <@user/id> <amount>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def say(self, ctx, *, args):
        try:
            await ctx.message.delete()
        except:
            pass
        if not args[0].isdigit():
            async with ctx.typing():
                await asyncio.sleep(1)
            await ctx.channel.send(args)
        else:
            channel_id = int(args.split(' ', 1)[0])
            channel = self.client.get_channel(channel_id)
            try:
                await channel.send(args.split(' ', 1)[1])
            except:
                async with ctx.typing():
                    await asyncio.sleep(1)
                await ctx.channel.send(args)

    @say.error
    async def say_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!say [channel-id] <message>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def reply(self, ctx, msgID, *, args):
        try:
            await ctx.message.delete()
        except:
            pass
        if not args[0].isdigit():
            async with ctx.typing():
                await asyncio.sleep(1)
            message = await ctx.channel.fetch_message(msgID)
            await message.reply(args)
        else:
            async with ctx.typing():
                await asyncio.sleep(1)
            channel_id = int(args.split(' ', 1)[0])
            channel = self.client.get_channel(channel_id)
            message = await channel.fetch_message(msgID)
            try:
                await message.reply(args.split(' ', 1)[1])
            except:
                message = await ctx.channel.fetch_message(msgID)
                await message.reply(args)

    @reply.error
    async def reply_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!reply <message-id> [channel-id] <message>.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def setstatus(self, ctx, status, activitytype, *, name):
        try:
            if activitytype.lower() == 'playing':
                activity = discord.Game(name=name)
            elif activitytype.lower() == 'streaming':
                try:
                    if name.lower().startswith('https://'):
                        embed = discord.Embed(
                            title='**:x: Use: bc!setstatus <status> <type> <activity> [url].**',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await ctx.send(embed = embed)
                        return
                    url = name.split('https://', 1)
                    name = url[0]
                    url = f'https://{url[1]}'
                except:
                    embed = discord.Embed(
                        title='**:x: Use: bc!setstatus <status> <type> <activity> [url].**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                    return
                activity = discord.Streaming(name=name, url=url)
            elif activitytype.lower() == 'listening':
                activity = discord.Activity(type=discord.ActivityType.listening, name=name)
            elif activitytype.lower() == 'watching':
                activity = discord.Activity(type=discord.ActivityType.watching, name=name)
            else:
                embed = discord.Embed(
                    title='**:x: Use: bc!setstatus <status> <type> <activity> [url].**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            if status.lower() == 'online':
                icon = discord.Status.online
            elif status.lower() == 'offline':
                icon = discord.Status.offline
            elif status.lower() == 'idle':
                icon = discord.Status.idle
            elif status.lower() == 'dnd':
                icon = discord.Status.dnd
            else:
                embed = discord.Embed(
                    title='**:x: Use: bc!setstatus <status> <type> <activity> [url].**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            await self.client.change_presence(status=icon, activity=activity)
            embed = discord.Embed(
                title='**:white_check_mark: Updated status.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        except:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    @setstatus.error
    async def setstatus_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!setstatus <status> <type> <activity> [url].**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
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
    async def resetstatus(self, ctx):
        status = discord.Status.online
        activity = discord.Activity(type=discord.ActivityType.listening, name='bc!help')
        await self.client.change_presence(status=status, activity=activity)
        embed = discord.Embed(
            title='**:white_check_mark: Reset status to default.**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @resetstatus.error
    async def resetstatus_error(self, ctx, error):
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
    async def devcmds(self, ctx):
        embed = discord.Embed(
            title='**Developer Commands.**',
            description='bc!addbank <@user/id> <amount>\nbc!addwallet <@user/id> <amount>\nbc!deinit\nbc!devcmds\nbc!init\nbc!load <extension>\nbc!reinit\nbc!reload <extension>\nbc!removebank <@user/id> <amount>\nbc!removewallet <@user/id> <amount>\nbc!reply <message-id> [channel-id] <message>\nbc!resetstatus\nbc!restart <duration>\nbc!run <code>\nbc!say [channel-id] <message>\nbc!setbank <@user/id> <amount>\nbc!setstatus <icon> <activity> <text> [url]\nbc!setwallet <@user/id> <amount>\nbc!shutdown\nbc!sync <extension>\nbc!unload <extension>',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @devcmds.error
    async def devcmds_error(self, ctx, error):
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
    client.add_cog(Dev(client))