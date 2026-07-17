import json

with open('/home/ai02/aiquoc/VNUF/train_classifier_colab.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        for i, line in enumerate(cell['source']):
            if "def clean_text" in line:
                cell['source'] = cell['source'][:i] + [
                    "def clean_text(text, label=None):\n",
                    "    text = str(text)\n",
                    "    if label is not None:\n",
                    "        if label in NEGATIVE_LABELS:\n",
                    "            for p in POS_PATTERNS:\n",
                    "                text = re.sub(p, '', text, flags=re.IGNORECASE)\n",
                    "        if label in POSITIVE_LABELS:\n",
                    "            for p in NEG_PATTERNS:\n",
                    "                text = re.sub(p, '', text, flags=re.IGNORECASE)\n",
                    "    return re.sub(r'\\s+', ' ', text).strip()\n"
                ] + cell['source'][i+9:]
                break

with open('/home/ai02/aiquoc/VNUF/train_classifier_colab.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print("Patched!")
