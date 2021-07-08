import argparse
import dfagent


class AgentTranslatorInterface:

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('agent_zip')
        self.parser.add_argument('-s', '--source', nargs='?', default='en', type=str)
        self.parser.add_argument('-t', '--target', type=str)
        self.parser.add_argument('-f', '--outfile', type=str)
        self.args = self.parser.parse_args()
        
        self.agent_zip = self.args.agent_zip
        self.source = self.args.source
        self.target = self.args.target
        self.outfile = self.args.outfile

    def __call__(self):
        self.agent = dfagent.DialogflowAgent(self.agent_zip, source=self.source, target=self.target)
        self.agent.translate_intents()
        self.agent.translate_responses()
    
    def print(self):
        print(self.args)

# Module testing purposes only!
if __name__ == '__main__':
    txi = AgentTranslatorInterface()
    txi.print()