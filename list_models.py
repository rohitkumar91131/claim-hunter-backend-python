
import httpx
import asyncio
import os
from app.config import settings

async def list_models():
    api_key = settings.GOOGLE_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Available Models:")
            for model in data.get('models', []):
                print(f"- {model['name']} (Supported methods: {model.get('supportedGenerationMethods')})")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(list_models())
