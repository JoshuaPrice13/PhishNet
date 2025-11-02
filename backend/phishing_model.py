# phishing_model.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Model name on Hugging Face
MODEL_NAME = "cybersectony/phishing-email-detection-distilbert_v2.4.1"

# Load once on import
print("Loading phishing detection model... (this may take a minute)")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()  # set to eval mode

labels = ["legitimate", "phishing"]
print("Model loaded and ready!")

def analyze_email(content: str):
    """
    Returns a dict: { result, confidence, is_phishing, risk_score }
    """
    if not isinstance(content, str):
        content = str(content or "")
    
    # Tokenize and get prediction
    inputs = tokenizer(content, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        logits = model(**inputs).logits
        prediction = int(torch.argmax(logits, dim=1).item())
        confidence = float(torch.softmax(logits, dim=1)[0][prediction].item())
    
    # Calculate risk score (0-100)
    if labels[prediction] == "phishing":
        risk_score = int(confidence * 100)
    else:
        risk_score = int((1 - confidence) * 100)
    
    return {
        "result": labels[prediction],
        "confidence": round(confidence, 4),
        "is_phishing": labels[prediction] == "phishing",
        "risk_score": risk_score
    }