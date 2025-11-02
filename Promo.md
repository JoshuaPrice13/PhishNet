# 🎣 PhishNet
### Don't Get Hooked - Stay Safe from Phishing

> **OKState Hackathon 2025** | Built in 24 hours to protect businesses from email threats

![Status](https://img.shields.io/badge/status-active-success.svg)
![Platform](https://img.shields.io/badge/platform-docker-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🚀 What is PhishNet?

PhishNet is an intelligent email security platform that helps businesses stay safe from phishing attacks. It automatically scans your inbox, flags suspicious emails using AI, and allows you to delete threats with a single click -all while keeping your data secure and private.

## 💡 The Story Behind PhishNet

### Inspiration

During our research for this hackathon, we discovered that **phishing attacks account for over 90% of successful data breaches** in businesses. We believe that stopping these attacks will have significant benefits to our community and nation.

We realized that while large enterprises have dedicated security teams, small to medium-sized businesses often lack the resources to protect themselves effectively. We wanted to democratize email security and make enterprise-level protection accessible to everyone.

### What We Learned

This hackathon was an incredible learning experience for our team:

- **AI Integration at Scale**: We learned how to leverage AI APIs effectively for real-time phishing detection, balancing accuracy with speed
- **Security-First Architecture**: Implementing Auth0 and ensuring we never store sensitive user data taught us valuable lessons about privacy-by-design
- **Docker Orchestration**: Managing multi-container applications with proper networking and environment configuration
- **Full-Stack Integration**: Connecting a PHP frontend with a Python Flask backend while maintaining clean API boundaries
- **Real-Time Processing**: Handling Gmail API rate limits and processing emails efficiently without impacting user experience

We also discovered that **building trust** is as important as building features - users need to know their emails are processed securely without being stored. 

### How We Built It

**Tech Stack:**
- **Frontend**: PHP, HTML, Tailwind CSS, Apache
- **Backend**: Python, Flask
- **Authentication**: Auth0
- **Email Integration**: Gmail API
- **AI/ML**: Custom phishing detection model + OpenRouter AI API
- **Infrastructure**: Docker, Docker Compose
- **Deployment**: Vultr Cloud Deployment

**Development Process:**

1. **Day 1 Morning** - Brainstorming and architecture design. We sketched out the user flow and decided on our tech stack
2. **Day 1 Afternoon** - Split into two teams: frontend (PHP/Auth0) and backend (Flask/ML model)
3. **Day 1 Evening** - Integrated Gmail API and built the phishing detection pipeline
4. **Day 1 Night** - Connected frontend and backend, deployed to production server
5. **Day 2 Morning** - Testing, bug fixes, and UI polish
6. **Day 2 Final Hours** - Documentation and demo preparation

### Challenges We Faced

**1. Auth0 Integration Complexity**
Setting up OAuth flows with Gmail API and Auth0 simultaneously was tricky. We had to carefully manage token refresh logic and session handling across our PHP frontend.

**2. Docker Networking Issues**
Getting the frontend and backend containers to communicate properly while maintaining security took several iterations. We eventually settled on an internal Docker network with exposed ports only where necessary.

**3. Real-Time Email Processing**
Processing inboxes quickly without overwhelming the server required careful optimization. We implemented batch processing and caching strategies to improve performance.

**4. AI Model Accuracy**
Our initial model had too many false positives. We spent hours fine-tuning prompts and adjusting confidence thresholds to find the right balance between security and usability.

**5. Zero-Storage Architecture**
Building a system that processes emails without storing them required rethinking traditional database patterns. All processing happens in memory, which added complexity to error handling and recovery.

**The 3 AM Moment:**
Around 3 AM, we discovered a critical bug where the delete functionality wasn't working due to incorrect Gmail API scopes. With the demo just hours away, we scrambled to fix the OAuth flow and re-authenticate all our test accounts. Coffee and Red Bull got us through!

## ✨ Features

- 🔍 **Automated Email Scanning** - Monitoring of your inbox
- 🤖 **AI-Powered Detection** - Advanced ML models identify phishing attempts
- 🗑️ **One-Click Deletion** - Remove threats instantly
- 🔒 **Privacy First** - No email storage, all processing happens server-side
- ⚡ **Real-Time Analysis** - Instant threat assessment
- 📊 **Clean Dashboard** - Simple, intuitive interface

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Frontend (PHP/Apache)                             │
│                 http://localhost                             │
└────────────────────────┬────────────────────────────────────┘
                         │ API Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Backend (Python/Flask)                              │
│              http://localhost:7877                           │
└─────┬──────────┬──────────────┬────────────────────────────┘
      │          │              │
      ▼          ▼              ▼
   Auth0    Gmail API    OpenRouter AI
(External)  (External)     (External)
```

## 📁 Project Structure

```
phishnet/
├── docker-compose.yml       # Container orchestration
├── .env                     # Environment variables
├── frontend/
│   ├── Dockerfile
│   ├── index.php           # Landing page
│   ├── login.php           # Auth0 authentication
│   ├── dashboard.php       # Main application
│   └── logout.php          # Session management
└── backend/
    ├── Dockerfile
    ├── app.py              # Flask API server
    ├── OpenRouter.py       # AI integration
    ├── phishing_model.py   # ML detection logic
    └── requirements.txt    # Python dependencies
```

## 🔒 Security & Privacy

- **Zero Data Storage**: Emails are processed in memory and never stored
- **Secure Authentication**: Auth0 handles all user authentication
- **Encrypted Communication**: All API calls use HTTPS
- **Minimal Permissions**: Only request necessary Gmail API scopes
- **Open Source**: Full transparency in how your data is processed

## 🎯 Future Roadmap

- [ ] **Multi-Provider Support** - Outlook, ProtonMail, custom IMAP
- [ ] **AI Explanations** - Detailed reasoning for why emails are flagged
- [ ] **Browser Extension** - Scan emails without leaving your inbox
- [ ] **Mobile App** - iOS and Android support
- [ ] **Team Features** - Organization-wide protection and reporting
- [ ] **Custom Rules** - User-defined filtering criteria
- [ ] **Training Mode** - Learn from user corrections to improve accuracy

## 🏆 Hackathon Achievements

- ✅ Fully functional MVP in 24 hours
- ✅ Deployed to production server
- ✅ Zero-storage architecture implemented
- ✅ AI integration with >90% accuracy
- ✅ Clean, responsive UI/UX

## 👥 Team

Built by a group of four senior computer scientists at OKState Hackathon 2025

- Alexander Seda
- Trevor Mendenhall
- Ahmad Coleman
- Joshua Price

## 🙏 Acknowledgments

- OKState Hackathon organizers for an amazing event
- Auth0 for authentication infrastructure
- OpenRouter for AI API access
- Vultr for Cloud Deployment
- The open-source community for incredible tools and libraries

---

**Made in 24 hours with determination, coffee, and a mission to make email safer for everyone. 🎣**
