import discord
import json
import requests
import praw
import random
import pickle
import os
from poll import Poll

class Bot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.polls = {}

    #Helper Methods
    def get_token(self):
        token = os.environ['DISCORD_TOKEN']
        if not token:
            print('Token is empty')
        return token
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
        
    #Save and load are untested.
    def save_polls(self):
        with open('polls.dat', 'wb') as file:
            pickle.dump(self.polls, protocol=pickle.HIGHEST_PROTOCOL)

    def load_polls(self):
        with open('polls.dat', 'rb') as file:
            self.polls = pickle.load(file) 

    async def print_poll(self, poll, channel): #TODO: Delete Old message   
        await self.send_message(channel, poll.print_poll())

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
            #arg[1] is the command
            #arg[2] and up are typically areguments for the operation
            #TODO Delete user commands after input

            if len(arg) < 2:
                await self.send_message(message.channel, "Incorrect command usage...")
            else:                 
                if arg[1] == "new": #TODO: Check if a poll is active or not
                    question = " ".join(arg[2:len(message.content)-1])
                    self.polls[message.channel.id] = Poll(question, message.channel.id) 
                    await self.print_poll(self.polls[message.channel.id], message.channel) 
                else:  
                    try:
                        selected = self.polls[message.channel.id]
                    except TypeError:
                        await self.send_message(message.channel, "That poll does not exist")

                    if arg[1] == "add" and selected.active == True:
                        answer = " ".join(arg[2:len(message.content)-1])
                        try:
                            selected.add_answer(answer)
                            await self.print_poll(selected, message.channel)
                        except IndexError:
                            await self.send_message(message.channel, "Max answers reached! No more answers can be added!")
                        
                    elif arg[1] == "nudge":
                        await self.print_poll(selected, message.channel)

                    elif arg[1] == "end":
                        selected.active = False

                    elif arg[1] == "vote":
                        try:
                            selected.vote(arg[2], message.author.id) 
                            await self.print_poll(selected, message.channel) 
                        except ValueError:
                            await self.send_message(message.channel, str(message.author.name + " just tried to vote twice... Shame!"))
                        except IndexError:
                            await self.send_message(message.channel, str(message.author.name + ", that is not a valid answer"))
                        
                    elif arg[1] == "help": #TODO Needs a help menu https://stackoverflow.com/questions/33066383/print-doc-in-python-3-script
                        return ''

                

    async def on_reaction_add(self, reaction, user):
        print('reaction') #TODO Reaction for voting!

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))