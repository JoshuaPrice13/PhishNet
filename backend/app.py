import requests
import google.oauth2.credentials
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
from dotenv import load_dotenv
import os
import re
from flask import Flask, jsonify, redirect, url_for, session, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure session to work across domains with improved cookie handling
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = '207.148.9.3'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request

# Enable CORS with credentials support
CORS(app, supports_credentials=True, origins=["http://207.148.9.3", "http://207.148.9.3:80"])

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.modify',
    'openid'
]

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"


def analyze_email_with_openrouter(email_content):
    """
    Analyze email content using OpenRouter's Llama 3.3 model

    Args:
        email_content (str): The email content to analyze

    Returns:
        dict: Contains risk_percentage and confidence_percentage
    """
    if not OPENROUTER_API_KEY:
        print("WARNING: OPENROUTER_API_KEY not found in environment variables")
        return {
            "risk_percentage": 0,
            "confidence_percentage": 50,
            "is_phishing": False
        }

    # Truncate email content if too long (OpenRouter has token limits)
    max_content_length = 2000
    if len(email_content) > max_content_length:
        email_content = email_content[:max_content_length] + "..."

    phishing_prompt = f"""You are a cybersecurity expert specializing in phishing email detection. Analyze the following email and provide TWO scores:

1. RISK PERCENTAGE (0-100): How likely is this email to be a phishing attempt?
   - 0-20: Very safe, clearly legitimate
   - 21-40: Mostly safe, minor concerns
   - 41-60: Moderate risk, suspicious elements
   - 61-80: High risk, likely phishing
   - 81-100: Critical risk, definitely phishing

2. CONFIDENCE PERCENTAGE (0-100): How confident are you in your risk assessment?
   - Higher confidence means you're more certain of your risk assessment
   - Lower confidence means the email is ambiguous or unclear

Consider these phishing indicators:
- Suspicious sender domain or email address
- Urgency tactics, threats, or pressure
- Requests for sensitive information (passwords, credit cards, SSN, bank info)
- Suspicious links or attachments
- Spelling and grammar errors
- Impersonation of known companies/people
- Too-good-to-be-true offers or prizes
- Mismatched URLs (hover text vs actual link)
- Generic greetings instead of personalized names
- Unusual requests from known contacts

Email to analyze:
---
{email_content}
---

Respond in EXACTLY this format (just two numbers on separate lines, nothing else):
RISK: [number 0-100]
CONFIDENCE: [number 0-100]"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": phishing_prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 50
    }

    try:
        response = requests.post(OPENROUTER_BASE_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        result = data['choices'][0]['message']['content'].strip()

        # Parse the response to extract risk and confidence
        risk_match = re.search(r'RISK:\s*(\d+)', result, re.IGNORECASE)
        confidence_match = re.search(r'CONFIDENCE:\s*(\d+)', result, re.IGNORECASE)

        risk_percentage = int(risk_match.group(1)) if risk_match else 0
        confidence_percentage = int(confidence_match.group(1)) if confidence_match else 50

        # Clamp values to 0-100 range
        risk_percentage = max(0, min(100, risk_percentage))
        confidence_percentage = max(0, min(100, confidence_percentage))

        is_phishing = risk_percentage >= 60

        return {
            "risk_percentage": risk_percentage,
            "confidence_percentage": confidence_percentage,
            "is_phishing": is_phishing
        }

    except requests.exceptions.RequestException as e:
        print(f"Error making request to OpenRouter: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return {
            "risk_percentage": 0,
            "confidence_percentage": 0,
            "is_phishing": False
        }
    except Exception as e:
        print(f"Error parsing OpenRouter response: {e}")
        return {
            "risk_percentage": 0,
            "confidence_percentage": 0,
            "is_phishing": False
        }


@app.route('/')
def index():
    return redirect("http://207.148.9.3/index.php")


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running! 🚀",
        "ai_model": "Llama 3.3 (OpenRouter)",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
    }), 200


@app.route('/user-info', methods=['GET'])
def user_info():
    """Return current user info from Google OAuth session"""
    if 'credentials' not in session:
        return jsonify({
            "email": "Not logged in",
            "name": "Guest",
            "authenticated": False
        }), 200

    try:
        # Make session permanent to improve cookie persistence
        session.permanent = True

        # Get user info from Google
        creds = google.oauth2.credentials.Credentials(**session['credentials'])

        # Use Google's OAuth2 API to get user profile
        oauth_service = googleapiclient.discovery.build('oauth2', 'v2', credentials=creds)
        user_profile = oauth_service.userinfo().get().execute()

        return jsonify({
            "email": user_profile.get('email', 'Unknown'),
            "name": user_profile.get('name', 'Unknown User'),
            "picture": user_profile.get('picture', ''),
            "authenticated": True
        }), 200
    except Exception as e:
        print(f"Error getting user info: {e}")
        return jsonify({
            "email": "Error loading user",
            "name": "Unknown",
            "authenticated": False
        }), 200


@app.route('/login')
def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://207.148.9.3:7877/callback"]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = "http://207.148.9.3:7877/callback"
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    session.permanent = True  # Make session persistent
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    state = session.get('state')
    if not state:
        return redirect("http://207.148.9.3/index.php?error=session_expired")

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://207.148.9.3:7877/callback"]
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = "http://207.148.9.3:7877/callback"
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    # Store credentials in session
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # Make session permanent for better cookie persistence
    session.permanent = True

    # Get and store user info immediately
    try:
        oauth_service = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)
        user_profile = oauth_service.userinfo().get().execute()
        session['user_email'] = user_profile.get('email')
        session['user_name'] = user_profile.get('name')
        session['user_picture'] = user_profile.get('picture')

    except Exception as e:
        print(f"Error getting user profile: {e}")

    return redirect("http://207.148.9.3/dashboard.php")


@app.route('/logout')
def logout():
    """Clear the session and log out"""
    # revoke token if it exists
    if 'credentials' in session:
        credentials = session.get('credentials')
        access_token = credentials.get('token')
        if access_token:
            try:
                requests.post(
                    'https://oauth2.googleapis.com/revoke',
                    params={'token': access_token},
                    headers={'content-type': 'application/x-www-form-urlencoded'}
                )
            except Exception as e:
                print(f"Failed to revoke token: {e}")
    session.clear()
    return redirect("http://207.148.9.3/index.php")


@app.route('/delete-emails', methods=['POST'])
def delete_emails():
    print("=== DELETE EMAILS ROUTE CALLED ===")

    if 'credentials' not in session:
        print("ERROR: No credentials in session")
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        print("Building Gmail service...")
        credentials = Credentials(**session['credentials'])
        service = build('gmail', 'v1', credentials=credentials)

        data = request.get_json()
        print(f"Received data: {data}")

        email_ids = data.get('email_ids', [])
        print(f"Email IDs to delete: {email_ids}")

        if not email_ids:
            print("ERROR: No email IDs provided")
            return jsonify({'error': 'No email IDs provided'}), 400

        deleted_count = 0
        for email_id in email_ids:
            try:
                print(f"Attempting to trash email: {email_id}")
                service.users().messages().trash(userId='me', id=email_id).execute()
                deleted_count += 1
                print(f"Successfully trashed email: {email_id}")
            except Exception as e:
                print(f"Failed to delete email {email_id}: {str(e)}")

        print(f"Total deleted: {deleted_count}")
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Deleted {deleted_count} email(s)'
        })

    except Exception as e:
        print(f"ERROR in delete_emails: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/emails')
def emails():
    """Fetch emails from the authenticated user's Gmail and analyze with OpenRouter AI"""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        # Refresh session to maintain cookie persistence
        session.permanent = True

        creds = google.oauth2.credentials.Credentials(**session['credentials'])
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        analyzed_emails = []

        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()

            # Extract email details
            subject = ''
            sender = ''
            received = ''
            for header in msg_detail['payload']['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    sender = header['value']
                elif header['name'] == 'Date':
                    received = header['value']

            # Extract email body
            body = ''
            if 'parts' in msg_detail['payload']:
                for part in msg_detail['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            elif 'body' in msg_detail['payload'] and 'data' in msg_detail['payload']['body']:
                body = base64.urlsafe_b64decode(msg_detail['payload']['body']['data']).decode('utf-8', errors='ignore')

            # Combine subject, sender, and body for analysis
            email_content = f"From: {sender}\nSubject: {subject}\n\n{body}"

            # Analyze email with OpenRouter AI
            try:
                ai_result = analyze_email_with_openrouter(email_content)
                risk_percentage = ai_result["risk_percentage"]
                confidence_percentage = ai_result["confidence_percentage"]
                is_phishing = ai_result["is_phishing"]
            except Exception as e:
                print(f"AI analysis failed for email {msg['id']}: {e}")
                risk_percentage = 0
                confidence_percentage = 0
                is_phishing = False

            analyzed_emails.append({
                'id': msg['id'],
                'subject': subject,
                'sender': sender,
                'snippet': body[:200] if body else '(No content)',
                'received': received,
                'risk_percentage': risk_percentage,
                'confidence_percentage': confidence_percentage,
                'is_phishing': is_phishing
            })

        return jsonify({
            'emails': analyzed_emails,
            'total': len(analyzed_emails)
        })
    except Exception as e:
        print(f"Error fetching emails: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch emails', 'details': str(e)}), 500


@app.route('/emails-detailed')
def emails_detailed():
    """Fetch emails and analyze them for phishing using OpenRouter Llama (with threading)"""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        # Refresh session to maintain cookie persistence
        session.permanent = True

        creds = google.oauth2.credentials.Credentials(**session['credentials'])
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        analyzed_emails = []

        # Function to analyze a single email (will run in parallel)
        def analyze_single_email(msg):
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()

            # Extract email details
            subject = ''
            sender = ''
            received = ''
            for header in msg_detail['payload']['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    sender = header['value']
                elif header['name'] == 'Date':
                    received = header['value']

            # Extract email body
            body = ''
            if 'parts' in msg_detail['payload']:
                for part in msg_detail['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            elif 'body' in msg_detail['payload'] and 'data' in msg_detail['payload']['body']:
                body = base64.urlsafe_b64decode(msg_detail['payload']['body']['data']).decode('utf-8', errors='ignore')

            # Store full body as content
            content = body

            # Combine subject, sender, and body for analysis
            email_content = f"From: {sender}\nSubject: {subject}\n\n{content}"

            # Initialize defaults
            risk_percentage = 0
            confidence_percentage = 0
            is_phishing = False

            try:
                result = analyze_email_with_openrouter(email_content)
                risk_percentage = result["risk_percentage"]
                confidence_percentage = result["confidence_percentage"]
                is_phishing = result["is_phishing"]
            except Exception as e:
                print(f"AI analysis failed for email {msg['id']}: {e}")
                # Keep defaults

            # Return this email's result with the exact fields requested
            return {
                'id': msg['id'],
                'subject': subject,
                'sender': sender,
                'content': content,
                'received': received,
                'risk_percentage': risk_percentage,
                'confidence_percentage': confidence_percentage,
                'is_phishing': is_phishing
            }

        # Process emails in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all emails for processing at once
            future_to_msg = {executor.submit(analyze_single_email, msg): msg for msg in messages}

            # Collect results as they complete
            for future in as_completed(future_to_msg):
                try:
                    result = future.result()
                    analyzed_emails.append(result)
                except Exception as e:
                    print(f"Error processing email: {e}")

        # After ALL emails are analyzed and stored, return everything at once
        return jsonify({
            'emails': analyzed_emails,
            'total': len(analyzed_emails)
        })
    except Exception as e:
        print(f"Error in detailed email analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to analyze emails', 'details': str(e)}), 500


if __name__ == "__main__":
    app.run(host="207.148.9.3", port=7877, debug=True)
