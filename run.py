from bot import Bot
import requests, os

bot = Bot()
bot.run(os.environ['DISCORD_TOKEN'])
