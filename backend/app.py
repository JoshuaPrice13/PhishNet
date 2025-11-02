import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from dotenv import load_dotenv
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, redirect, url_for, session, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import json
from phishing_model import analyze_email  # Import our AI model

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configure session to work across domains
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'  # Share cookies across localhost
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Enable CORS with credentials support
CORS(app, supports_credentials=True, origins=["http://localhost", "http://localhost:80"])

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

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
    """Return current user info from Google OAuth session"""
    if 'credentials' not in session:
        return jsonify({
            "email": "Not logged in",
            "name": "Guest",
            "authenticated": False
        }), 200
    
    try:
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
    
    # Store credentials in session
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Get and store user info immediately
    try:
        oauth_service = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)
        user_profile = oauth_service.userinfo().get().execute()
        session['user_email'] = user_profile.get('email')
        session['user_name'] = user_profile.get('name')
        session['user_picture'] = user_profile.get('picture')
        
        # Make session permanent (lasts 24 hours)
        session.permanent = True
    except Exception as e:
        print(f"Error getting user profile: {e}")
    
    return redirect("http://localhost/dashboard.php")

@app.route('/logout')
def logout():
    """Clear the session and log out"""
    session.clear()
    return redirect("http://localhost/index.php")

@app.route('/emails')
def emails():
    """Fetch emails from the authenticated user's Gmail and analyze with AI"""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
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
            
            # Analyze with AI model
            email_content = f"Subject: {subject}\nFrom: {sender}\n\n{body[:1000]}"
            ai_result = analyze_email(email_content)
            
            analyzed_emails.append({
                'id': msg['id'],
                'subject': subject,
                'sender': sender,
                'snippet': body[:200] if body else '(No content)',
                'received': received,
                'risk_score': ai_result['risk_score'],
                'is_phishing': ai_result['is_phishing'],
                'confidence': ai_result['confidence'],
                'ai_result': ai_result['result']
            })
        
        return jsonify({
            'emails': analyzed_emails,
            'total': len(analyzed_emails)
        })
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return jsonify({'error': 'Failed to fetch emails', 'details': str(e)}), 500


@app.route('/emails-detailed')
def emails_detailed():
    """Fetch emails and analyze them for phishing using Llama via Groq (with threading)"""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
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
            
            # Map confidence to a 0-100 scale for risk_score
            risk_score = round(result["confidence"] * 100, 2)
            
            # is_phishing boolean
            is_phishing = result["is_phishing"]
            
            try:
                result = analyze_email(content)
                risk_score = round(result["confidence"] * 100, 2)
                is_phishing = result["is_phishing"]

            except Exception as e:
                # Return error and log server side
                risk_score = 0
                is_phishing = False
                return jsonify({"error": "Model inference failed", "detail": str(e)}), 500
            
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
    except Exception as e:
        print(f"Error in detailed email analysis: {e}")
        return jsonify({'error': 'Failed to analyze emails', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7877, debug=True)