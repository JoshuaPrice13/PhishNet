<?php
session_start();
$BACKEND_URL = getenv('BACKEND_URL') ?: 'http://localhost:7877';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - PhishNet</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              primary: '#004D61',
              secondary: '#00A6A6',
              accent: '#FFD166',
              danger: '#EF476F',
              background: '#F8F9FA'
            }
          }
        }
      }
    </script>
</head>
<body class="bg-background min-h-screen font-sans text-gray-800">
    <!-- Navigation -->
    <nav class="bg-primary shadow-md">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold text-accent">PhishNet</h1>
            <div class="flex items-center gap-4">
                <div class="flex items-center gap-3">
                    <img id="user-picture" src="" alt="" class="w-10 h-10 rounded-full border-2 border-accent hidden">
                    <div>
                        <div class="text-background font-semibold" id="user-name">Loading...</div>
                        <div class="text-background/70 text-sm" id="user-email">Checking authentication...</div>
                    </div>
                </div>
                <a href="<?php echo $BACKEND_URL; ?>/logout" class="text-accent hover:text-danger transition font-medium">Logout</a>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-8">
        <!-- Welcome Banner -->
        <div class="bg-gradient-to-r from-primary to-secondary p-6 rounded-xl shadow-lg mb-6 text-white">
            <div class="flex items-center gap-4">
                <img id="welcome-picture" src="" alt="" class="w-16 h-16 rounded-full border-4 border-accent hidden">
                <div class="flex-1">
                    <h2 class="text-2xl font-bold mb-1">Welcome, <span id="welcome-name">User</span>! 👋</h2>
                    <p class="text-white/90">📧 <span id="welcome-email">user@example.com</span></p>
                </div>
                <div class="text-right">
                    <div id="backend-status" class="text-sm">Checking...</div>
                </div>
            </div>
        </div>

        <!-- Stats -->
        <div class="grid md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-primary text-sm mb-1 font-semibold">Total Emails Fetched</div>
                <div class="text-3xl font-bold text-primary" id="total-emails">0</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-primary text-sm mb-1 font-semibold">Gmail Connection</div>
                <div class="text-xl font-bold" id="connection-status">
                    <span class="text-gray-400">⏳ Checking...</span>
                </div>
            </div>
        </div>

        <!-- Actions -->
        <div class="bg-white rounded-lg shadow p-6 mb-8 border border-secondary/10">
            <h2 class="text-xl font-bold text-primary mb-4">Actions</h2>
            <div class="flex flex-wrap gap-4">
                <button onclick="loadEmails()"
                        class="bg-secondary text-white px-6 py-3 rounded-lg hover:bg-secondary/80 transition shadow-sm">
                    🔄 Refresh Inbox
                </button>
            </div>
        </div>

        <!-- Email List -->
        <div class="bg-white rounded-lg shadow border border-secondary/10">
            <div class="p-6 border-b border-secondary/10 bg-background">
                <h2 class="text-xl font-bold text-primary">📧 Gmail Inbox</h2>
            </div>
            <div id="email-list" class="divide-y divide-secondary/10">
                <div class="p-6 text-center text-gray-500">
                    ⏳ Loading your emails...
                </div>
            </div>
        </div>
    </div>

    <script>
        const BACKEND_URL = '<?php echo $BACKEND_URL; ?>';
        let emails = [];

        // Check backend health
        async function checkBackend() {
            try {
                const response = await fetch(`${BACKEND_URL}/health`, {
                    credentials: 'include'  // Send cookies with request
                });
                const data = await response.json();
                
                let statusHtml = `<span class="text-white/90">✅ ${data.message}</span>`;
                if (data.llama_configured) {
                    statusHtml += ` <span class="text-accent">| 🤖 AI Ready</span>`;
                }
                
                document.getElementById('backend-status').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('backend-status').innerHTML = 
                    `<span class="text-danger">❌ Offline</span>`;
                console.error('Backend check failed:', error);
            }
        }

        // Check user info and display it
        async function checkUserInfo() {
            try {
                const response = await fetch(`${BACKEND_URL}/user-info`, {
                    credentials: 'include'  // Send cookies with request
                });
                const data = await response.json();
                
                // Update navigation
                document.getElementById('user-email').textContent = data.email;
                document.getElementById('user-name').textContent = data.name;
                
                // Update welcome banner
                document.getElementById('welcome-name').textContent = data.name;
                document.getElementById('welcome-email').textContent = data.email;
                
                // Show profile pictures if available
                if (data.picture) {
                    const navPic = document.getElementById('user-picture');
                    const welcomePic = document.getElementById('welcome-picture');
                    navPic.src = data.picture;
                    welcomePic.src = data.picture;
                    navPic.classList.remove('hidden');
                    welcomePic.classList.remove('hidden');
                }
                
                if (data.authenticated) {
                    document.getElementById('connection-status').innerHTML = 
                        `<span class="text-green-600">✅ Connected</span>`;
                } else {
                    document.getElementById('connection-status').innerHTML = 
                        `<span class="text-red-600">❌ Not Connected</span>`;
                }
                
                return data.authenticated;
            } catch (error) {
                console.error('Error checking user info:', error);
                document.getElementById('user-email').textContent = 'Error loading user';
                document.getElementById('user-name').textContent = 'Error';
                return false;
            }
        }

        // Load emails from Gmail
        async function loadEmails() {
            // Show loading state
            document.getElementById('email-list').innerHTML = 
                '<div class="p-6 text-center text-gray-500">⏳ Loading emails from Gmail...</div>';
            
            try {
                const response = await fetch(`${BACKEND_URL}/emails`, {
                    credentials: 'include'  // Send cookies with request
                });
                
                // Check if we need to login
                if (!response.ok) {
                    throw new Error('Not authenticated or failed to fetch emails');
                }
                
                const data = await response.json();
                
                // Handle the email array
                if (data.emails && Array.isArray(data.emails)) {
                    emails = data.emails;
                    displayEmails();
                    updateStats();
                    
                    // Update connection status on success
                    document.getElementById('connection-status').innerHTML = 
                        `<span class="text-green-600">✅ Connected</span>`;
                } else {
                    throw new Error('Invalid response format');
                }
            } catch (error) {
                console.error('Error loading emails:', error);
                document.getElementById('email-list').innerHTML = `
                    <div class="p-6 text-center">
                        <div class="text-red-500 mb-4">❌ Failed to load emails</div>
                        <p class="text-gray-600 mb-4">You may need to authenticate with Gmail first.</p>
                        <a href="${BACKEND_URL}/login" 
                           class="inline-block bg-secondary text-white px-6 py-3 rounded-lg hover:bg-secondary/80 transition">
                            Login with Gmail
                        </a>
                    </div>
                `;
                document.getElementById('connection-status').innerHTML = 
                    `<span class="text-red-600">❌ Not Connected</span>`;
            }
        }

        // Display emails in the UI
        function displayEmails() {
            const emailList = document.getElementById('email-list');
            
            if (emails.length === 0) {
                emailList.innerHTML = '<div class="p-6 text-center text-gray-500">No emails found in your inbox</div>';
                return;
            }

            // Display emails as a list
            emailList.innerHTML = emails.map((subject, index) => `
                <div class="p-6 hover:bg-gray-50 transition">
                    <div class="flex items-start gap-4">
                        <div class="flex-shrink-0 w-10 h-10 bg-secondary/20 rounded-full flex items-center justify-center text-secondary font-bold">
                            ${index + 1}
                        </div>
                        <div class="flex-1">
                            <div class="font-semibold text-lg text-gray-800 mb-1">
                                ${escapeHtml(subject) || '(No Subject)'}
                            </div>
                            <div class="text-gray-500 text-sm">
                                📧 Email from your Gmail inbox
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        // Update stats
        function updateStats() {
            const total = emails.length;
            document.getElementById('total-emails').textContent = total;
        }

        // Escape HTML to prevent XSS
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Initialize on page load
        window.addEventListener('load', async () => {
            // Check backend health first
            await checkBackend();
            
            // Load and display user info
            const authenticated = await checkUserInfo();
            
            // If authenticated, automatically load emails
            if (authenticated) {
                await loadEmails();
            } else {
                // Show login prompt
                document.getElementById('email-list').innerHTML = `
                    <div class="p-6 text-center">
                        <div class="text-gray-500 mb-4">You need to authenticate with Gmail first.</div>
                        <a href="${BACKEND_URL}/login" 
                           class="inline-block bg-secondary text-white px-6 py-3 rounded-lg hover:bg-secondary/80 transition">
                            Login with Gmail
                        </a>
                    </div>
                `;
            }
        });
    </script>
</body>
</html>