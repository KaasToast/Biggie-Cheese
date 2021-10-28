import discord
import sqlite3
import os
import datetime
import random
import time
import traceback

from discord_components import *
from discord.ext import commands
from discord.ext.commands import *
from pathlib import Path

DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()
threeup = twoup.parent.absolute()
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

class Economics(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['bal'])
    async def balance(self, ctx, member : discord.Member=None):
        if member == self.client.user:
            embed = discord.Embed(
                title=f'**{member.name}\'s balance:**',
                description='Wallet: ∞ :cheese:\nBank: ∞ :cheese:',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member is None:
            member = ctx.author
        user_id = member.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
        SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
        table_exists = SQL.fetchone()
        if table_exists is None:
            SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                        (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
            db.commit()
        SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
        wallet = SQL.fetchone()
        walletbal = wallet[0]
        SQL.execute(f'select Bank from Economy where User_ID="{user_id}"')
        bank = SQL.fetchone()
        bankbal = bank[0]
        embed = discord.Embed(
            title=f'**{member.name}\'s balance:**',
            description=f'Wallet: {walletbal:,} :cheese:\nBank: {bankbal:,} :cheese:',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @balance.error
    async def balance_error(self, ctx, error):
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

    @commands.command(aliases=['pay'])
    async def give(self, ctx, member : discord.Member, money):
        if member == ctx.author:
            embed = discord.Embed(
                title='**:x: You cannot give cheese to yourself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member == self.client.user:
            embed = discord.Embed(
                title='**:x: Biggie Cheese already has enough cheese.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        author_id = ctx.message.author.id
        user_id = member.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
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
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            authorbalance = SQL.fetchone()
            if int(money) > int(authorbalance[0]):
                embed = discord.Embed(
                    title='**:x: You don\'t have enough cheese in your wallet!**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
                authorbalance = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
                targetbalance = SQL.fetchone()
                authornewbalance = int(authorbalance[0]) - int(money)
                targetnewbalance = int(targetbalance[0]) + int(money)
                SQL.execute(f'update Economy set Wallet="{int(authornewbalance)}" where User_ID="{author_id}"')
                db.commit()
                SQL.execute(f'update Economy set Wallet="{int(targetnewbalance)}" where User_ID="{user_id}"')
                db.commit()
                embed = discord.Embed(
                    title=f'**You gave {member.name} {int(money):,} :cheese:**',
                    description=f'Your new wallet balance is: {int(authornewbalance):,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!give <@user/id> <amount> or bc!help give for more info.**',
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

    @commands.command(aliases=['dep'])
    async def deposit(self, ctx, money):
        author_id = ctx.author.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
        if money in ['all', 'max']:
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            authorwallet = SQL.fetchone()
            SQL.execute(f'select Bank from Economy where User_ID="{author_id}"')
            authorbank = SQL.fetchone()
            newwallet = int(authorwallet[0]) - int(authorwallet[0])
            newbank = int(authorbank[0]) + int(authorwallet[0])
            SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
            db.commit()
            SQL.execute(f'update Economy set Bank="{int(newbank)}" where User_ID="{author_id}"')
            db.commit()
            embed = discord.Embed(
                title=f'**Deposited {int(authorwallet[0]):,} :cheese: to your bank**',
                description=f'Your new bank balance is: {int(newbank):,} :cheese:',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        elif money.isdigit() == False:
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
            return
        else:
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            authorwallet = SQL.fetchone()
            if int(money) > int(authorwallet[0]):
                embed = discord.Embed(
                    title='**:x: You don\'t have enough cheese in your wallet!**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
                authorwallet = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{author_id}"')
                authorbank = SQL.fetchone()
                newwallet = int(authorwallet[0]) - int(money)
                newbank = int(authorbank[0]) + int(money)
                SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
                db.commit()
                SQL.execute(f'update Economy set Bank="{int(newbank)}" where User_ID="{author_id}"')
                db.commit()
                embed = discord.Embed(
                    title=f'**Deposited {int(money):,} :cheese: to your bank**',
                    description=f'Your new bank balance is: {int(newbank):,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!deposit <amount> or bc!help deposit for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def withdraw(self, ctx, money):
        author_id = ctx.author.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
        if money in ['all', 'max']:
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            authorwallet = SQL.fetchone()
            SQL.execute(f'select Bank from Economy where User_ID="{author_id}"')
            authorbank = SQL.fetchone()
            newwallet = int(authorwallet[0]) + int(authorbank[0])
            newbank = int(authorbank[0]) - int(authorbank[0])
            SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
            db.commit()
            SQL.execute(f'update Economy set Bank="{int(newbank)}" where User_ID="{author_id}"')
            db.commit()
            embed = discord.Embed(
                title=f'**Withdrawed {int(authorbank[0]):,} :cheese: to your wallet**',
                description=f'Your new wallet balance is: {int(newwallet):,} :cheese:',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        elif money.isdigit() == False:
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
            SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
            table_exists = SQL.fetchone()
            if table_exists is None:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
            SQL.execute(f'select Bank from Economy where User_ID="{author_id}"')
            authorbank = SQL.fetchone()
            if int(money) > int(authorbank[0]):
                embed = discord.Embed(
                    title='**:x: You don\'t have enough cheese in your bank!**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
                authorwallet = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{author_id}"')
                authorbank = SQL.fetchone()
                newwallet = int(authorwallet[0]) + int(money)
                newbank = int(authorbank[0]) - int(money)
                SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
                db.commit()
                SQL.execute(f'update Economy set Bank="{int(newbank)}" where User_ID="{author_id}"')
                db.commit()
                embed = discord.Embed(
                    title=f'**Withdrawed {int(money):,} :cheese: to your wallet**',
                    description=f'Your new wallet balance is: {int(newwallet):,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            
    @withdraw.error
    async def withdraw_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!withdraw <amount> or bc!help withdraw for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        author_id = ctx.author.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
        SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
        table_exists = SQL.fetchone()
        if table_exists is None:
            SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                        (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
            db.commit()
        SQL.execute(f'select DailyStreakExpiration from Economy where User_ID="{author_id}"')
        oldstreakexpiration = SQL.fetchone()
        SQL.execute(f'select DailyStreak from Economy where User_ID="{author_id}"')
        oldstreak = SQL.fetchone()
        SQL.execute(f'select DailyStreakHS from Economy where User_ID="{author_id}"')
        oldstreakhs = SQL.fetchone()
        SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
        authorwallet = SQL.fetchone()
        if oldstreakexpiration[0] == 'None':
            newstreakexpiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 48)
            newstreakcount = 1
            if newstreakcount > oldstreakhs[0]:
                SQL.execute(f'update Economy set DailyStreakHS="{newstreakcount}" where User_ID="{author_id}"')
                db.commit()
            SQL.execute(f'update Economy set DailyStreak="{newstreakcount}" where User_ID="{author_id}"')
            db.commit()
            SQL.execute(f'update Economy set DailyStreakExpiration="{newstreakexpiration}" where User_ID="{author_id}"')
            db.commit()
            newwallet = authorwallet[0] + 5000
            SQL.execute(f'update Economy set Wallet="{newwallet}" where User_ID="{author_id}"')
            db.commit()
            embed = discord.Embed(
                title='**You claimed your reward of 5,000 :cheese:**',
                description=f'Streak: 0 (1,0x multiplier)\nNew wallet balance: {int(newwallet):,} :cheese:',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            olddateformatted = datetime.datetime.strptime(oldstreakexpiration[0], f'%Y-%m-%d %H:%M:%S.%f')
            if olddateformatted < datetime.datetime.utcnow():
                newstreakexpiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 48)
                newstreakcount = 1
                if newstreakcount > oldstreakhs[0]:
                    SQL.execute(f'update Economy set DailyStreakHS="{newstreakcount}" where User_ID="{author_id}"')
                    db.commit()
                SQL.execute(f'update Economy set DailyStreak="{newstreakcount}" where User_ID="{author_id}"')
                db.commit()
                SQL.execute(f'update Economy set DailyStreakExpiration="{newstreakexpiration}" where User_ID="{author_id}"')
                db.commit()
                newwallet = authorwallet[0] + 5000
                SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
                db.commit()
                embed = discord.Embed(
                    title='**You claimed your reward of 5,000 :cheese:**',
                    description=f'Streak: 0 (1,0x multiplier)\nNew wallet balance: {int(newwallet):,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            elif datetime.datetime.utcnow() < olddateformatted:
                newstreakexpiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 48)
                newstreakcount = oldstreak[0] + 1
                if newstreakcount > oldstreakhs[0]:
                    SQL.execute(f'update Economy set DailyStreakHS="{newstreakcount}" where User_ID="{author_id}"')
                    db.commit()
                SQL.execute(f'update Economy set DailyStreak="{newstreakcount}" where User_ID="{author_id}"')
                db.commit()
                SQL.execute(f'update Economy set DailyStreakExpiration="{newstreakexpiration}" where User_ID="{author_id}"')
                db.commit()
                if oldstreak[0] == 0:
                    multiplier = 1
                else:
                    multiplier = oldstreak[0] / 10 + 1
                bonus = 5000 * multiplier
                newwallet = authorwallet[0] + int(bonus)
                SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
                db.commit()
                embed = discord.Embed(
                    title=f'**You claimed your reward of {int(bonus):,} :cheese:**',
                    description=f'Streak: {oldstreak[0]} ({multiplier}x multiplier)\nNew wallet balance: {int(newwallet):,} :cheese:',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            cooldown = round(error.retry_after)
            timer = time.strftime('%H hours %M minutes and %S seconds', time.gmtime(cooldown))
            embed = discord.Embed(
                title='**You already claimed your daily reward today.**',
                description=f'You can claim again in {timer}',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        author_id = ctx.author.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
        SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
        table_exists = SQL.fetchone()
        if table_exists is None:
            SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                        (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
            db.commit()
        SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
        walletbalance = SQL.fetchone()
        money = random.randint(1000,10000)
        newbalance = walletbalance[0] + money
        SQL.execute(f'update Economy set Wallet="{newbalance}" where User_ID="{author_id}"')
        db.commit()
        embed = discord.Embed(
            title=f'You went to work and got paid {money:,} :cheese:',
            description=f'Your new wallet balance is: {newbalance:,} :cheese:',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            cooldown = round(error.retry_after)
            timer = time.strftime('%M minutes and %S seconds', time.gmtime(cooldown))
            embed = discord.Embed(
                title='**You already worked recently.**',
                description=f'You can work again in {timer}',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def top(self, ctx):
        seed = random.randint(1000000000,2000000000)
        async def callback(interaction):
            nonlocal seed
            if interaction.author == ctx.author and interaction.custom_id == f'wallet{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                try:
                    await message.delete()
                except:
                    pass
                SQL.execute('select User_ID from Economy order by Wallet desc limit 10')
                walletusers = SQL.fetchall()
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[0][0]}"')
                username1 = SQL.fetchone()
                username1 = self.client.get_user(username1[0])
                if username1 is None:
                    username1 = 'Deleted User'
                else:
                    username1 = username1.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[1][0]}"')
                username2 = SQL.fetchone()
                username2 = self.client.get_user(username2[0])
                if username2 is None:
                    username2 = 'Deleted User'
                else:
                    username2 = username2.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[2][0]}"')
                username3 = SQL.fetchone()
                username3 = self.client.get_user(username3[0])
                if username3 is None:
                    username3 = 'Deleted User'
                else:
                    username3 = username3.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[3][0]}"')
                username4 = SQL.fetchone()
                username4 = self.client.get_user(username4[0])
                if username4 is None:
                    username4 = 'Deleted User'
                else:
                    username4 = username4.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[4][0]}"')
                username5 = SQL.fetchone()
                username5 = self.client.get_user(username5[0])
                if username5 is None:
                    username5 = 'Deleted User'
                else:
                    username5 = username5.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[5][0]}"')
                username6 = SQL.fetchone()
                username6 = self.client.get_user(username6[0])
                if username6 is None:
                    username6 = 'Deleted User'
                else:
                    username6 = username6.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[6][0]}"')
                username7 = SQL.fetchone()
                username7 = self.client.get_user(username7[0])
                if username7 is None:
                    username7 = 'Deleted User'
                else:
                    username7 = username7.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[7][0]}"')
                username8 = SQL.fetchone()
                username8 = self.client.get_user(username8[0])
                if username8 is None:
                    username8 = 'Deleted User'
                else:
                    username8 = username8.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[8][0]}"')
                username9 = SQL.fetchone()
                username9 = self.client.get_user(username9[0])
                if username9 is None:
                    username9 = 'Deleted User'
                else:
                    username9 = username9.name
                SQL.execute(f'select User_ID from Economy where User_ID="{walletusers[9][0]}"')
                username10 = SQL.fetchone()
                username10 = self.client.get_user(username10[0])
                if username10 is None:
                    username10 = 'Deleted User'
                else:
                    username10 = username10.name
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[0][0]}"')
                wallet1 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[1][0]}"')
                wallet2 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[2][0]}"')
                wallet3 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[3][0]}"')
                wallet4 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[4][0]}"')
                wallet5 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[5][0]}"')
                wallet6 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[6][0]}"')
                wallet7 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[7][0]}"')
                wallet8 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[8][0]}"')
                wallet9 = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{walletusers[9][0]}"')
                wallet10 = SQL.fetchone()
                embed = discord.Embed(
                    title='Wallet balance leaderboard.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(
                    name='User',
                    value=f'1. {username1}\n2. {username2}\n3. {username3}\n4. {username4}\n5. {username5}\n6. {username6}\n7. {username7}\n8. {username8}\n9. {username9}\n10. {username10}',
                    inline=True
                )
                embed.add_field(
                    name='Wallet balance',
                    value=f'{wallet1[0]:,} :cheese:\n{wallet2[0]:,} :cheese:\n{wallet3[0]:,} :cheese:\n{wallet4[0]:,} :cheese:\n{wallet5[0]:,} :cheese:\n{wallet6[0]:,} :cheese:\n{wallet7[0]:,} :cheese:\n{wallet8[0]:,} :cheese:\n{wallet9[0]:,} :cheese:\n{wallet10[0]:,} :cheese:',
                    inline=True
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            elif interaction.author == ctx.author and interaction.custom_id == f'bank{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                try:
                    await message.delete()
                except:
                    pass
                SQL.execute('select User_ID from Economy order by Bank desc limit 10')
                bankusers = SQL.fetchall()
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[0][0]}"')
                username1 = SQL.fetchone()
                username1 = self.client.get_user(username1[0])
                if username1 is None:
                    username1 = 'Deleted User'
                else:
                    username1 = username1.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[1][0]}"')
                username2 = SQL.fetchone()
                username2 = self.client.get_user(username2[0])
                if username2 is None:
                    username2 = 'Deleted User'
                else:
                    username2 = username2.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[2][0]}"')
                username3 = SQL.fetchone()
                username3 = self.client.get_user(username3[0])
                if username3 is None:
                    username3 = 'Deleted User'
                else:
                    username3 = username3.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[3][0]}"')
                username4 = SQL.fetchone()
                username4 = self.client.get_user(username4[0])
                if username4 is None:
                    username4 = 'Deleted User'
                else:
                    username4 = username4.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[4][0]}"')
                username5 = SQL.fetchone()
                username5 = self.client.get_user(username5[0])
                if username5 is None:
                    username5 = 'Deleted User'
                else:
                    username5 = username5.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[5][0]}"')
                username6 = SQL.fetchone()
                username6 = self.client.get_user(username6[0])
                if username6 is None:
                    username6 = 'Deleted User'
                else:
                    username6 = username6.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[6][0]}"')
                username7 = SQL.fetchone()
                username7 = self.client.get_user(username7[0])
                if username7 is None:
                    username7 = 'Deleted User'
                else:
                    username7 = username7.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[7][0]}"')
                username8 = SQL.fetchone()
                username8 = self.client.get_user(username8[0])
                if username8 is None:
                    username8 = 'Deleted User'
                else:
                    username8 = username8.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[8][0]}"')
                username9 = SQL.fetchone()
                username9 = self.client.get_user(username9[0])
                if username9 is None:
                    username9 = 'Deleted User'
                else:
                    username9 = username9.name
                SQL.execute(f'select User_ID from Economy where User_ID="{bankusers[9][0]}"')
                username10 = SQL.fetchone()
                username10 = self.client.get_user(username10[0])
                if username10 is None:
                    username10 = 'Deleted User'
                else:
                    username10 = username10.name
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[0][0]}"')
                bank1 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[1][0]}"')
                bank2 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[2][0]}"')
                bank3 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[3][0]}"')
                bank4 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[4][0]}"')
                bank5 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[5][0]}"')
                bank6 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[6][0]}"')
                bank7 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[7][0]}"')
                bank8 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[8][0]}"')
                bank9 = SQL.fetchone()
                SQL.execute(f'select Bank from Economy where User_ID="{bankusers[9][0]}"')
                bank10 = SQL.fetchone()
                embed = discord.Embed(
                    title='Bank balance leaderboard.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(
                    name='User',
                    value=f'1. {username1}\n2. {username2}\n3. {username3}\n4. {username4}\n5. {username5}\n6. {username6}\n7. {username7}\n8. {username8}\n9. {username9}\n10. {username10}',
                    inline=True
                )
                embed.add_field(
                    name='Bank balance',
                    value=f'{bank1[0]:,} :cheese:\n{bank2[0]:,} :cheese:\n{bank3[0]:,} :cheese:\n{bank4[0]:,} :cheese:\n{bank5[0]:,} :cheese:\n{bank6[0]:,} :cheese:\n{bank7[0]:,} :cheese:\n{bank8[0]:,} :cheese:\n{bank9[0]:,} :cheese:\n{bank10[0]:,} :cheese:',
                    inline=True
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            elif interaction.author == ctx.author and interaction.custom_id == f'daily_streak{seed}' and interaction.message == message:
                await interaction.respond(type=6)
                try:
                    await message.delete()
                except:
                    pass
                SQL.execute('select User_ID from Economy order by DailyStreak desc limit 10')
                dailystreakusers = SQL.fetchall()
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[0][0]}"')
                username1 = SQL.fetchone()
                username1 = self.client.get_user(username1[0])
                if username1 is None:
                    username1 = 'Deleted User'
                else:
                    username1 = username1.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[1][0]}"')
                username2 = SQL.fetchone()
                username2 = self.client.get_user(username2[0])
                if username2 is None:
                    username2 = 'Deleted User'
                else:
                    username2 = username2.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[2][0]}"')
                username3 = SQL.fetchone()
                username3 = self.client.get_user(username3[0])
                if username3 is None:
                    username3 = 'Deleted User'
                else:
                    username3 = username3.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[3][0]}"')
                username4 = SQL.fetchone()
                username4 = self.client.get_user(username4[0])
                if username4 is None:
                    username4 = 'Deleted User'
                else:
                    username4 = username4.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[4][0]}"')
                username5 = SQL.fetchone()
                username5 = self.client.get_user(username5[0])
                if username5 is None:
                    username5 = 'Deleted User'
                else:
                    username5 = username5.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[5][0]}"')
                username6 = SQL.fetchone()
                username6 = self.client.get_user(username6[0])
                if username6 is None:
                    username6 = 'Deleted User'
                else:
                    username6 = username6.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[6][0]}"')
                username7 = SQL.fetchone()
                username7 = self.client.get_user(username7[0])
                if username7 is None:
                    username7 = 'Deleted User'
                else:
                    username7 = username7.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[7][0]}"')
                username8 = SQL.fetchone()
                username8 = self.client.get_user(username8[0])
                if username8 is None:
                    username8 = 'Deleted User'
                else:
                    username8 = username8.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[8][0]}"')
                username9 = SQL.fetchone()
                username9 = self.client.get_user(username9[0])
                if username9 is None:
                    username9 = 'Deleted User'
                else:
                    username9 = username9.name
                SQL.execute(f'select User_ID from Economy where User_ID="{dailystreakusers[9][0]}"')
                username10 = SQL.fetchone()
                username10 = self.client.get_user(username10[0])
                if username10 is None:
                    username10 = 'Deleted User'
                else:
                    username10 = username10.name
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[0][0]}"')
                dailystreak1 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[1][0]}"')
                dailystreak2 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[2][0]}"')
                dailystreak3 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[3][0]}"')
                dailystreak4 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[4][0]}"')
                dailystreak5 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[5][0]}"')
                dailystreak6 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[6][0]}"')
                dailystreak7 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[7][0]}"')
                dailystreak8 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[8][0]}"')
                dailystreak9 = SQL.fetchone()
                SQL.execute(f'select DailyStreak from Economy where User_ID="{dailystreakusers[9][0]}"')
                dailystreak10 = SQL.fetchone()
                embed = discord.Embed(
                    title='Daily streak leaderboard.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(
                    name='User',
                    value=f'1. {username1}\n2. {username2}\n3. {username3}\n4. {username4}\n5. {username5}\n6. {username6}\n7. {username7}\n8. {username8}\n9. {username9}\n10. {username10}',
                    inline=True
                )
                embed.add_field(
                    name='Daily streak',
                    value=f'{dailystreak1[0]:,}\n{dailystreak2[0]:,}\n{dailystreak3[0]:,}\n{dailystreak4[0]:,}\n{dailystreak5[0]:,}\n{dailystreak6[0]:,}\n{dailystreak7[0]:,}\n{dailystreak8[0]:,}\n{dailystreak9[0]:,}\n{dailystreak10[0]:,}',
                    inline=True
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        embed = discord.Embed(
            title='Select leaderboard type:',
            description='1️⃣ Wallet\n2️⃣ Bank\n3️⃣ Daily streak',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        message = await ctx.send(embed = embed,
            components=[
                [
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Wallet', custom_id=f'wallet{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Bank', custom_id=f'bank{seed}'), callback),
                    self.client.components_manager.add_callback(Button(style=ButtonStyle.red, label='Daily Streak', custom_id=f'daily_streak{seed}'), callback),
                ]
            ]
        )

    @commands.command()
    async def streak(self, ctx, member : discord.Member=None):
        if member is None:
            member = ctx.author
        user_id = member.id
        startingbal = 0
        streak = 0
        streakexpiration = str(None)
        SQL.execute(f'select Wallet from Economy where User_ID="{user_id}"')
        table_exists = SQL.fetchone()
        if table_exists is None:
            SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                        (user_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
            db.commit()
        SQL.execute(f'select DailyStreak from Economy where User_ID="{user_id}"')
        dailystreak = SQL.fetchone()
        SQL.execute(f'select DailyStreakHS from Economy where User_ID="{user_id}"')
        dailystreakhs = SQL.fetchone()
        SQL.execute(f'select VoteStreak from Economy where User_ID="{user_id}"')
        votestreak = SQL.fetchone()
        SQL.execute(f'select VoteStreakHS from Economy where User_ID="{user_id}"')
        votestreakhs = SQL.fetchone()
        SQL.execute(f'select DailyStreakExpiration from Economy where User_ID="{user_id}"')
        dailystreakexpiration = SQL.fetchone()        
        if dailystreakexpiration[0] == 'None':
            dailystreakexpiration = 'Expired'
        else:
            formatteddailyexpiration = datetime.datetime.strptime(dailystreakexpiration[0], f'%Y-%m-%d %H:%M:%S.%f')
            formatteddailyexpiration = formatteddailyexpiration - datetime.datetime.utcnow()
            seconds = int(formatteddailyexpiration.total_seconds())
            hours = seconds // 3600
            seconds = seconds - (hours * 3600)
            minutes = seconds // 60
            seconds = seconds - (minutes * 60)
            dailystreakexpiration = '{:02} Hours, {:02} Minutes and {:02} Seconds'.format(int(hours), int(minutes), int(seconds))
        SQL.execute(f'select VoteStreakExpiration from Economy where User_ID="{user_id}"')
        votestreakexpiration = SQL.fetchone()        
        if votestreakexpiration[0] == 'None':
            votestreakexpiration = 'Expired'
        else:
            formattedvoteexpiration = datetime.datetime.strptime(votestreakexpiration[0], f'%Y-%m-%d %H:%M:%S.%f')
            formattedvoteexpiration = formattedvoteexpiration - datetime.datetime.utcnow()
            seconds = int(formattedvoteexpiration.total_seconds())
            hours = seconds // 3600
            seconds = seconds - (hours * 3600)
            minutes = seconds // 60
            seconds = seconds - (minutes * 60)
            votestreakexpiration = '{:02} Hours, {:02} Minutes and {:02} Seconds'.format(int(hours), int(minutes), int(seconds))
        embed = discord.Embed(
            title=f'**{member.name}\'s Streak information**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(
            url=member.avatar_url
        )
        embed.add_field(
            name='Daily streak:',
            value=dailystreak[0],
            inline=True
        )
        embed.add_field(
            name='Daily streak highscore:',
            value=dailystreakhs[0],
            inline=True
        )
        embed.add_field(
            name='Daily streak expiration:',
            value=dailystreakexpiration,
            inline=False
        )
        embed.add_field(
            name='Vote streak:',
            value=votestreak[0],
            inline=True
        )
        embed.add_field(
            name='Vote streak highscore:',
            value=votestreakhs[0],
            inline=True
        )
        embed.add_field(
            name='Vote streak expiration:',
            value=votestreakexpiration,
            inline=False
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        voter = self.client.get_user(int(data['user']))
        if int(data['bot']) == self.client.user.id:
            if data['type'] == 'upvote':
                author_id = voter.id
                startingbal = 0
                streak = 0
                streakexpiration = str(None)
                SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
                table_exists = SQL.fetchone()
                if table_exists is None:
                    SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                                (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                    db.commit()
                SQL.execute(f'select VoteStreakExpiration from Economy where User_ID="{author_id}"')
                oldstreakexpiration = SQL.fetchone()
                SQL.execute(f'select VoteStreak from Economy where User_ID="{author_id}"')
                oldstreak = SQL.fetchone()
                SQL.execute(f'select VoteStreakHS from Economy where User_ID="{author_id}"')
                oldstreakhs = SQL.fetchone()
                SQL.execute(f'select Wallet from Economy where User_ID="{author_id}"')
                authorwallet = SQL.fetchone()
                if oldstreakexpiration[0] == 'None':
                    newstreakexpiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 48)
                    newstreakcount = 1
                    if newstreakcount > oldstreakhs[0]:
                        SQL.execute(f'update Economy set VoteStreakHS="{newstreakcount}" where User_ID="{author_id}"')
                        db.commit()
                    SQL.execute(f'update Economy set VoteStreak="{newstreakcount}" where User_ID="{author_id}"')
                    db.commit()
                    SQL.execute(f'update Economy set VoteStreakExpiration="{newstreakexpiration}" where User_ID="{author_id}"')
                    db.commit()
                    newwallet = authorwallet[0] + 20000
                    SQL.execute(f'update Economy set Wallet="{newwallet}" where User_ID="{author_id}"')
                    db.commit()
                    embed = discord.Embed(
                        title='**Thank you for voting! You received a reward of 20,000 :cheese:**',
                        description=f'Streak: 0 (1,0x multiplier)\nNew wallet balance: {int(newwallet):,} :cheese:',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await voter.send(embed = embed)
                else:
                    olddateformatted = datetime.datetime.strptime(oldstreakexpiration[0], f'%Y-%m-%d %H:%M:%S.%f')
                    if olddateformatted < datetime.datetime.utcnow():
                        newstreakexpiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 48)
                        newstreakcount = 1
                        if newstreakcount > oldstreakhs[0]:
                            SQL.execute(f'update Economy set VoteStreakHS="{newstreakcount}" where User_ID="{author_id}"')
                            db.commit()
                        SQL.execute(f'update Economy set VoteStreak="{newstreakcount}" where User_ID="{author_id}"')
                        db.commit()
                        SQL.execute(f'update Economy set VoteStreakExpiration="{newstreakexpiration}" where User_ID="{author_id}"')
                        db.commit()
                        newwallet = authorwallet[0] + 20000
                        SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
                        db.commit()
                        embed = discord.Embed(
                            title='**Thank you for voting! You received a reward of 20,000 :cheese:**',
                            description=f'Streak: 0 (1,0x multiplier)\nNew wallet balance: {int(newwallet):,} :cheese:',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await voter.send(embed = embed)
                    elif datetime.datetime.utcnow() < olddateformatted:
                        newstreakexpiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 48)
                        newstreakcount = oldstreak[0] + 1
                        if newstreakcount > oldstreakhs[0]:
                            SQL.execute(f'update Economy set VoteStreakHS="{newstreakcount}" where User_ID="{author_id}"')
                            db.commit()
                        SQL.execute(f'update Economy set VoteStreak="{newstreakcount}" where User_ID="{author_id}"')
                        db.commit()
                        SQL.execute(f'update Economy set VoteStreakExpiration="{newstreakexpiration}" where User_ID="{author_id}"')
                        db.commit()
                        if oldstreak[0] == 0:
                            multiplier = 1
                        else:
                            multiplier = oldstreak[0] / 10 + 1
                        bonus = 20000 * multiplier
                        newwallet = authorwallet[0] + int(bonus)
                        SQL.execute(f'update Economy set Wallet="{int(newwallet)}" where User_ID="{author_id}"')
                        db.commit()
                        embed = discord.Embed(
                            title=f'**Thank you for voting! You received a reward of {int(bonus):,} :cheese:**',
                            description=f'Streak: {oldstreak[0]} ({multiplier}x multiplier)\nNew wallet balance: {int(newwallet):,} :cheese:',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await voter.send(embed = embed)

    @commands.command()
    async def vote(self, ctx):
        try:
            author_id = ctx.author.id
            startingbal = 0
            streak = 0
            streakexpiration = str(None)
            SQL.execute(f'select VoteStreakExpiration from Economy where User_ID="{ctx.author.id}"')
            votestreakexpiration = SQL.fetchone()
            if not votestreakexpiration:
                SQL.execute('insert into Economy(User_ID, Wallet, Bank, DailyStreak, DailyStreakExpiration, DailyStreakHS, VoteStreak, VoteStreakExpiration, VoteStreakHS) values(?,?,?,?,?,?,?,?,?)',
                            (author_id, startingbal, startingbal, streak, streakexpiration, streak, streak, streakexpiration, streak))
                db.commit()
                embed = discord.Embed(
                    title='**To vote for the bot use the following link:**',
                    description='[Vote](https://biggiecheese.xyz/vote)',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            elif votestreakexpiration[0] == 'None':
                embed = discord.Embed(
                    title='**To vote for the bot use the following link:**',
                    description='[Vote](https://biggiecheese.xyz/vote)',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                return
            expiration = datetime.datetime.strptime(votestreakexpiration[0], f'%Y-%m-%d %H:%M:%S.%f')        
            expiration = expiration - datetime.timedelta(hours=36)
            delta_cooldown = expiration - datetime.datetime.utcnow()
            hours, remainder = divmod(int(delta_cooldown.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            if hours >= 12:
                embed = discord.Embed(
                    title='**To vote for the bot use the following link:**',
                    description='[Vote](https://biggiecheese.xyz/vote)',
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
                    title='**You already voted in the past 12 hours.**',
                    description=f'You can vote again in {hours} hours {minutes} minutes and {seconds} seconds',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        except:
            traceback.print_exc()

def setup(client):
    client.add_cog(Economics(client))