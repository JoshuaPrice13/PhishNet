#!/bin/bash

# Script to generate self-signed SSL certificates for development

mkdir -p ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=PhishNet/OU=Dev/CN=localhost"

echo "✅ Self-signed SSL certificates generated in nginx/ssl/"
echo "⚠️  WARNING: These are for DEVELOPMENT ONLY. Use real certificates in production!"
