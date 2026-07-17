# Data Lineage — Emotion Classifier Dataset

Tài liệu này ghi lại toàn bộ quá trình tiến hoá của các file dữ liệu trong `Data/`,
theo dạng `file nguồn → hành động → file kết quả`, để không ai (kể cả tương lai
chính mình) phải đoán lại việc đã làm.

**Quy ước:**
- ✅ = bước đã xác nhận chắc chắn (tự tay làm/kiểm chứng trong phiên làm việc này)
- ❓ = bước không rõ chi tiết (do công cụ/tool khác thực hiện trước đó, suy luận
  từ dữ liệu quan sát được, không có log gốc)

---

## A. Nhánh Classifier (ViSoBERT, 7 nhãn cảm xúc)

### A0. Nguồn thô

```
Data/raw_sources/
├── chat_emotions_clean2_utf8.csv
├── emotion_classification.csv
├── llm_assistant.csv
├── uit_vsmec/
└── vigoemotions/
        │
        │  ❓ (gộp/tiền xử lý từ nhiều nguồn — không rõ script gốc)
        ▼
emotion_7label_data.csv  (10.250 dòng, 7 nhãn, cân bằng ~1500/nhãn)
```

### A1. Phát hiện & sửa bug pipeline (không đổi nhãn, chỉ đổi cách xử lý text)

- ✅ Phát hiện bug: `clean_text` xoá emoji **theo nhãn** lúc train, nhưng
  `label=None` lúc inference → xoá cả 2 chiều → lệch phân phối train/inference.
- ✅ Fix: bỏ hẳn việc xoá emoji khỏi text đưa vào model. Train + inference
  dùng **nguyên văn** (chỉ chuẩn hoá khoảng trắng). Việc xoá emoji-theo-nhãn chỉ
  còn dùng nội bộ cho QC (`strip_contradictory_signal`), không đụng vào text
  model học.
- Không có file mới sinh ra ở bước này — chỉ sửa code trong `train_classifier_colab.ipynb`.

### A2. Train baseline (data còn nhiễu nhãn) → đo baseline

```
emotion_7label_data.csv
        │  ✅ Train ViSoBERT (cell 1-10), text nguyên văn
        ▼
Model baseline: accuracy ~59-60%, F1 ~58-59%, top2 ~77%
(model này chỉ dùng để dò lỗi, không phải model cuối)
```

### A3. K-Fold Out-of-Fold — máy dò nhãn nghi ngờ

```
emotion_7label_data.csv
        │  ✅ cell 8a: StratifiedKFold 5 fold, mỗi fold train 3 epoch,
        │     chấm fold nó CHƯA học → out-of-fold probs cho 100% data
        ▼
rv_meta.csv          (10.250 dòng, metadata: raw_text, label, emotion_current...)
oof_pred_probs.npy   (10.250 x 7, xác suất dự đoán ngoài mẫu)
```

### A4. Cleanlab + Icon heuristic — chấm điểm nghi ngờ

```
rv_meta.csv + oof_pred_probs.npy
        │  ✅ cell 8b: cleanlab (normalized_margin) + heuristic
        │     "icon nói 1 đằng, chữ nói 1 nẻo" (strip_contradictory_signal)
        ▼
all_suspects_full.csv   (3248 dòng nghi ngờ, đầy đủ, không cap — nguồn tham chiếu gốc)
review_candidates.csv  (500 dòng đầu, cap theo score — ❌ SAU NÀY BỊ THAY THẾ, xem A5)
```

### A5. Phân loại theo kiểu mâu thuẫn → tách nhỏ để duyệt

```
all_suspects_full.csv (3248)
        │  ✅ Phân loại original_label vs predicted_label:
        │     - polarity_flip: tích cực ↔ tiêu cực hẳn        (645)
        │     - neutral_mix:   một bên trung_tinh              (1011)
        │     - chong_lan_hop_le: cặp gần nghĩa (buon/that_vong...) (1552)
        │     - trung_du_doan: model đoán trùng nhãn gốc        (40)
        ▼
review_triaged.csv        (3248, có evidence+suggestion — ❌ tiền thân, bị thay bởi 2 file dưới)
review_mau_thuan.csv      (1583 = polarity_flip + neutral_mix gộp thô — ❌ bị thay bằng bản tách riêng)
        │
        ├──► review_polarity_flip.csv  (645)   → xem A6
        └──► review_neutral_mix.csv    (1011)  → xem A7

(chong_lan_hop_le 1552 + trung_du_doan 40: quyết định BỎ QUA, không duyệt —
 giá trị thấp, đa số là chồng lấn cảm xúc tự nhiên hoặc model đã đoán đúng)
```

### A6. Vòng 1 — Duyệt `polarity_flip` (645 dòng)

```
review_polarity_flip.csv (645, cột action/new_label/review_note ban đầu trống)
        │  ✅ Duyệt tay từng dòng, ưu tiên 308 dòng có gợi ý (evidence≥3)
        │  ✅ Soát riêng 19 dòng "X → vui chỉ vì cleanlab tự tin" (icon mỉa mai đánh lừa)
        │     → sửa lại 6 dòng bị flip sai (id 4701, 9763, 985, 2241, 1186, 9850)
        │     → giữ 1 dòng flip đúng (id 1597, "đục khoét tuổi thơ" = nostalgia vui)
        ▼
review_polarity_flip.csv (645, ĐÃ DUYỆT XONG: 96 change, 549 keep)
        │  ✅ Áp theo `id` vào data gốc
        ▼
emotion_7label_data.csv  (96 nhãn đã đổi — GHI ĐÈ TRỰC TIẾP file gốc)
```

### A7. Vòng 2 — Duyệt `neutral_mix` (1011 dòng)

```
review_neutral_mix.csv (1011, action/new_label/review_note ban đầu trống)
        │
        ├─ ✅ 349 dòng: rule-based keep (triết lý/lời khuyên/phủ định/tin tức)
        │     → tách riêng: ruled_keeps_349.csv (subset tham khảo)
        │
        ├─ ✅ 3 dòng: "Pure statement/observation" (câu trần thuật khách quan
        │     bị gán nhầm cảm xúc) → change sang trung_tinh
        │     ("Ngược chiều ở cao tốc", "Truy xét chủ thầu...", "...biên bản là may")
        │
        └─ ❓ 659 dòng: "Trust human emotion label over model's neutral guess"
              — quyết định KEEP HÀNG LOẠT, KHÔNG đọc từng câu (detector yếu +
              chi phí đọc quá cao). Đây là mảng DUY NHẤT trong toàn bộ 3248 dòng
              nghi ngờ chưa từng được human/AI đọc kỹ.
              → tách riêng để 2nd-opinion: review_2nd_opinion.csv (đang PENDING,
                xem mục A9)
        ▼
review_neutral_mix.csv (1011, ĐÃ DUYỆT XONG: 3 change, 1008 keep)
        │  ✅ Áp theo `id` vào data gốc
        ▼
emotion_7label_data.csv  (+3 nhãn đổi nữa — tổng cộng 99 nhãn đã sửa so với gốc)
```

### A8. Tổ chức lại thư mục — đặt tên đúng vai trò

```
emotion_7label_data.csv (99 fix, đang nằm nhầm ở raw_sources/ dù không còn "raw")
        │  ✅ mv + rename
        ▼
Data/active_inputs/emotion_training.csv   ← FILE TRAIN CHÍNH THỨC HIỆN TẠI

Data/active_inputs/emotion_7label_data_cleaned.csv (bản cũ, THIẾU 3 fix vòng 2)
        │  ✅ archive (không xoá, chỉ cách ly khỏi active_inputs)
        ▼
Data/pipeline_artifacts/emotion_7label_data_cleaned_STALE_missing3fixes.csv
```

`train_classifier_colab.ipynb`: `DATA_PATH` và cell 8c `CLEANED_PATH` đã cập nhật
trỏ về `Data/active_inputs/emotion_training.csv` (cả đọc lẫn ghi cùng 1 file,
không tạo thêm bản `_cleaned` mới mỗi vòng duyệt nữa).

### A9. Việc còn treo (chưa xong)

```
review_2nd_opinion.csv (659 dòng, action/new_label ĐÃ XOÁ TRẮNG để chấm mù)
        │  ⏳ ĐANG CHỜ: gửi cho 1 AI khác chấm độc lập, kèm bộ chính sách gán nhãn
        │     (nghĩa đen câu chữ, icon xã giao ≠ cảm xúc, phủ định, ngưỡng cường độ...)
        ▼
[CHƯA CÓ — khi nhận kết quả về: diff với quyết định "keep" hiện tại trong
 review_neutral_mix.csv, chỗ nào 2 bên bất đồng thì người quyết định lần cuối,
 rồi áp tiếp vào emotion_training.csv]
```

---

## B. Nhánh Assistant/LLM (chatbot tư vấn — KHÔNG liên quan đến A)

⚠️ Nhánh này tách biệt hoàn toàn khỏi data classifier ở trên. Không được gộp
2 nhánh — assistant dùng taxonomy 5 nhãn (thiếu `trung_tinh`, `hy_vong`), không
tương thích với classifier 7 nhãn.

```
❓ (nguồn: bộ CBT tiếng Anh "ChatCBT", không rõ xuất xứ chính xác)
        ▼
Data/pipeline_artifacts/merged.csv          (621 dòng, system/user/assistant tiếng Anh)
        │  ❓ dịch sang tiếng Việt + gán emotion_id
        ▼
Data/pipeline_artifacts/train_with_emotion.csv  (621 dòng, user_vi/assistant_vi/emotion)
        │  ❓ (không rõ bước trung gian — có thể gộp thêm nguồn khác)
        ▼
Data/active_inputs/mapped_dataset_7label_cleaned.csv
   (2653 dòng: input/original_emotion/mapped_emotion/topic/output
    — có cột `topic` với giá trị "Khủng hoảng" [97 dòng, bạo hành + trầm cảm/
    tuyệt vọng] dùng làm tín hiệu cho safety gate, KHÔNG dùng để fine-tune)

Data/active_inputs/llm_assistant_fixed.csv   ❓ (quan hệ với raw_sources/llm_assistant.csv
                                                 chưa được xác minh trong phiên này)
```

**Lưu ý:** 2 file `merged.csv` và `train_with_emotion.csv` hiện đang nằm trong
`pipeline_artifacts/` (thư mục vốn dành cho artifact của nhánh A) — nên chuyển
sang `raw_sources/` hoặc thư mục riêng cho nhánh assistant để tránh nhầm lẫn
tiếp trong tương lai (đã đề xuất, chưa thực hiện).

---

## Tóm tắt trạng thái file hiện tại

| File | Vai trò | Trạng thái |
|---|---|---|
| `active_inputs/emotion_training.csv` | **Data train classifier chính thức** | ✅ 99/99 fix đã áp |
| `active_inputs/mapped_dataset_7label_cleaned.csv` | Data train assistant | ✅ ổn, có safety topic |
| `pipeline_artifacts/all_suspects_full.csv` | Nguồn tham chiếu 3248 nghi ngờ | Giữ — dùng đối chiếu |
| `pipeline_artifacts/review_polarity_flip.csv` | Bằng chứng 96 sửa vòng 1 | Giữ — audit cho báo cáo |
| `pipeline_artifacts/review_neutral_mix.csv` | Bằng chứng 3 sửa + 1008 keep vòng 2 | Giữ — audit cho báo cáo |
| `pipeline_artifacts/review_2nd_opinion.csv` | 659 dòng chờ AI khác chấm | ⏳ Đang chờ kết quả |
| `pipeline_artifacts/rv_meta.csv` + `oof_pred_probs.npy` | K-fold OOF (tốn 35' GPU) | Giữ — tái dùng nếu duyệt thêm vòng |
| `pipeline_artifacts/review_candidates.csv` | Shortlist 500 sơ khai | Lỗi thời — có thể xoá |
| `pipeline_artifacts/review_triaged.csv` | Tiền thân trước khi tách polarity/neutral | Lỗi thời — có thể xoá |
| `pipeline_artifacts/review_mau_thuan.csv` | Phân loại thô ban đầu | Lỗi thời — có thể xoá |
| `pipeline_artifacts/ruled_keeps_349.csv` | Subset trung gian | Lỗi thời — đã gộp vào neutral_mix |
| `pipeline_artifacts/emotion_7label_data_cleaned_STALE_missing3fixes.csv` | Bản cũ thiếu 3 fix | Archive — đừng dùng |
| `pipeline_artifacts/merged.csv`, `train_with_emotion.csv` | Nguồn CBT cho assistant | Đặt nhầm thư mục — nên chuyển |
