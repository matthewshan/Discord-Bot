import discord
import json
import requests
import praw
import random
from poll import Poll

class Bot(discord.Client):
    polls = {}

    #Helper Methods
    '''
    # Method to open text a return it in the form of a String
    '''
    def get_token(self, filename):
        try:
            tokenFile = open('tokens/' + filename, 'r')
            token = tokenFile.read().rstrip()
            tokenFile.close()
        except IOError:
            print('Failed to retrieve token from ' + filename)
            exit(1)
        return token

    #Core Methods#
    def reddit(self,sub):
            reddit = praw.Reddit(client_id='Lz8v84RHrHl_Jw',
                                 client_secret=self.get_token("reddit.txt"),
                                 user_agent='Discord Bot')
            submission = random.choice(list(reddit.subreddit(sub).hot(limit=50)))
            if(not submission.over_18):
                return ('From reddit.com/r/' + sub +':\n**' + submission.title + '**\n' + submission.url + '\n')
            else:
                return ('Uh oh... It looks like the a randomly selected post was Not Safe For Work. It will not be posted on this chat')

    def get_weather(self, zip):
        print('Accessing OpenWeatherMapAPI with token')
        weatherToken = self.get_token('weather.txt')
        weatherAddress = 'http://api.openweathermap.org/data/2.5/forecast?zip=' + str(
            zip) + ',us&APPID=' + weatherToken

        print('Retrieving JSON Data ')
        weatherJSON = requests.get(weatherAddress).json()
        if weatherJSON['cod'] != '200':
            print(weatherJSON)
            return (
                "Uh oh... There seems to be a problem retrieving weather info for the entered ZIP Code")

        weatherTemp = str(
            round((weatherJSON['list'][0]['main']['temp']) * (9 / 5) - 459.67))
        weatherStatus = weatherJSON['list'][0]['weather'][0]['main']
        location = weatherJSON['city']['name'] + ', ' + weatherJSON['city'][
            'country']

        return ('Here is the current weather in ' + location + ', ' + str(
                zip) + ':\n```The temperature is ' + weatherTemp +
                ' degrees fahrenheit\nCurrently the weather status is '
                + weatherStatus + '```')
                
    #Discord API Methods#
    async def on_message(self, message):
        #Note. Await stops other processes until this one is done

        #print('Message from {0.author}: {0.content} from {0.channel}'.format(message))
        if message.author == self.user:
                return

        arg = []
        arg = message.content.split(" ")

        if arg[0] == "!reddit":
            if len(arg) > 2: #
                await self.send_message(message.channel,"Incorrect command usage.\nExample: `!reddit [*Subreddit*]`")
            elif len(arg) == 1:
                arg.append("ProgrammerHumor")

            print("Retrieving post from /r/" + arg[1])

            await self.send_message(message.channel,self.reddit(arg[1]))
        
        elif arg[0] == "!weather":
            if (len(arg) == 1):
                await self.send_message(message.channel, self.get_weather(49401))
            elif (len(arg) == 2):
                print(arg[1])
                await self.send_message(message.channel, self.get_weather(arg[1]))
        
        elif arg[0] == "!poll":
            #Users can create a poll. The bot will keep track of the amount of votes and resend messages as they are
            #nudged
            if len(arg) < 2:
                await self.send_message(message.channel, "Incorrect command usage...")

            if arg[1] == "new":
                self.polls.update({message.channel : Poll(arg[2:len(msg)-1]}))
                print(self.polls[message.channel])

            elif arg[1] == "add":
                self.polls.add_answers(arg[2:len(msg)-1])

            elig

            elif arg[1] == "end":
                print ('End Poll')

            elif arg[1] == "edit":
                print('Edit Poll')

            elif arg[1] == "nudge":
                print('Nudge')

            elif arg[1] == "help":
                return ''

    async def on_reaction_add(self, reaction, user):
        print('reaction')

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

