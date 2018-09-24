class Poll():
    question = ''
    answers = []
    active = True

    def __init__(self, q, a):
        if type(a) is not list:
            raise TypeError('The provided answers is not a list.. {} was provided instead'.format(a))
        question = q
        answers = a

    def add_answer(self, input):
        if not self.active:
            raise ValueError("Poll is inactive!!!")
        if len(self.answers) >= 26:
            raise IndexError('There are already 26 answers!')
        self.answers.append(input)
0