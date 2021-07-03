import os
import json
import zipfile

class ZipfileError(Exception):
    pass

class DialogflowAgent:

    def __init__(self, agent_zip: str, overwrite=False):
        self.agent_zip = agent_zip
        self.agent_name = self.check_agent(self.agent_zip, overwrite=overwrite)
        self.response_intents = self.get_response_intents(self.agent_name)
        self.response_intent_names = [name for name in self.response_intents.keys()]
        
    def response_intent(self, response_intent_name, lang='en'):
        resp_intent_path = self.response_intents[response_intent_name].training_phrases[lang][1]
        with open(resp_intent_path, 'rb') as src:
            data = json.load(src)
        return data
    
    @staticmethod
    def check_agent(agent_zip, overwrite=False) -> str:
        if not os.path.exists(agent_zip):
            raise FileNotFoundError(f'No agent file ({agent_zip}) was found')
        if not zipfile.is_zipfile(agent_zip):
            raise ZipfileError(f'Something is wrong with the provided agent file ({agent_zip}).')        
        print(f'Agent file {agent_zip} found; parsing agent file.')
            
        agent_name, ext = os.path.splitext(agent_zip)
        if os.path.isdir(agent_name) and not overwrite:
            print(f'Agent file {agent_name} has already been unzipped.')
        else:
            print(f'Creating or overwriting the {agent_name} directory.')
            with zipfile.ZipFile(agent_zip) as archive:
                archive.extractall(path=agent_name)
        return agent_name
    
    @staticmethod
    def get_response_intents(agent_name: str) -> List[ResponseIntent]:
        response_intents = {}
        intents_path = os.path.join(agent_name, 'intents')
        for intent in os.listdir(intents_path):
            intent_name, ext = os.path.splitext(intent)
            if '_usersays_' not in intent:
                response_intents[intent_name] = ResponseIntent(intent_name, intents_path)
        return response_intents
