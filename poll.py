class Poll():
    question = ''
    answers = []
    id = ''
    active = True

    def __init__(self, q, i):
        self.question = q
        self.answers = []
        self.id = i

    def add_answer(self, input):
        if not self.active:
            raise ValueError("Poll is inactive!!!")
        if len(self.answers) >= 26:
            raise IndexError('There are already 26 answers!')
        self.answers.append(input)

    def set_id(self, input):
        self.id = input
    
    def print_poll(self):
        msg = self.question + '\n'
        for s in len(self.answers):
            msg.append(str('\t' + s))

        return msg