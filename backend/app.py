import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, redirect, url_for, session, request
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
