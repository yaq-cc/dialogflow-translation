from rich import print
from dfagent import DialogflowAgent

agent = DialogflowAgent('Language-Test-Agent-2.zip', target='es')
agent.translate_intents() # Translate all non-response (usersays) intents
agent.translate_responses() # Translate all response (root) intents

# sample = agent.response_intents[2]
# print(sample)
# agent.translate_response(sample) # Translate all response (root) intents
