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
print("Model loaded.")

def analyze_email(content: str):
    """
    Returns a dict: { result, confidence, is_phishing }
    """
    if not isinstance(content, str):
        content = str(content or "")

    inputs = tokenizer(content, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        prediction = int(torch.argmax(logits, dim=1).item())
        confidence = float(torch.softmax(logits, dim=1)[0][prediction].item())

    return {
        "result": labels[prediction],
        "confidence": round(confidence, 4),
        "is_phishing": labels[prediction] == "phishing"
    }
