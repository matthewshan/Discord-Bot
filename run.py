from bot import Bot
import requests

bot = Bot()
# print(requests.get('https://custardquotesapi.azurewebsites.net/quotes', headers={'ApiKey': bot.get_token('API_KEY')}).json())
bot.run(bot.get_token('DISCORD_TOKEN'))
