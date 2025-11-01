# PhishNet
Okstate Hackathon 2025



# PhishNet Docker Setup (Simplified - HTTP Only)

## Architecture

```
Browser
  ↓ HTTP
Frontend (PHP/Apache) - http://localhost
  ↓ API Calls
Backend (Python/Flask) - http://localhost:5000

Auth0 (External) - Authentication
Microsoft Graph API (External) - Outlook email access
Gemini API (External) - AI phishing detection
```

## Project Structure

```
phishnet/
├── docker-compose.yml
├── .env
├── frontend/
│   ├── Dockerfile
│   ├── index.php
│   ├── login.php
│   ├── dashboard.php
│   └── logout.php
└── backend/
    ├── Dockerfile
    ├── app.py
    └── requirements.txt
```

## Useful Commands

Stop everything
``` bash
docker-compose down
```

Start again (faster)
``` bash
docker-compose up
```

View logs
``` bash
docker-compose logs -f
```

Restart backend only
``` bash
docker-compose restart backend
```

See running containers
``` bash
docker-compose ps
```




