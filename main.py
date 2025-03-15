import discord
import logging
from googletrans import Translator
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

translator = Translator()

translations_cache = {}

async def check_permissions(guild):
    permissions = guild.me.guild_permissions
    if not permissions.manage_channels or not permissions.manage_roles:
        return False
    return True

def get_translation(text, src_lang='auto', dest_lang='en'):
    if text in translations_cache:
        return translations_cache[text]
    translated = translator.translate(text, src=src_lang, dest=dest_lang).text
    translations_cache[text] = translated
    return translated

async def translate_and_rename_channels(guild, src_lang, dest_lang):
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
            try:
                if channel.type == discord.ChannelType.private:
                    continue

                detected_lang = translator.detect(channel.name).lang
                if detected_lang != dest_lang:
                    translated_name = get_translation(channel.name, src=detected_lang, dest=dest_lang)
                    await channel.edit(name=translated_name)
                    logging.info(f"Channel {channel.name} translated to {translated_name}")
                    await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error translating channel {channel.name}: {e}")

async def translate_and_rename_roles(guild, src_lang, dest_lang):
    for role in guild.roles:
        if role.name != "@everyone":
            try:
                detected_lang = translator.detect(role.name).lang
                if detected_lang != dest_lang:
                    translated_name = get_translation(role.name, src=detected_lang, dest=dest_lang)
                    await role.edit(name=translated_name)
                    logging.info(f"Role {role.name} translated to {translated_name}")
                    await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error translating role {role.name}: {e}")

async def translate_server(guild, message, src_lang='auto', dest_lang='en'):
    if not await check_permissions(guild):
        await message.channel.send("I do not have the necessary permissions to rename channels or roles.")
        return
    
    await message.channel.send("Translating channels and roles...")

    await translate_and_rename_channels(guild, src_lang, dest_lang)
    await translate_and_rename_roles(guild, src_lang, dest_lang)

    await message.channel.send("Translation complete. All channels and roles have been translated.")

async def preview_translation(guild, message, src_lang, dest_lang):
    preview = "Channels to be translated:\n"
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
            preview += f"{channel.name} -> {get_translation(channel.name, src=src_lang, dest=dest_lang)}\n"
    
    preview += "\nRoles to be translated:\n"
    for role in guild.roles:
        if role.name != "@everyone":
            preview += f"{role.name} -> {get_translation(role.name, src=src_lang, dest=dest_lang)}\n"
    
    await message.channel.send(preview)

async def list_channels_and_roles(guild, message):
    channels = "\n".join([channel.name for channel in guild.channels if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel)])
    roles = "\n".join([role.name for role in guild.roles if role.name != "@everyone"])

    await message.channel.send(f"Current channels:\n{channels}\n\nCurrent roles:\n{roles}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!translate_server'):
        guild = message.guild
        args = message.content.split(' ')
        if len(args) == 3:
            src_lang = args[1]
            dest_lang = args[2]
        else:
            src_lang = 'auto'
            dest_lang = 'en'
        await translate_server(guild, message, src_lang, dest_lang)

    if message.content.startswith('!preview_translation'):
        guild = message.guild
        args = message.content.split(' ')
        if len(args) == 3:
            src_lang = args[1]
            dest_lang = args[2]
        else:
            src_lang = 'auto'
            dest_lang = 'en'
        await preview_translation(guild, message, src_lang, dest_lang)

    if message.content.startswith('!list_channels_and_roles'):
        guild = message.guild
        await list_channels_and_roles(guild, message)

@client.event
async def on_ready():
    logging.info(f'Bot logged in as {client.user}')

client.run(TOKEN)
