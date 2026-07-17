# 2. Kiến trúc Mô hình Đích & Thuộc tính Soft Multi-Label (Target Model & Soft Multi-Label Analysis)

Mô hình đích sử dụng kiến trúc **ViSoBERT** phân loại thành 7 nhãn cảm xúc cốt lõi:
`['vui', 'buon', 'lo_au', 'gian_du', 'trung_tinh', 'hy_vong', 'that_vong']`

### Cơ chế Soft Multi-Label khi Inference:
Mô hình hỗ trợ đầu ra Soft Multi-label nhờ việc lấy nhãn Top-2 nếu xác suất $p_2 \ge 0.15$ và khoảng cách $p_1 - p_2 \le 0.40$. Sau đó, bộ lọc `INCOMPATIBLE` sẽ loại bỏ các cặp nhãn mâu thuẫn:
```python
INCOMPATIBLE = [
    ('vui', 'buon'), ('vui', 'lo_au'), ('vui', 'that_vong'), ('vui', 'gian_du'),
    ('hy_vong', 'buon'), ('hy_vong', 'gian_du'), ('hy_vong', 'that_vong')
]
```

### Phân tích tính an toàn của nhãn tiêu cực:
- **Tập các nhãn tiêu cực (`buon`, `lo_au`, `that_vong`, `gian_du`) tương hợp hoàn toàn với nhau**. Điều này cho phép mô hình mô tả chính xác những trạng thái hỗn hợp như buồn lo (sad-anxious) hoặc buồn tủi vọng tưởng (sad-disappointed).
- Tuy nhiên, **tuyệt đối không dùng nhãn `that_vong` (Thất vọng) cho các câu tự tử/tự hại**. Về mặt ngữ nghĩa, thất vọng (`that_vong`) là trạng thái kỳ vọng không đạt được, thường phản ứng ở mức độ chán nản nhẹ đến vừa. Việc gán các câu tự sát sang thất vọng làm giảm mức độ khẩn cấp, dẫn đến chatbot không kích hoạt đúng các kịch bản cứu hộ khẩn cấp mà chỉ đưa ra lời khuyên xoa dịu thông thường. 
- Các câu tự sát/tự hại phải được gán vào `buon` (đau khổ cùng cực) hoặc `lo_au` (sợ hãi/bất an cho tính mạng), kết hợp với một **Cơ chế Safety Override (Bộ lọc an toàn kiểm soát trước)** để đảm bảo an toàn tuyệt đối.
