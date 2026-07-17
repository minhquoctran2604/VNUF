# Báo cáo Phân tích Ánh xạ Nhãn Cảm xúc (SCOUT-emotion_mapping)

Thư mục này chứa báo cáo phân tích chi tiết của Executor (Scouter) về việc ánh xạ nhãn cảm xúc từ bộ dữ liệu nguồn sang mô hình ViSoBERT 7 nhãn. Do báo cáo chi tiết có độ dài lớn (>150 dòng), nội dung được chia nhỏ thành các tài liệu thành phần như sau:

## Danh mục tài liệu thành phần:
1. **[01-analysis.md](file:///home/ai02/aiquoc/VNUF/.reports/vnuf_data_review/SCOUT-emotion_mapping/01-analysis.md)**: Phân tích chi tiết đặc trưng và từ khóa phổ biến của 6 nhãn cảm xúc nguồn trong tập dữ liệu khủng hoảng/tư vấn.
2. **[02-soft-multilabel.md](file:///home/ai02/aiquoc/VNUF/.reports/vnuf_data_review/SCOUT-emotion_mapping/02-soft-multilabel.md)**: Đánh giá kiến trúc mô hình ViSoBERT đích, cơ chế suy diễn nhãn mềm (Soft Multi-label) và các quy tắc loại trừ nhãn tương khắc (`INCOMPATIBLE`).
3. **[03-rules.md](file:///home/ai02/aiquoc/VNUF/.reports/vnuf_data_review/SCOUT-emotion_mapping/03-rules.md)**: Bảng quy tắc ánh xạ nhãn chi tiết cho tập huấn luyện và thiết kế cơ chế **Safety-Override (Bộ lọc an toàn kiểm soát trước)** để ngăn chặn rủi ro tự hại/bạo hành.
4. **[04-stats.md](file:///home/ai02/aiquoc/VNUF/.reports/vnuf_data_review/SCOUT-emotion_mapping/04-stats.md)**: Thống kê định lượng phân phối nhãn trước và sau ánh xạ, đánh giá rủi ro mất cân bằng lớp và các giải pháp khắc phục (Class Weights, Data Augmentation, Label Smoothing).
5. **[05-code.md](file:///home/ai02/aiquoc/VNUF/.reports/vnuf_data_review/SCOUT-emotion_mapping/05-code.md)**: Mã nguồn Python mẫu sử dụng Pandas để tự động hóa quy trình ánh xạ nhãn cảm xúc.
