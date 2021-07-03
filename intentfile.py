from rich import print
import os
from dfagent import DialogflowAgent


class IntentFile:

    def __init__(self, fp):
        self.fp = fp
        self.path, self.file = os.path.split(self.fp)
        self.name, self.ext = os.path.splitext(self.file)
        self.type = 'response' if '_usersays_' not in self.name else 'user_says'
        self.langs = None 



if __name__ == '__main__':
    agent = DialogflowAgent('MyCity311demo.zip', target='fr')
    sample = agent.response_intents[0]
    print(vars(IntentFile(sample)))

