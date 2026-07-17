# BIÊN BẢN DUYỆT THIẾT KẾ ÁNH XẠ NHÃN CẢM XÚC (REVIEW-emotion_mapping)

- **Ngày ban hành**: 15/07/2026
- **Trạng thái phê duyệt**: **CHẤP THUẬN (APPROVED)**
- **Nhà phê duyệt**: Đội ngũ Golden Triangle Review (Tech Lead và Reviewer)

Tài liệu này tổng hợp các quy tắc ánh xạ nhãn cảm xúc đã được phê duyệt chính thức từ bộ dữ liệu hỗ trợ tinh thần nguồn (`Data/...csv`) sang mô hình ViSoBERT 7 nhãn cảm xúc đích, kèm theo cơ chế an toàn bắt buộc và phương án xử lý kỹ thuật.

---

## 1. Tóm tắt Quy tắc Ánh xạ Nhãn được phê duyệt (Approved Mapping Rules)

Quy trình ánh xạ từ 6 nhãn nguồn sang 7 nhãn đích của mô hình huấn luyện dựa trên phân rã từ khóa ngữ cảnh và phân tích mức độ nghiêm trọng:

1. **`Vui vẻ`** $\rightarrow$ `vui` (mặc định). Nếu chứa từ khóa kỳ vọng tương lai (`hy vọng`, `mong là`...) $\rightarrow$ `hy_vong`.
2. **`Buồn bã`** $\rightarrow$ `buon` (mặc định). Nếu chứa từ khóa bất lực, thất vọng vì không đạt kỳ vọng (`thất vọng`, `nản`...) $\rightarrow$ `that_vong`.
3. **`Lo âu`** $\rightarrow$ `lo_au` (100%).
4. **`Tức giận`** $\rightarrow$ `gian_du` (100%).
5. **`Trầm cảm/Tuyệt vọng`** $\rightarrow$ Phân rã theo mức độ nguy hại:
   - Các biểu hiện tự hại, tự tử $\rightarrow$ Ánh xạ sang `buon` hoặc `lo_au` (không được đưa vào `that_vong`).
   - Các bế tắc cuộc sống thông thường (không tự hại) $\rightarrow$ Ánh xạ sang `that_vong`.
6. **`Bạo hành`** $\rightarrow$ Phân rã theo phản ứng cảm xúc của nạn nhân:
   - Phản kháng, căm hận $\rightarrow$ Ánh xạ sang `gian_du`.
   - Sợ hãi, đe dọa trực tiếp $\rightarrow$ Ánh xạ sang `lo_au`.
   - Bị kiểm soát, cô lập mối quan hệ $\rightarrow$ Ánh xạ sang `that_vong`.
   - Tủi thân, khóc lóc $\rightarrow$ Ánh xạ sang `buon`.

---

## 2. Thiết kế Cơ chế Safety-Override (Bắt buộc)

Do tính chất nhạy cảm của các câu thuộc nhóm `Trầm cảm/Tuyệt vọng` và `Bạo hành`, hệ thống chatbot phải triển khai một lớp lọc an toàn chạy trước mô hình (Safety-Override Filter) dựa trên regex/từ khóa:
- **Tín hiệu Tự sát/Tự hại**: Nhận diện từ khóa (`tự tử`, `muốn chết`, `kết thúc cuộc sống`, `tự sát`...). Trả ngay thông tin Đường dây nóng Hỗ trợ Tâm lý Quốc gia: **1800 599 920** (24/7, miễn phí).
- **Tín hiệu Bạo hành/Xâm hại Nguy cấp**: Nhận diện từ khóa (`chồng đánh`, `bị xâm hại`, `bị bắt cóc`...). Trả ngay thông tin Tổng đài Quốc gia Bảo vệ Trẻ em & Gia đình: **111** hoặc Cảnh sát **113**.

---

## 3. Khả năng Tương thích với Cơ chế Soft Multi-label khi Inference

Mô hình đích hỗ trợ đầu ra Soft Multi-label khi dự báo. Bộ lọc tương hợp nhãn `INCOMPATIBLE` quy định:
```python
INCOMPATIBLE = [
    ('vui', 'buon'), ('vui', 'lo_au'), ('vui', 'that_vong'), ('vui', 'gian_du'),
    ('hy_vong', 'buon'), ('hy_vong', 'gian_du'), ('hy_vong', 'that_vong')
]
```
- Các nhãn tiêu cực (`buon`, `lo_au`, `that_vong`, `gian_du`) **hoàn toàn tương hợp với nhau**. 
- Điều này cho phép khi người dùng thực tế chia sẻ các câu trầm cảm/bạo hành phức tạp, mô hình có thể kích hoạt đầu ra đa nhãn tiêu cực cùng lúc (ví dụ: `['buon', 'lo_au']` hoặc `['buon', 'that_vong']`), phản ánh chính xác trạng thái tâm lý hỗn hợp mà không vi phạm các ràng buộc tương khắc nhãn.

---

## 4. Xử lý Mất cân bằng Lớp (Class Imbalance)

Sau khi ánh xạ, nhãn `lo_au` sẽ trở thành nhãn đa số (~39.4%), trong khi `hy_vong` (~1.9%) và `that_vong` (~4.0%) là các nhãn thiểu số nghiêm trọng. Các giải pháp kỹ thuật đã phê duyệt:
- **Trọng số lớp (Class Weights)**: Tự động tính toán bằng `compute_class_weight` trong notebook để phạt nặng sai số trên lớp thiểu số.
- **Label Smoothing**: Đặt tham số `label_smoothing=0.1` trong Cross-Entropy Loss để hạn chế sự tự tin thái quá vào lớp đa số.
- **Tăng cường dữ liệu**: Dịch ngược (Back-Translation) Việt-Anh-Việt đối với các mẫu thuộc nhóm thiểu số `hy_vong` và `that_vong`.

---

## 5. Dấu phê duyệt của Đội ngũ (Consensus Stamp)

Chúng tôi, đội ngũ Golden Triangle Review, chính thức xác nhận đề xuất ánh xạ nhãn cảm xúc phiên bản v3 đã **ĐẠT (PASS)** tất cả các tiêu chuẩn đánh giá về ngữ nghĩa học, an toàn kỹ thuật và đạo đức AI.

```
[ GOLDEN TRIANGLE CONSENSUS STAMP ]
----------------------------------
STATUS: APPROVED
DATE: 2026-07-15
TECH LEAD: reviewer-tech-lead (reviewer-tech-lead)
REVIEWER: Mapping Logic Reviewer (reviewer_agent)
EXECUTOR: Codebase & Dataset Scouter (scouter_agent)
----------------------------------
```
Tập dữ liệu sau ánh xạ (`mapped_dataset_7label.csv`) được phê duyệt để đưa vào huấn luyện mô hình.
