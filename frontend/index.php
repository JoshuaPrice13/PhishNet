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

<body class="bg-primary text-background min-h-screen flex flex-col justify-center">
  <div class="container mx-auto px-6 py-12 text-center">

    <!-- Logo / Header -->
    <div class="mb-16">
      <h1 class="text-6xl font-extrabold text-accent tracking-wide mb-4 drop-shadow-lg">
        PhishNet
      </h1>
      <p class="text-2xl text-secondary font-semibold mb-2">
        AI-Powered Email Security
      </p>
      <p class="text-lg text-background/80 max-w-2xl mx-auto">
        Protect your inbox with deep learning–based phishing detection and real-time defense.
      </p>
    </div>

    <!-- Features -->
    <div class="grid md:grid-cols-3 gap-8 mb-16">
      <div class="bg-background/10 p-6 rounded-xl border border-background/20 backdrop-blur-sm hover:bg-background/20 transition">
        <div class="text-4xl mb-3">🤖</div>
        <h3 class="font-bold text-lg mb-2 text-accent">AI Analysis</h3>
        <p class="text-background/80 text-sm">Uses large language models to detect subtle phishing attempts.</p>
      </div>

      <div class="bg-background/10 p-6 rounded-xl border border-background/20 backdrop-blur-sm hover:bg-background/20 transition">
        <div class="text-4xl mb-3">📧</div>
        <h3 class="font-bold text-lg mb-2 text-accent">Outlook Integration</h3>
        <p class="text-background/80 text-sm">Seamlessly connects with Microsoft Outlook and other email providers.</p>
      </div>

      <div class="bg-background/10 p-6 rounded-xl border border-background/20 backdrop-blur-sm hover:bg-background/20 transition">
        <div class="text-4xl mb-3">⚡</div>
        <h3 class="font-bold text-lg mb-2 text-accent">Real-Time Defense</h3>
        <p class="text-background/80 text-sm">Flags malicious links and attachments before they hit your inbox.</p>
      </div>
    </div>

    <!-- Call to Action -->
    <div class="bg-background/10 p-10 rounded-xl shadow-lg max-w-lg mx-auto border border-background/20">
      <h2 class="text-3xl font-bold text-accent mb-4">Get Started</h2>
      <p class="text-background/80 mb-6">
        Connect your Outlook account and let PhishNet’s AI guard your inbox.
      </p>
      <a href="/login"
         class="bg-accent text-primary px-8 py-4 rounded-lg font-semibold text-lg shadow-md hover:bg-accent/80 transition">
        Login
      </a>
    </div>

  </div>
</body>
</html>

