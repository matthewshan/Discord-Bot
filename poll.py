class Poll():
    #Question of the poll
    question = '' 

    #Keys: A-Z, Values: [Answer, Votes]
    answers = {} 

    #Channel ID
    channel = None 

    #Checks if the poll is active or not
    active = True 

    #This is the ASCII char before A
    track = '@' 


    '''
    Constructor for the poll which takes question and channelID 

    @param q is the new self.question
    @param i is the new self.channel
    '''
    def __init__(self, q, i):
        self.question = q
        self.channel = i


    '''
    Adds an answer to self.answers

    @param input is the new answer that will be put in self.answers
    '''
    def add_answer(self, input):
        if not self.active:
            raise ValueError("Poll is inactive!!!")
        if len(self.answers) >= 26:
            raise IndexError('There are already 26 answers!')
        track = char(ord(track+1))
        self.answers.update({str(track) : [input, 0]})
        print(self.answers)
        
    
    '''
    Prints the poll

    @returns The poll's status in a string format
    '''
    def print_poll(self):
        msg = '**' + self.question + '**\n'
        for s in self.answers.items():
            msg = msg + str(s + '\t' + self.answers[s] + '\n')

        return msg


    '''
    Adds a number for a vote
    '''
    def vote(self, c):
        c = c.upper()
        if instanceof(str) and c == 1 and ord(c) >= 65 and ord(c) <= 90:
            self.answers[c][1] += 1
            return "Okay" #TODO After changing the ansers array to a dict, add a vote
        else: 
            raise ValueError("Not an answer!")

    #TODO Save polls method
