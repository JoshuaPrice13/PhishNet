import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, redirect, url_for, session, request
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@app.route('/')
def index():
    return redirect("http://localhost/index.php")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running! 🚀",
        "llama_configured": bool(os.getenv('GROQ_API_KEY')),
    }), 200

@app.route('/user-info', methods=['GET'])
def user_info():
    """Return current user info from session"""
    # In a real app, this would validate Auth0 token
    return jsonify({
        "email": "user@example.com",
        "name": "Test User",
        "authenticated": True
    })


@app.route('/login')
def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:7877/callback"]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:7877/callback"]
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(url_for('index'))

@app.route('/emails')
def emails():
    """Fetch emails and analyze them for phishing using Llama via Groq (with threading)"""
    if 'credentials' not in session:
        return redirect(url_for('login'))
    
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
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg_detail['payload'] and 'data' in msg_detail['payload']['body']:
            body = base64.urlsafe_b64decode(msg_detail['payload']['body']['data']).decode('utf-8')
        
        # Store full body as content
        content = body
        
        # Limit body for AI analysis (to save costs)
        body_for_ai = body[:1000]
        
        # Send to Llama AI and wait for response
        try:
            prompt = f"""Analyze this email for phishing likelihood. Respond with ONLY a number between 0-100 (the percentage likelihood it's phishing).

Subject: {subject}
From: {sender}
Body: {body_for_ai}

Respond with just the number (e.g., 85 or 15)."""

            llama_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a cybersecurity expert. Respond only with a number 0-100."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 10
                }
            )
            
            if llama_response.status_code == 200:
                result_text = llama_response.json()['choices'][0]['message']['content'].strip()
                # Extract number from AI response
                risk_score = int(''.join(filter(str.isdigit, result_text)))
                
                # Calculate boolean
                is_phishing = risk_score >= 50
            else:
                risk_score = 0
                is_phishing = False
                
        except Exception as e:
            risk_score = 0
            is_phishing = False
            print(f"Error analyzing email: {e}")
        
        # Return this email's result with the exact fields requested
        return {
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'content': content,
            'received': received,
            'risk_score': risk_score,
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7877, debug=True)
