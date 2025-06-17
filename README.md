# ScriptCord

[![Downloads](https://img.shields.io/github/downloads/Program132/ScriptCord/total?style=for-the-badge)](https://github.com/Program132/ScriptCord/releases)  
[![Code Size](https://img.shields.io/github/languages/code-size/Program132/ScriptCord?style=for-the-badge)](https://github.com/Program132/ScriptCord)  
[![Latest Release](https://img.shields.io/github/release/Program132/ScriptCord?style=for-the-badge)](https://github.com/Program132/ScriptCord/releases/latest)  

---

## 🔥 Introduction

**ScriptCord** is a tiny DSL (domain-specific language) that lets you drive Discord bots without writing `discord.py` boilerplate:  
- Send messages & reactions  
- Manage roles  
- Build rich embeds  
- Auto-detect server & channels if you don’t specify a `GUILD`  

---

## 🛠 Installation

```bash
git clone https://github.com/Program132/ScriptCord.git
cd ScriptCord
pip install -r requirements.txt
```

Create a config.json with your bot token:
```
{
  "token": "YOUR_DISCORD_BOT_TOKEN"
}
```

## 🚀 Quickstart
Write a .sc script (see “Syntax” below).

In your main.py, wrap everything in ScriptCord:
```python
import json
import discord
from ScriptCord import ScriptCord

# 1. Load token
with open("config.json") as f:
    cfg = json.load(f)

# 2. Create Discord client
intents = discord.Intents.default()
client  = discord.Client(intents=intents)

# 3. Instantiate runner
runner = ScriptCord(client, "my_script.sc")

@client.event
async def on_ready():
    print(f"Bot is ready: {client.user}")
    await runner.run()

client.run(cfg["token"])
```

## ⚙️ Script Syntax
Each script must start with a config directive on line 1:
```
config DEFAULT   # or `config COMMAND`
```
- `DEFAULT` scripts run immediately when you ask to.
- `COMMAND` scripts define a slash/prefix command (not covered currently, coming soon, like events).

### DEFAULT Configuration

You can set the current GUILD where you want to bot search channels, messages etc. if you don't the bot will search everywhere the bot is so it can be very long.
```
set GUILD 123456789012345678
```

### COMMAND Configuration (COMING SOON)

Required variables:
- COMMAND_NAME
- DESCRIPTION

Optional variables:
- ALIASES
- ARGUMENTS
- GUILD

## Send a message
```
send "Hello, world!" 987654321098765432
```

## React to a message
```
react "👍" 987654321098765432
```

## Manage roles
```
role:add    111222333444555666 777888999000111222
role:remove 111222333444555666 777888999000111222
```

## Create & send embeds

- Create embed:
```
embed:create myEmbed
```
- Configure title/URL/description/color (hex with #):
```
embed:conf myEmbed "Title" "https://..." "Description" "#1abc9c"
```
- (Optional) Set author:
```
embed:set_author myEmbed "Bot Name" "https://..." "https://.../icon.png"
```
- (Optional) Set thumbnails:
```
embed:set_thumbnails myEmbed "https://.../thumb.png"
```
- Add fields, inline or block:
```
embed:add_l  myEmbed "Field Title" "Value"   # inline
embed:add_nl myEmbed "Field Title" "Value"   # block
```
- (Optional) Set footer:
```
embed:set_footer myEmbed "Footer text here"
```
- Send the embed:
```
embed:send myEmbed 987654321098765432
```

##  Declare & Use local variables

``` 
setl myLocalVar "The value of my local var"
```
Example:
```
config DEFAULT
set GUILD 1269814367105454174

setl msgContent "Hi, how are you?"
setl id_channel 1383949031377600532

send msgContent 1383949031377600532
```


## 🎯 What ScriptCord Handles
- Auto-detect server & channel from any guild your bot is in.
- Track where messages were sent, so react is fast (no brute-force scan).
- Strip # from hex colors before passing to discord.Color.
- Support for large numeric IDs in set GUILD, send, react, etc.