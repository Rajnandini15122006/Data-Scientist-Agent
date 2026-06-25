import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Set your API key
API_KEY = "AIzaSyBI5Yb6mGXg_1nmhErVnKaL2frY5DEyEo4"  # Replace with your actual key
os.environ["GOOGLE_API_KEY"] = API_KEY

# Test different models
models_to_test = [
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash"
]

for model_name in models_to_test:
    try:
        print(f"\nTesting {model_name}...")
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        response = llm.invoke("Hello, say 'working' if you can read this.")
        print(f"✅ {model_name} is WORKING!")
        print(f"Response: {response.content}")
        break  # Use the first working model
    except Exception as e:
        print(f"❌ {model_name} failed: {str(e)[:100]}")

print("\nTest complete!")