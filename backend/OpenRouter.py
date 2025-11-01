import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OpenRouterClient:
    """Client for interacting with OpenRouter API"""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.3-8b-instruct:free"

    def send_message(self, message, temperature=0.7, max_tokens=500):
        """
        Send a message to the OpenRouter API and get a response

        Args:
            message (str): The message to send to the model
            temperature (float): Temperature for response generation (0.0-1.0)
            max_tokens (int): Maximum number of tokens in the response

        Returns:
            str: The model's response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            print(f"Error making request to OpenRouter: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise


def main():
    """Test function to demonstrate OpenRouter integration"""
    print("Initializing OpenRouter client...")
    client = OpenRouterClient()

    # Send a test message
    test_message = "Hello! Can you tell me a short fun fact about llamas?"
    print(f"\nSending test message: '{test_message}'")
    print("-" * 50)

    response = client.send_message(test_message)

    print(f"\nModel Response:")
    print(response)
    print("-" * 50)
    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
