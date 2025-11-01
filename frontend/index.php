<?php
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhishNet - AI Email Security</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-primary min-h-screen">
    <div class="container mx-auto px-4 py-16">
        <div class="max-w-4xl mx-auto text-center">
            <!-- Header -->
            <div class="mb-12">
                <h1 class="text-6xl font-bold text-primary-600 mb-4">
                    PhishNet
                </h1>
                <p class="text-2xl text-gray-700 mb-2">
                    AI-Powered Email Security Platform
                </p>
                <p class="text-lg text-gray-600">
                    Protect your Outlook inbox with intelligent phishing detection
                </p>
            </div>

            <!-- Features -->
            <div class="grid md:grid-cols-3 gap-6 mb-12">
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    <div class="text-4xl mb-3">🤖</div>
                    <h3 class="font-bold text-lg mb-2">AI Analysis</h3>
                    <p class="text-gray-600 text-sm">Powered by Meta Llama to detect phishing attempts</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    <div class="text-4xl mb-3">📧</div>
                    <h3 class="font-bold text-lg mb-2">Outlook Integration</h3>
                    <p class="text-gray-600 text-sm">Seamlessly connects with Microsoft Outlook</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    <div class="text-4xl mb-3">⚡</div>
                    <h3 class="font-bold text-lg mb-2">Real-time Protection</h3>
                    <p class="text-gray-600 text-sm">Instant threat detection and alerts</p>
                </div>
            </div>

            <!-- CTA Button -->
            <div class="bg-white p-8 rounded-lg shadow-xl max-w-md mx-auto">
                <h2 class="text-2xl font-bold mb-4">Get Started</h2>
                <p class="text-gray-600 mb-6">
                    Connect your Outlook account and let AI protect you from phishing attacks
                </p>
                <a href="/login.php" 
                   class="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 inline-block font-semibold text-lg transition">
		    Login
                </a>
            </div>
        </div>
    </div>
</body>
</html>
