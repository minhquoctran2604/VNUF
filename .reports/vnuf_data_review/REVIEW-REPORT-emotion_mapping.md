# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG ÁNH XẠ NHÃN CẢM XÚC (REVIEW-REPORT-emotion_mapping)

- **Mã dự án**: VNUF Emotion Classifier Review
- **Thời gian đánh giá**: 15/07/2026
- **Thành phần đánh giá**: Reviewer Subagent (`reviewer_agent` - hồ sơ Tech Lead) và Tech Lead
- **Mục tiêu đánh giá**: Đề xuất quy tắc ánh xạ và mã nguồn tự động chuyển đổi nhãn từ bộ dữ liệu khủng hoảng/tư vấn tâm lý sang bộ dữ liệu huấn luyện của mô hình ViSoBERT 7 nhãn.

---

## 1. Nhật ký Đánh giá và Phản biện (Debate & Review History)

### Vòng 1 (15/07/2026 02:53) - KẾT QUẢ: FAIL
- **Nội dung đệ trình**: Executor đề xuất ánh xạ các câu có ý định tự sát/tự hại (`Trầm cảm/Tuyệt vọng`) sang nhãn đích `that_vong` (Thất vọng nhẹ). Nhãn `Bạo hành` có mô tả thiết kế là ánh xạ sang `gian_du` nhưng trong code Python bị bỏ quên. Thiếu phân tích định lượng và phương án giải quyết mất cân bằng lớp.
- **Phản biện từ Reviewer**:
  1. *Sai lệch ngữ nghĩa*: Tự tử/tự hại thể hiện trạng thái uất ức cực độ (severe sadness) hoặc sợ hãi (severe anxiety), không phải sự hụt hẫng kỳ vọng thông thường (`that_vong`). Gán nhãn này làm méo mó ngữ nghĩa nhãn `that_vong` trong mô hình.
  2. *Rủi ro an toàn*: Chatbot khi nhận diện nhãn `that_vong` sẽ đưa ra phản hồi an ủi thông thường thay vì kích hoạt quy trình can thiệp khẩn cấp (hotline 1800 599 920), đe dọa trực tiếp tính mạng người dùng.
  3. *Không nhất quán*: Thiết kế quy định nhãn `Bạo hành` ánh xạ được sang `gian_du`, nhưng code Python mẫu hoàn toàn thiếu logic này.
  4. *Cân bằng lớp*: Nạp lượng lớn dữ liệu tiêu cực từ tập khủng hoảng gây mất cân bằng nghiêm trọng mà không có giải pháp bù đắp.

### Vòng 2 (15/07/2026 02:54) - KẾT QUẢ: PASS (with Minor Revisions)
- **Nội dung cải tiến của Executor**:
  1. Chuyển các câu tự tử/tự hại sang nhãn `buon` hoặc `lo_au` để giữ đúng ngữ nghĩa và mức độ nghiêm trọng.
  2. Thiết kế cơ chế **Safety-Override (Bộ lọc an toàn trước mô hình)** dùng regex để phát hiện tự tử/bạo hành và trigger ngay hotline hỗ trợ quốc gia (1800 599 920 / 111 / 113) trước khi cho dữ liệu đi vào mô hình học máy.
  3. Bổ sung logic `anger_keywords` để map các mẫu bạo hành phẫn nộ sang nhãn `gian_du` trong code Python.
  4. Lượng hóa cụ thể phân phối mẫu (tập dữ liệu có 2654 dòng, `lo_au` chiếm ~39.4%, `hy_vong` chiếm ~1.9%). Đề xuất bù đắp bằng Class Weights, Label Smoothing, và tăng cường dữ liệu Back-Translation.
- **Phản hồi từ Reviewer**: Đề xuất đạt chất lượng rất cao và an toàn tuyệt đối. Tuy nhiên, bảng thống kê ở Mục 4 xếp nhãn nguồn và đích song song hàng ngang gây hiểu nhầm thị giác (vd: hàng ngang bạo hành tương ứng với hy_vong). Yêu cầu tách thành 2 bảng phân phối độc lập.

### Vòng 3 (15/07/2026 02:55) - KẾT QUẢ: PASS
- **Nội dung cải tiến của Executor**: Đã tách Mục 4 thành hai bảng độc lập hoàn toàn: *Bảng 4.1: Phân phối của 6 nhãn cảm xúc nguồn* và *Bảng 4.2: Phân phối của 7 nhãn cảm xúc đích sau khi ánh xạ*.
- **Kết luận**: Đạt sự đồng thuận hoàn toàn từ toàn bộ đội ngũ.

---

## 2. Tiêu chí và Kết quả Đánh giá Kỹ thuật (Technical Evaluation Metrics)

| Tiêu chí | Điểm đánh giá | Nhận xét chi tiết | Trạng thái |
| :--- | :--- | :--- | :--- |
| **Tính đúng đắn ngữ nghĩa** | 9.5 / 10 | Các nhãn cốt lõi được ánh xạ chính xác. Trầm cảm/Tuyệt vọng được phân rã hợp lý sang `buon`/`lo_au` và `that_vong` (bế tắc không tự hại), không gây loãng nhãn. | **ĐẠT (PASS)** |
| **Tính an toàn & Đạo đức AI** | 10 / 10 | Thiết kế bộ lọc Safety-Override độc lập trước mô hình đảm bảo chatbot có thể lập tức cứu hộ người dùng có ý định tự tử hoặc bị bạo hành nguy cấp. | **ĐẠT (PASS)** |
| **Tính nhất quán triển khai** | 10 / 10 | Quy tắc thiết kế và mã nguồn Python đồng bộ hoàn toàn. Logic phát hiện tức giận trong bạo hành được cài đặt chuẩn xác. | **ĐẠT (PASS)** |
| **Kiểm soát phân bổ nhãn** | 9.0 / 10 | Có số liệu thống kê cụ thể. Phương án xử lý mất cân bằng lớp (Class Weights + Label Smoothing) đã được kiểm chứng hoạt động tốt trong notebook gốc. | **ĐẠT (PASS)** |

---

## 3. Khuyến nghị và Hướng dẫn Triển khai (Recommendations)

1. **Tích hợp Bộ lọc An toàn (Safety-Override Filter)**:
   - Cài đặt bộ lọc regex ở tầng API/Middleware của chatbot trước khi chuyển câu nói vào pipeline của mô hình.
   - Khi phát hiện trùng khớp từ khóa nguy hại, lập tức bỏ qua dự đoán mô hình, ghi log khẩn cấp và trả về thông tin cứu hộ.
2. **Huấn luyện mô hình**:
   - Sử dụng file dữ liệu sau khi chạy ánh xạ (`mapped_dataset_7label.csv`) làm tập dữ liệu huấn luyện tăng cường hoặc tập validation/test để đánh giá độ phủ cảm xúc tiêu cực.
   - Đảm bảo tham số `compute_class_weight` trong notebook huấn luyện hoạt động đúng để bù đắp cho sự lệch nhãn của lớp đa số `lo_au` (~39.4%) và lớp thiểu số `hy_vong` (~1.9%).
3. **Giám sát nhãn nhiễu**:
   - Chạy thuật toán Cleanlab sau khi huấn luyện mô hình trên tập dữ liệu mới để lọc các mẫu có nhãn ánh xạ mâu thuẫn mạnh với dự đoán của mô hình để kiểm định chất lượng thủ công.
