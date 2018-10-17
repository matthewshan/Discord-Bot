class Poll(object):
    '''
    Constructor for the poll which takes question and channelID 

    @param q is the new self.question
    @param c is the new self.channel
    '''
    def __init__(self, q, c):
        #Question of the poll
        self.question = q

        #Keys: A-Z, Values: [Answer, Votes]
        self.answers = {} 

        #Users
        self.users = []

        #Channel ID
        self.channel = c

        #Checks if the poll is active or not
        self.active = True 

        #This is the ASCII char before A
        self.track = 96

        #This is the last printed poll sent
        self.prev_msg = None


    '''
    Adds an answer to self.answers

    @param input is the new answer that will be put in self.answers
    '''
    def add_answer(self, input):
        if len(self.answers) >= 26:
            raise IndexError("There are already 26 answers!")
        self.track = self.track+1
        self.answers.update({chr(self.track) : [input, 0]})
        
    
    '''
    Prints the poll

    @returns The poll's status in a string format
    '''
    def print_poll(self):
        msg = "**" + self.question + "**\n"

        if len(self.answers) == 0:
            msg = msg + "*There are currently no answers to the poll*"

        for s in self.answers.keys():
            msg = msg + ":regional_indicator_" + s + ": - " + self.answers[s][0] + ". `Votes:` `" + str(self.answers[s][1]) + "`\n"

        return str(msg)


    '''
    Adds a number for a vote
    '''
    def vote(self, c, user): #TODO Emoji System and unique votes
        if user in self.users:
            raise ValueError("User has already voted!")
        c = c.lower()
        if type(str) and ord(c) >= 97 and ord(c) <= 122:
            self.answers[c][1] += 1
            self.users.append(user)
        else: 
            raise IndexError("Not an answer!")

    #TODO Save polls method?
