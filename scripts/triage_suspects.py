# Auto-triage suspect labels: stack multiple evidence layers, suggest action per row.
# Input : Data/all_suspects_full.csv  (from notebook cell 8b)
# Output: Data/review_triaged.csv     (sorted by evidence strength, with suggestions)
import pandas as pd

POSITIVE = {'vui', 'hy_vong'}
NEGATIVE = {'buon', 'lo_au', 'gian_du', 'that_vong'}
NEUTRAL  = {'trung_tinh'}

# Explicit keyword evidence for each label (conservative — only unambiguous words)
LABEL_CUES = {
    'vui':        ['vui quá', 'hạnh phúc', 'tuyệt vời', 'sung sướng', 'mừng quá', 'thích quá'],
    'buon':       ['buồn', 'hối hận', 'khóc', 'cô đơn', 'đau lòng', 'tủi thân'],
    'lo_au':      ['lo lắng', 'lo âu', 'sợ hãi', 'bất an', 'hoảng', 'căng thẳng', 'stress'],
    'gian_du':    ['tức', 'giận', 'ghét', 'bực', 'phẫn nộ', 'tẩy chay', 'mất dạy', 'vô đạo đức'],
    'that_vong':  ['thất vọng', 'chán', 'nhạt', 'tệ quá', 'phí thời gian'],
    'hy_vong':    ['hy vọng', 'mong mọi chuyện', 'sẽ ổn', 'cố lên', 'tin rằng'],
    'trung_tinh': [],
}

def polarity_flip(o, p):
    return (o in POSITIVE and p in NEGATIVE) or (o in NEGATIVE and p in POSITIVE)

def neutral_mix(o, p):
    return (o in NEUTRAL) != (p in NEUTRAL)  # one neutral, one strong emotion

d = pd.read_csv('Data/all_suspects_full.csv')

d['ev_flip']    = d.apply(lambda r: polarity_flip(r['original_label'], r['predicted_label']), axis=1)
d['ev_neutral'] = d.apply(lambda r: neutral_mix(r['original_label'], r['predicted_label']), axis=1)
d['ev_lowprob'] = d['original_label_probability'] < 0.05
d['ev_keyword'] = d.apply(
    lambda r: any(k in str(r['text_raw']).lower() for k in LABEL_CUES.get(r['predicted_label'], [])), axis=1)
d['ev_dualflag'] = d['icon_flag'].notna() & d['cleanlab_suspect']

# Evidence score: flip/neutral-mix is the entry condition, others add confidence
d['evidence'] = (
    d['ev_flip'].astype(int) * 2          # polarity flip = strongest single signal
    + d['ev_neutral'].astype(int)         # neutral-vs-strong mix
    + d['ev_lowprob'].astype(int)
    + d['ev_keyword'].astype(int)
    + d['ev_dualflag'].astype(int)
)

# Suggestion: only for rows with a conflict (flip or neutral mix); higher evidence = stronger suggestion
def suggest(r):
    if not (r['ev_flip'] or r['ev_neutral']):
        return ''  # adjacent pair — likely fine, review only if bored
    if r['evidence'] >= 3:
        return f"change->{r['predicted_label']}"
    return 'review'  # conflict but weaker evidence — read before deciding

d['suggestion'] = d.apply(suggest, axis=1)
d['action'] = ''
d['new_label'] = ''
d['review_note'] = ''

d = d.sort_values(['evidence', 'label_quality_score'], ascending=[False, True])
cols = ['id', 'text_raw', 'original_label', 'predicted_label',
        'original_label_probability', 'label_quality_score',
        'evidence', 'suggestion', 'action', 'new_label', 'review_note']
d[cols].to_csv('Data/review_triaged.csv', index=False)

print('Tổng:', len(d))
print('\nPhân bố evidence score:')
print(d['evidence'].value_counts().sort_index(ascending=False).to_string())
print('\nPhân bố suggestion:')
print(d['suggestion'].replace('', '(cap thap - chong lan)').value_counts().to_string())
n_strong = (d['suggestion'].str.startswith('change')).sum()
print(f'\n=> {n_strong} dòng có đề xuất đổi nhãn sẵn (evidence >= 3) — lướt xác nhận là chính')
print('=> Xuất Data/review_triaged.csv (sắp theo evidence giảm dần)')
