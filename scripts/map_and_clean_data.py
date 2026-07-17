import pandas as pd
import re

def clean_and_normalize(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def normalize_abbreviations(text):
    if not isinstance(text, str):
        return ""
    # Word-boundary replacements to avoid partial matches
    replacements = {
        r'\bko\b': 'không',
        r'\bkh\b': 'không',
        r'\bk\b': 'không',
        r'\bkhg\b': 'không',
        r'\bđc\b': 'được',
        r'\bdc\b': 'được',
        r'\bac\b': 'anh chị',
        r'\bbt\b': 'biết',
        r'\bng\b': 'người',
        r'\br\b': 'rồi',
        r'\brùi\b': 'rồi',
        r'\bmn\b': 'mọi người'
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def remove_brand_leaks(text):
    if not isinstance(text, str):
        return ""
    # Remove Yomost brand leakage
    text = re.sub(r'\byomost\s+lun\s+nha\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byomost\s+nhé\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byomost\b', '', text, flags=re.IGNORECASE)
    # Clean up trailing spaces or punctuation issues after deletion
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    return text.strip()

def paraphrase_templates(text, idx):
    if not isinstance(text, str):
        return ""
    
    # 1. Bình tĩnh nào!
    if text.startswith("Bình tĩnh nào!"):
        alt = [
            "Hít thở sâu một chút nhé...",
            "Mọi việc rồi sẽ ổn thôi, hãy cùng ngồi lại nào...",
            "Mình hiểu bạn đang cảm thấy thế nào, hãy bình tâm lại chút nhé..."
        ][idx % 3]
        text = text.replace("Bình tĩnh nào!", alt, 1)
        
    # 2. Nghe mình này nhé,
    if text.startswith("Nghe mình này nhé,"):
        alt = [
            "Bạn ơi, hãy chia sẻ cùng mình nhé,",
            "Mình đang lắng nghe bạn đây,",
            "Hãy cùng mình xem xét việc này nhé,"
        ][idx % 3]
        text = text.replace("Nghe mình này nhé,", alt, 1)
        
    # 3. Uống ngụm nước lạnh đi đã.
    if text.startswith("Uống ngụm nước lạnh đi đã."):
        alt = [
            "Thả lỏng cơ thể ra một chút nào.",
            "Hãy nhắm mắt lại và thở đều một lát nhé.",
            "Uống một ngụm nước ấm rồi thở nhẹ ra nào."
        ][idx % 3]
        text = text.replace("Uống ngụm nước lạnh đi đã.", alt, 1)
        
    # 4. Thở ra đi, thở ra.
    if text.startswith("Thở ra đi, thở ra."):
        alt = [
            "Bình tĩnh lại một chút nào bạn ơi.",
            "Hãy để sự bực bội này trôi đi một lát nhé.",
            "Hãy tập trung vào hơi thở một lát nào."
        ][idx % 3]
        text = text.replace("Thở ra đi, thở ra.", alt, 1)
        
    # 5. Wow xịn xò vậy!
    if text.startswith("Wow xịn xò vậy!"):
        alt = [
            "Tận hưởng khoảnh khắc này nhé!",
            "Chúc mừng bạn vì thành quả tuyệt vời này!",
            "Thật là một niềm vui xứng đáng cho nỗ lực của bạn!"
        ][idx % 3]
        text = text.replace("Wow xịn xò vậy!", alt, 1)
        
    return text

def map_row_to_target_label(row):
    text = clean_and_normalize(row['Input']).lower()
    source_label = row['Emotion']
    
    # 1. Joy / Vui vẻ
    if source_label == 'Vui vẻ':
        hope_keywords = ['hy vọng', 'mong rằng', 'mong là', 'tương lai', 'trông đợi', 'tin tưởng']
        if any(w in text for w in hope_keywords):
            return 'hy_vong'
        return 'vui'
        
    # 2. Sadness / Buồn bã
    elif source_label == 'Buồn bã':
        disappointment_keywords = ['thất vọng', 'thất zọng', 'nản', 'chán nản', 'bất lực', 'bế tắc', 'buông xuôi']
        if any(w in text for w in disappointment_keywords):
            return 'that_vong'
        return 'buon'
        
    # 3. Anxiety / Lo âu
    elif source_label == 'Lo âu':
        return 'lo_au'
        
    # 4. Anger / Tức giận
    elif source_label == 'Tức giận':
        return 'gian_du'
        
    # 5. Depression/Despair / Trầm cảm/Tuyệt vọng
    elif source_label == 'Trầm cảm/Tuyệt vọng':
        suicide_keywords = [
            'tự tử', 'muốn chết', 'kết thúc cuộc đời', 'biến mất', 'gánh nặng', 
            'nhảy xuống', 'tự hại', 'thư tuyệt mệnh', 'chết đi', 'không muốn sống', 
            'thiết sống', 'cắt cổ tay', 'uống thuốc tự', 'nhảy cầu', 'nhảy lầu', 'chán sống'
        ]
        if any(w in text for w in suicide_keywords):
            if any(w in text for w in ['sợ', 'lo sợ', 'hoang mang', 'ám ảnh', 'tim đập', 'mất ngủ', 'rén']):
                return 'lo_au'
            return 'buon'
            
        despair_keywords = ['bế tắc', 'tuyệt vọng', 'vô nghĩa', 'vô dụng', 'bất lực']
        if any(w in text for w in despair_keywords):
            return 'that_vong'
            
        return 'buon'
        
    # 6. Abuse / Bạo hành
    elif source_label == 'Bạo hành':
        anger_keywords = [
            'căm ghét', 'căm hận', 'hận', 'tức giận', 'điên lên', 
            'muốn đập lại', 'phẫn nộ', 'bất bình', 'chửi', 'căm thù'
        ]
        if any(w in text for w in anger_keywords):
            return 'gian_du'
            
        fear_keywords = [
            'đánh', 'đập', 'bạo lực', 'bạo hành', 'tấn công', 'đe dọa', 
            'sợ', 'quấy rối', 'lạm dụng', 'xâm hại', 'stalking', 'bắt nạt', 'tống tiền'
        ]
        if any(w in text for w in fear_keywords):
            return 'lo_au'
            
        control_keywords = [
            'kiểm soát', 'cô lập', 'không có chỗ đi', 'không biết làm thế nào để thoát', 
            'giam cầm', 'bế tắc', 'không cho gặp'
        ]
        if any(w in text for w in control_keywords):
            return 'that_vong'
            
        sad_keywords = ['tủi thân', 'đau lòng', 'buồn', 'khóc', 'sụp đổ']
        if any(w in text for w in sad_keywords):
            return 'buon'
            
        return 'lo_au'
        
    else:
        return 'trung_tinh'

def process_dataset(source_path, target_path):
    print(f"Đang đọc dữ liệu từ: {source_path}")
    df = pd.read_csv(source_path)
    
    # Ánh xạ nhãn cảm xúc
    df['mapped_emotion'] = df.apply(map_row_to_target_label, axis=1)
    
    # Làm sạch cột Output (cho LLM fine-tuning)
    df['cleaned_output'] = df['Output'].apply(clean_and_normalize)
    df['cleaned_output'] = df['cleaned_output'].apply(remove_brand_leaks)
    df['cleaned_output'] = df['cleaned_output'].apply(normalize_abbreviations)
    
    # Paraphrase tiền tố rập khuôn
    for idx, row in df.iterrows():
        df.at[idx, 'cleaned_output'] = paraphrase_templates(row['cleaned_output'], idx)
        
    # Tạo dataframe đích đầy đủ thông tin sạch
    df_output = pd.DataFrame({
        'input': df['Input'].apply(clean_and_normalize),
        'original_emotion': df['Emotion'],
        'mapped_emotion': df['mapped_emotion'],
        'topic': df['Topic'],
        'output': df['cleaned_output']
    })
    
    # Loại bỏ các dòng trống
    df_output = df_output[df_output['input'] != '']
    df_output = df_output.dropna(subset=['mapped_emotion', 'output'])
    
    print("\n=== Phân bổ nhãn sau khi ánh xạ ===")
    print(df_output['mapped_emotion'].value_counts())
    
    df_output.to_csv(target_path, index=False)
    print(f"\nĐã ghi file kết quả thành công ra: {target_path}")

if __name__ == "__main__":
    SOURCE_CSV = "/home/ai02/aiquoc/VNUF/Data/...csv"
    TARGET_CSV = "/home/ai02/aiquoc/VNUF/Data/mapped_dataset_7label_cleaned.csv"
    process_dataset(SOURCE_CSV, TARGET_CSV)
