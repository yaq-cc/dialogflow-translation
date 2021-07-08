import os
import json
import zipfile
from typing import List
from copy import deepcopy
from google.cloud import translate_v2 as translate
from rich import print


class ZipfileError(Exception):
    pass

class DialogflowAgent:

    DO_NOT_TRANSLATE = ['@sys.name', '@sys.person', '@sys.geo-city']

    def __init__(self, agent_zip: str, overwrite=False, source='en', target='es', outfile=None):
        self.agent_zip = agent_zip
        self.translator = translate.Client()
        self.source = source
        self.target = target
        self.agent_name = self.check_agent(self.agent_zip, overwrite=overwrite)
        self.outfile = outfile
        self.response_intents: List[str] = []
        self.intents: List[str] = []
        self.get_intents()

    def __del__(self):
        new_zip = 'new_' + self.agent_zip if self.outfile is None else self.outfile
        zip_fps = []
        for root, dirs, files in os.walk(self.agent_name):
            for file in files:
                fp = os.path.join(root, file)
                zip_fps.append(fp)
        with zipfile.ZipFile(new_zip, 'w') as arch:
            for fp in zip_fps:
                arch.write(fp)

    def translate(self, text, source='en', target='es'):
        self.target = self.target if not target else target
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        result = self.translator.translate(text, target_language=self.target, format_='text')
        return result.get('translatedText')

    def check_agent(self, agent_zip, overwrite=False) -> str:
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

    def get_intents(self):
        intents_path = os.path.join(self.agent_name, 'intents')
        for intent in os.listdir(intents_path):
            intent_fp = os.path.join(intents_path, intent)
            if '_usersays_' not in intent:
                self.response_intents.append(intent_fp)
            else:
                self.intents.append(intent_fp)
        return self

    def translate_response(self, intent_fp):
        with open(intent_fp, 'r') as src:
            response_intent = json.load(src)
        responses = response_intent.get('responses')
        for response in responses:
            parameters = [
                (p['value'], p['id'])
                for p in response.get('parameters')
            ]
            messages = response.get('messages')
            new_message = None
            target_found = False
            for message in messages:
                message_language = message.get('lang')
                if message_language == self.source:
                    new_message = deepcopy(message)
                    new_message['lang'] = self.target
                    if not new_message.get('speech'):
                        print('NO Speeches')
                        continue
                    for index, speech in enumerate(new_message['speech']):
                        for p in parameters:
                            speech = speech.replace(p[0], p[1])
                        _speech = self.translate(speech, source=self.source, target=self.target)
                        for p in parameters:
                            _speech = _speech.replace(p[1], p[0])
                        new_message['speech'][index] = _speech
                elif message_language == self.target:
                    if message.get('speech'):
                        target_found = True
                else:
                    continue
            if not target_found:
                messages.append(new_message)
        return response_intent

    def translate_responses(self):
        tot_responses = len(self.response_intents)
        for index, response_fp in enumerate(self.response_intents):
            print(f'Working on {index + 1} / {tot_responses} response intents')
            new_response_intent = self.translate_response(response_fp)
            with open(response_fp, 'w')  as dest:
                json.dump(new_response_intent, dest, indent=4)

    def translate_intent(self, intent_fp):
        with open(intent_fp, 'r') as src:
            response_intent = json.load(src)
        for phrase_index, phrase in enumerate(response_intent):
            response_intent[phrase_index]['lang'] = self.target # Set the language to target.
            for part_index, part in enumerate(phrase['data']):
                if part.get('meta') not in self.DO_NOT_TRANSLATE:
                    response_intent[phrase_index]['data'][part_index]['text'] = self.translate(part['text'], target=self.target)
        return response_intent

    def translate_intents(self):
        source_intents = [intent for intent in self.intents if '_usersays_en' in intent]
        tot_intents = len(source_intents)
        print(f'Total intents: {tot_intents}')
        for index, intent in enumerate(source_intents):
            print(f'Working on {index + 1} / {tot_intents} usersays intents')
            path, file = os.path.split(intent)
            name, ext = os.path.splitext(file)
            root, lang = name.split('_usersays_')
            new_intent_fp = os.path.join(path, root + '_usersays_' + self.target + ext)
            with open(new_intent_fp, 'w') as src:
                tx = self.translate_intent(intent)
                json.dump(tx, src, indent=4)
                