<?php
session_start();

// Check if user is logged in (in real app, validate Auth0 session)
//if (!isset($_SESSION['user_id'])) {
    //header('Location: /login.php');  // fix this once the login redirect works
    //exit;
//}

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
                <span class="text-background font-medium">
                    <?php echo htmlspecialchars($_SESSION['user_email']); ?>
                </span>
                <a href="/logout.php" class="text-accent hover:text-danger transition">Logout</a>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-8">
        <!-- Backend Status -->
        <div class="bg-secondary/10 border-l-4 border-secondary p-4 mb-6 rounded">
            <div class="flex items-center">
                <div class="flex-1">
                    <p class="text-primary">
                        <strong>Backend Status:</strong> <span id="backend-status">Checking...</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- Stats -->
        <div class="grid md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-primary text-sm mb-1 font-semibold">Total Emails</div>
                <div class="text-3xl font-bold text-primary" id="total-emails">0</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-primary text-sm mb-1 font-semibold">Flagged as Phishing</div>
                <div class="text-3xl font-bold text-danger" id="phishing-count">0</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6 border border-secondary/10">
                <div class="text-primary text-sm mb-1 font-semibold">Safe Emails</div>
                <div class="text-3xl font-bold text-secondary" id="safe-count">0</div>
            </div>
        </div>

        <!-- Actions -->
        <div class="bg-white rounded-lg shadow p-6 mb-8 border border-secondary/10">
            <h2 class="text-xl font-bold text-primary mb-4">Actions</h2>
            <div class="flex flex-wrap gap-4">
                <button onclick="loadEmails()"
                        class="bg-secondary text-white px-6 py-3 rounded-lg hover:bg-secondary/80 transition shadow-sm">
                    🔄 Scan Outlook Inbox
                </button>
                <button onclick="purgePhishing()"
                        class="bg-danger text-white px-6 py-3 rounded-lg hover:bg-danger/80 transition shadow-sm">
                    🗑 Purge Flagged Emails
                </button>
            </div>
        </div>

        <!-- Email List -->
        <div class="bg-white rounded-lg shadow border border-secondary/10">
            <div class="p-6 border-b border-secondary/10 bg-background">
                <h2 class="text-xl font-bold text-primary">📧 Email Analysis</h2>
            </div>
            <div id="email-list" class="divide-y divide-secondary/10">
                <div class="p-6 text-center text-gray-500">
                    Click “Scan Outlook Inbox” to analyze your emails
                </div>
            </div>
        </div>
    </div>

    <script>
        let emails = [];

        // Check backend health on load
        async function checkBackend() {
            try {
                const response = await fetch('http://localhost:7877/health');
                const data = await response.json();
                document.getElementById('backend-status').innerHTML = 
                    `<span class="text-green-600 font-bold">✅ ${data.message}</span>`;
            } catch (error) {
                document.getElementById('backend-status').innerHTML = 
                    `<span class="text-red-600 font-bold">❌ Backend not reachable</span>`;
            }
        }

        async function loadEmails() {
            try {
                const response = await fetch('http://localhost:7877/emails');
                const data = await response.json();
                emails = data.emails;
                displayEmails();
                updateStats();
            } catch (error) {
                console.error('Error loading emails:', error);
                alert('Failed to load emails. Check backend connection.');
            }
        }

        function displayEmails() {
            const emailList = document.getElementById('email-list');
            
            if (emails.length === 0) {
                emailList.innerHTML = '<div class="p-6 text-center text-gray-500">No emails found</div>';
                return;
            }

            emailList.innerHTML = emails.map(email => `
                <div class="p-6 hover:bg-gray-50 ${email.is_phishing ? 'bg-red-50' : ''}">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex-1">
                            <div class="font-bold text-lg mb-1">${email.subject}</div>
                            <div class="text-gray-600 text-sm mb-2">From: ${email.sender}</div>
                            <div class="text-gray-700 mb-2">${email.snippet}</div>
                            <div class="text-gray-400 text-xs">Received: ${new Date(email.received).toLocaleString()}</div>
                        </div>
                        <div class="ml-4">
                            <div class="text-right mb-2">
                                <span class="inline-block px-3 py-1 rounded-full text-sm font-bold ${
                                    email.risk_score >= 70 ? 'bg-red-100 text-red-700' :
                                    email.risk_score >= 40 ? 'bg-yellow-100 text-yellow-700' :
                                    'bg-green-100 text-green-700'
                                }">
                                    Risk: ${email.risk_score}%
                                </span>
                            </div>
                        </div>
                    </div>
                    ${email.is_phishing ? `
                        <div class="bg-red-100 border-l-4 border-red-500 p-3 mt-3">
                            <div class="font-bold text-red-700 mb-1">⚠️ Phishing Detected</div>
                            <div class="text-red-600 text-sm">${email.reason}</div>
                        </div>
                    ` : `
                        <div class="text-green-600 text-sm mt-2">✅ ${email.reason}</div>
                    `}
                </div>
            `).join('');
        }

        function updateStats() {
            const total = emails.length;
            const phishing = emails.filter(e => e.is_phishing).length;
            const safe = total - phishing;

            document.getElementById('total-emails').textContent = total;
            document.getElementById('phishing-count').textContent = phishing;
            document.getElementById('safe-count').textContent = safe;
        }

        async function purgePhishing() {
            const phishingEmails = emails.filter(e => e.is_phishing);
            
            if (phishingEmails.length === 0) {
                alert('No phishing emails to delete');
                return;
            }

            if (!confirm(`Delete ${phishingEmails.length} flagged email(s)?`)) {
                return;
            }

            try {
                const response = await fetch('http://localhost:7877/purge-emails', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email_ids: phishingEmails.map(e => e.id)
                    })
                });

                const data = await response.json();
                alert(data.message);
                
                // Remove deleted emails from display
                emails = emails.filter(e => !e.is_phishing);
                displayEmails();
                updateStats();
            } catch (error) {
                console.error('Error purging emails:', error);
                alert('Failed to delete emails');
            }
        }

        // Check backend on load
        window.addEventListener('load', () => {
            checkBackend();
            loadEmails();
        });
    </script>
</body>
</html>
