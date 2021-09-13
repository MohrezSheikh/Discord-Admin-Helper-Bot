import discord
import json
import os
from discord.ext import commands


TOKEN = 'Your Token'


def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)


    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix = get_prefix, help_command=commands.MinimalHelpCommand())


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(TOKEN)
