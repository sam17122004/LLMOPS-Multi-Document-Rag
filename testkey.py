import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

response = requests.get(url)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit()

models = response.json().get("models", [])

print("=" * 80)
print("AVAILABLE MODELS")
print("=" * 80)

embedding_models = []

for model in models:
    name = model.get("name")
    methods = model.get("supportedGenerationMethods", [])

    print(f"\nModel: {name}")
    print(f"Supported Methods: {methods}")

    if "embedContent" in methods:
        embedding_models.append(name)

print("\n" + "=" * 80)
print("EMBEDDING MODELS")
print("=" * 80)

if embedding_models:
    for model in embedding_models:
        print(model)
else:
    print("❌ No embedding models available for this API key.")