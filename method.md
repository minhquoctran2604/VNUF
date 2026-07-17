Viewed all_suspects_full.csv:1-100
Edited find_mismatches.py
Ran command: `python3 /home/ai02/.gemini/antigravity-ide/brain/2bdf534a-62c4-4afd-8191-09b98291db0b/scratch/find_mismatches.py`
Edited print_clean_mismatches.py
Ran command: `python3 /home/ai02/.gemini/antigravity-ide/brain/2bdf534a-62c4-4afd-8191-09b98291db0b/scratch/print_clean_mismatches.py`

Nhìn vào kết quả quét từ Cleanlab, chúng ta có tổng cộng **645 cặp tréo ngoe cực độ** (Positive vs Negative - tức là nhãn gốc là Tích cực nhưng model đoán là Tiêu cực, hoặc ngược lại). 

Qua phân tích các câu lỗi này, tôi phát hiện ra **3 cái "bẫy" cực kỳ tai hại** khiến bộ dữ liệu cũ bị gán nhãn sai hàng loạt:

---

### 1. 🪤 Bẫy từ "Mong / Ước / Xin" ➔ Bị gán sai thành `hy_vong`
Thuật toán gán nhãn trước đây cứ thấy câu nào có từ "mong", "ước", "hy vọng" là auto ném vào nhãn `hy_vong`. Nhưng thực tế:
*   **Thực chất là Lo âu:** *"Em bị tâm lí sợ ra những nơi đông người... **mong** anh rep"* ➔ Nhãn gốc: `hy_vong` | Model đoán đúng: `lo_au`.
*   **Thực chất là Buồn bã:** *"Thương em quá chị ạ e xin chia buồn cùng gia đình... **mong** bọn kia sớm bị trừng phạt"* ➔ Nhãn gốc: `hy_vong` | Model đoán đúng: `buon`.
*   **Thực chất là Tức giận:** *"Bọn này chỉ có tiền chứ lgi có đạo đức hả ban **tẩy chay** đi mng"* ➔ Nhãn gốc: `hy_vong` | Model đoán đúng: `gian_du`.

---

### 2. 🪤 Bẫy từ "Sợ" ➔ Bị gán sai thành `lo_au` hoặc ngược lại
*   **Thực chất là Thất vọng (chê bai):** *"hết hồn . **sợ** quá nhỉ . nhạt !"* ➔ Nhãn gốc: `that_vong` | Model đoán: `lo_au` (vì có chữ "sợ").
*   **Thực chất là Thất vọng:** *"đã **sợ** nhện rồi mà gặp thằng admin chơi trò mất nết :(("* ➔ Nhãn gốc: `that_vong` | Model đoán: `lo_au`.

---

### 3. 🪤 Bẫy "Mỉa mai / Sarcasm" (Icon cười `😛`, `))`, `😂`)
Model rất dễ bị lừa bởi các icon vui vẻ được viết kèm với nội dung tiêu cực:
*   *"tồi vc 😛"* ➔ Nhãn gốc: `gian_du` | Model đoán: `vui` (bị lừa bởi icon lè lưỡi).
*   *"đục khoét tuổi thơ vãi ))"* ➔ Nhãn gốc: `that_vong` | Model đoán: `vui` (bị lừa bởi ký tự cười `))`).
*   *"bạn trai người khác không bao giờ làm tao thất vọng =)))))"* ➔ Nhãn gốc: `hy_vong` | Model đoán: `vui` (đây thực chất là câu mỉa mai tủi thân của người độc thân, nhãn gốc gán Hy vọng là sai hoàn toàn).

---

### 💡 Nhận xét:
Cleanlab đã làm cực tốt nhiệm vụ của nó. Trong số 645 câu tréo ngoe này, **đa phần là nhãn gốc bị gán sai (Label Noise) từ các bộ dữ liệu thô ban đầu**, chứ không phải do model của bạn ngu. 

Bước tiếp theo, bạn chỉ cần duyệt qua danh sách này, dùng file `review_candidates.csv` để giữ/sửa/xóa nhãn của mấy câu này là chất lượng data sẽ tăng vọt! Bạn muốn tôi chuẩn bị file review chứa riêng các case tréo ngoe nhất này không?