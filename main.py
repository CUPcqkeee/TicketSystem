import sqlite3
import dotenv

import disnake
import os

from disnake.ext import commands

dotenv.load_dotenv()


# КОНЧЕНИ БОТ
bot = commands.Bot(
    command_prefix=os.getenv("PREFIX"),
    intents=disnake.Intents.all(),
    case_insensitive=True,
    help_command=None,
    allowed_mentions=disnake.AllowedMentions.all())

# БД
db = sqlite3.connect("TS.db")
cursor = db.cursor()



# КОНЧЕНИ ЗАГРУЗКА МОДУЛЕЙ
path = "./cogs"
for root, dirs, files in os.walk(path):
    for filename in files:
        if filename.endswith(".py"):
            cog_path = os.path.relpath(os.path.join(root, filename), path)
            module = os.path.splitext(cog_path)[0].replace(os.sep, '.')
            bot.load_extension(f"cogs.{module}")

token = os.getenv("TOKEN")
bot.run(token)
