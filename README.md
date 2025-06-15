# ScriptCord

[![Downloads](https://img.shields.io/github/downloads/Program132/ScriptCord/total?style=for-the-badge)](https://github.com/Program132/ScriptCord/releases)
[![Code size](https://img.shields.io/github/languages/code-size/Program132/ScriptCord?style=for-the-badge)](https://github.com/Program132/ScriptCord)
[![Last Release](https://img.shields.io/github/release/Program132/ScriptCord?style=for-the-badge)](https://github.com/Program132/ScriptCord/releases/latest)

# 🔥 Introduction
ScriptCord is a scripting language designed to simplify the creation of Discord bots using an intuitive and accessible syntax. It allows users to define commands, send messages, add reactions, manage roles, and create embeds.

# 🛠 Installation
Before getting started, make sure you have Python 3.8+ installed and install the required dependencies:

```
git clone https://github.com/your-repo/ScriptCord.git
cd ScriptCord
pip install -r requirements.txt
```

# ⚙️ Language Syntax

## 🚀 Create a Command
A script can be set as a command by assigning values to the global variables COMMAND_NAME, DESCRIPTION, and ALIASES.
- COMMAND_NAME is the name of the command.
- DESCRIPTION is the command's description.
- ALIASES represents alternative names for the command, separated by commas.

IMPORTANT: Command names and aliases must not contain spaces.

```
config COMMAND
set COMMAND_NAME "hello"
set DESCRIPTION "Sends a welcome message"
set ALIASES "hi, greetings"
```

## ✉️ Send a Message to a Channel
Specify the message and the channel ID where the message should be sent.

```
send "Welcome to the server!" 123456789012345678
```

## 😀 Add a Reaction
Specify the emoji (wrapped in quotes) and the message ID where the reaction should be placed.

```
react ":smile:" 987654321098765432
```

## 🔰 Add/Remove a Role to a Member
Specify the action (add or remove), the member ID, and the role ID.

```
role:add 111222333444555666 777888999000111222
role:remove 111222333444555666 777888999000111222
```

## 📌 Create and Send Embeds
Embeds allow structured messages with rich formatting in Discord. You can configure their title, description, color, fields, author, thumbnail, footer, and send them.

1️⃣ Create a new embed:
```
embed:create embedName
```

2️⃣ Configure an embed:
```
embed:conf embedName "My Title" "My URL" "My Desc" "My Color"
```

3️⃣ Set the author:
```
embed:set_author embedName "Name" "URL" "Icon URL"
```

4️⃣ Add a thumbnail:
```
embed:set_thumbails embedName "URL"
```

5️⃣ Add fields (inline or non-inline):
```
embed:add_l embedName "Title" "Value"
embed:add_nl embedName "Title" "Value"
```

6️⃣ Set the footer:
```
embed:set_footer embedName "Footer text"
```

7️⃣ Send the embed to a channel:
```
embed:send embedName 4546545648979165156
```