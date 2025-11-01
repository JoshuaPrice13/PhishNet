import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, redirect, url_for, session, request
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

pp = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Configuration
LLAMA_API_KEY = os.getenv('LLAMA_API_KEY')

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('login'))
    return '<a href="/emails">Read Gmail Emails</a>'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running! 🚀",
        "llama_configured": bool(LLAMA_API_KEY),
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

@app.route('/emails', methods=['GET'])
def get_emails():
    """
    Fetch emails from Microsoft Graph API (Outlook)
    
    In production, this would:
    1. Get access token from request
    2. Call Microsoft Graph API: GET https://graph.microsoft.com/v1.0/me/messages
    3. Parse and return email data
    """
    # Mock data for now
    return jsonify({
        "emails": [
            {
                "id": "1",
                "subject": "URGENT: Verify your account immediately!",
                "sender": "security@micrsoft-support.com",  # Note typo
                "snippet": "Your account will be suspended unless you verify within 24 hours...",
                "received": "2024-11-01T10:30:00Z",
                "risk_score": 95,
                "is_phishing": True,
                "reason": "Suspicious sender domain (misspelled 'microsoft'), urgency tactics, requests for account verification"
            },
            {
                "id": "2",
                "subject": "Weekly Team Meeting - Friday 2PM",
                "sender": "manager@yourcompany.com",
                "snippet": "Hi team, reminder about our weekly sync on Friday at 2PM...",
                "received": "2024-11-01T09:15:00Z",
                "risk_score": 5,
                "is_phishing": False,
                "reason": "Legitimate internal sender, standard meeting invitation format"
            },
            {
                "id": "3",
                "subject": "You've won a free iPhone 15!",
                "sender": "prizes@totally-legit-giveaway.biz",
                "snippet": "Congratulations! Click here to claim your prize now...",
                "received": "2024-11-01T08:45:00Z",
                "risk_score": 98,
                "is_phishing": True,
                "reason": "Too good to be true offer, suspicious domain (.biz), urgent call to action"
            },
            {
                "id": "4",
                "subject": "Your Amazon Order #123-4567890-1234567",
                "sender": "auto-confirm@amazon.com",
                "snippet": "Thank you for your order. Your package will arrive on Nov 5...",
                "received": "2024-10-31T18:20:00Z",
                "risk_score": 10,
                "is_phishing": False,
                "reason": "Legitimate Amazon domain, standard transaction format, realistic order number"
            }
        ],
        "total": 4
    })

@app.route('/analyze-email', methods=['POST'])
def analyze_email():
    """
    Analyze a single email with Gemini API
    
    In production, this would:
    1. Extract email content from request
    2. Call Gemini API with prompt
    3. Parse AI response for risk assessment
    """
    data = request.json
    email_content = data.get('content', '')
    
    # Mock analysis for now
    return jsonify({
        "risk_score": 75,
        "is_phishing": True,
        "reason": "Contains suspicious links and requests for personal information",
        "indicators": [
            "Suspicious sender domain",
            "Urgency tactics",
            "Requests for sensitive information",
            "Spelling/grammar errors"
        ]
    })

@app.route('/purge-emails', methods=['POST'])
def purge_emails():
    """
    Delete flagged emails via Microsoft Graph API
    
    In production, this would:
    1. Get email IDs from request
    2. For each ID, call: DELETE https://graph.microsoft.com/v1.0/me/messages/{id}
    3. Return success/failure status
    """
    data = request.json
    email_ids = data.get('email_ids', [])
    
    return jsonify({
        "success": True,
        "deleted_count": len(email_ids),
        "message": f"Successfully deleted {len(email_ids)} email(s)"
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
                "redirect_uris": ["http://localhost:5000/callback"]
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
                "redirect_uris": ["http://localhost:5000/callback"]
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
    if 'credentials' not in session:
        return redirect(url_for('login'))
    creds = google.oauth2.credentials.Credentials(**session['credentials'])
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    output = '<h1>Last 10 Emails:</h1><ul>'
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        subject = ''
        for header in msg_detail['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
        output += f'<li>{subject}</li>'
    output += '</ul>'
    return output

if __name__ == "__main__":
    app.run(debug=True)
