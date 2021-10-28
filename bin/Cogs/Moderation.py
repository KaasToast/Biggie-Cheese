import discord
import datetime
import re
import os
import sqlite3

from humanfriendly import format_timespan
from discord.ext import commands
from discord.ext.commands import *
from pathlib import Path

DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()

databasepath = f'{twoup}/Databases/Expirations.db'
db = sqlite3.connect(os.path.join(DIR, databasepath))
SQL = db.cursor()
SQL.execute('create table if not exists Expirations('
                    '"Type" TEXT, '
                    '"User_ID" INTEGER, '
                    '"Server_ID" INTEGER, '
                    '"Expiration" TEXT'
                    ')')

databasepath2 = f'{twoup}/Databases/Infractions.db'
db2 = sqlite3.connect(os.path.join(DIR, databasepath2))
SQL2 = db2.cursor()
SQL2.execute('create table if not exists Infractions('
                    '"User_ID" INTEGER, '
                    '"Server_ID" INTEGER, '
                    '"Description" TEXT, '
                    '"Date" TEXT'
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

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot ban yourself!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member.id == self.client.user.id:
            embed = discord.Embed(
                title='**:x: I cannot ban myself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot ban that user.**',
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
            SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
            modlog = SQL3.fetchone()
            if modlog is not None:
                if modlog[0] != 'None':
                    channel = self.client.get_channel(int(modlog[0]))
                    embed = discord.Embed(
                        title='**User banned**',
                        description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\nDuration: Permanent\n\n**Reason:**\n{reason}',
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
            sqltype = 'Ban'
            unmutedate = 'Permanent'
            SQL.execute('insert into Expirations(Type, User_ID, Server_ID, Expiration) values(?,?,?,?)',
                        (sqltype, member.id, ctx.guild.id, unmutedate))
            db.commit()
            embed = discord.Embed(
                title=f'**You were banned from {ctx.guild.name} for: {reason}.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            try:
                await member.send(embed = embed)
            except:
                pass
            embed = discord.Embed(
                title=f'**:white_check_mark: {member.name} was banned!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            await member.ban(reason = reason)
        
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!ban <@user/id> [reason] or bc!help ban for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing the ban members permission.**',
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

    @commands.command(aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount):
        if amount.isdigit():
            try:
                await ctx.channel.purge(limit=int(amount) + 1)
                SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
                modlog = SQL3.fetchone()
                if modlog is not None:
                    if modlog[0] != 'None':
                        channel = self.client.get_channel(int(modlog[0]))
                        embed = discord.Embed(
                            title='**Channel purged**',
                            description=f'Moderator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\nMessages: {amount}',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_thumbnail(
                            url=ctx.author.avatar_url
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await channel.send(embed = embed)
            except discord.Forbidden:
                embed = discord.Embed(
                    title='**:x: I am missing the manage messages permission.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(text='\u200b', icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png')
                await ctx.send(embed = embed)
                return
            embed = discord.Embed(
                title=f'**:white_check_mark: Succesfully deleted {amount} messages!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed, delete_after = 3)        
        if not amount.isdigit():
            embed = discord.Embed(
                title='**:x: Value must be 1 or higher.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!clear <amount> or bc!help clear for more info.**',
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
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break     
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot kick yourself!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member.id == self.client.user.id:
            embed = discord.Embed(
                title='**:x: I cannot kick myself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot kick that user.**',
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
            SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
            modlog = SQL3.fetchone()
            if modlog is not None:
                if modlog[0] != 'None':
                    channel = self.client.get_channel(int(modlog[0]))
                    embed = discord.Embed(
                        title='**User kicked**',
                        description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\n\n**Reason:**\n{reason}',
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
            sqltype = 'Kick'
            unmutedate = 'Permanent'
            SQL.execute('insert into Expirations(Type, User_ID, Server_ID, Expiration) values(?,?,?,?)',
                        (sqltype, member.id, ctx.guild.id, unmutedate))
            db.commit()
            embed = discord.Embed(
                title=f'**You were kicked from {ctx.guild.name} for: {reason}.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            try:
                await member.send(embed = embed)
            except:
                pass
            embed = discord.Embed(
                title=f'**:white_check_mark: {member.name} was kicked!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            await member.kick(reason = reason)
    
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!kick <@user/id> [reason] or bc!help kick for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing the kick members permission.**',
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

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def lock(self, ctx):
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog is not None:
            if modlog[0] != 'None':
                channel = self.client.get_channel(int(modlog[0]))
                embed = discord.Embed(
                    title='**Channel locked**',
                    description=f'Moderator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(
                    url=ctx.author.avatar_url
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await channel.send(embed = embed)
        embed = discord.Embed(
            title='**:white_check_mark: Channel locked!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite = overwrite)
        
    @lock.error
    async def lock_error(self, ctx, error):
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing the manage channels permission.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True)
    async def mutedrole(self, ctx, argument):
        if not argument.lower() in ['create', 'delete']:
            embed = discord.Embed(
                title='**:x: Use: bc!mutedrole <create/delete> or bc!help mutedrole for more info.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if argument.lower() == 'create':
            mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
            if mutedrole:
                embed = discord.Embed(
                    title='**:x: This server already has a muted role.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                async with ctx.typing():
                    mutedrole = await ctx.guild.create_role(name='Biggie Mute')
                    for channel in ctx.guild.channels:
                        await channel.set_permissions(mutedrole, speak=False, send_messages=False, add_reactions=False, stream=False)
                    embed = discord.Embed(
                        title='**:white_check_mark: Biggie Mute role created.**',
                        description='**Please check the following:**\n- The role must be above users that need to be able to be muted.\n- Biggie Cheese\'s role must be higher than the muted role.\n- Roles of users that need to be immune to mutes must be higher than the muted role.',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
        elif argument.lower() == 'delete':
            mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
            if not mutedrole:
                embed = discord.Embed(
                    title='**:x: This server does not have a muted role.**',
                    description='You can set one with bc!mutedrole create',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                try:
                    await mutedrole.delete()
                    embed = discord.Embed(
                        title='**:white_check_mark: Delete muted role.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)
                except discord.Forbidden:
                    embed = discord.Embed(
                        title='**:x: This role is too high for me to edit.**',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await ctx.send(embed = embed)

    @mutedrole.error
    async def mutedrole_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!mutedrole <create/delete> or bc!help mutedrole for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing one or more of the following permissions:**',
                description='- manage roles\n- manage channels',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def mute(self, ctx, member : discord.Member, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        bot_member = ctx.guild.get_member(self.client.user.id)
        if not mutedrole:
            embed = discord.Embed(
                title='**:x: This server does not have a muted role.**',
                description='You can set one with bc!mutedrole create',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if mutedrole.position > bot_member.top_role.position:
            embed = discord.Embed(
                title='**:x: Mutedrole is set too high so I cannot access it.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break     
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot mute yourself!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member.id == self.client.user.id:
            embed = discord.Embed(
                title='**:x: I cannot mute myself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot mute that user.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        if mutedrole in member.roles:
            embed = discord.Embed(
                title='**:x: This user is already muted.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog is not None:
            if modlog[0] != 'None':
                channel = self.client.get_channel(int(modlog[0]))
                embed = discord.Embed(
                    title='**User muted**',
                    description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\nDuration: Permanent\n\n**Reason:**\n{reason}',
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
        sqltype = 'Mute'
        unmutedate = 'Permanent'
        SQL.execute('insert into Expirations(Type, User_ID, Server_ID, Expiration) values(?,?,?,?)',
                    (sqltype, member.id, ctx.guild.id, unmutedate))
        db.commit()
        embed = discord.Embed(
            title=f'**You were muted in {ctx.guild.name} for: {reason}.**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        try:
            await member.send(embed = embed)
        except:
            pass
        embed = discord.Embed(
            title=f'**:white_check_mark: {member.name} was muted!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        await member.add_roles(mutedrole, reason = reason)
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        for channel in ctx.guild.channels:
            await channel.set_permissions(mutedrole, speak=False, send_messages=False, add_reactions=False, stream=False)
        
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!mute <@user/id> [reason] or bc!help mute for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing one or more of the following permissions:**',
                description='- manage roles',
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
            
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User):
        try:
            await ctx.guild.unban(user)
            SQL.execute(f'delete from Expirations where Server_ID="{ctx.guild.id}" and User_ID="{user.id}" and Type="Ban"')
            db.commit()
            embed = discord.Embed(
                title=f'**:white_check_mark: Unbanned {user.name}!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
            modlog = SQL3.fetchone()
            if modlog is not None:
                if modlog[0] != 'None':
                    channel = self.client.get_channel(int(modlog[0]))
                    embed = discord.Embed(
                        title='**User unbanned**',
                        description=f'User: {user.mention}\nID: {user.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=user.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)
        except:
            embed = discord.Embed(
                title='**:x: This user is not banned.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
    
    @unban.error
    async def unban_error(self, ctx, error):      
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!unban <id> or bc!help unban for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing the ban members permission.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        if isinstance(error, UserNotFound):
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
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog is not None:
            if modlog[0] != 'None':
                channel = self.client.get_channel(int(modlog[0]))
                embed = discord.Embed(
                    title='**Channel unlocked**',
                    description=f'Moderator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(
                    url=ctx.author.avatar_url
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await channel.send(embed = embed)
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        embed = discord.Embed(
            title='**:white_check_mark: Channel unlocked!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        
    @unlock.error
    async def unlock_error(self, ctx, error):
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing the manage channels permission.**',
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
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True, mute_members=True)
    async def unmute(self, ctx, member : discord.Member):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        if not mutedrole in target_roles:
            embed = discord.Embed(
                title=f'**:x: {member.name} is not muted.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot unmute that user.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        await member.remove_roles(mutedrole)
        SQL.execute(f'delete from Expirations where Server_ID="{ctx.guild.id}" and User_ID="{member.id}" and Type="Mute"')
        db.commit()
        embed = discord.Embed(
            title=f'**:white_check_mark: Unmuted {member.name}!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog is not None:
            if modlog[0] != 'None':
                channel = self.client.get_channel(int(modlog[0]))
                embed = discord.Embed(
                    title='**User unmuted**',
                    description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}',
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
        
    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!unmute <@user/id> or bc!help unmute for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing one or more of the following permissions:**',
                description='- manage roles\n- manage channels\n- mute members',
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

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member : discord.Member, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot warn yourself!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member.id == self.client.user.id:
            embed = discord.Embed(
                title='**:x: I cannot warn myself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_pos > author_pos:
            embed = discord.Embed(
                title='**:x: You cannot warn that user.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        SQL2.execute(f'select Date from Infractions where User_ID="{member.id}" and Server_ID="{ctx.guild.id}"')
        length = SQL2.fetchall()
        if len(length) == 10:
            embed = discord.Embed(
                title='**:x: This user already has 10 warns.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
        modlog = SQL3.fetchone()
        if modlog is not None:
            if modlog[0] != 'None':
                channel = self.client.get_channel(int(modlog[0]))
                embed = discord.Embed(
                    title='**User warned**',
                    description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\n\n**Reason:**\n{reason}',
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
        embed = discord.Embed(
            title=f'**You were warned in {ctx.guild.name} for: {reason}.**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        try:
            await member.send(embed = embed)
        except:
            pass
        embed = discord.Embed(
            title=f'**:white_check_mark: {member.name} was warned!**',
            color=(0xFFFF00),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text='\u200b',
            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
        )
        await ctx.send(embed = embed)
        SQL2.execute(f'insert into Infractions(User_ID, Server_ID, Description, Date) values(?,?,?,?)',
                    (member.id, ctx.guild.id, reason, datetime.datetime.now()))
        db2.commit()
    
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!warn <@user/id> [reason] or bc!help warn for more info.**',
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
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def tempban(self, ctx, member : discord.Member, duration, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot ban yourself!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member.id == self.client.user.id:
            embed = discord.Embed(
                title='**:x: I cannot ban myself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot ban that user.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
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
        unbandate = datetime.datetime.utcnow() + datetime.timedelta(seconds = timestr_to_seconds(duration))
        if timestr_to_seconds(duration) == 0:
            embed = discord.Embed(
                title='**:x: Use: bc!tempban <@user/id> <duration> [reason] or bc!help tempban for more info.**',
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
                title='**:x: Cannot ban user for longer than 100 years.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            formattedtime = format_timespan(timestr_to_seconds(duration))
            SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
            modlog = SQL3.fetchone()
            if modlog is not None:
                if modlog[0] != 'None':
                    channel = self.client.get_channel(int(modlog[0]))
                    embed = discord.Embed(
                        title='**User banned**',
                        description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\nDuration: {formattedtime}\n\n**Reason:**\n{reason}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=ctx.author.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)
            sqltype = 'Ban'
            SQL.execute('insert into Expirations(Type, User_ID, Server_ID, Expiration) values(?,?,?,?)',
                        (sqltype, member.id, ctx.guild.id, unbandate))
            db.commit()
            embed = discord.Embed(
                title=f'**You were banned for {formattedtime} in {ctx.guild.name} for: {reason}.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            try:
                await member.send(embed = embed)
            except:
                pass
            embed = discord.Embed(
                title=f'**:white_check_mark: {member.name} was banned for {formattedtime}!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            await member.ban(reason = reason)

    @tempban.error
    async def tempban_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!tempban <@user/id> <duration> [reason] or bc!help tempban for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing the ban members permission.**',
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

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True, mute_members=True)
    async def tempmute(self, ctx, member : discord.Member, duration, *, reason=None):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        bot_member = ctx.guild.get_member(self.client.user.id)
        if not mutedrole:
            embed = discord.Embed(
                title='**:x: This server does not have a muted role.**',
                description='You can set one with bc!mutedrole create',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if mutedrole.position > bot_member.top_role.position:
            embed = discord.Embed(
                title='**:x: Mutedrole is set too high so I cannot access it.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if member == ctx.message.author:
            embed = discord.Embed(
                title='**:x: You cannot mute yourself!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if member.id == self.client.user.id:
            embed = discord.Embed(
                title='**:x: I cannot mute myself.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot mute that user.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        if mutedrole in member.roles:
            embed = discord.Embed(
                title='**:x: This user is already muted.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
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
        unmutedate = datetime.datetime.utcnow() + datetime.timedelta(seconds = timestr_to_seconds(duration))
        if timestr_to_seconds(duration) == 0:
            embed = discord.Embed(
                title='**:x: Use: bc!tempmute <@user/id> <duration> [reason] or bc!help tempmute for more info.**',
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
                title='**:x: Cannot mute user for longer than 100 years.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            formattedtime = format_timespan(timestr_to_seconds(duration))
            SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
            modlog = SQL3.fetchone()
            if modlog is not None:
                if modlog[0] != 'None':
                    channel = self.client.get_channel(int(modlog[0]))
                    embed = discord.Embed(
                        title='**User muted**',
                        description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\nDuration: {formattedtime}\n\n**Reason:**\n{reason}',
                        color=(0xFFFF00),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.set_thumbnail(
                        url=ctx.author.avatar_url
                    )
                    embed.set_footer(
                        text='\u200b',
                        icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                    )
                    await channel.send(embed = embed)
            sqltype = 'Mute'
            SQL.execute('insert into Expirations(Type, User_ID, Server_ID, Expiration) values(?,?,?,?)',
                        (sqltype, member.id, ctx.guild.id, unmutedate))
            db.commit()
            embed = discord.Embed(
                title=f'**You were muted for {formattedtime} in {ctx.guild.name} for: {reason}.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            try:
                await member.send(embed = embed)
            except:
                pass
            embed = discord.Embed(
                title=f'**:white_check_mark: {member.name} was muted for {formattedtime}!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            await member.add_roles(mutedrole, reason = reason)
            mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
            for channel in ctx.guild.channels:
                await channel.set_permissions(mutedrole, speak=False, send_messages=False, add_reactions=False, stream=False)

    @tempmute.error
    async def tempmute_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!tempmute <@user/id> <duration> [reason] or bc!help tempmute for more info.**',
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
        if isinstance(error, BotMissingPermissions):
            embed = discord.Embed(
                title='**:x: I am missing one or more of the following permissions:**',
                description='- manage roles\n- manage channels\n- mute members',
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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server_id = member.guild.id
        user_id = member.id
        SQL.execute(f'select User_ID from Expirations where Server_ID="{server_id}" and User_ID="{user_id}" and Type="Mute"')
        table_exists = SQL.fetchone()
        if table_exists is None:
            return
        else:
            mutedrole = discord.utils.get(member.guild.roles, name='Biggie Mute')
            if not mutedrole:
                bcrole = discord.utils.get(member.guild.roles, name='Biggie Cheese')
                rolepos = bcrole.position
                mutedrole = await member.guild.create_role(name='Biggie Mute')
                await mutedrole.edit(position=rolepos)
                for channel in member.guild.channels:
                    await channel.set_permissions(mutedrole, speak=False, send_messages=False, add_reactions=False, stream=False)
            await member.add_roles(mutedrole)
            for channel in member.guild.channels:
                    await channel.set_permissions(mutedrole, speak=False, send_messages=False, add_reactions=False, stream=False)

    @commands.command(aliases=['infractions'])
    @commands.has_permissions(kick_members=True)
    async def warns(self, ctx, member : discord.Member):
        user_id = member.id
        server_id = ctx.guild.id
        results = []
        SQL2.execute(f'select Date from Infractions where User_ID="{user_id}" and Server_ID="{server_id}"')
        infractiondate = SQL2.fetchall()
        dates = []
        for entry in infractiondate:
            dates.append(entry[0])
        for date in dates:
            SQL2.execute(f'select Description from Infractions where User_ID="{user_id}" and Server_ID="{server_id}" and Date="{date}"')
            infractiondescription = SQL2.fetchone()
            timeobject = round(datetime.datetime.strptime(date, f'%Y-%m-%d %H:%M:%S.%f').timestamp())
            formatted = f'<t:{timeobject}>'
            results.append(f'{formatted} • {infractiondescription[0]}')
        length = len(results)
        results.reverse()
        final = []
        for i, result in enumerate(results, 1):
            final.append(f'{i}. {result}')
        if length == 0:
            embed = discord.Embed(
                title=f'**:x: This user doesn\'t have any infractions.**',
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
                title=f'**{member.name}\'s infractions:**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            embed.add_field(
                name='Total:',
                value=f'{length} infraction(s)',
                inline=False
            )
            embed.add_field(
                name='Last 10 infractions:',
                value='\n'.join(final),
                inline=False
            )
            await ctx.send(embed = embed)

    @warns.error
    async def warns_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!warns <@user/id> or bc!help warns for more info.**',
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

    @commands.command(aliases=['clearinfractions'])
    @commands.has_permissions(kick_members=True)
    async def clearwarns(self, ctx, member : discord.Member, id=None):
        user_id = member.id
        server_id = ctx.guild.id
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot clear that users warns.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        SQL2.execute(f'select Description from Infractions where User_ID="{user_id}" and Server_ID="{server_id}"')
        table_exists = SQL2.fetchone()
        if table_exists is None:
            embed = discord.Embed(
                title=f'**:x: This user doesn\'t have any infractions.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
            return
        if id is None:
            SQL2.execute(f'delete from Infractions where User_ID="{user_id}" and Server_ID="{server_id}"')
            db2.commit()
            embed = discord.Embed(
                title=f'**:white_check_mark: Removed {member.name}\'s infractions.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        elif not id.isdigit():
            embed = discord.Embed(
                title='**:x: Use: bc!clearwarns <@user/id> [warn-id]',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        else:
            SQL2.execute(f'select Date from Infractions where User_ID="{user_id}" and Server_ID="{server_id}"')
            infractiondate = SQL2.fetchall()
            if len(infractiondate) < int(id) or int(id) < 1:
                embed = discord.Embed(
                    title='**:x: Use: bc!clearwarns <@user/id> [warn-id]',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
            else:
                entries = []
                for entry in infractiondate:
                    entries.append(entry[0])
                entries.reverse()
                SQL2.execute(f'delete from Infractions where User_ID="{user_id}" and Server_ID="{server_id}" and Date="{entries[int(id) - 1]}"')
                db2.commit()
                embed = discord.Embed(
                    title=f'**:white_check_mark: Removed 1 of {member.name}\'s infractions.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(
                    text='\u200b',
                    icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                )
                await ctx.send(embed = embed)
        
    @clearwarns.error
    async def clearwarns_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!clearwarns <@user/id> [warn-id] or bc!help clearwarns for more info.**',
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

    @commands.command(aliases=['purgeuser'])
    @commands.has_permissions(manage_messages=True)
    async def clearuser(self, ctx, member : discord.Member, amount):
        mutedrole = discord.utils.get(ctx.guild.roles, name='Biggie Mute')
        author_pos = ctx.author.top_role.position
        target_roles = member.roles
        for role in reversed(target_roles):
            if role == mutedrole:
                continue
            else:
                target_pos = role.position
                break
        if target_pos >= author_pos:
            embed = discord.Embed(
                title='**:x: You cannot clear messages from that user.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)
        elif amount.isdigit():
            try:
                msg = []
                async for m in ctx.channel.history():
                    if len(msg) >= int(amount):
                        break
                    if m.author == member:
                        msg.append(m)
                await ctx.channel.delete_messages(msg)
                SQL3.execute(f'select ModLog from Logging where Server_ID="{ctx.guild.id}"')
                modlog = SQL3.fetchone()
                if modlog is not None:
                    if modlog[0] != 'None':
                        channel = self.client.get_channel(int(modlog[0]))
                        embed = discord.Embed(
                            title='**User purged**',
                            description=f'User: {member.mention}\nID: {member.id}\nModerator: {ctx.author.mention}\nModerator ID: {ctx.author.id}\nChannel: {ctx.channel.mention}\nMessages: {amount}',
                            color=(0xFFFF00),
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.set_thumbnail(
                            url=ctx.author.avatar_url
                        )
                        embed.set_footer(
                            text='\u200b',
                            icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
                        )
                        await channel.send(embed = embed)
            except discord.Forbidden:
                embed = discord.Embed(
                    title='**:x: I am missing the manage messages permission.**',
                    color=(0xFFFF00),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(text='\u200b', icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png')
                await ctx.send(embed = embed)
                return
            try:
                await ctx.message.delete()
            except:
                pass
            embed = discord.Embed(
                title=f'**:white_check_mark: Succesfully deleted {amount} messages from {member.name}!**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed, delete_after = 3)
        else:
            embed = discord.Embed(
                title='**:x: Value must be 1 or higher.**',
                color=(0xFFFF00),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(
                text='\u200b',
                icon_url='https://cdn.discordapp.com/attachments/818581089017790479/827483570398298172/biggiecheese.png'
            )
            await ctx.send(embed = embed)

    @clearuser.error
    async def clearuser_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = discord.Embed(
                title='**:x: Use: bc!clearuser <@user/id> <amount> or bc!help clearuser for more info.**',
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

def setup(client):
    client.add_cog(Moderation(client))