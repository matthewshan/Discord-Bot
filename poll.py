class Poll():
    question = ''
    answers = [] #TODO Change this into a dictionary with votes 
    channel = ''
    active = True

    def __init__(self, q, i):
        self.question = q
        self.answers = []
        self.channel = i

    def add_answer(self, input):
        if not self.active:
            raise ValueError("Poll is inactive!!!")
        if len(self.answers) >= 26:
            raise IndexError('There are already 26 answers!')
        self.answers.append(input)

    def set_id(self, input):
        self.id = input
    
    def print_poll(self):
        msg = '**' + self.question + '**\n'
        for s in self.answers:
            msg = msg + str('\t' + s + '\n')

        return msg

    def vote(self, c):
        c = c.upper()
        if instanceof(str) and c == 1 and ord(c) >= 65 and ord(c) <= 90:
            return "Okay" #TODO After changing the ansers array to a dict, add a vote
        return "Bad" 

    #TODO Save polls method
