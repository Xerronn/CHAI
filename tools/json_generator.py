import re

#side project, probably will be useless. looks at the python file and strips out the intents
#could potentially be used to automatically generate json files if I pre-coded the phrases
with open('sprint2.py') as infile:
    rawIntents = ", ".join(re.findall('@ask.intent\(.+\)',infile.read()))
    
    intents = re.findall('"(.*?)"', rawIntents)
    print(set(intents))

    