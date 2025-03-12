import ollama 
from prompts.SBtoEOPrompt import system_message

ollama.create(model="sb-extractor", from_="llama3.2", system=system_message)

ollama.list()
