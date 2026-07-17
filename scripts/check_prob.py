import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

MODEL_DIR = "/home/ai02/aiquoc/VNUF/emotion_model_results"

label_list = ['vui', 'buon', 'lo_au', 'gian_du', 'trung_tinh', 'hy_vong', 'that_vong']
id2label = {i: l for i, l in enumerate(label_list)}

def main():
    # find the latest checkpoint
    checkpoints = [d for d in os.listdir(MODEL_DIR) if d.startswith('checkpoint')]
    if checkpoints:
        latest = max(checkpoints, key=lambda x: int(x.split('-')[1]))
        model_path = os.path.join(MODEL_DIR, latest)
    else:
        model_path = MODEL_DIR

    tokenizer = AutoTokenizer.from_pretrained('uitnlp/visobert')
    try:
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
    except Exception as e:
        print("Error loading:", e)
        return

    model.eval()

    sentences = [
        'Thất vọng quá, mong đợi nhiều mà được cái này huhu',
        'Thất vọng quá, mong đợi nhiều mà được cái này',
        'Thất vọng quá, được cái này huhu',
    ]

    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors='pt', truncation=True, max_length=128)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = F.softmax(logits, dim=1).squeeze().tolist()

        print(f"Probabilities for: '{sentence}'")
        for i, p in enumerate(probs):
            if p > 0.1:
                print(f"  {id2label[i]}: {p:.4f}")
        print("-" * 30)

if __name__ == "__main__":
    main()
