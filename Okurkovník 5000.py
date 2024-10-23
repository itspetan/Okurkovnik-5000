from discord import Embed
from discord.ui import Button, View
from collections import defaultdict
from discord.ext import commands, tasks
from datetime import datetime, timedelta

import os
import re
import sys
import time
import json
import random
import asyncio
import discord
import logging
import subprocess

# Nastavení logování
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.presences = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!c ", intents=intents)

# Rankovací systém - inicializace proměnné user_points
user_points = defaultdict(int)  # Defaultní hodnoty bodů pro uživatele

# Inicializace user_points
user_points = {}

# Načtení bodů z JSON souboru při startu bota
if os.path.exists("points.json"):
    with open("points.json", "r") as f:
        user_points = json.load(f)  # Načítáme všechny body do user_points
else:
    # Pokud soubor neexistuje, vytvořte prázdný JSON soubor
    with open("points.json", "w") as f:
        json.dump({}, f)  # Vytvoření prázdného JSON

# Uložení bodů do JSON souboru
def save_points():
    with open("points.json", "w") as f:
        json.dump(user_points, f)

# Přidání bodů při každé zprávě
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    # Inicializace uživatelských bodů, pokud ještě neexistují
    if user_id not in user_points:
        user_points[user_id] = {"message_points": 0, "voice_points": 0}  # Inicializace uživatelských bodů

    user_points[user_id]["message_points"] += 1  # Přidá 2 body za zprávu

    save_points()  # Uložení bodů

    await bot.process_commands(message)

# Inicializace user_points
user_points = {}

# Načtení bodů z JSON souboru při startu bota
if os.path.exists("points.json"):
    with open("points.json", "r") as f:
        user_points = json.load(f)  # Načítáme body do user_points
else:
    user_points = {}

# Uložení bodů do JSON souboru při ukončení bota
def save_points():
    with open("points.json", "w") as f:
        json.dump(user_points, f)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            permissions = guild.me.permissions_in(channel)
            if permissions.view_channel and permissions.connect:
                print(f"Bot má oprávnění pro hlasový kanál: {channel.name}")
            else:
                print(f"Bot NEMÁ oprávnění pro hlasový kanál: {channel.name}")


# Příkaz pro zobrazení ranku
@bot.command()
async def rank(ctx):
    allowed_channel_id = 1298188027058720829  # Změň na skutečné ID kanálu

    # Zkontroluj, jestli uživatel má roli administrátora nebo moderátora
    is_admin_or_mod = any(role.permissions.administrator for role in ctx.author.roles) or \
                      any(role.name == "Moderátor" for role in ctx.author.roles)  # Změň "Moderátor" na skutečný název role, pokud je potřeba

    # Kontrola, zda je příkaz spuštěn v povoleném kanálu nebo jestli uživatel je admin/mod
    if ctx.channel.id != allowed_channel_id and not is_admin_or_mod:
        await ctx.send("Tento příkaz můžeš použít pouze v konkrétní místnosti!")
        await ctx.send(
            "https://cdn.discordapp.com/attachments/1297689264372449351/1298225458411868190/Discord_kn6OlKm5bV.png?ex=6718ca2d&is=671778ad&hm=01bf77ce82816e7953da29231832a2940e43dbbac4777c378c2a85664da8ce47&")
        return

    user_id = str(ctx.author.id)

    # Body za zprávy a hlasový kanál
    message_points = user_points.get(user_id, {}).get("message_points", 0)

    # Příprava textu pro zobrazení
    rank_message = (
        f"### **Tvá osobní statistika**\n"
        f"✏️ Počet zpráv: {message_points}\n"
    )

    # Odeslání zprávy s statistikami
    await ctx.send(rank_message)

# Příkaz pro zobrazení leaderboardu
@bot.command()
async def leaderboard(ctx):
    allowed_channel_id = 1298188027058720829  # Změň na skutečné ID kanálu

    # Zkontroluj, jestli uživatel má roli administrátora nebo moderátora
    is_admin_or_mod = any(role.permissions.administrator for role in ctx.author.roles) or \
                      any(role.name == "Moderátor" for role in
                          ctx.author.roles)  # Změň "Moderátor" na skutečný název role, pokud je potřeba

    # Kontrola, zda je příkaz spuštěn v povoleném kanálu nebo jestli uživatel je admin/mod
    if ctx.channel.id != allowed_channel_id and not is_admin_or_mod:
        await ctx.send("Tento příkaz můžeš použít pouze v konkrétní místnosti!")
        await ctx.send("https://cdn.discordapp.com/attachments/1297689264372449351/1298225458411868190/Discord_kn6OlKm5bV.png?ex=6718ca2d&is=671778ad&hm=01bf77ce82816e7953da29231832a2940e43dbbac4777c378c2a85664da8ce47&")
        return

    sorted_message_users = sorted(user_points.items(), key=lambda x: x[1]["message_points"], reverse=True)[:10]


    # Seznam s body za zprávy
    message_leaderboard_message = "### 🏆 **Top 10 uživatelů v chatu** 🏆\n"

    for i, (user_id, points) in enumerate(sorted_message_users, start=1):
        user = await bot.fetch_user(int(user_id))
        message_leaderboard_message += f"{i}. **{user.name}**: {points['message_points']} zpráv\n"

    # Odeslání zprávy s body za zprávy
    await ctx.send(message_leaderboard_message)


# Příkaz verify pro přidání role "Ověřený člen"
@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def verify(ctx):
    logging.info(f'Příkaz verify spuštěn uživatelem {ctx.author}')
    role = discord.utils.get(ctx.guild.roles, name="Ověřený člen")
    if role:
        logging.info(f'Roli "Ověřený člen" nalezena')
        if role not in ctx.author.roles:
            await ctx.author.add_roles(role)
            await ctx.send(f'{ctx.author.mention} byl(a) verifikován(a) a přidán(a) do role {role.name}')
            logging.info(f'Uživatel {ctx.author} byl přidán do role "Ověřený člen"')
        else:
            await ctx.send(f'{ctx.author.mention} již má roli {role.name}')
            logging.info(f'Uživatel {ctx.author} již má roli "Ověřený člen"')
    else:
        await ctx.send(f'Roli "Ověřený člen" nebylo možné najít. Ujistěte se, že roli máte vytvořenou na serveru.')
        logging.error(f'Roli "Ověřený člen" nebylo možné najít')

@verify.error
async def verify_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Na verifikací uživatelů nemáš dostatečná oprávnění")

# ID kanálů a zpráv, na které bude bot reagovat
CHANNEL_ID = 297122145218068544  # Nahraď ID kanálu pro verifikaci
MESSAGE_ID_VERIFY = 1297126828409880687  # Zpráva pro roli "Ověřený člen"
MESSAGE_ID_REACTIONS = 1297139237099147305  # Zpráva pro filmy, seriály a knihy, hry a memes

# Emoji a jejich přiřazené role
EMOJI_ROLE_MAP = {
    '✅': 1297126994957303808,  # ID role pro "Ověřený člen"
    '🎥': 1297139399972360204,  # ID role pro Filmy
    '📺': 1297139454925996042,  # ID role pro Seriály
    '📖': 1297139482801344563,  # ID role pro Knihy
    '🎮': 1297508885501968394,   # ID role pro Hry
    '🤡': 1297952632983257182,   # ID role pro Memes
    '🎵': 1297954452401295410,   # ID role pro Hudbu
    '☕': 1297956632034148477,   # ID role pro Čaje a kávy
    '🍗': 1297956661818032128,   # ID role pro Foodporn
    '📸': 1297956684198711376   # ID role pro Fotografie
}

CHANNEL_ID = 1297122145218068544  # Nahraď ID kanálu pro verifikaci
MESSAGE_ID_VERIFY = 1297126828409880687


@bot.event
async def on_ready():
    print(f'{bot.user} je nyní online a připraven.')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            message_verify = await channel.fetch_message(MESSAGE_ID_VERIFY)
            await message_verify.add_reaction('✅')
        except Exception as e:
            logging.error(f'Chyba při přidávání reakce: {e}')
    else:
        logging.error(f'Kanál s ID {CHANNEL_ID} nebyl nalezen.')


@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    emoji = str(payload.emoji)
    if emoji in EMOJI_ROLE_MAP:
        role_id = EMOJI_ROLE_MAP[emoji]
        role = guild.get_role(role_id)

        if role:
            await member.add_roles(role)
            logging.info(f"Role {role.name} byla přidána uživateli {member.name}")


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    # Zkontrolujeme, jestli emoji odpovídá našim mapovaným emoji
    emoji = str(payload.emoji)
    if emoji in EMOJI_ROLE_MAP:
        role_id = EMOJI_ROLE_MAP[emoji]
        role = guild.get_role(role_id)

        if role is not None:
            await member.remove_roles(role)
            print(f"Role {role.name} byla odebrána uživateli {member.name}")

@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    emoji = str(payload.emoji)
    if emoji in EMOJI_ROLE_MAP:
        role_id = EMOJI_ROLE_MAP[emoji]
        role = guild.get_role(role_id)

        if role:
            await member.remove_roles(role)
            logging.info(f"Role {role.name} byla odebrána uživateli {member.name}")

@bot.event
async def on_ready():
    print(f'Clara je připravena. Je přihlášena jako {bot.user}')


async def log_to_channel(embed, view):
    log_channel = bot.get_channel(1297140073615069236)
    if log_channel:
        await log_channel.send(embed=embed, view=view)
    else:
        print(f"Nepodařilo se najít kanál logu s ID {1297140073615069236}")

async def log_to_channel(embed, view=None):
    log_channel = bot.get_channel (1297140073615069236)
    if log_channel:
        await log_channel.send(embed=embed, view=view)
    else:
        print(f"Nepodařilo se najít kanál logu s ID {1297140073615069236}")

@bot.event
async def on_message_delete(message):
    if not message.guild:
        return

    embed = discord.Embed(title="🗑️ Zpráva smazána", color=discord.Color.red())
    embed.add_field(name="Autor zprávy", value=message.author.mention, inline=True)
    embed.add_field(name="Kanál", value=message.channel.mention, inline=True)
    embed.add_field(name="Smazaná zpráva", value=message.content or "No content", inline=False)
    embed.add_field(name="ID zprávy", value=message.id, inline=False)
    embed.add_field(name="Čas", value=message.created_at, inline=False)

    view = View()
    jump_button = Button(label="Jump to context", url=message.jump_url)
    view.add_item(jump_button)

    await log_to_channel(embed, view)


@bot.event
async def on_message_edit(before, after):
    if not before.guild:
        return

    embed = discord.Embed(title="✏️ Zpráva upravena", color=discord.Color.orange())
    embed.add_field(name="Autor zprávy", value=before.author.mention, inline=True)
    embed.add_field(name="Kanál", value=before.channel.mention, inline=True)
    embed.add_field(name="Před úpravou", value=before.content or "No content", inline=False)
    embed.add_field(name="Po úpravě", value=after.content or "No content", inline=False)
    embed.add_field(name="ID zprávy", value=before.id, inline=False)
    embed.add_field(name="Čas", value=before.created_at, inline=False)

    view = View()
    jump_button = Button(label="Skočit na zprávu", url=before.jump_url)
    view.add_item(jump_button)

    await log_to_channel(embed, view)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="📥 Připojil se uživatel", color=discord.Color.green())
    embed.add_field(name="Člen", value=member.mention, inline=True)
    embed.add_field(name="ID člena", value=member.id, inline=True)
    embed.add_field(name="Čas", value=member.joined_at, inline=False)

    await log_to_channel(embed, None)

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(title="📤 Uživatel se odpojil", color=discord.Color.red())
    embed.add_field(name="Člen", value=member.mention, inline=True)
    embed.add_field(name="ID člena", value=member.id, inline=True)
    embed.add_field(name="Čas", value=member.joined_at, inline=False)

    await log_to_channel(embed, None)

@bot.event
async def on_member_update(before, after):
    changes = []
    if before.display_name != after.display_name:
        changes.append(f"📝 Přezdívka změněna z {before.display_name} na {after.display_name}")
    if before.roles != after.roles:
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        if added_roles:
            changes.append(f"➕ Přidány role: {', '.join([role.name for role in added_roles])}")
        if removed_roles:
            changes.append(f"➖ Odebrány role: {', '.join([role.name for role in removed_roles])}")
    if changes:
        embed = discord.Embed(title="🔄 Aktualizace člena", color=discord.Color.blue())
        embed.add_field(name="Člen", value=before.mention, inline=True)
        embed.add_field(name="Změny", value="\n".join(changes), inline=False)

        await log_to_channel(embed, None)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_voice_state_update(member, before, after):
    generator_channel_name = "📢┃Generátor"
    category_name = "Hlasové místnosti"

    # Kontrola, zda uživatel vstoupil do generátoru
    if after.channel and after.channel.name == generator_channel_name:
        category = discord.utils.get(member.guild.categories, name=category_name)
        if not category:
            category = await member.guild.create_category(category_name)

        # Vytvoření nové hlasové místnosti s názvem uživatele
        new_channel = await member.guild.create_voice_channel(name=f"{member.display_name}'s voice", category=category)
        await member.move_to(new_channel)

        # Spuštění kontroly prázdnosti místnosti
        await check_empty_voice_channel(new_channel)

async def check_empty_voice_channel(channel):
    while True:
        await asyncio.sleep(1)  # Kontrola každých 5 minut
        if not channel.members:
            await channel.delete(reason="Automatické odstranění prázdné místnosti")
            break  # Ukončení smyčky po smazání kanálu


@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def mute(ctx, member: discord.Member, duration: str = None, *, reason=None):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        await ctx.send('Roli "Muted" nebylo možné najít. Ujistěte se, že roli máte vytvořenou na serveru.')
        logging.error('Roli "Muted" nebylo možné najít')
        return

    await member.add_roles(role, reason=reason)

    if duration is None:
        # Permanentní mute, pokud není zadána doba
        await ctx.send(f'Uživatel {member.mention} byl umlčen permanentně. Důvod: {reason}')
        logging.info(f'Uživatel {member} byl umlčen permanentně. Důvod: {reason}')
    else:
        # Zpracování časového formátu (např. 1m pro minuty, 1h pro hodiny)
        match = re.match(r"(\d+)([smhd])", duration)
        if match:
            time_value = int(match.group(1))
            time_unit = match.group(2)

            if time_unit == 's':
                duration_seconds = time_value
            elif time_unit == 'm':
                duration_seconds = time_value * 60
            elif time_unit == 'h':
                duration_seconds = time_value * 3600
            elif time_unit == 'd':
                duration_seconds = time_value * 86400
            else:
                await ctx.send("Neplatný časový formát. Použijte s (sekundy), m (minuty), h (hodiny), d (dny).")
                return

            await ctx.send(f'Uživatel {member.mention} byl umlčen na {duration}. Důvod: {reason}')
            logging.info(f'Uživatel {member} byl umlčen na {duration}. Důvod: {reason}')

            # Po uplynutí doby mutování roli odstraníme
            await asyncio.sleep(duration_seconds)
            await member.remove_roles(role)
            await ctx.send(f'Uživatel {member.mention} byl odmlčen.')
            logging.info(f'Uživatel {member} byl odmlčen.')
        else:
            await ctx.send("Neplatný časový formát. Použijte s (sekundy), m (minuty), h (hodiny), d (dny).")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("S touto rolí tohle člověče dělat nemůžeš, už to neděléééj!")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        await ctx.send('Roli "Muted" nebylo možné najít. Ujistěte se, že roli máte vytvořenou na serveru.')
        logging.error('Roli "Muted" nebylo možné najít')
        return

    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f'Uživatel {member.mention} byl odmlčen.')
        logging.info(f'Uživatel {member} byl odmlčen.')
    else:
        await ctx.send(f'Uživatel {member.mention} nemá roli "Muted".')
        logging.info(f'Uživatel {member} nemá roli "Muted".')

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("S touto rolí tohle člověče dělat nemůžeš, už to neděléééj!")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Uživatel {member} byl zabanován za {reason}')
    logging.info(f'Uživatel {member} byl zabanován za {reason}')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Tohle asi nepůjde človíčku")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Uživatel {member} byl vyhozen za {reason}')
    logging.info(f'Uživatel {member} byl vyhozen za {reason}')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("S touto rolí tohle člověče dělat nemůžeš, už to neděléééj!")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Prosím, zadejte kladné číslo")
        return
    if amount > 1000:
            await ctx.send("Můžeš smazat maximálně 1000 zpráv najednou")
            return
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 protože zahrnujeme i příkaz
    await ctx.send(f'Smazáno {len(deleted) - 1} zpráv', delete_after=5)  # Upozornění, které se smaže po 5 sekundách

# Zachytávání chyby, pokud uživatel nemá potřebnou roli
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Nemůžeš mazat zprávy jen tak, na to musíš být **Administrátor** nebo **Moderátor**. Co blázníš?")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def ping(ctx):
    # Měří latenci bota a odešle ji jako zprávu
    latency = bot.latency * 1000  # Latence v milisekundách
    await ctx.send(f'Okurkovník 5000 má latenci {latency:.2f} ms')

# Zachytávání chyby, pokud uživatel nemá potřebnou roli
@ping.error
async def ping_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Proč mě rušíš? Tenhle příkaz slouží pouze **Administrátorům** a **Moderátorům**")


@bot.event
async def on_ready():
    print('Okurkovník 5000 je spuštěn!')
    await bot.change_presence(activity=discord.CustomActivity(name='Jsem online a vidím tě!',emoji='🖥️'))


@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def version(ctx):
    """Aktuálni verze Clary"""
    message = (
        "# **Aktuální verze Okurkovník 5000 1.9.5** (Update 23.10.2024)\n"
        "**Verze Okurkovník 5000 1.9.5 (Alpha)** (23.10.2024) Novinky: Přidány gamereset all, upraven ping\n"
        "**Verze Okurkovník 5000 1.9.4 (Alpha)** (23.10.2024) Novinky: Přidány příkazy\n"
        "**Verze Okurkovník 5000 1.9.3 (Alpha)** (23.10.2024) Novinky: Opětovná úprava logiky upgradů a výprav\n"
        "**Verze Okurkovník 5000 1.9.2 (Alpha)** (23.10.2024) Novinky: Úprava logiky upgradů a výprav\n"
        "**Verze Okurkovník 5000 1.9.1 (Alpha)** (23.10.2024) Novinky: Nový profil, Výprava, Upgrade\n"
        "**Verze Okurkovník 5000 1.9 (Alpha)** (23.10.2024) Novinky: Vývoj hry RPG Okurkovo Dobrodružství\n"
        "**Verze Okurkovník 5000 1.8 (Alpha)** (22.10.2024) Novinky: Rank systém zpráv, Leaderboard systém, update systém oprávnění, export databáze s daty\n"
        "**Verze Okurkovník 5000 1.7 (Alpha)** (21.10.2024) Novinky: Oprava kódu\n"
        "**Verze Okurkovník 5000 1.6 (Alpha)** (20.10.2024) Novinky: Přidán Úprava kódu a sjednocení, Ping, přepracování příkazu Mute, opraven generátor voice místností úprava časového rozdílu u automaticky mazaných zpráv\n"
        "**Verze Okurkovník 5000 1.5 (Alpha)** (19.10.2024) Novinky: Přidán Status (Odpojeno), a úprava kódu\n"
        "**Verze Okurkovník 5000 1.4 (Alpha)** (13.8.2024) Novinky: Přidán log serveru\n"
        "**Verze Okurkovník 5000 1.3 (Alpha)** (13.8.2024) Novinky: Úprava kódu\n"
        "**Verze Okurkovník 5000 1.2 (Alpha)** (8.8.2024) Novinky: Přidán Restart (Odpojeno), Shutdown (Odpojeno) \n"
        "**Verze Okurkovník 5000 1.1 (Alpha)** (8.8.2024) Novinky: Přidán Clear, Version\n"
        "**Verze Okurkovník 5000 1.0 (Alpha)** (7.8.2024) Novinky: Přidán Ban, Kick, Mute, Help, Unmute, Verify\n"


    )
    await ctx.send(message)

@version.error
async def version_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Zobrazení mých dosavadních verzí slouží pouze pro naše interní programátory")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def čajovna(ctx):
        # Vytvoření zprávy s textem
        message_text = "Navštivte eshop s čaji AfternoonTea!"

        # Vytvoření tlačítka s odkazem na web
        button = Button(label="Čaje a nečaje", url="https://www.afternoon-tea.cz/Caje-a-necaje-c46_0_1.htm")  # Zadej URL
        button2 = Button(label="Káva", url="https://www.afternoon-tea.cz/Kava-c47_0_1.htm")
        button3 = Button(label="Kakao", url="https://www.afternoon-tea.cz/kakao-horka-cokolada")
        button4 = Button(label="Sladké a slané", url="https://www.afternoon-tea.cz/sladke-slane")
        button5 = Button(label="Přislušenství", url="https://www.afternoon-tea.cz/prislusenstvi")

        # Vytvoření view, aby bylo možné tlačítko zobrazit
        view = View()
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        view.add_item(button5)

        # Cesta k obrázku (musí být přístupný z internetu)
        image_url = "https://cdn.discordapp.com/attachments/1297689264372449351/1297689297545072741/1652856037logo_03.png?ex=67177f96&is=67162e16&hm=626672cba497c81480b64fdc4a93f20d8ac4671478564bf609f2f5b995d59735&"  # Nahraď URL obrázku

        # Odeslání zprávy s obrázkem a tlačítkem
        embed = discord.Embed(title="Vítejte v Čajovně!")
        embed.set_image(url=image_url)  # Přidání obrázku do zprávy

        await ctx.send(embed=embed, view=view)

    # Zachytávání chyby, pokud uživatel nemá potřebnou roli
@čajovna.error
async def čajovna_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Tento příkaz je stále ve fázi vývoje, hned jak bude spuštěn tak se ti ozvu")

@bot.command()
@commands.has_any_role("Administrátor", "Moderátor")
async def status(ctx):
    # Odešle zprávu do kanálu s textem "Bot je aktivní"
    await ctx.send('**Jsem aktivní**')

@status.error
async def status_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("Tenhle příkaz bohužel použít nemůžeš, ale neboj jsem tady a jsem aktivní")

#Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra #Vlastní RPG Hra
# Načtení dat uživatelů z JSON souboru
def load_data():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Uložení dat uživatelů do JSON souboru
def save_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)


# Příkaz pro výpravu
@bot.command()
async def vyprava(ctx):
    users = load_data()
    user_id = str(ctx.author.id)

    # Inicializace uživatele a všech potřebných atributů, pokud neexistují
    if user_id not in users:
        users[user_id] = {
            "penize": 0, "vypravy": 0, "ziskano_celkem": 0,
            "mec_lvl": 0, "brneni_lvl": 0, "batoh_lvl": 0, "talisman_lvl": 0,
            "last_vyprava_time": 0  # Inicializace času výpravy na 0
        }
    else:
        # Kontrola a případná inicializace pro jednotlivé atributy, pokud chybí
        if "last_vyprava_time" not in users[user_id]:
            users[user_id]["last_vyprava_time"] = 0  # Inicializace na 0 při absenci hodnoty
        if "mec_lvl" not in users[user_id]:
            users[user_id]["mec_lvl"] = 1
        if "brneni_lvl" not in users[user_id]:
            users[user_id]["brneni_lvl"] = 1
        if "batoh_lvl" not in users[user_id]:
            users[user_id]["batoh_lvl"] = 1
        if "talisman_lvl" not in users[user_id]:
            users[user_id]["talisman_lvl"] = 1

        # Zkontroluj, zda uběhla hodina od poslední výpravy
        current_time = time.time()
        last_vyprava_time = users[user_id]["last_vyprava_time"]

        time_left = 10 - (current_time - last_vyprava_time)  # Zbývající čas v sekundách

        if time_left > 0:
            minutes_left = int(time_left // 60)
            seconds_left = int(time_left % 60)

            # Vytvoření embedu s informací o zbývajícím čase a obrázkem
            embed = discord.Embed(
                title="Plánuji další výpravu",
                description=f"Teď jsi se z jedné výpravy vrátil a hned chceš na další? Na další výpravu se můžu vydat za {minutes_left} minut a {seconds_left} sekund.",
                color=discord.Color.red()
            )

            # Nastavení obrázku do embedu (nahraď odkaz svým obrázkem)
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/1297689264372449351/1298567054873591808/Gemini_Generated_Image_qcbjs9qcbjs9qcbj.jpeg?ex=671a0850&is=6718b6d0&hm=4fd50657cd6f69628bcc4b6affab4f9128b1d6302b53a54f8d43e67798fc70f6&")

            await ctx.send(embed=embed)
            return

    # Výpočet bonusu podle úrovní vybavení
    mec_bonus = users[user_id]["mec_lvl"] * 0.05  # Každá úroveň meče dává 5% bonus
    brneni_bonus = users[user_id]["brneni_lvl"] * 0.05  # Každá úroveň brnění dává 5% bonus
    batoh_bonus = users[user_id]["batoh_lvl"] * 0.05  # Každá úroveň batohu dává 5% bonus
    talisman_bonus = users[user_id]["talisman_lvl"] * 0.05  # Každá úroveň talismanu dává 5% bonus

    # Generování základní odměny z výpravy
    odmena = random.randint(10, 200)

    # Celkový bonus z vybavení
    celkovy_bonus = odmena * (1 + mec_bonus + brneni_bonus + batoh_bonus + talisman_bonus)
    celkovy_bonus = round(celkovy_bonus)  # Zaokrouhlení odměny

    # Uložení času poslední výpravy
    users[user_id]["last_vyprava_time"] = current_time

    # Získání šance na vyšší zisk
    chance_bonus = sum([users[user_id][item] for item in ["mec_lvl", "brneni_lvl", "batoh_lvl", "talisman_lvl"]])

    # Získání maximální odměny
    max_odmena = odmena + (chance_bonus * 10)  # 10 $ za každou úroveň

    # Náhodně zvolíme odměnu mezi základní odměnou a maximální odměnou
    final_odmena = random.randint(odmena, max_odmena)

    # Šance na přepadení
    sance_na_prepadeni = random.random()

    if sance_na_prepadeni <= 0.15:
        # Název, obrázek a procento ztráty pro jednotlivé typy přepadení
        prepadeni_typy = {
            "Smog v Ostravě tě oslepil natolik, že jsi z batohu upustil peníze": {
                "obrazek": "https://cdn.discordapp.com/attachments/1297689264372449351/1298560066378530857/Smog.jpeg?ex=671a01cd&is=6718b04d&hm=4918727a8657d5493951610334ecf952b0be479d440004f58b78cde6b501469f&",
                "ztrata_procento": 0.20  # Ztráta 20%
            },
            "Pochybná existence v Praze ti nenápadně z batohu vytáhla peníze": {
                "obrazek": "https://cdn.discordapp.com/attachments/1297689264372449351/1298560065904840774/Praha.jpeg?ex=671a01cd&is=6718b04d&hm=ef9a1acb4658da102de97df39c37d3e605fbf1a9bb6bdff31b0227c2fb983390&",
                "ztrata_procento": 0.20  # Ztráta 20%
            },
            "V tajemném lese jsi zakopl o kořen stromu, sklouzl jsi se ze svahu a z batohu ti vypadly peníze": {
                "obrazek": "https://cdn.discordapp.com/attachments/1297689264372449351/1298560130299990070/Zakopla_v_tajemnem_lese.jpeg?ex=671a01dd&is=6718b05d&hm=049b600dde2ec2d7585381fe5fab098d50c25a9bb5874a7f17643bf466eb084c&",
                "ztrata_procento": 0.50  # Ztráta 50%
            },
            "Převáděl jsi peníze na svůj účet ale Okurkovník špatně zadal platbu": {
                "obrazek": "https://cdn.discordapp.com/attachments/1297689264372449351/1298560218934022214/Zpracovana_platba.jpeg?ex=671a01f2&is=6718b072&hm=faec4442e277ee6e721f950052ee55b295e4e9b1f94600b2ce4087ef2fcb51ec&",
                "ztrata_procento": 1  # Ztráta 100%
            },
            "Při výpravě v Oklahomě tě pohltilo silné tornádo a z batohu se ti ztratily peníze": {
                "obrazek": "https://cdn.discordapp.com/attachments/1297689264372449351/1298560293949018122/Okurka_tornado.jpeg?ex=671a0204&is=6718b084&hm=9d8b5aca1947a026858e7c905e43147d7c1f011b0ec21e4bf0b2bbf82bdf6a53&",
                "ztrata_procento": 2.5  # Ztráta 250
            },
            "Při průzkumu Havajských ostrovů jsi narazil na Tsunami které tě vzalo s sebou": {
                "obrazek": "https://cdn.discordapp.com/attachments/1297689264372449351/1298560294251003947/Okurka_tsunami.jpeg?ex=671a0204&is=6718b084&hm=466120616b89c1ffbef5947cdf7987053de864a84fbf4bc43a3706f11077b36a&",
                "ztrata_procento": 2.5  # Ztráta 250%
            }
        }

        # Náhodný výběr typu přepadení
        nazev_prepadeni, data_prepadeni = random.choice(list(prepadeni_typy.items()))
        ztrata_procento = data_prepadeni["ztrata_procento"]
        obrazek = data_prepadeni["obrazek"]

        # Výpočet ztráty podle procenta pro daný typ přepadení
        ztrata = round(celkovy_bonus * ztrata_procento)

        # Uložení změny peněz po přepadení
        users[user_id]["penize"] -= ztrata

        # Vytvoření embedu s názvem přepadení, procentem ztráty a obrázkem
        embed = discord.Embed(
            title=f"Výprava se moc nezdařila. {nazev_prepadeni}!",
            description=f"Při výpravě jsi ztratil(a) {ztrata} $",
            color=discord.Color.red()
        )
        embed.set_image(url=obrazek)

        # Poslání zprávy o přepadení
        await ctx.send(embed=embed)

    users[user_id]["penize"] += celkovy_bonus
    users[user_id]["vypravy"] += 1
    users[user_id]["ziskano_celkem"] += celkovy_bonus
    await ctx.send(f'**{ctx.author.name}** se vydal na výpravu a získal {celkovy_bonus} $')

    save_data(users)
    await ctx.send(f'Po výpravě máš {users[user_id]["penize"]} $')


@bot.command(name="profil")
async def profil(ctx):
    users = load_data()
    user_id = str(ctx.author.id)

    # Pokud uživatel neexistuje, inicializuje se nový profil
    if user_id not in users:
        users[user_id] = {"penize": 0, "vypravy": 0, "ziskano_celkem": 0,
                          "mec_lvl": 0, "brneni_lvl": 0, "batoh_lvl": 0, "talisman_lvl": 0}

    user_data = users[user_id]

    # Získání dat pro zobrazení v profilu
    penize = user_data["penize"]
    vypravy = user_data["vypravy"]
    mec_lvl = user_data.get("mec_lvl", 1)
    brneni_lvl = user_data.get("brneni_lvl", 1)
    batoh_lvl = user_data.get("batoh_lvl", 1)
    talisman_lvl = user_data.get("talisman_lvl", 1)

    # Ceny vylepšení (pro herní část profilu)
    prices = {
        "mec": mec_lvl * 100,
        "brneni": brneni_lvl * 150,
        "batoh": batoh_lvl * 50,
        "talisman": talisman_lvl * 200
    }

    # Zpráva profilu uživatele
    profil_msg = (f'**Profil uživatele {ctx.author.name}:**\n'
                  f'💰 Peníze: {penize} $\n'
                  f'📅 Počet výprav: {vypravy}\n'
                  f'⚔️ Úroveň meče: {mec_lvl}\n'
                  f'🛡️ Úroveň brnění: {brneni_lvl}\n'
                  f'🎒 Úroveň batohu: {batoh_lvl}\n'
                  f'🔮 Úroveň talismanu: {talisman_lvl}')

    # Odeslání zprávy s uživatelským profilem
    await ctx.send(profil_msg)

    # Uložení dat, pokud byla inicializována nová data
    save_data(users)

class UpgradeView(View):
    def __init__(self, user_id, ceny, users):
        super().__init__()
        self.user_id = user_id
        self.ceny = ceny
        self.users = users

    # Funkce pro tlačítko meče
    @discord.ui.button(label="Meč", style=discord.ButtonStyle.primary)
    async def upgrade_mec(self, interaction: discord.Interaction, button: Button):
        await self.upgrade_item(interaction, "mec")

    # Funkce pro tlačítko brnění
    @discord.ui.button(label="Brnění", style=discord.ButtonStyle.primary)
    async def upgrade_brneni(self, interaction: discord.Interaction, button: Button):
        await self.upgrade_item(interaction, "brneni")

    # Funkce pro tlačítko batohu
    @discord.ui.button(label="Batoh", style=discord.ButtonStyle.primary)
    async def upgrade_batoh(self, interaction: discord.Interaction, button: Button):
        await self.upgrade_item(interaction, "batoh")

    # Funkce pro tlačítko talismanu
    @discord.ui.button(label="Talisman", style=discord.ButtonStyle.primary)
    async def upgrade_talisman(self, interaction: discord.Interaction, button: Button):
        await self.upgrade_item(interaction, "talisman")

    async def upgrade_item(self, interaction: discord.Interaction, item):
        user_id = str(interaction.user.id)  # Opraven přístup k uživateli

        if user_id != self.user_id:  # Ověření, zda jde o správného uživatele
            await interaction.response.send_message("Nemůžeš použít toto tlačítko, zadej svůj příkaz !c upgrade", ephemeral=True)
            return

        cena = self.ceny[item]

        if self.users[user_id]["penize"] < cena:
            await interaction.response.send_message(f'Nemáš dost peněz na zakoupení {item}. Potřebuješ {cena} $.', ephemeral=True)
            return

        # Získání aktuální úrovně itemu
        current_level = self.users[user_id].get(f"{item}_lvl", 0)

        # Kontrola maximální úrovně
        if current_level >= 5:
            await interaction.response.send_message(f"Tento {item} již dosáhl maximální úrovně 5 a nelze ho dále upgradovat.", ephemeral=True)
            return

        # Odečteme peníze a zvýšíme úroveň zakoupeného vybavení
        self.users[user_id]["penize"] -= cena
        self.users[user_id][f"{item}_lvl"] += 1  # Zvýšení úrovně itemu

        save_data(self.users)
        await interaction.response.send_message(f'Zakoupil(a) jsi {item}. Nyní máš {self.users[user_id]["penize"]} $.')
        self.stop()

@bot.command()
async def upgrade(ctx, item: str = None):
    users = load_data()
    user_id = str(ctx.author.id)

    # Ceny pro jednotlivé položky (meč, brnění, batoh, talisman)
    ceny = {
        "mec": 10000,
        "brneni": 10000,
        "batoh": 10000,
        "talisman": 10000
    }

    # Kontrola, zda uživatel existuje
    if user_id not in users:
        await ctx.send("Nemáš účet. Použij příkaz pro vytvoření účtu.")
        return

    if item is None:
        # Získání aktuálních úrovní itemů
        item_buttons = []
        for item_name in ceny.keys():
            current_level = users[user_id].get(f"{item_name}_lvl", 0)
            if current_level < 5:  # Zobrazit pouze itemy, které lze upgradovat
                item_buttons.append(item_name)

        # Vytvoření interaktivních tlačítek pro dostupné itemy
        view = UpgradeView(user_id, ceny, users)
        await ctx.send("Vyber, co chceš upgradovat:", view=view)
        return

    # Kontrola, zda uživatel zadal platný item
    if item not in ceny:
        await ctx.send(f"Položka '{item}' není k dispozici v obchodě. Dostupné položky: mec, brneni, batoh, talisman.")
        return

    # Získání aktuální úrovně itemu
    current_level = users[user_id].get(f"{item}_lvl", 0)

    # Přidání slovníku pro mapování názvů itemů
    item_names = {
        "mec": "Meč",
        "brneni": "Brnění",
        "batoh": "Batoh",
        "talisman": "Talisman"
    }

    # Kontrola maximální úrovně
    if current_level >= 5:
        await ctx.send(f"Tento {item_names} již dosáhl maximální úrovně 5 a nelze ho dále upgradovat")
        return

    cena = ceny[item]

    if users[user_id]["penize"] < cena:
        await ctx.send(f'Nemáš dost peněz na zakoupení {item}. Potřebuješ {cena} $.')
        return

    # Odečteme peníze a zvýšíme úroveň zakoupeného vybavení
    users[user_id]["penize"] -= cena
    users[user_id][f"{item}_lvl"] += 1  # Zvýšení úrovně itemu

    # Uložení změn
    save_data(users)


    # Získání aktuální úrovně všech itemů
    current_levels = {
        "mec": users[user_id].get("mec_lvl", 0),
        "brneni": users[user_id].get("brneni_lvl", 0),
        "batoh": users[user_id].get("batoh_lvl", 0),
        "talisman": users[user_id].get("talisman_lvl", 0)
    }

    await ctx.send(f'Zakoupil(a) jsi {item}. Nyní máš {users[user_id]["penize"]} $ a úroveň {item} je nyní {users[user_id][f"{item}_lvl"]}.')


    # Funkce pro zobrazení úrovní jako čtverečků
    def level_representation(level, max_level=5):
        filled = "🟩 " * level
        empty = "⬜ " * (max_level - level)
        return filled + empty

    # Připravíme zprávu
    embed = discord.Embed(
        title=f"Herní profil pro {ctx.author.name}",
        color=discord.Color.green()
    )

    # Přidání aktuálních vylepšení do zprávy
    embed.add_field(name="Aktuální úrovně vylepšení",
                    value=f"Meč: {level_representation(mec_lvl)}\nBrnění: {level_representation(brneni_lvl)}\nBatoh: {level_representation(batoh_lvl)}\nTalisman: {level_representation(talisman_lvl)}",
                    inline=False)

    # Přidání dostupných vylepšení k nákupu
    embed.add_field(name="Dostupná vylepšení k nákupu",
                    value=f"Meč: {prices['mec']} $\nBrnění: {prices['brneni']} $\nBatoh: {prices['batoh']} $\nTalisman: {prices['talisman']} $",
                    inline=False)

    await ctx.send(embed=embed)


@bot.command(name="gamereset")
@commands.has_permissions(administrator=True)  # Pouze pro adminy
async def gamereset(ctx, option: str, user: discord.User = None):
    users = load_data()

    # Reset všech uživatelů
    if option == "all":
        for user_id in users:
            users[user_id]["penize"] = 0
            users[user_id]["vypravy"] = 0
            users[user_id]["mec_lvl"] = 0
            users[user_id]["brneni_lvl"] = 0
            users[user_id]["batoh_lvl"] = 0
            users[user_id]["talisman_lvl"] = 0
            users[user_id]["ziskano_celkem"] = 0

        # Uložení změn
        save_data(users)
        await ctx.send("Herní statistiky všech uživatelů byly resetovány.")

    # Reset jednoho uživatele
    elif option == "user" and user:
        user_id = str(user.id)

        # Kontrola, zda hráč existuje
        if user_id not in users:
            await ctx.send(f'Uživatel {user.name} nemá herní profil.')
            return

        # Reset herních statistik pro daného uživatele
        users[user_id]["penize"] = 0
        users[user_id]["vypravy"] = 0
        users[user_id]["mec_lvl"] = 0
        users[user_id]["brneni_lvl"] = 0
        users[user_id]["batoh_lvl"] = 0
        users[user_id]["talisman_lvl"] = 0
        users[user_id]["ziskano_celkem"] = 0

        # Uložení změn
        save_data(users)
        await ctx.send(f'Herní statistiky pro {user.name} byly resetovány.')

    else:
        await ctx.send(
            "Neplatný příkaz. Použijte '!c gamereset all' pro reset všech hráčů nebo '!c gamereset user @uživatel' pro reset jednoho hráče.")

# Příkaz pro obsloužení chyby nedostatku oprávnění
@gamereset.error
async def gamereset_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nemáš dostatečná oprávnění k použití tohoto příkazu.")

@bot.command(name="prikazy")
async def prikazy(ctx):
    image_url = 'https://cdn.discordapp.com/attachments/1297689264372449351/1298671274897313873/Discord_fnqtEd5UIB.png?ex=671a6960&is=671917e0&hm=f30803bb42224e3e487fb6ed9a2509cb401272bd771a09a25dfb1598775757d6&'
    await ctx.send("Pro přiblížení příkazů prosím klikni na obrázek!", embed=discord.Embed().set_image(url=image_url))



bot.run('BOTTOKEN')


# Poslední úprava 23.10.2024 21:01
