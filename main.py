import asyncio
import json
import os
import time
from datetime import datetime

import discord
import pytz
from discord import Message, Guild, TextChannel, Permissions
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

################################################################
################################################################
async def errorembed(ctx, error):
    embederror = discord.Embed(
        description=f"> Following information could help you with fixing the error: \n``{error}``\n \n"
                    f"[We can also help you with this problem!](https://discord.gg/YkvqJtB)\n", color=0xef4747)
    embederror.set_author(name="Something went wrong!",
                          icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
    embederror.set_footer(icon_url=f"{ctx.author.avatar_url}",
                          text=f"{ctx.bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
    return embederror


################################################################

# Der Botstart
@bot.event
async def on_ready():
    # Startinfo
    print(" ")
    print("Bot started! | Information:")
    print(f"- Name: {bot.user.name}")
    print(f"- Bot-ID: {bot.user.id}")
    print(f"- Server using {bot.user.name}:",
          len(bot.guilds))
    # Bot Presence
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("sasaki.me"))
    await asyncio.sleep(120)
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("sasaki.me"))
    await asyncio.sleep(120)
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("sasaki.me"))
    await asyncio.sleep(120)


if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)


@bot.command()
@commands.is_owner()
async def connect(ctx):
        if not guild_exists(ctx.guild.id):
            server = {
                "guildid": ctx.guild.id,
                "channelid": ctx.channel.id,
                "invite": f'{(await ctx.channel.create_invite()).url}'
            }
            servers["servers"].append(server)
            with open('servers.json', 'w') as f:
                json.dump(servers, f, indent=4)
            embed = discord.Embed(title="",
                                  description="Sparkle connects you to other people. \nThis means you can chat easily across discord servers! \nSounds nice, right?\n\n"
                                              f"> The chat has been activated in: ``#{ctx.message.channel}``; ``{ctx.message.guild}``",
                                  color=0x4cd137)
            embed.set_author(icon_url="https://cdn.discordapp.com/emojis/718597401518014514.png?v=1", name="Welcome to the Sparkle Globalchat!")
            embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                                  text=f"Setup by: {ctx.message.author.name}#{ctx.message.author.discriminator}")
        try:
            await ctx.send(embed=embed)
        except Exception as error:
            try:
                message = await ctx.send(
                    "> **Sparkle is working with embeds, you should Servermanagement the 'Embed Links' permission, to use Crowby!**\n"
                    f"> ``{error}``")
                await asyncio.sleep(10)
                await message.delete()
                await message.delete()
            except Exception as error:
                embed = await errorembed(error, ctx)
                await ctx.author.send(embed=embed)
                return
        else:
            embed = discord.Embed(description="I can't do this!\r\n"
                                              "Sparkle only supports one globalchat each server.",
                                  color=0xeb2f06)
            await ctx.send(embed=embed)


#########################################

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.content.startswith('!'):
        if get_globalChat(message.guild.id, message.channel.id):
            await sendAll(message)
    await bot.process_commands(message)


#########################################

async def sendAll(message: Message):
    conent = message.content
    author = message.author
    attachments = message.attachments
    de = pytz.timezone('Europe/Berlin')
    embed = discord.Embed(description=conent, timestamp=datetime.now().astimezone(tz=de), color=author.color)

    icon = author.avatar_url
    embed.set_author(name=author.name, icon_url=icon)

    icon_url = f"{bot.user.avatar_url}"
    icon = message.guild.icon_url
    if icon:
        icon_url = icon
    embed.set_thumbnail(url=icon_url)
    embed.set_footer(text='Sent from: {}'.format(message.guild.name))

    link = '[Sasaki Support](https://discord.gg/YkvqJtB)\n'
    globalchat = get_globalChat(message.guild.id, message.channel.id)
    if len(globalchat["invite"]) > 0:
        invite = globalchat["invite"]
        if 'discord.gg' not in invite:
            invite = 'https://discord.gg/{}'.format(invite)
        link += f'[Join this Community-Server!]({invite})'

    embed.add_field(name='Sparkle, your global-chat!', value=link, inline=False)

    if len(attachments) > 0:
        img = attachments[0]
        embed.set_image(url=img.url)

    for server in servers["servers"]:
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                perms: Permissions = channel.permissions_for(guild.get_member(bot.user.id))
                if perms.send_messages:
                    if perms.embed_links and perms.attach_files and perms.external_emojis:
                        await channel.send(embed=embed)
                    else:
                        await channel.send('{0}: {1}'.format(author.name, conent))
                        await channel.send("Oh, I can't do this!\n**Doublecheck my permissions.**")
    await message.delete()


###############################

def guild_exists(guildid):
    for server in servers['servers']:
        if int(server['guildid'] == int(guildid)):
            return True
    return False


def get_globalChat(guild_id, channelid=None):
    globalChat = None
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            if channelid:
                if int(server["channelid"]) == int(channelid):
                    globalChat = server
            else:
                globalChat = server
    return globalChat


def get_globalChat_id(guild_id):
    globalChat = -1
    i = 0
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            globalChat = i
        i += 1
    return globalChat





# ERRORHANDLER
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            description=f"> Following information could help you with fixing the error: \n```{error}```\n",
            color=0xef4747)
        embed.set_author(name="Something went wrong!",
                         icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
        embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                         text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
        try:
            message = await ctx.send(content=None, embed=embed)
            await asyncio.sleep(15)
            await ctx.message.delete()
            await message.delete()
            return
        except Exception as error:
            try:
                message = await ctx.send(
                    f"> *{bot.user.name} is working with embeds, you should Servermanagement the 'Embed Links' permission, to use {bot.user.name}!*")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await message.delete()
                return
            except discord.Forbidden:
                embed = discord.Embed(
                    description=f"> Following information could help you with fixing the error: \n```{error}```\n",
                    color=0xef4747)
                embed.set_author(name="Something went wrong!",
                                 icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
                embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                                 text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
                return


    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            description=f"> Use ``+help`` to see all commands!\n```{error}```\n", color=0xef4747)
        embed.set_author(name="Command not found!",
                         icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
        embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                         text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
        try:
            message = await ctx.send(content=None, embed=embed)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await message.delete()
            return
        except Exception as error:
            try:
                message = await ctx.send(
                    f"> *{bot.user.name} is working with embeds, you should Servermanagement the 'Embed Links' permission, to use {bot.user.name}!*")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await message.delete()
                return
            except Exception as error:
                embederror = discord.Embed(
                    description=f"> Following information could help you with fixing the error: \n``{error}``\n \n"
                                f"[We can also help you with this problem!](https://discord.gg/YkvqJtB)\n",
                    color=0xef4747)
                embederror.set_author(name="Something went wrong!",
                                      icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
                embederror.set_footer(icon_url=f"{ctx.author.avatar_url}",
                                      text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
                await ctx.author.send(embed=embed)
                return
        except discord.Forbidden:
            embed = discord.Embed(
                description=f"> Use ``+help`` to see all commands!\n```{error}```\n", color=0xef4747)
            embed.set_author(name="Command not found!",
                             icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
            embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                             text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
            return


    elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description=f"> Use ``+help [command]`` to see the usage of this command!\n```{error}```\n", color=0xef4747)
        embed.set_author(name="That didn't work!",
                         icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
        embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                         text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
        try:
            message = await ctx.send(content=None, embed=embed)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await message.delete()
            return
        except Exception as error:
            try:
                message = await ctx.send(
                    f"> *{bot.user.name} is working with embeds, you should Servermanagement the 'Embed Links' permission, to use {bot.user.name}!*")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await message.delete()
                return
            except Exception as error:
                embederror = discord.Embed(
                    description=f"> Following information could help you with fixing the error: \n``{error}``\n \n"
                                f"[We can also help you with this problem!](https://discord.gg/YkvqJtB)\n",
                    color=0xef4747)
                embederror.set_author(name="Something went wrong!",
                                      icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
                embederror.set_footer(icon_url=f"{ctx.author.avatar_url}",
                                      text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
                await ctx.author.send(embed=embed)
                return


    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            description=f"> Following information could help you with fixing the error: \n```{error}```\n",
            color=0xef4747)
        embed.set_author(name="Something went wrong!",
                         icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
        embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                         text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
        try:
            message = await ctx.send(content=None, embed=embed)
            await asyncio.sleep(10)
            await ctx.message.delete()
            await message.delete()
            return
        except Exception as error:
            try:
                message = await ctx.send(
                    f"> *{bot.user.name} is working with embeds, you should Servermanagement the 'Embed Links' permission, to use {bot.user.name}!*")
                await asyncio.sleep(10)
                await ctx.message.delete()
                await message.delete()
                return
            except discord.Forbidden:
                embed = discord.Embed(
                    description=f"> Following information could help you with fixing the error: \n```{error}```\n",
                    color=0xef4747)
                embed.set_author(name="Something went wrong!",
                                 icon_url=f"https://cdn.discordapp.com/emojis/700765858984886292.png?v=1")
                embed.set_footer(icon_url=f"{ctx.author.avatar_url}",
                                 text=f"{bot.user.name} Errorhandling | {ctx.message.author.name}#{ctx.message.author.discriminator}")
                return
    
############################################

bot.run('TOKEN')
