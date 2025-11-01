from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OUTLOOK_CLIENT_ID = os.getenv('OUTLOOK_CLIENT_ID')
OUTLOOK_CLIENT_SECRET = os.getenv('OUTLOOK_CLIENT_SECRET')
OUTLOOK_TENANT_ID = os.getenv('OUTLOOK_TENANT_ID', 'common')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running! 🚀",
        "auth0_configured": bool(AUTH0_DOMAIN),
        "gemini_configured": bool(GEMINI_API_KEY),
        "outlook_configured": bool(OUTLOOK_CLIENT_ID)
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

@app.route('/outlook-auth', methods=['GET'])
def outlook_auth():
    """
    Initiate OAuth flow for Microsoft Outlook
    
    Returns the authorization URL to redirect user to
    """
    # Microsoft identity platform authorization endpoint
    auth_url = f"https://login.microsoftonline.com/{OUTLOOK_TENANT_ID}/oauth2/v2.0/authorize"
    
    params = {
        "client_id": OUTLOOK_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost/callback",
        "scope": "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.ReadWrite offline_access",
        "response_mode": "query"
    }
    
    # Build URL with parameters
    import urllib.parse
    auth_url_with_params = auth_url + "?" + urllib.parse.urlencode(params)
    
    return jsonify({
        "auth_url": auth_url_with_params
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
