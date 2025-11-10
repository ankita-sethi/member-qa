#function with name of the file and name of the person returnig all messages in timestamp order = latest first
import json
import os
import google.generativeai as genai
from pathlib import Path
from string import Template

curr_file=Path("data/store.json")

def get_messages(file_path, name):
    with open(file_path,'r',encoding='utf-8') as file:
        raw=json.load(file)
    messages=raw[name]
    sorted_message=sorted(messages, key=lambda x:x["timestamp"], reverse = True)
    result = [f'{m["timestamp"]}:{m["message"]}' for m in sorted_message]
    context= "\n".join(result)
    return context

# print(get_messages(curr_file, "Amina"))
#create python template string?

def get_prompt(context,name,ques):

    t = Template("""
You are a question-answering assistant that answers questions asked by members.  
You must refer to the member $name and the $context provided and answer based on it.

Your answer must:
- Be related to the question asked.
- Refer only to the member context. which is messages and timestamp
- Avoid explaining where the data came from.
- Keep the response concise and in a conversational asnwer
- Dont explicilty mention the timestamps when answering unless asked.

Member name: $name

Messages and timestamp:
$context

User question:
$question

example:
question:When is Layla planning her trip to London?
answer: Layla is planning her trip to London next month.

If you don’t know the answer, reply with: "Apologies, I am not sure about this question."
""")
    
    prompt = t.safe_substitute(name=name, context=context,question=ques)
    return prompt

def link_llm(prompt):
    # sends prompt to open ai

    api_key=os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found. Please set it first.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.0-flash")

    # Generate the response
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating response: {e}"

name ="Amina"
ques= "When is amina husband birthday"
context_r = get_messages(curr_file,name)
prompt_r = get_prompt(context_r,name,ques)
answer = link_llm(prompt_r)

print("model response")
print(answer)


