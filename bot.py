import discord, sys, json, requests, praw, prawcore, random, pickle, os, mimetypes, urllib.request, traceback, os
from poll import Poll
from pytz import timezone
from datetime import datetime
from quotes import QuotesConnection

class Bot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.connection = QuotesConnection()
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
    
    # def check_image(self, url):
    #     #https://stackoverflow.com/questions/10543940/check-if-a-url-to-an-image-is-up-and-exists-in-python
    #     mimetype,encoding = mimetypes.guess_type(url)
    #     return (mimetype and mimetype.startswith('image'))
        
    #Save and load are untested.
    def save_polls(self):
        with open('polls.dat', 'wb') as file:
            pickle.dump(self.polls, protocol=pickle.HIGHEST_PROTOCOL)

    def load_polls(self):
        with open('polls.dat', 'rb') as file:
            self.polls = pickle.load(file) 

    async def print_poll(self, poll, channel): #TODO: Delete Old message   
        await channel.send(poll.print_poll())

    #Core Methods#
    async def meme_of_the_day(self):
        time_zone = timezone('EST')
        est_time = datetime.now(time_zone)
        if est_time.hour == 7:
            channel = self.get_channel(618635474470305793)
            await channel.send("Meme of the day:", embed=self.reddit('ProgrammerHumor', True))

    def reddit(self,sub,top=False):
            reddit = praw.Reddit(client_id='f-vPBrJFobgQcg',
                                 client_secret=self.get_token("REDDIT_TOKEN"),
                                 user_agent='discord-bot')
            try:
                if not top:
                    posts = list(reddit.subreddit(sub).hot(limit=20))
                else:  
                    posts = list(reddit.subreddit(sub).top('day'))[0]
            except prawcore.exceptions:
                return discord.Embed(title='Uh oh... It looks likes like there are not pots from /r/' + sub, description='Try a different sub', color=0x333333)
            print("List of posts: " + str(posts))  
            if not posts:
                return discord.Embed(title='Uh oh... It looks likes like there are not pots from /r/' + sub, description='Try a different sub', color=0x333333)
                      
            submission = random.choice(posts)  
                
            
            mes_title = 'From reddit.com/r/' + sub +':\n'
            mes_desc = '> By /u/' + submission.author.name + '\n '
            mes = discord.Embed(title=mes_title, description=mes_desc, color=0x333333)
            
            post_desc = '\n'
            if submission.selftext:
                if len(submission.selftext) > 1024:
                    post_desc = submission.selftext[0:500] + "... \n***Read More here:*** " 
                else: 
                    post_desc += submission.selftext + '\n'
            post_desc += submission.shortlink
            
            mes.add_field(name=submission.title, value=post_desc, inline=True)
            mes.set_footer(text=' Upvotes: ' + str(submission.score))
            
            if(not 'reddit' in submission.url):
                mes.set_image(url=submission.url)

            mes.set_thumbnail(url=submission.subreddit.stylesheet.subreddit.icon_img)

            # try:
            #     subURL = "https://www.reddit.com/r/"+submission.subreddit.display_name+"/about.json"
            #     print(subURL)
            #     subJSON = requests.get(subURL).json()
            #     print(subJSON)
            #     thumbnail = subJSON['data']['icon_img']
            #     mes.set_thumbnail(url=thumbnail)
            # except:
            #     traceback.print_exc(file=sys.stdout)

            if(not submission.over_18):
                #return ('From reddit.com/r/' + sub +':\n**' + submission.title + '**\n' + submission.url + '\n')
                return mes
            else:
                mes = discord.Embed(title='Uh oh... It looks like the a randomly selected post is marked NSFW. Text and image blocked. :underage: ', description='Link: ||' + submission.shortlink + '||', color=0x333333)
                return mes

    def get_weather(self, zip):
        print('Accessing OpenWeatherMapAPI with token')
        weatherToken = self.get_token('WEATHER_TOKEN')
        weatherAddress = 'http://api.openweathermap.org/data/2.5/forecast?zip=' + str(
            zip) + ',us&APPID=' + weatherToken

        print('Retrieving JSON Data ')
        weatherJSON = requests.get(weatherAddress).json()
        if weatherJSON['cod'] != '200':
            print(weatherJSON)
            return ("Uh oh... There seems to be a problem retrieving weather info for the entered ZIP Code")

        weatherTempK = weatherJSON['list'][0]['main']['temp']
        weatherTempF = round((weatherTempK* (9 / 5) - 459.67))
        weatherStatus = weatherJSON['list'][0]['weather'][0]['main']
        location = weatherJSON['city']['name'] + ', ' + weatherJSON['city']['country']
        icon = weatherJSON['list'][0]['weather'][0]['icon']

        # mes = ('Here is the current weather in ' + location + ', ' + str(
        #         zip) + ':\n```The temperature is ' + weatherTemp +
        #         ' degrees fahrenheit\nCurrently the weather status is '
        #         + weatherStatus + '```')

        location_title = ('> ' + location + ', ' + str(zip) + '')
        temperature_title = 'The temperature is `'  + str(weatherTempF) + ' degrees` fahrenheit.' 
        status_title= 'Currently the weather status is `' + weatherStatus + '`'

        if (weatherTempF <= 0):
            temperature_desc = " It's really cold out there! Be careful! :snowflake: \n"
            color = 0x0011ff
        elif (weatherTempF < 32):
            temperature_desc = "> Looking like its below freezing. Bring a coat! :snowman: \n"
            color = 0x33FFF9
        elif (weatherTempF < 60):
            temperature_desc = "> It's looking chilly out there. Wear some layers! :leaves: \n"
            color =  0x6D65BF
        elif(weatherTempF < 82):
            temperature_desc = "> Now that's what we like to see. :sunglasses: \n"
            color = 0x33FF80
        else:
            temperature_desc = "> Woah, it's getting kind of hot. Stay hydrated! \n"
            color = 0xFF3333
        
        status_desc = '> ' + weatherJSON['list'][0]['weather'][0]['description'].capitalize() + '.\n'
        
        icon = icon.replace("n", "d")

        image_link = 'http://openweathermap.org/img/wn/' + icon + '@2x.png'

        mes = discord.Embed(title="Here's the current weather in:", description=location_title, color=color)
        mes.set_thumbnail(url=image_link)
        mes.add_field(name=temperature_title, value=temperature_desc, inline=True)
        mes.add_field(name=status_title, value=status_desc, inline=True)

        return mes  
                
    #Discord API Methods#
    async def on_message(self, message):
        #Note. Await stops other processes until this one is done
        channel = message.channel 

        #print('Message from {0.author}: {0.content} from {0.channel}'.format(message))
        if message.author == self.user:
                return

        arg = []
        arg = message.content.split(" ")

        if message.author.id == 691687543829168140:
            await message.channel.send("Mary did you know?")
        elif message.author.id == 691689285094604841:
            await message.channel.send("Hey Chris, do you have Java?")

        whitelist = [570800314702364713, 412316581171822622, 572224322014412830] #Server Ids that can use quotes 

        if arg[0].lower() == "!help":
            await message.channel.send( "Commands: \n `!reddit [sub]` - Retrieves a random hot post from the given sub. Defaults to /r/ProgrammerHumor\n`!weather [zipcode]` - Retrieves the weather from the given zip code. Defaults to Allendale.\n `!poll [argument]` - See `!poll help` for more information")
        
        elif arg[0].lower() == "!debug" and message.author.id == 186642747220951040:
            if arg[1].lower() == "channelid":
                await message.channel.send( str(message.channel.id))
            elif arg[1].lower() == "serverid":
                await message.channel.send( str(message.channel.guild.id))
            elif arg[1].lower() == "users":
                mes = "**Here are the users:\n**"
                for i in message.channel.guild.members:
                    mes += "Name -  " + i.name + "\tId - " + str(i.id) + "\n"
                await message.channel.send( mes)
            elif arg[1].lower() == "help":
                await message.channel.send("`channelID`, `serverID`, `users`")

        elif arg[0].lower() == "!test" and message.author.id == 186642747220951040:
            if arg[1].lower() == "embedded":
                mes = discord.Embed(title="Test Embedded Message", description="Description", color=0xff0000)
                mes.add_field(name="My first field", value="Hello World", inline=False)
                await message.channel.send(embed=mes)

                
        elif arg[0].lower() == "!quotes" and (message.channel.guild.id in whitelist):
            if arg[1].lower() == "help":
                await message.channel.send( "Arguments:\n`check` - Lists the people in the database\n`list [Person]` - View the list of quotes given by a person\n`add [Quote] ~ [Person]` - Adds a quote to the database. **Important Note**: Make sure to have `~` as the delimitor between the quote and person\n")
            elif arg[1].lower() == "check":
                people = self.connection.get_people()
                mes = "`"
                mes += '`, `'.join(people)
                mes += "`"
                await message.channel.send( mes)
            elif arg[1].lower() == "list":
                person = ' '.join(arg[2:len(arg)])
                quotes = self.connection.get_quotes(person)
                if not quotes:
                    await message.channel.send( "Person `" + str(person) + "` does not exist")
                    return
                mes = "**Quotes from** `" + str(person) + "`:" 
                char_length = len(mes)
                for quote in quotes:
                    temp = "\n-\n> " + quote.replace("\n", "\n> ")
                    char_length += len(temp)
                    if char_length > 2000:
                        await message.channel.send(mes)
                        mes = ""
                        char_length = len(temp)
                    mes += temp
                await message.channel.send(mes) #Turn this into an embedded message eventually
            elif arg[1].lower() == "add":
                info = (' '.join(arg[2:len(arg)])).split("~")
                if len(info) == 1:
                    await message.channel.send( "Make sure to have `~` as the delimitor between the quote and person!!!")
                    return
                quote = info[0]
                person = info[1].strip()    
                mes = self.connection.insert_quote(quote, person, message.author.id)
                await message.channel.send(mes)
            elif arg[1].lower() == "merge":
                temp = (' '.join(arg[2:len(arg)])).split(">")
                if len(temp) != 2:
                    await message.channel.send("Invalid Syntax. Try: `!quotes merge [name1], [name2] > [new_name]")
                old_names = temp[0].split(",")
                for i in range(0, len(old_names)):
                    old_names[i] = old_names[i].strip()
                new_name = temp[1].strip()
                mes = self.connection.merge_people(old_names, new_name)
                await message.channel.send(mes)


        elif arg[0].lower() == "!reddit":
            if len(arg) > 2: #
                await message.channel.send("Incorrect command usage.\nExample: `!reddit [*Subreddit*]`")
            elif len(arg) == 1:
                arg.append("ProgrammerHumor")

            print("Retrieving post from /r/" + arg[1])
            try:
                await message.channel.send(embed=self.reddit(arg[1]))
            except:
                await message.channel.send("Unexpected error. :robot:")
                traceback.print_exc(file=sys.stdout)
        
        elif arg[0].lower() == "!weather":
            if (len(arg) == 1):
                await message.channel.send(embed=self.get_weather(49401))
            elif (len(arg) == 2):
                print(arg[1])
                await message.channel.send(embed=self.get_weather(arg[1]))
        
        elif arg[0].lower() == "!poll":
            #arg[1] is the command
            #arg[2] and up are typically areguments for the operation
            #TODO Delete user commands after input

            if len(arg) < 2:
                await message.channel.send( "Incorrect command usage... Try !poll help")
            else:     
                if arg[1].lower() == "help": #TODO Needs a help menu https://stackoverflow.com/questions/33066383/print-doc-in-python-3-script
                        await message.channel.send("Poll Commands\n`new [question]` - creates a new poll in the channel\n`add [option]` - adds a new option to the current poll\n`nudge` - nudges the poll in the channel\n`vote [letter]` - vote for a letter\n`end` - ends the poll")            
                elif arg[1].lower() == "new": #TODO: Check if a poll is active or not
                    if len(arg) < 3:
                        await message.channel.send( "*Please enter a prompt for the poll*")
                    else:
                        question = " ".join(arg[2:len(message.content)-1])
                        self.polls[message.channel.id] = Poll(question, message.channel.id) 
                        await self.print_poll(self.polls[message.channel.id], message.channel) 
                else:  
                    try:
                        selected = self.polls[message.channel.id]
                    except TypeError and KeyError:
                        await message.channel.send( "That poll does not exist")
                        return

                    if arg[1].lower() == "add" and selected.active:
                        answer = " ".join(arg[2:len(message.content)-1])
                        try:
                            selected.add_answer(answer)
                            await self.print_poll(selected, message.channel)
                        except IndexError:
                            await message.channel.send( "Max answers reached! No more answers can be added!")
                        
                    elif arg[1].lower() == "nudge" and selected.active:
                        await self.print_poll(selected, message.channel)

                    elif arg[1].lower() == "end" and selected.active:
                        selected.active = False
                        await message.channel.send( "Poll ended")

                    elif arg[1].lower() == "vote" and selected.active:
                        try:
                            selected.vote(arg[2], message.author.id) 
                            await self.print_poll(selected, message.channel) 
                        except ValueError:
                            await message.channel.send( str(message.author.name + " just tried to vote twice... Shame!"))
                        except IndexError:
                            await message.channel.send( str(message.author.name + ", that is not a valid answer"))
                        
                    

                

    async def on_reaction_add(self, reaction, user):
        print('reaction') #TODO Reaction for voting!

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        try:
            await self.meme_of_the_day()
        except:
            traceback.print_exc(file=sys.stdout)

    async def send_message(self, channel, msg):
        await channel.send(msg)