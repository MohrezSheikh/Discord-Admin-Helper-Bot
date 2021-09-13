import asyncio
from sys import prefix
import discord
import random
import json
from discord import client
from discord.ext import commands, tasks
from itertools import cycle
from discord.ext.commands.errors import CommandNotFound


status = cycle(['Your Custom Status'])


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    class DurationConverter(commands.Converter):
        async def convert(self, ctx, argument):
            amount = argument[:-1]
            unit = argument[-1]

            if amount.isdigit() and unit in ['s', 'm']:
                return (int(amount), unit)

            raise commands.BadArgument(message='Not a valid duration')


    #EVENTS
    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()
        print('Bot is ready')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)


        prefixes[str(guild.id)] = '.'

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent = 4)

    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)


        prefixes.pop(str(guild.id))

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent = 4)


    #COMMANDS
    @commands.has_permissions(manage_messages=True)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong!\n{round(self.client.latency * 1000)}ms')

    
    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt.',
                 'Yes - definitely.',
                 'As I see it, yes.',
                 'Most likely.',
                 'Outlook good.',
                 'Yes.',
                 'Sings point to yes.',
                 'Reply hazy, try again.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 "Don't count on it.",
                 'My reply is no.',
                 'My sources say no.',
                 'Outlook not so good.',
                 'Very doubtful.']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command()
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=amount)


    @commands.command()
    async def kick(self, ctx, member : commands.MemberConverter, *, reason=None):
        await member.guild.kick(member)
        await ctx.send(f'{member} has been kicked.')

    @commands.command()
    async def tempban(self, ctx, member : commands.MemberConverter, duration : DurationConverter):

        multiplier = {'s': 1, 'm': 60}
        amount, unit = duration

        await ctx.guild.ban(member)
        await ctx.send(f'{member} has been banned for {amount}{unit}.')
        await asyncio.sleep(amount * multiplier[unit])
        await ctx.guild.unban(member)


    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return


    @commands.command()
    async def changeprefix(self, ctx, prefix):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)


        prefixes[str(ctx.guild.id)] = prefix

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent = 4)

        await ctx.send(f'Prefix changed to {prefix}')


    #TASKS
    @tasks.loop(seconds=5)
    async def change_status(self):
        await self.client.change_presence(activity=discord.Game(next(status)))

        
    #ERRROS
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Invalid command used.')


    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please specify an amount of messages to delete.')
        

def setup(client):
    client.add_cog(Admin(client))