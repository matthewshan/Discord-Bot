import discord
import json
import requests
import praw
import random
import pickle
import os
from poll import Poll
from connection import QuotesConnection

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

        whitelist = [570800314702364713, 412316581171822622] #Server Ids that can use quotes 

        if arg[0].lower() == "!help":
            await self.send_message(message.channel, "Commands: \n `!reddit [sub]` - Retrieves a random hot post from the given sub. Defaults to /r/ProgrammerHumor\n`!weather [zipcode]` - Retrieves the weather from the given zip code. Defaults to Allendale.\n `!poll [argument]` - See `!poll help` for more information")
        
        elif arg[0].lower() == "!debug" and message.author.id == 186642747220951040:
            if arg[1].lower() == "channelid":
                await self.send_message(message.channel, str(message.channel.id))
            elif arg[1].lower() == "serverid":
                await self.send_message(message.channel, str(message.channel.guild.id))
            elif arg[1].lower() == "users":
                mes = "**Here are the users:\n**"
                for i in message.channel.guild.members:
                    mes += "Name -  " + i.name + "\tId - " + str(i.id) + "\n"
                await self.send_message(message.channel, mes)

        elif arg[0].lower() == "!test" and message.author.id == 186642747220951040:
            if arg[1].lower() == "embedded":
                mes = discord.Embed(title="Test Embedded Message", description="Description", color=0xff0000)
                mes.add_field(name="My first field", value="Hello World", inline=False)
                await message.channel.send(embed=mes)

                
        elif arg[0].lower() == "!quotes" and (message.channel.guild.id in whitelist):
            connection = QuotesConnection()
            if arg[1].lower() == "help":
                await self.send_message(message.channel, "Arguments:\n`check` - Lists the people in the database\n`list [Person]` - View the list of quotes given by a person\n`add [Quote] ~ [Person]` - Adds a quote to the database. **Important Note**: Make sure to have `~` as the delimitor between the quote and person\n")
            elif arg[1].lower() == "check":
                people = connection.get_people()
                mes = "`"
                mes += '`, `'.join(people)
                mes += "`"
                await self.send_message(message.channel, mes)
            elif arg[1].lower() == "list":
                person = ' '.join(arg[2:len(arg)])
                quotes = connection.get_quotes(person)
                if not quotes:
                    await self.send_message(message.channel, "Person `" + str(person) + "` does not exist")
                    return
                mes = "**Quotes from** `" + str(person) + ":`\n> "
                mes += '\n\n> '.join(quotes)
                await self.send_message(message.channel, mes)
               
            elif arg[1].lower() == "add":
                info = (' '.join(arg[2:len(arg)])).split("~")
                if len(info) == 1:
                    await self.send_message(message.channel, "Make sure to have `~` as the delimitor between the quote and person!!!")
                    return
                quote = info[0].strip()
                person = info[1].strip()
                mes = connection.insert_quote(quote, person, message.author.name)
                await self.send_message(message.channel, mes)

        elif arg[0].lower() == "!reddit":
            if len(arg) > 2: #
                await self.send_message(message.channel,"Incorrect command usage.\nExample: `!reddit [*Subreddit*]`")
            elif len(arg) == 1:
                arg.append("ProgrammerHumor")

            print("Retrieving post from /r/" + arg[1])

            await self.send_message(message.channel,self.reddit(arg[1]))
        
        elif arg[0].lower() == "!weather":
            if (len(arg) == 1):
                await self.send_message(message.channel, self.get_weather(49401))
            elif (len(arg) == 2):
                print(arg[1])
                await self.send_message(message.channel, self.get_weather(arg[1]))
        
        elif arg[0].lower() == "!poll":
            #arg[1] is the command
            #arg[2] and up are typically areguments for the operation
            #TODO Delete user commands after input

            if len(arg) < 2:
                await self.send_message(message.channel, "Incorrect command usage... Try !poll help")
            else:     
                if arg[1].lower() == "help": #TODO Needs a help menu https://stackoverflow.com/questions/33066383/print-doc-in-python-3-script
                        await self.send_message(message.channel,"Poll Commands\n`new [question]` - creates a new poll in the channel\n`add [option]` - adds a new option to the current poll\n`nudge` - nudges the poll in the channel\n`vote [letter]` - vote for a letter\n`end` - ends the poll")            
                elif arg[1].lower() == "new": #TODO: Check if a poll is active or not
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

                    if arg[1].lower() == "add" and selected.active:
                        answer = " ".join(arg[2:len(message.content)-1])
                        try:
                            selected.add_answer(answer)
                            await self.print_poll(selected, message.channel)
                        except IndexError:
                            await self.send_message(message.channel, "Max answers reached! No more answers can be added!")
                        
                    elif arg[1].lower() == "nudge" and selected.active:
                        await self.print_poll(selected, message.channel)

                    elif arg[1].lower() == "end" and selected.active:
                        selected.active = False
                        await self.send_message(message.channel, "Poll ended")

                    elif arg[1].lower() == "vote" and selected.active:
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