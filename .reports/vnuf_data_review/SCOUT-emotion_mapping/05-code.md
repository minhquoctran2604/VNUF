# 5. Mã nguồn Python Ánh xạ Nhãn (Python Script Proposal)

Dưới đây là mã nguồn Python đã cập nhật (v2) đồng bộ logic ánh xạ nhãn bạo hành tức giận (`gian_du`) và xử lý an toàn cho các câu tự tử/tự hại (ánh xạ về `buon`/`lo_au` thay vì `that_vong`).

```python
import pandas as pd
import re

def clean_and_normalize(text):
    if not isinstance(text, str):
        return ""
    # Chuẩn hóa khoảng trắng
    return re.sub(r'\s+', ' ', text).strip()

def map_row_to_target_label(row):
    text = clean_and_normalize(row['Input']).lower()
    source_label = row['Emotion']
    
    # 1. Ánh xạ VUI VẺ
    if source_label == 'Vui vẻ':
        hope_keywords = ['hy vọng', 'mong rằng', 'mong là', 'tương lai', 'trông đợi', 'tin tưởng']
        if any(w in text for w in hope_keywords):
            return 'hy_vong'
        return 'vui'
        
    # 2. Ánh xạ BUỒN BÃ
    elif source_label == 'Buồn bã':
        disappointment_keywords = ['thất vọng', 'thất zọng', 'nản', 'chán nản', 'bất lực', 'bế tắc', 'buông xuôi']
        if any(w in text for w in disappointment_keywords):
            return 'that_vong'
        return 'buon'
        
    # 3. Ánh xạ LO ÂU
    elif source_label == 'Lo âu':
        return 'lo_au'
        
    # 4. Ánh xạ TỨC GIẬN
    elif source_label == 'Tức giận':
        return 'gian_du'
        
    # 5. Ánh xạ TRẦM CẢM/TUYỆT VỌNG (Giải quyết Rủi ro An toàn và Sai lệch Ngữ nghĩa)
    elif source_label == 'Trầm cảm/Tuyệt vọng':
        # Các câu tự tử, tự hại đặc biệt nguy hiểm -> Phải chuyển sang 'buon' hoặc 'lo_au'
        # để chatbot dễ nhận diện hỗ trợ phù hợp, cấm ánh xạ sang 'that_vong' (Thất vọng nhẹ).
        suicide_keywords = [
            'tự tử', 'muốn chết', 'kết thúc cuộc đời', 'biến mất', 'gánh nặng', 
            'nhảy xuống', 'tự hại', 'thư tuyệt mệnh', 'chết đi', 'không muốn sống', 
            'thiết sống', 'cắt cổ tay', 'uống thuốc tự', 'nhảy cầu', 'nhảy lầu', 'chán sống'
        ]
        if any(w in text for w in suicide_keywords):
            # Nếu chứa trạng thái lo sợ hoang mang -> lo_au, ngược lại -> buon (u uất)
            if any(w in text for w in ['sợ', 'lo sợ', 'hoang mang', 'ám ảnh', 'tim đập', 'mất ngủ', 'rén']):
                return 'lo_au'
            return 'buon'
            
        # Trầm cảm thể hiện sự tuyệt vọng/bế tắc cuộc sống thông thường (Không tự hại) -> that_vong
        despair_keywords = ['bế tắc', 'tuyệt vọng', 'vô nghĩa', 'vô dụng', 'bất lực']
        if any(w in text for w in despair_keywords):
            return 'that_vong'
            
        return 'buon'
        
    # 6. Ánh xạ BẠO HÀNH (Đồng bộ Thiết kế và Code)
    elif source_label == 'Bạo hành':
        # Tức giận, phẫn nộ trong bối cảnh bị bạo hành -> gian_du (Đồng bộ thiết kế)
        anger_keywords = [
            'căm ghét', 'căm hận', 'hận', 'tức giận', 'điên lên', 
            'muốn đập lại', 'phẫn nộ', 'bất bình', 'chửi', 'căm thù'
        ]
        if any(w in text for w in anger_keywords):
            return 'gian_du'
            
        # Sợ hãi thể xác và đe dọa an toàn -> lo_au
        fear_keywords = [
            'đánh', 'đập', 'bạo lực', 'bạo hành', 'tấn công', 'đe dọa', 
            'sợ', 'quấy rối', 'lạm dụng', 'xâm hại', 'stalking', 'bắt nạt', 'tống tiền'
        ]
        if any(w in text for w in fear_keywords):
            return 'lo_au'
            
        # Sự kiểm soát, cô lập dẫn đến bế tắc và mất hy vọng -> that_vong
        control_keywords = [
            'kiểm soát', 'cô lập', 'không có chỗ đi', 'không biết làm thế nào để thoát', 
            'giam cầm', 'bế tắc', 'không cho gặp'
        ]
        if any(w in text for w in control_keywords):
            return 'that_vong'
            
        # Buồn bã, tủi thân do hoàn cảnh -> buon
        sad_keywords = ['tủi thân', 'đau lòng', 'buồn', 'khóc', 'sụp đổ']
        if any(w in text for w in sad_keywords):
            return 'buon'
            
        # Mặc định cho bạo hành là nỗi lo sợ, bất an cho tính mạng
        return 'lo_au'
        
    else:
        return 'trung_tinh'
        
def process_dataset(source_path, target_path):
    print(f"Đang đọc dữ liệu từ: {source_path}")
    df = pd.read_csv(source_path)
    
    # Thực hiện ánh xạ nhãn
    df['mapped_emotion'] = df.apply(map_row_to_target_label, axis=1)
    
    # Tạo định dạng chuẩn cho huấn luyện
    df_output = pd.DataFrame({
        'text': df['Input'].apply(clean_and_normalize),
        'emotion': df['mapped_emotion']
    })
    
    # Lọc bỏ các dòng trống
    df_output = df_output[df_output['text'] != '']
    df_output = df_output.dropna(subset=['emotion'])
    
    print("\n=== Phân bố nhãn sau khi ánh xạ (v2) ===")
    print(df_output['emotion'].value_counts())
    
    df_output.to_csv(target_path, index=False)
    print(f"\nĐã ghi file kết quả thành công ra: {target_path}")

if __name__ == "__main__":
    SOURCE_CSV = "/home/ai02/aiquoc/VNUF/Data/...csv"
    TARGET_CSV = "/home/ai02/aiquoc/VNUF/Data/mapped_dataset_7label.csv"
    process_dataset(SOURCE_CSV, TARGET_CSV)
```
