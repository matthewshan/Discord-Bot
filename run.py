from bot import Bot
import requests

bot = Bot()
bot.run(os.environ['DISCORD_TOKEN'])
