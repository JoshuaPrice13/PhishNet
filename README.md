# PhishNet
Okstate Hackathon 2025

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

## Server Information

**Production Server: PhishNet-Vultr**

- **IP Address:** 207.148.9.3
- **Location:** Chicago
- **OS:** Debian 11 x64 (bullseye)
- **Resources:**
  - 4 vCPUs
  - 16 GB RAM
  - 80 GB NVMe Storage
- **Username:** root
- **Created:** 7 hours ago

## PhishNet Docker Setup

### Architecture
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

### Useful Commands

Start containers
``` bash
docker-compose up -d
```

Stop containers
``` bash
docker-compose down
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