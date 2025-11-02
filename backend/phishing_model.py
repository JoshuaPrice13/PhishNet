
# phishing_model.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json
from pathlib import Path

# Model name on Huging Face
MODEL_NAME = "cybersectony/phishing-email-detection-distilbert_v2.4.1"

# Load once on import
print("Loading phishing detection model... (this may take a minute)")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()  # set to eval mode

labels = ["legitimate_email", "phishing_email", "legitimate_url", "phishing_url_alt"]

def analyze_email(email_text):
    inputs = tokenizer(email_text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0].tolist()
    
    # Model labels: ["legitimate_email", "phishing_email", "legitimate_url", "phishing_url"]
    phishing_prob = probs[1] + probs[3]  # sum phishing email + phishing URL
    is_phishing = phishing_prob > 0.5      # threshold you can tune
    risk_score = int(phishing_prob * 100)
    
    # Pick the highest probability for result display
    max_idx = probs.index(max(probs))
    result_label = ["legitimate_email", "phishing_email", "legitimate_url", "phishing_url"][max_idx]
    
    return {
        "result": result_label,
        "confidence": round(max(probs), 4),
        "is_phishing": is_phishing,
        "risk_score": risk_score
    }
