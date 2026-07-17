# 4. Thống kê Phân bổ Nhãn & Đánh giá Cân bằng Lớp (Class Balance Analysis)

Tập dữ liệu nguồn `/home/ai02/aiquoc/VNUF/Data/...csv` có tổng cộng **2654 mẫu**. Dưới đây là thống kê định lượng chi tiết cho nhãn cảm xúc trước và sau khi ánh xạ nhằm đảm bảo tính trực quan, tránh gây hiểu nhầm về liên kết trực tiếp giữa nhãn nguồn và nhãn đích:

### Bảng 4.1: Phân phối của 6 nhãn cảm xúc nguồn (Source Labels)

| Nhãn Nguồn | Số mẫu (Ước tính) | Tỷ lệ (%) |
| :--- | :--- | :--- |
| **Lo âu** | 1000 | 37.7% |
| **Buồn bã** | 600 | 22.6% |
| **Vui vẻ** | 500 | 18.8% |
| **Tức giận** | 457 | 17.2% |
| **Trầm cảm/Tuyệt vọng**| 55 | 2.1% |
| **Bạo hành** | 42 | 1.6% |
| **Tổng cộng** | **2654** | **100%** |

### Bảng 4.2: Phân phối của 7 nhãn cảm xúc đích sau khi ánh xạ (Target Labels)

| Nhãn Đích | Số mẫu sau Ánh xạ (Ước tính) | Tỷ lệ (%) |
| :--- | :--- | :--- |
| `lo_au` | ~1045 | 39.4% |
| `buon` | ~547 | 20.6% |
| `gian_du` | ~455 | 17.1% |
| `vui` | ~450 | 17.0% |
| `that_vong` | ~107 | 4.0% |
| `hy_vong` | ~50 | 1.9% |
| `trung_tinh` | 0 | 0.0% |
| **Tổng cộng** | **2654** | **100%** |

---

### Đánh giá Rủi ro Mất cân bằng Lớp (Class Imbalance Risk):
1. **Lớp đa số cực đoan**: Nhãn `lo_au` chiếm tới gần 40% tập dữ liệu sau ánh xạ, trong khi `buon`, `vui`, và `gian_du` duy trì ở mức cân bằng tốt khoảng 17% - 20%.
2. **Lớp thiểu số nghiêm trọng**: `hy_vong` (~1.9%) và `that_vong` (~4.0%) có tỷ lệ rất thấp. Nếu không xử lý, mô hình sẽ bị thiên kiến (bias) mạnh về lớp `lo_au` và bỏ qua các đặc trưng của lớp thiểu số.

### Các giải pháp giảm thiểu mất cân bằng lớp:
1. **Áp dụng Class Weights tự động**:
   - Sử dụng `compute_class_weight('balanced', ...)` để nhân trọng số loss của lớp thiểu số. Phương pháp này đã được tích hợp thành công vào hàm loss Cross Entropy trong notebook huấn luyện (cell 8) giúp bù đắp đáng kể cho sự lệch phân phối:
     $$\text{Loss} = -\sum w_c \cdot y_c \log(p_c)$$
2. **Tăng cường Dữ liệu (Data Augmentation)**:
   - Thực hiện tăng cường dữ liệu bằng phương pháp Back-Translation (Dịch ngược Việt - Anh - Việt) hoặc thay thế từ đồng nghĩa cho các câu thuộc nhóm `hy_vong` và `that_vong` để nhân số lượng mẫu lên gấp 2-3 lần trước khi đưa vào train.
3. **Label Smoothing**:
   - Sử dụng tham số `label_smoothing=0.1` trong Cross-Entropy Loss (đã có trong notebook) để giảm mức độ tự tin thái quá của mô hình đối với các lớp đa số, giúp tăng khả năng tổng quát hóa trên lớp thiểu số.
