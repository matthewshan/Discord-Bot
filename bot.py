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
    '''
    # Method to open text a return it in the form of a String
    '''
    def get_token(self, name):
        try:
            token = os.environ[name]
            return token
        except Exception:
            print('Failed to retrieve token from ' + name)
            exit(1)
        
        
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
            reddit = praw.Reddit(client_id='f-vPBrJFobgQcg',
                                 client_secret=self.get_token("REDDIT_TOKEN"),
                                 user_agent='discord-bot')
            submission = random.choice(list(reddit.subreddit(sub).hot(limit=50)))
            if(not submission.over_18):
                return ('From reddit.com/r/' + sub +':\n**' + submission.title + '**\n' + submission.url + '\n')
            else:
                return ('Uh oh... It looks like the a randomly selected post was Not Safe For Work. It will not be posted on this chat')

    def get_weather(self, zip):
        print('Accessing OpenWeatherMapAPI with token')
        weatherToken = self.get_token('WEATHER_TOKEN')
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
        channel = message.channel 

        #print('Message from {0.author}: {0.content} from {0.channel}'.format(message))
        if message.author == self.user:
                return

        arg = []
        arg = message.content.split(" ")

        if arg[0] == "!help":
            await self.send_message(message.channel, "Commands: \n `!reddit [sub]` - Retrieves a random hot post from the given sub. Defaults to /r/ProgrammerHumor\n`!weather [zipcode]` - Retrieves the weather from the given zip code. Defaults to Allendale.\n `!poll [argument]` - See `!poll help` for more information")

        elif arg[0] == "!reddit":
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
                await self.send_message(message.channel, "Incorrect command usage... Try !poll help")
            else:     
                if arg[1] == "help": #TODO Needs a help menu https://stackoverflow.com/questions/33066383/print-doc-in-python-3-script
                        await self.send_message(message.channel,"Poll Commands\n`new [question]` - creates a new poll in the channel\n`add [option]` - adds a new option to the current poll\n`nudge` - nudges the poll in the channel\n`vote [letter]` - vote for a letter\n`end` - ends the poll")            
                elif arg[1] == "new": #TODO: Check if a poll is active or not
                    if len(arg) < 3:
                        await self.send_message(message.channel, "*Please enter a prompt for the poll*")
                    else:
                        question = " ".join(arg[2:len(message.content)-1])
                        self.polls[message.channel.id] = Poll(question, message.channel.id) 
                        await self.print_poll(self.polls[message.channel.id], message.channel) 
                else:  
                    try:
                        selected = self.polls[message.channel.id]
                    except TypeError and KeyError:
                        await self.send_message(message.channel, "That poll does not exist")
                        return

                    if arg[1] == "add" and selected.active:
                        answer = " ".join(arg[2:len(message.content)-1])
                        try:
                            selected.add_answer(answer)
                            await self.print_poll(selected, message.channel)
                        except IndexError:
                            await self.send_message(message.channel, "Max answers reached! No more answers can be added!")
                        
                    elif arg[1] == "nudge" and selected.active:
                        await self.print_poll(selected, message.channel)

                    elif arg[1] == "end" and selected.active:
                        selected.active = False
                        await self.send_message(message.channel, "Poll ended")

                    elif arg[1] == "vote" and selected.active:
                        try:
                            selected.vote(arg[2], message.author.id) 
                            await self.print_poll(selected, message.channel) 
                        except ValueError:
                            await self.send_message(message.channel, str(message.author.name + " just tried to vote twice... Shame!"))
                        except IndexError:
                            await self.send_message(message.channel, str(message.author.name + ", that is not a valid answer"))
                        
                    

                

    async def on_reaction_add(self, reaction, user):
        print('reaction') #TODO Reaction for voting!

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def send_message(self, channel, msg):
        await channel.send(msg)