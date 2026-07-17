# Báo Cáo Quy Trình Xử Lý Dữ Liệu VNUF

> **Date**: 2026-07-16
> **Type**: Data Processing Flow
> **Author**: `agent:reporter`

## 📊 Tổng Quan (Executive Summary)
Báo cáo này mô tả luồng xử lý và chuẩn hóa dữ liệu từ file nguồn ban đầu (dataset 2.6k dòng) sang file dữ liệu đích sạch và an toàn hơn. Mục tiêu của quá trình xử lý là đồng bộ nhãn cảm xúc với model ViSoBERT (7 nhãn), loại bỏ các lỗi văn bản, và giảm thiểu rủi ro từ các nội dung nhạy cảm.

---

## 📥 1. Dữ liệu Đầu Vào (Input)
* **File nguồn:** `Data/...csv`
* **Số lượng:** Khoảng 2,654 dòng.
* **Tình trạng:**
  * Có 6 nhãn cảm xúc gốc (Vui vẻ, Buồn bã, Lo âu, Tức giận, Trầm cảm/Tuyệt vọng, Bạo hành).
  * Trong đó, nhãn `Trầm cảm/Tuyệt vọng` và `Bạo hành` là nhãn hành vi/tình huống, KHÔNG PHẢI là nhãn cảm xúc thuần túy.

---

## ⚠️ 2. Các Vấn Đề Gặp Phải (Issues Identified)
1. **Lệch nhãn (Label Mismatch):** Mô hình mục tiêu ViSoBERT yêu cầu 7 nhãn cảm xúc (`vui`, `buon`, `lo_au`, `gian_du`, `so_hai`, `ngac_nhien`, `khinh_bi`, hoặc biến thể `that_vong`, `hy_vong`), nhưng file gốc chỉ có 6 nhãn và không tương thích.
2. **Rủi ro An toàn (Safety Risks):** Các nhãn `Trầm cảm/Tuyệt vọng` và `Bạo hành` chứa các nội dung nhạy cảm, dễ kích hoạt rủi ro an toàn cho model.
3. **Lỗi Rập khuôn (Template Repetition):** LLM sinh ra output thường xuyên lặp lại 5 mẫu câu cửa miệng (VD: "Bình tĩnh nào!", "Nghe mình này nhé,", "Wow xịn xò vậy!").
4. **Lỗi Văn bản (Text Artifacts):** Chứa nhiều từ viết tắt không nhất quán (ko, khg, rùi, mn, ac...) và bị rò rỉ tên thương hiệu quảng cáo ("Yomost nhé", "Yomost lun nha").

---

## ⚙️ 3. Quá Trình Xử Lý (Processing Flow)
**Công cụ xử lý:** Script `map_and_clean_data.py`.

* **Bước 3.1 - Mapping Nhãn (Label Mapping):**
  * `Vui vẻ` → Map thành `vui` hoặc `hy_vong` (dựa trên keyword).
  * `Buồn bã` → Map thành `buon` hoặc `that_vong` (dựa trên keyword).
  * `Lo âu` → Map thành `lo_au`.
  * `Tức giận` → Map thành `gian_du`.
  * `Trầm cảm/Tuyệt vọng` → Phân rã về `buon`, `lo_au`, hoặc `that_vong`. Đặc biệt chặn chặt các keyword tự tử để xếp vào nhãn an toàn.
  * `Bạo hành` → Phân rã về `gian_du`, `lo_au`, `that_vong`, hoặc `buon`.

* **Bước 3.2 - Làm Sạch Văn Bản (Text Cleaning):**
  * Xóa triệt để các rò rỉ thương hiệu (`yomost`).
  * Chuẩn hóa từ viết tắt (`ko` → `không`, `đc` → `được`, `rùi` → `rồi`...).

* **Bước 3.3 - Đa dạng hóa (Paraphrasing):**
  * Nhận diện 5 cụm từ rập khuôn ở đầu câu.
  * Thay thế xoay vòng (round-robin) bằng 3 biến thể khác nhau để giúp model học được văn phong đa dạng hơn.

---

## 📤 4. Dữ liệu Đầu Ra (Output)
* **File đích:** `Data/mapped_dataset_7label_cleaned.csv` (Hiện đã được chuyển vào `Data/data_to_use/`)
* **Đặc điểm:**
  * Dữ liệu sạch, không còn quảng cáo hay viết tắt rác.
  * Dữ liệu đã được phân bổ lại vào 7 nhãn cảm xúc an toàn và tương thích với ViSoBERT.
  * Output đa dạng hơn, ít rập khuôn hơn.

---

## 🚀 5. Khuyến nghị Tiếp Theo (Next Steps)
1. **Merge Data:** Gộp file đích `mapped_dataset_7label_cleaned.csv` này với file baseline `emotion_7label_data.csv` (10k dòng).
2. **Huấn luyện:** Dùng tập dữ liệu gộp để tiếp tục quá trình Fine-tune ViSoBERT/LLM.
