import os, google.generativeai as genai

os.environ["GEMINI_API_KEY"] = "Ai key here"

print("Library version:", genai.__version__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = [m.name for m in genai.list_models()]
print("\nAvailable models:")
for m in models:
    print(m)
