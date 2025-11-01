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

    def send_message(self, message, temperature=0.3, max_tokens=10):
        """
        Send an email to analyze for phishing and get a confidence score

        Args:
            message (str): The email content to analyze
            temperature (float): Temperature for response generation (lower = more deterministic)
            max_tokens (int): Maximum number of tokens in the response

        Returns:
            str: A single number between 0-100 representing phishing confidence percentage
        """

        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.3-8b-instruct:free"

        phishing_prompt = f"""You are a phishing detection expert. Analyze the following email and return ONLY a single number between 0 and 100, where:
        - 0 means definitely NOT a phishing email (completely legitimate)
        - 100 means definitely IS a phishing email (certain threat)

        Consider these phishing indicators:
        - Suspicious sender domain or email address
        - Urgency tactics or threats
        - Requests for sensitive information (passwords, credit cards, SSN)
        - Suspicious links or attachments
        - Spelling and grammar errors
        - Impersonation of known companies/people
        - Too-good-to-be-true offers
        - Mismatched URLs
        - Generic greetings instead of personalized

        Email to analyze:
        {message}

        Respond with ONLY the number (0-100), nothing else."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": phishing_prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            result = data['choices'][0]['message']['content'].strip()
            
            # Extract just the number if there's any extra text
            import re
            number_match = re.search(r'\d+\.?\d*', result)
            if number_match:
                return number_match.group()
            return result

        except requests.exceptions.RequestException as e:
            print(f"Error making request to OpenRouter: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

"""
def main():
    #Test function to demonstrate OpenRouter integration
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

"""
