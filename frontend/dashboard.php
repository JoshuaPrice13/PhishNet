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
        <div class="grid md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-primary text-sm mb-1 font-semibold">Total Emails Analyzed</div>
                <div class="text-3xl font-bold text-primary" id="total-emails">0</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-danger text-sm mb-1 font-semibold">🚨 Phishing Detected</div>
                <div class="text-3xl font-bold text-danger" id="phishing-emails">0</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-secondary text-sm mb-1 font-semibold">✅ Safe Emails</div>
                <div class="text-3xl font-bold text-secondary" id="safe-emails">0</div>
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
		<button onclick="deletePhishingEmails()"
        	        class="bg-danger text-white px-6 py-3 rounded-lg hover:bg-danger/80 transition shadow-sm">
    		    🗑️ Delete Phishing Emails
		</button>
            </div>
        </div>

        <!-- Email List -->
        <div class="bg-white rounded-lg shadow border border-secondary/10">
            <div class="p-6 border-b border-secondary/10 bg-background">
                <h2 class="text-xl font-bold text-primary">📧 Email Analysis Results</h2>
                <p class="text-gray-600 text-sm mt-1">AI-powered phishing detection using DistilBERT</p>
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
                    const phishingCount = emails.filter(e => e.is_phishing).length;
                    if (phishingCount > 0) {
                        //alert(`⚠️ WARNING: ${phishingCount} phishing email(s) detected!`);
                    }
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

	// Delete all phishing emails
	async function deletePhishingEmails() {
	    const phishingEmails = emails.filter(e => e.is_phishing);
	    
	    if (phishingEmails.length === 0) {
	        alert('No phishing emails to delete');
	        return;
	    }
	    
	    if (!confirm(`Are you sure you want to delete ${phishingEmails.length} phishing email(s)? This cannot be undone.`)) {
	        return;
	    }
	    
	    try {
	        // Extract email IDs
	        const emailIds = phishingEmails.map(e => e.id);
	        
	        const response = await fetch(`${BACKEND_URL}/delete-emails`, {
	            method: 'POST',
	            credentials: 'include',
	            headers: {
	                'Content-Type': 'application/json'
	            },
	            body: JSON.stringify({ email_ids: emailIds })
	        });
	        
	        if (!response.ok) {
	            throw new Error('Failed to delete emails');
	        }
	        
	        const data = await response.json();
	        alert(`✅ Successfully deleted ${data.deleted_count} phishing email(s)`);
	        
	        // Reload emails to refresh the list
	        await loadEmails();
	    } catch (error) {
	        console.error('Error deleting emails:', error);
	        alert('❌ Failed to delete emails. Please try again.');
	    }
	}

        // Display emails in the UI
        function displayEmails() {
            const emailList = document.getElementById('email-list');
            
            if (emails.length === 0) {
                emailList.innerHTML = '<div class="p-6 text-center text-gray-500">No emails found in your inbox</div>';
                return;
            }

            // Display emails with color coding based on risk
            emailList.innerHTML = emails.map((email, index) => {
                // Determine background color and border based on risk
                let bgColor = 'bg-white';
                let borderColor = 'border-l-4 border-green-500';
                let riskBadge = 'bg-green-100 text-green-700';
                let riskIcon = '✅';
                
                if (email.is_phishing) {
                    bgColor = 'bg-red-50';
                    borderColor = 'border-l-4 border-red-600';
                    riskBadge = 'bg-red-100 text-red-700';
                    riskIcon = '🚨';
                } else if (email.risk_score >= 30) {
                    bgColor = 'bg-yellow-50';
                    borderColor = 'border-l-4 border-yellow-500';
                    riskBadge = 'bg-yellow-100 text-yellow-700';
                    riskIcon = '⚠️';
                }
                
                return `
                <div class="p-6 hover:bg-gray-50 transition ${bgColor} ${borderColor}">
                    <div class="flex items-start gap-4">
                        <div class="flex-shrink-0 text-3xl">
                            ${riskIcon}
                        </div>
                        <div class="flex-1">
                            <div class="flex justify-between items-start mb-2">
                                <div class="flex-1">
                                    <div class="font-bold text-lg text-gray-800 mb-1">
                                        ${escapeHtml(email.subject) || '(No Subject)'}
                                    </div>
                                    <div class="text-gray-600 text-sm mb-2">
                                        From: ${escapeHtml(email.sender)}
                                    </div>
                                    <div class="text-gray-700 text-sm mb-2">
                                        ${escapeHtml(email.snippet)}
                                    </div>
                                    <div class="text-gray-400 text-xs">
                                        ${email.received}
                                    </div>
                                </div>
                                <div class="ml-4 text-right">
                                    <span class="inline-block px-3 py-1 rounded-full text-sm font-bold ${riskBadge}">
                                        Risk: ${email.risk_score}%
                                    </span>
                                    <div class="text-xs text-gray-500 mt-1">
                                        Confidence: ${(email.confidence * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                            ${email.is_phishing ? `
                                <div class="bg-red-100 border-l-4 border-red-500 p-3 mt-3">
                                    <div class="font-bold text-red-700 mb-1">⚠️ PHISHING DETECTED</div>
                                    <div class="text-red-600 text-sm">
                                        This email has been flagged as a potential phishing attempt by our AI model.
                                    </div>
                                </div>
                            ` : email.risk_score >= 30 ? `
                                <div class="bg-yellow-100 border-l-4 border-yellow-500 p-3 mt-3">
                                    <div class="font-bold text-yellow-700 mb-1">⚠️ Moderate Risk</div>
                                    <div class="text-yellow-600 text-sm">
                                        Exercise caution with this email.
                                    </div>
                                </div>
                            ` : `
                                <div class="text-green-600 text-sm mt-2 flex items-center gap-2">
                                    <span>✅ This email appears safe</span>
                                </div>
                            `}
                        </div>
                    </div>
                </div>
            `}).join('');
        }

        // Update stats
        function updateStats() {
            const total = emails.length;
            const phishing = emails.filter(e => e.is_phishing).length;
            const safe = total - phishing;
            
            document.getElementById('total-emails').textContent = total;
            document.getElementById('phishing-emails').textContent = phishing;
            document.getElementById('safe-emails').textContent = safe;
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
