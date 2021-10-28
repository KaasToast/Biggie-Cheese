import discord
import sqlite3
import datetime
import os

from discord.ext import commands, tasks
from discord.ext.commands import *
from pathlib import Path

DIR = os.path.dirname(__file__)
path = Path(__file__)
oneup = path.parent.absolute()
twoup = oneup.parent.absolute()
threeup = twoup.parent.absolute()

moderationdatabasepath = f'{twoup}/Databases/Expirations.db'
moderationdb = sqlite3.connect(os.path.join(DIR, moderationdatabasepath))
moderationSQL = moderationdb.cursor()
moderationSQL.execute('create table if not exists Expirations('
                    '"Type" TEXT, '
                    '"User_ID" INTEGER, '
                    '"Server_ID" INTEGER, '
                    '"Expiration" TEXT'
                    ')')

economicsdatabasepath = f'{twoup}/Databases/Economics.db'
economicsdb = sqlite3.connect(os.path.join(DIR, economicsdatabasepath))
economicsSQL = economicsdb.cursor()
economicsSQL.execute('create table if not exists Economy('
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
reminddatabasepath = f'{twoup}/Databases/Reminders.db'
reminddb = sqlite3.connect(os.path.join(DIR, reminddatabasepath))
remindSQL = reminddb.cursor()
remindSQL.execute('create table if not exists Reminders('
                    '"User_ID" INTEGER, '
                    '"Reason" TEXT, '
                    '"Date" TEXT'
                    ')')

class Loops(commands.Cog):

    def __init__(self, client):
        self.client = client
        if not self.main_loop.is_running():
            self.main_loop.start()

    def cog_unload(self):
        self.main_loop.cancel()
   
    @tasks.loop(minutes=1.0)
    async def main_loop(self):
        economicsSQL.execute('select User_ID from Economy')
        IDs = economicsSQL.fetchall()
        for id in IDs:
            economicsSQL.execute(f'select DailyStreakExpiration from Economy where User_ID="{int(id[0])}"')
            expiration = economicsSQL.fetchone()
            if not expiration or expiration[0] == 'None':
                pass
            else:
                formatted = datetime.datetime.strptime(expiration[0], f'%Y-%m-%d %H:%M:%S.%f')
                if formatted < datetime.datetime.utcnow():
                    newstreak = 0
                    newstreakexpiration = str(None)
                    economicsSQL.execute(f'update Economy set DailyStreak="{newstreak}" where User_ID="{int(id[0])}"')
                    economicsdb.commit()
                    economicsSQL.execute(f'update Economy set DailyStreakExpiration="{newstreakexpiration}" where User_ID="{int(id[0])}"')
                    economicsdb.commit()
            economicsSQL.execute(f'select VoteStreakExpiration from Economy where User_ID="{int(id[0])}"')
            expiration = economicsSQL.fetchone()
            if not expiration or expiration[0] == 'None':
                pass
            else:
                formatted = datetime.datetime.strptime(expiration[0], f'%Y-%m-%d %H:%M:%S.%f')
                if formatted < datetime.datetime.utcnow():
                    newstreak = 0
                    newstreakexpiration = None
                    economicsSQL.execute(f'update Economy set VoteStreak="{newstreak}" where User_ID="{int(id[0])}"')
                    economicsdb.commit()
                    economicsSQL.execute(f'update Economy set VoteStreakExpiration="{newstreakexpiration}" where User_ID="{int(id[0])}"')
                    economicsdb.commit()
        moderationSQL.execute(f'select Server_ID from Expirations')
        IDs = moderationSQL.fetchall()
        for id in IDs:
            guild = self.client.get_guild(int(id[0]))
            moderationSQL.execute(f'select User_ID from Expirations where Server_ID="{guild.id}" and Type="Ban"')
            guildbans = moderationSQL.fetchall()
            if not guildbans:
                pass
            else:
                length = len(guildbans) - 1
                while length >= 0:
                    moderationSQL.execute(f'select Expiration from Expirations where Server_ID="{guild.id}" and User_ID="{guildbans[length][0]}" and Type="Ban"')
                    expiration = moderationSQL.fetchone()
                    user = self.client.get_user(int(guildbans[length][0]))
                    if user is None:
                        pass
                    else:
                        if expiration[0] == 'Permanent':
                            try:
                                await guild.fetch_ban(user)
                            except discord.NotFound:
                                moderationSQL.execute(f'delete from Expirations where Server_ID="{guild.id}" and User_ID="{user.id}" and Type="Ban"')
                                moderationdb.commit()
                        else:
                            try:
                                await guild.fetch_ban(user)
                            except discord.NotFound:
                                moderationSQL.execute(f'delete from Expirations where Server_ID="{guild.id}" and User_ID="{user.id}" and Type="Ban"')
                                moderationdb.commit()
                            timeobj = datetime.datetime.strptime(expiration[0], '%Y-%m-%d %H:%M:%S.%f')
                            if timeobj > datetime.datetime.utcnow():
                                pass
                            else:
                                await guild.unban(user)
                                moderationSQL.execute(f'delete from Expirations where Server_ID="{guild.id}" and User_ID="{user.id}" and Type="Ban"')
                                moderationdb.commit()
                    length = length - 1
            moderationSQL.execute(f'select User_ID from Expirations where Server_ID="{guild.id}" and Type="Mute"')
            guildmutes = moderationSQL.fetchall()
            if not guildmutes:
                pass
            else:
                length = len(guildmutes) - 1
                while length >= 0:
                    moderationSQL.execute(f'select Expiration from Expirations where Server_ID="{guild.id}" and User_ID="{guildmutes[length][0]}" and Type="Mute"')
                    expiration = moderationSQL.fetchone()
                    user = guild.get_member(int(guildmutes[length][0]))
                    if user is None:
                        pass
                    else:
                        mutedrole = discord.utils.get(guild.roles, name='Biggie Mute')
                        if not mutedrole in user.roles:
                            moderationSQL.execute(f'delete from Expirations where Server_ID="{guild.id}" and User_ID="{user.id}" and Type="Mute"')
                            moderationdb.commit()
                        elif expiration[0] == 'Permanent':
                            pass
                        else:
                            timeobj = datetime.datetime.strptime(expiration[0], '%Y-%m-%d %H:%M:%S.%f')
                            if timeobj > datetime.datetime.utcnow():
                                pass
                            else:                            
                                await user.remove_roles(mutedrole)
                                moderationSQL.execute(f'delete from Expirations where Server_ID="{guild.id}" and User_ID="{user.id}" and Type="Mute"')
                                moderationdb.commit()
                    length = length - 1
            moderationSQL.execute(f'select User_ID from Expirations where Server_ID="{guild.id}" and Type="Kick"')
            guildkicks = moderationSQL.fetchall()
            if not guildkicks:
                pass
            else:
                length = len(guildkicks) - 1
                while length >= 0:
                    user = self.client.get_user(int(guildkicks[length][0]))
                    if user is None:
                        pass
                    else:
                        if guild.get_member(user.id) is None:
                            pass
                        else:
                            moderationSQL.execute(f'delete from Expirations where Server_ID="{guild.id}" and User_ID="{user.id}" and Type="Kick"')
                            moderationdb.commit()
                    length = length - 1
        remindSQL.execute('select User_ID from Reminders')
        IDs = remindSQL.fetchall()
        for id in IDs:
            remindSQL.execute(f'select Date from Reminders where User_ID="{int(id[0])}"')
            userreminders = remindSQL.fetchall()
            if not userreminders:
                pass
            else:
                length = len(userreminders) - 1
                while length >= 0:
                    date = userreminders[length][0]
                    timeobj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
                    if timeobj > datetime.datetime.utcnow():
                        pass
                    else:
                        remindSQL.execute(f'select Reason from Reminders where User_ID="{int(id[0])}" and Date="{date}"')
                        reason = remindSQL.fetchone()
                        try:
                            user = self.client.get_user(int(id[0]))
                            await user.send(reason[0])
                        except:
                            pass
                        remindSQL.execute(f'delete from Reminders where User_ID="{int(id[0])}" and Date="{date}"')
                        reminddb.commit()
                    length = length - 1

def setup(client):
    client.add_cog(Loops(client))