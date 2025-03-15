import discord
import logging
from googletrans import Translator
import asyncio
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurer les logs
logging.basicConfig(level=logging.INFO)

# Créer une instance d'Intents pour permettre au bot d'écouter certains événements
intents = discord.Intents.default()
intents.message_content = True  # Permet au bot de lire le contenu des messages

# Créer une instance du client Discord avec les intents
client = discord.Client(intents=intents)

# Initialiser le traducteur
translator = Translator()

# Cache pour les traductions (éviter les appels API répétés)
translations_cache = {}

# Fonction pour vérifier si le bot a les permissions nécessaires
async def check_permissions(guild):
    permissions = guild.me.guild_permissions
    if not permissions.manage_channels or not permissions.manage_roles:
        return False
    return True

# Fonction pour obtenir la traduction depuis le cache ou l'API
def get_translation(text, src_lang='auto', dest_lang='en'):
    if text in translations_cache:
        return translations_cache[text]
    translated = translator.translate(text, src=src_lang, dest=dest_lang).text
    translations_cache[text] = translated  # Cache la traduction
    return translated

# Fonction pour traduire et renommer les salons
async def translate_and_rename_channels(guild, src_lang, dest_lang):
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
            try:
                if channel.type == discord.ChannelType.private:
                    continue  # Ignorer les salons privés

                # Vérifier la langue source avant de traduire
                detected_lang = translator.detect(channel.name).lang
                if detected_lang != dest_lang:  # Si la langue n'est pas la langue de destination
                    translated_name = get_translation(channel.name, src=detected_lang, dest=dest_lang)
                    await channel.edit(name=translated_name)
                    logging.info(f"Salon {channel.name} traduit en {translated_name}")
                    await asyncio.sleep(1)  # Pour éviter d'envoyer trop de requêtes
            except Exception as e:
                logging.error(f"Erreur lors de la traduction du salon {channel.name}: {e}")

# Fonction pour traduire et renommer les rôles
async def translate_and_rename_roles(guild, src_lang, dest_lang):
    for role in guild.roles:
        if role.name != "@everyone":  # On ignore le rôle @everyone
            try:
                # Vérifier la langue source avant de traduire
                detected_lang = translator.detect(role.name).lang
                if detected_lang != dest_lang:  # Si la langue n'est pas la langue de destination
                    translated_name = get_translation(role.name, src=detected_lang, dest=dest_lang)
                    await role.edit(name=translated_name)
                    logging.info(f"Rôle {role.name} traduit en {translated_name}")
                    await asyncio.sleep(1)  # Pour éviter d'envoyer trop de requêtes
            except Exception as e:
                logging.error(f"Erreur lors de la traduction du rôle {role.name}: {e}")

# Fonction principale pour traduire l'intégralité du serveur
async def translate_server(guild, message, src_lang='auto', dest_lang='en'):
    if not await check_permissions(guild):
        await message.channel.send("Je n'ai pas les permissions nécessaires pour renommer les salons ou rôles.")
        return
    
    await message.channel.send("Traduction des salons et rôles en cours...")

    # Traduire les salons et rôles
    await translate_and_rename_channels(guild, src_lang, dest_lang)
    await translate_and_rename_roles(guild, src_lang, dest_lang)

    await message.channel.send("Traduction terminée. Tous les salons et rôles ont été traduits.")

# Commande pour afficher les salons et rôles avant traduction
async def preview_translation(guild, message, src_lang, dest_lang):
    preview = "Salons à traduire :\n"
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
            preview += f"{channel.name} -> {get_translation(channel.name, src=src_lang, dest=dest_lang)}\n"
    
    preview += "\nRôles à traduire :\n"
    for role in guild.roles:
        if role.name != "@everyone":
            preview += f"{role.name} -> {get_translation(role.name, src=src_lang, dest=dest_lang)}\n"
    
    await message.channel.send(preview)

# Commande pour afficher la liste des rôles et salons
async def list_channels_and_roles(guild, message):
    channels = "\n".join([channel.name for channel in guild.channels if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel)])
    roles = "\n".join([role.name for role in guild.roles if role.name != "@everyone"])


    await message.channel.send(f"Salons actuels:\n{channels}\n\nRôles actuels:\n{roles}")

# Gérer les commandes avec les permissions
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Commande pour traduire tout le serveur
    if message.content.startswith('!translate_server'):
        guild = message.guild
        args = message.content.split(' ')
        if len(args) == 3:
            src_lang = args[1]  # Langue source (par exemple 'fr')
            dest_lang = args[2]  # Langue de destination (par exemple 'en')
        else:
            src_lang = 'auto'
            dest_lang = 'en'
        await translate_server(guild, message, src_lang, dest_lang)

    # Commande pour afficher les traductions prévues
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

    # Commande pour lister les salons et rôles
    if message.content.startswith('!list_channels_and_roles'):
        guild = message.guild
        await list_channels_and_roles(guild, message)

# Gérer l'événement on_ready
@client.event
async def on_ready():
    logging.info(f'Bot connecté en tant que {client.user}')

# Lancer le bot avec le token depuis le fichier .env
client.run(TOKEN)
