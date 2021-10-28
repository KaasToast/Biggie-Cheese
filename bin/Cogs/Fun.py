import discord
import datetime
import random
import asyncpraw
import sqlite3
import os
import asyncio
import aiohttp

from dotenv import load_dotenv
from functools import partial
from typing import Union
from discord_components import *
from discord.ext import commands
from discord.ext.commands import *
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from pathlib import Path

topics = []
DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()
threeup = twoup.parent.absolute()
topicfile = f'{twoup}/Topics/Topics.txt'
with open(topicfile, mode = 'r') as f:
    for line in f:
        topics.append(line)
    f.close()
databasepath = f'{twoup}/Databases/Marriages.db'
db = sqlite3.connect(os.path.join(DIR, databasepath))
SQL = db.cursor()
SQL.execute('create table if not exists Marriages('
                    '"User_One" INTEGER, '
                    '"User_Two" INTEGER, '
                    '"Date" TEXT'
                    ')')

load_dotenv(f'{threeup}/.env')
PRAW_CLIENT_ID = os.getenv('PRAW_CLIENT_ID')
PRAW_CLIENT_SECRET = os.getenv('PRAW_CLIENT_SECRET')
PRAW_PASSWORD = os.getenv('PRAW_PASSWORD')

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.pending = []

    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:
        avatar_url = user.avatar_url_as(format='png')
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_url)) as response:
                avatar_bytes = await response.read()
        return avatar_bytes

    @commands.command(aliases=['bc'])
    async def biggiecheese(self, ctx):
        embed = discord.Embed(
            title='**Give it up, for the one and only: Biggie Cheese!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_image(
            url=('https://cdn.discordapp.com/attachments/725146279155335244/822913985837006870/biggiecheese.png')
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)

    @staticmethod
    def processhorny(avatar_bytes: bytes, name: str) -> BytesIO:
        number = random.randint(0, 100)
        pfp = Image.open(BytesIO(avatar_bytes)).convert('RGBA')
        pfp = pfp.resize((530,530))                
        if number == 0:
            horny = Image.open(f'{twoup}/Images/horny/horny0.png').convert('RGBA')
            textbox2pos = (365,550)    
        elif number <= 5:
            horny = Image.open(f'{twoup}/Images/horny/horny5.png').convert('RGBA')
            textbox2pos = (365,520)   
        elif number <= 10:
            horny = Image.open(f'{twoup}/Images/horny/horny10.png').convert('RGBA')
            textbox2pos = (365,490)    
        elif number <= 15:
            horny = Image.open(f'{twoup}/Images/horny/horny15.png').convert('RGBA')
            textbox2pos = (365,460)     
        elif number <= 20:
            horny = Image.open(f'{twoup}/Images/horny/horny20.png').convert('RGBA')
            textbox2pos = (365,430)
        elif number <= 25:
            horny = Image.open(f'{twoup}/Images/horny/horny25.png').convert('RGBA')
            textbox2pos = (365,400)
        elif number <= 30:
            horny = Image.open(f'{twoup}/Images/horny/horny30.png').convert('RGBA')
            textbox2pos = (365,370)
        elif number <= 35:
            horny = Image.open(f'{twoup}/Images/horny/horny35.png').convert('RGBA')
            textbox2pos = (365,340)
        elif number <= 40:
            horny = Image.open(f'{twoup}/Images/horny/horny40.png').convert('RGBA')
            textbox2pos = (365,310)
        elif number <= 45:
            horny = Image.open(f'{twoup}/Images/horny/horny45.png').convert('RGBA')
            textbox2pos = (365,280)
        elif number <= 50:
            horny = Image.open(f'{twoup}/Images/horny/horny50.png').convert('RGBA')
            textbox2pos = (365,250)
        elif number <= 55:
            horny = Image.open(f'{twoup}/Images/horny/horny55.png').convert('RGBA')
            textbox2pos = (365,220)
        elif number <= 60:
            horny = Image.open(f'{twoup}/Images/horny/horny60.png').convert('RGBA')
            textbox2pos = (365,190)
        elif number <= 65:
            horny = Image.open(f'{twoup}/Images/horny/horny65.png').convert('RGBA')
            textbox2pos = (365,160)
        elif number <= 70:
            horny = Image.open(f'{twoup}/Images/horny/horny70.png').convert('RGBA')
            textbox2pos = (365,160)
        elif number <= 75:
            horny = Image.open(f'{twoup}/Images/horny/horny75.png').convert('RGBA')
            textbox2pos = (365,130)
        elif number <= 80:
            horny = Image.open(f'{twoup}/Images/horny/horny80.png').convert('RGBA')
            textbox2pos = (365,100)
        elif number <= 85:
            horny = Image.open(f'{twoup}/Images/horny/horny85.png').convert('RGBA')
            textbox2pos = (365,70)
        elif number <= 90:
            horny = Image.open(f'{twoup}/Images/horny/horny90.png').convert('RGBA')
            textbox2pos = (365,40)
        elif number <= 95:
            horny = Image.open(f'{twoup}/Images/horny/horny95.png').convert('RGBA')
            textbox2pos = (365,10)
        elif number <= 100:
            horny = Image.open(f'{twoup}/Images/horny/horny100.png').convert('RGBA')
            textbox2pos = (365,10)
        W, H = (280,80)
        textbox = Image.new('RGBA',(W,H))
        fontsize = 1
        img_fraction = 0.8
        font = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize)
        while font.getsize(name)[0] < img_fraction*textbox.size[0]:
            fontsize += 1
            font = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize)            
        draw = ImageDraw.Draw(textbox)
        w, h = font.getsize(name)
        draw.text(((W-w)/2,(H-h)/2), name, font=font)        
        W2, H2 = (135,70)
        textbox2 = Image.new('RGBA',(W2,H2))
        font2 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', 50)
        draw2 = ImageDraw.Draw(textbox2)
        w2, h2 = font2.getsize(f'{number}%')
        draw2.text(((W2-w2)/2,(H2-h2)/2), f'{number}%', font=font2)            
        final = Image.new('RGBA',(1920,1080))
        final.paste(horny, (0,0))
        final.paste(textbox, (1190,825), mask=textbox)
        final.paste(textbox2, textbox2pos, mask=textbox2)
        final.paste(pfp, (945,275), mask=pfp)
        final_buffer = BytesIO()
        final.save(final_buffer, 'png')
        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def horny(self, ctx, member : discord.Member=None):
        async with ctx.typing():
            if member is None:
                member = ctx.author
            name = member.name
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.processhorny, avatar_bytes, name)
            final_buffer = await self.client.loop.run_in_executor(None, fn)            
            embed = discord.Embed(
                title=f'**{name}\'s Horny level.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            file = discord.File(
                filename='image.png',
                fp=final_buffer
            )
            embed.set_image(
                url='attachment://image.png'
            )
            await ctx.send(file = file, embed = embed)
        
    @horny.error
    async def horny_error(self, ctx, error):
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

    @staticmethod
    def processjail(avatar_bytes: bytes) -> BytesIO:
        pfp = Image.open(BytesIO(avatar_bytes)).convert('RGBA').convert('L')
        pfp = pfp.resize((800,800))
        jail = Image.open(f'{twoup}/Images/jail.png').convert('RGBA')
        final = Image.new('RGBA', (800,800), (0, 0, 0, 0))
        final.paste(pfp, (0,0))
        final.paste(jail, (0,0), mask=jail)
        final_buffer = BytesIO()
        final.save(final_buffer, 'png')
        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def jail(self, ctx, member : discord.Member=None):
        async with ctx.typing():
            if member == None:
                member = ctx.author                    
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.processjail, avatar_bytes)
            final_buffer = await self.client.loop.run_in_executor(None, fn)
            embed = discord.Embed(
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            file = discord.File(
                filename='image.png',
                fp=final_buffer
            )
            embed.set_image(
                url='attachment://image.png'
            )
            await ctx.send(file = file, embed = embed)
        
    @jail.error
    async def jail_error(self, ctx, error):
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

    @commands.command()
    async def meme(self, ctx):
        async with ctx.typing():
            reddit = asyncpraw.Reddit(
                client_id=PRAW_CLIENT_ID,
                client_secret=PRAW_CLIENT_SECRET,
                username='BiggieCheeseDotPy',
                password=PRAW_PASSWORD,
                user_agent='BiggieCheese'
            )
            subreddit = await reddit.subreddit('memes')
            all_subs = []
            hot = subreddit.hot(limit=50)
            async for submission in hot:
                all_subs.append(submission)
            random_sub = random.choice(all_subs)
            url = random_sub.url
            embed = discord.Embed(
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_image(
                url = url
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    async def poll(self, ctx, *, question):
        try:
            await ctx.message.delete()
        except:
            pass
        author = ctx.message.author
        embed = discord.Embed(
            description=f'{question}',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(
            name=f'{author.name}#{author.discriminator}',
            icon_url=author.avatar_url
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        message = await ctx.send(embed = embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!poll <question> or bc!help poll for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @staticmethod
    def processship(avatar1_bytes: bytes, avatar2_bytes: bytes, member1: discord.Member, member2: discord.Member, bot_id: int) -> BytesIO:
        if member1.id == bot_id:
            number = 100
        elif member2.id == bot_id:
            number = 100
        elif member1.bot:
            number = 0
        elif member2.bot:
            number = 0
        else:
            number = random.randint(0, 100)
        name1 = member2.name
        name2 = member1.name
        pfp1 = Image.open(BytesIO(avatar1_bytes)).convert('RGBA')
        pfp1 = pfp1.resize((500,500))
        pfp2 = Image.open(BytesIO(avatar2_bytes)).convert('RGBA')
        pfp2 = pfp2.resize((500,500))
        ship = Image.open(f'{twoup}/Images/ship.png').convert('RGBA')
        W, H = (415,185)
        textbox = Image.new('RGBA', (W,H))
        fontsize = 1
        img_fraction = 0.8
        font = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize)        
        while font.getsize(name2)[0] < img_fraction*textbox.size[0]:
            fontsize += 1
            font = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize)        
        draw = ImageDraw.Draw(textbox)
        w, h = font.getsize(name2)
        draw.text(((W-w)/2,(H-h)/2), name2, font=font)
        W2, H2 = (415,185)
        textbox2 = Image.new('RGBA', (W2,H2))
        fontsize2 = 1
        img_fraction2 = 0.8
        font2 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize2)        
        while font2.getsize(name1)[0] < img_fraction2*textbox2.size[0]:
            fontsize2 += 1
            font2 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize2)        
        draw2 = ImageDraw.Draw(textbox2)
        w2, h2 = font2.getsize(name1)
        draw2.text(((W2-w2)/2,(H2-h2)/2), name1, font=font2)
        W3, H3 = (400,200)
        textbox3 = Image.new('RGBA', (W3,H3))
        fontsize3 = 1
        img_fraction3 = 0.35
        font3 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize3)        
        while font3.getsize(f'{number}%')[0] < img_fraction3*textbox3.size[0]:
            fontsize3 += 1
            font3 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize3)        
        draw3 = ImageDraw.Draw(textbox3)
        w3, h3 = font3.getsize(f'{number}%')
        draw3.text(((W3-w3)/2,(H3-h3)/2), f'{number}%', font=font3)
        final = Image.new('RGBA',(1920,1080))
        final.paste(ship, (0,0))
        final.paste(textbox, (280,820), mask=textbox)
        final.paste(textbox2, (1220,70), mask=textbox2)
        final.paste(textbox3, (762,425), mask=textbox3)
        final.paste(pfp1, (300,290), mask=pfp1)
        final.paste(pfp2, (1120,290), mask=pfp2)
        if member1.bot:
            if not member1.id == bot_id:
                font4 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', 60)
                draw4 = ImageDraw.Draw(final)
                text = f'{member1.name} hates everyone'
                draw4.text((810,910), text, font=font4)
            else:
                font4 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', 60)
                draw4 = ImageDraw.Draw(final)
                text = 'Bot always loves you <3'
                draw4.text((810,910), text, font=font4)
        elif member2.bot:
            if not member2.id == bot_id:
                font4 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', 60)
                draw4 = ImageDraw.Draw(final)
                text = f'{member2.name} hates everyone'
                draw4.text((810,910), text, font=font4)
            else:
                font4 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', 60)
                draw4 = ImageDraw.Draw(final)
                text = 'Bot always loves you <3'
                draw4.text((810,910), text, font=font4)
        final_buffer = BytesIO()
        final.save(final_buffer, 'png')
        final_buffer.seek(0)
        return final_buffer
        

    @commands.command()
    async def ship(self, ctx, member1 : discord.Member, member2 : discord.Member=None):
        async with ctx.typing():
            if member2 is None:
                member2 = ctx.message.author        
            avatar1_bytes = await self.get_avatar(member1)
            avatar2_bytes = await self.get_avatar(member2)
            bot_id = self.client.user.id
            fn = partial(self.processship, avatar1_bytes, avatar2_bytes, member1, member2, bot_id)
            final_buffer = await self.client.loop.run_in_executor(None, fn)
            embed = discord.Embed(
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            file = discord.File(
                filename='image.png',
                fp=final_buffer
            )
            embed.set_image(
                url='attachment://image.png'
            )
            await ctx.send(file = file, embed = embed)
        
    @ship.error
    async def ship_error(self, ctx, error):
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
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!ship [@user1/id] <@user2/id> or bc!help ship for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    bot.sniped_messages = {}
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        bot.sniped_messages[message.guild.id] = (message.content, message.author, message.channel, message.created_at)
        
    @commands.command()
    async def snipe(self, ctx):
        try:
            contents, author, channel, time = bot.sniped_messages[ctx.guild.id]
            formattedtime = time.strftime(f'%Y/%m/%d')
            embed = discord.Embed(
                description=contents,
                color=(0xFFFF00)
            )
            embed.set_author(
                name=f'{author.name}#{author.discriminator}',
                icon_url=author.avatar_url
            )
            embed.set_footer(
                text=f'Deleted in #{channel.name} on {formattedtime}.',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        except:
            embed = discord.Embed(
                title='**:x: There is nothing to snipe!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    bot.edit_sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        bot.edit_sniped_messages[message_before.guild.id] = (message_before.content, message_after.content, message_before.author, message_before.channel, message_after.created_at)

    @commands.command(aliases=['esnipe'])
    async def editsnipe(self, ctx):
        try:
            old_contents, new_contents, author, channel, time = bot.edit_sniped_messages[ctx.guild.id]
            formattedtime = time.strftime(f'%Y/%m/%d')
            embed = discord.Embed(
                description=f'**Old:**\n{old_contents}\n\n**New:**\n{new_contents}',
                color=(0xFFFF00)
            )
            embed.set_author(
                name=f'{author.name}#{author.discriminator}',
                icon_url=author.avatar_url
            )
            embed.set_footer(
                text=f'Edited in #{channel.name} on {formattedtime}.',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        except:
            embed = discord.Embed(
                title='**:x: There is nothing to snipe!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @staticmethod
    def processwanted(avatar_bytes: bytes) -> BytesIO:
        pfp = Image.open(BytesIO(avatar_bytes))
        pfp = pfp.resize((650,650))
        wanted = Image.open(fp=f'{twoup}/Images/wanted.png')
        final = Image.new('RGBA', (1200,1600), (0, 0, 0, 0))
        final.paste(wanted, (0,0))
        final.paste(pfp, (275,500), mask=pfp)
        final_buffer = BytesIO()
        final.save(final_buffer, 'png')
        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def wanted(self, ctx, member : discord.Member=None):
        async with ctx.typing():
            if member == None:
                member = ctx.author
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.processwanted, avatar_bytes)
            final_buffer = await self.client.loop.run_in_executor(None, fn)
            embed = discord.Embed(
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            file = discord.File(
                filename='image.png',
                fp=final_buffer
            )
            embed.set_image(
                url='attachment://image.png'
            )
            await ctx.send(file = file, embed = embed)
        
    @wanted.error
    async def wanted_error(self, ctx, error):
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

    @commands.command()
    async def topic(self, ctx):
        seed = random.randrange(0, len(topics))
        topic = topics[seed]
        await ctx.send(topic)

    @commands.command(aliases=['propose'])
    async def marry(self, ctx, member : discord.Member):
        author_id = ctx.message.author.id
        target_id = member.id
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot marry yourself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if author_id in self.pending:
            embed = discord.Embed(
                title='**:x: You already have a pending proposal.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_id in self.pending:
            embed = discord.Embed(
                title='**:x: This user already has a pending proposal.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        SQL.execute(f'select User_One from Marriages where User_One="{author_id}"')
        author_ismarried = SQL.fetchone()
        if author_ismarried is not None:
            embed = discord.Embed(
                title='**:x: You are already married.**',
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
            SQL.execute(f'select User_One from Marriages where User_One="{target_id}"')
            target_ismarried = SQL.fetchone()
            if target_ismarried is not None:
                embed = discord.Embed(
                    title=f'**:x: {member.name} is already married.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                self.pending.append(target_id)
                self.pending.append(author_id)
                embed = discord.Embed(
                    title=f'**{ctx.message.author.name} proposed to {member.name}.**',
                    description='They have one minute to respond by typing `yes` or `no`.',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
                def check(m):
                    return m.channel == ctx.channel and m.author == member and m.content.lower() in ['yes', 'no']
                try:
                    answer = await self.client.wait_for('message', timeout=60, check=check)
                    self.pending.remove(target_id)
                    self.pending.remove(author_id)
                except asyncio.TimeoutError:
                    self.pending.remove(target_id)
                    self.pending.remove(author_id)
                    return
                answer = answer.content
                if answer.lower() == 'yes':
                    time = datetime.datetime.now()
                    SQL.execute(f'insert into Marriages(User_One, User_Two, Date) values(?,?,?)',
                                (author_id, target_id, time))
                    db.commit()
                    SQL.execute(f'insert into Marriages(User_One, User_Two, Date) values(?,?,?)',
                                (target_id, author_id, time))
                    db.commit()
                    embed = discord.Embed(
                        title=f'**{ctx.message.author.name} and {member.name} are now happily married!**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                elif answer.lower() == 'no':
                    embed = discord.Embed(
                        title=f'**{member.name} rejected {ctx.message.author.name} </3**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)

    @commands.command()
    async def divorce(self, ctx):
        author_id = ctx.message.author.id
        SQL.execute(f'select User_One from Marriages where User_One="{author_id}"')
        author_ismarried = SQL.fetchone()
        if author_ismarried is None:
            embed = discord.Embed(
                title='**:x: You are not married.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            SQL.execute(f'select User_Two from Marriages where User_One="{author_id}"')
            user_id = SQL.fetchone()
            user = self.client.get_user(user_id[0])
            SQL.execute(f'delete from Marriages where User_One="{author_id}"')
            db.commit()
            SQL.execute(f'delete from Marriages where User_One="{user_id[0]}"')
            db.commit()
            embed = discord.Embed(
                title=f'**{ctx.message.author.name} divorced {user.name} </3**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @staticmethod
    def processmarriage(avatar1_bytes: bytes, avatar2_bytes: bytes, name1: str, name2: str, timeformatted: str) -> BytesIO:
        pfp1 = Image.open(BytesIO(avatar1_bytes)).convert('RGBA')
        pfp1 = pfp1.resize((500,500))
        pfp2 = Image.open(BytesIO(avatar2_bytes)).convert('RGBA')
        pfp2 = pfp2.resize((500,500))
        number = 100
        ship = Image.open(f'{twoup}/Images/ship.png').convert('RGBA')
        W, H = (415,185)
        textbox = Image.new('RGBA', (W,H))
        fontsize = 1
        img_fraction = 0.8
        font = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize)
        while font.getsize(name2)[0] < img_fraction*textbox.size[0]:
            fontsize += 1
            font = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize)
        draw = ImageDraw.Draw(textbox)
        w, h = font.getsize(name2)
        draw.text(((W-w)/2,(H-h)/2), name2, font=font)
        W2, H2 = (415,185)
        textbox2 = Image.new('RGBA', (W2,H2))
        fontsize2 = 1
        img_fraction2 = 0.8
        font2 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize2)
        while font2.getsize(name1)[0] < img_fraction2*textbox2.size[0]:
            fontsize2 += 1
            font2 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize2)
        draw2 = ImageDraw.Draw(textbox2)
        w2, h2 = font2.getsize(name1)
        draw2.text(((W2-w2)/2,(H2-h2)/2), name1, font=font2)
        W3, H3 = (400,200)
        textbox3 = Image.new('RGBA', (W3,H3))
        fontsize3 = 1
        img_fraction3 = 0.35
        font3 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize3)
        while font3.getsize(f'{number}%')[0] < img_fraction3*textbox3.size[0]:
            fontsize3 += 1
            font3 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', fontsize3)
        draw3 = ImageDraw.Draw(textbox3)
        w3, h3 = font3.getsize(f'{number}%')
        draw3.text(((W3-w3)/2,(H3-h3)/2), f'{number}%', font=font3)
        final = Image.new('RGBA',(1920,1080))
        final.paste(ship, (0,0))
        final.paste(textbox, (280,820), mask=textbox)
        final.paste(textbox2, (1220,70), mask=textbox2)
        final.paste(textbox3, (760,425), mask=textbox3)
        font4 = ImageFont.truetype(f'{twoup}/Fonts/boldfont.ttf', 60)
        draw4 = ImageDraw.Draw(final)
        text = timeformatted
        draw4.text((80,110), text, font=font4)
        final.paste(pfp1, (300,290), mask=pfp1)
        final.paste(pfp2, (1120,290), mask=pfp2)
        final_buffer = BytesIO()
        final.save(final_buffer, 'png')
        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def marriage(self, ctx, member : discord.Member=None):
        async with ctx.typing():
            if member is None:
                author_id = ctx.message.author.id
                author = ctx.message.author
                author_name = ctx.message.author.name
            else:
                author_id = member.id
                author = member
                author_name = member.name
            SQL.execute(f'select User_One from Marriages where User_One="{author_id}"')
            author_ismarried = SQL.fetchone()
            if author_ismarried is None:
                if member is None:
                    embed = discord.Embed(
                        title='**:x: You are not married.**',
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
                        title='**:x: This user is not married.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
            else:
                SQL.execute(f'select User_Two from Marriages where User_One="{author_id}"')
                user_id = SQL.fetchone()
                user = self.client.get_user(user_id[0])
                user_name = user.name
                SQL.execute(f'select Date from Marriages where User_One="{author_id}"')
                time = SQL.fetchone()
                timeobject = datetime.datetime.strptime(time[0], f'%Y-%m-%d %H:%M:%S.%f')
                timeformatted = timeobject.strftime('Married since: %d\' %B %Y')
                name1 = user_name
                name2 = author_name
                avatar1_bytes = await self.get_avatar(author)
                avatar2_bytes = await self.get_avatar(user)
                fn = partial(self.processmarriage, avatar1_bytes, avatar2_bytes, name1, name2, timeformatted)
                final_buffer = await self.client.loop.run_in_executor(None, fn)
                embed = discord.Embed(
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                file = discord.File(
                    filename='image.png',
                    fp=final_buffer
                )
                embed.set_image(
                    url='attachment://image.png'
                )
                await ctx.send(file = file, embed = embed)

def setup(client):
    client.add_cog(Fun(client))