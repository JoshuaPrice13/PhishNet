# PhishNet
Okstate Hackathon 2025

PhishNet helps businesses stay safe from phishing by automatically scanning emails, flagging threats, and allowing one-click deletion. Built with a PHP/HTML/Tailwind frontend and Python Flask backend, all processing happens securely on our server without storing user data. Future updates will expand provider support and add AI explanations for flagged emails.

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
    ├── OpenRouter.py
    ├── phishing_model.py
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
Backend (Python/Flask) - http://localhost:7877

Auth0 (External) - Authentication
Google API (External) - Gmail email access
AI API (External) - AI trained on phishing
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
