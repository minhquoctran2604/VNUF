# 1. Phân tích Dữ liệu Nguồn & Đặc trưng (Source Dataset Analysis)

Tập dữ liệu nguồn `...csv` bao gồm các cột chính:
- **Input**: Câu nói hoặc lời chia sẻ của người dùng.
- **Emotion**: Nhãn cảm xúc nguồn (gồm 6 nhãn: `Lo âu`, `Buồn bã`, `Vui vẻ`, `Tức giận`, `Trầm cảm/Tuyệt vọng`, `Bạo hành`).
- **Topic**: Chủ đề của cuộc hội thoại (ví dụ: `Công việc`, `Cuộc sống`, `Học tập`, `Tình cảm`, `Khủng hoảng`).
- **Output**: Câu phản hồi mang tính hỗ trợ, tư vấn từ hệ thống chatbot.

### Phân tích đặc trưng các nhãn nguồn:

1. **Vui vẻ (Joy/Happiness)**:
   - *Đặc trưng*: Thể hiện niềm vui, sự hài lòng, phấn khích hoặc yêu đời khi đạt được thành quả (ví dụ: nhận học bổng, pass môn, sếp khen, được crush nhắn tin).
   - *Từ khóa phổ biến*: `vui xỉu`, `sướng rơn`, `yêu đời`, `phấn khích`, `phê`, `tuyệt vời`.

2. **Buồn bã (Sadness)**:
   - *Đặc trưng*: Cảm giác cô đơn, tủi thân, hụt hẫng hoặc u sầu do mất mát hoặc thất bại ở mức độ nhẹ đến trung bình (ví dụ: thú cưng đi mất, trượt môn, sếp la, chia tay).
   - *Từ khóa phổ biến*: `tủi thân`, `chán nản`, `cô đơn`, `trống rỗng`, `buồn thiu`, `muốn khóc`, `hic`, `😢`.

3. **Lo âu (Anxiety/Fear)**:
   - *Đặc trưng*: Căng thẳng, lo sợ tương lai mông lung, quá tải công việc, hoặc áp lực từ thi cử/tiền bạc.
   - *Từ khóa phổ biến*: `đổ mồ hôi hột`, `rén`, `lo lắng`, `overthinking`, `hoang mang`, `áp lực`, `run`, `tim đập thình thịch`.

4. **Tức giận (Anger/Frustration)**:
   - *Đặc trưng*: Sự bức xúc, phẫn nộ trước các tình huống bất công hoặc khó chịu (ví dụ: khách hàng hủy hẹn phút chót, bạn mượn tiền không trả, bị xe tạt nước).
   - *Từ khóa phổ biến*: `muốn bùng cháy`, `tức á`, `cay thật sự`, `điên máu`, `sôi máu`, `giận tím người`, `🤬`, `🔥`.

5. **Trầm cảm/Tuyệt vọng (Depression/Despair)**:
   - *Đặc trưng*: Trạng thái tâm lý tiêu cực sâu sắc, kiệt sức và bế tắc. Đặc biệt, nhóm này chứa các biểu hiện tự làm hại bản thân (self-harm) hoặc có suy nghĩ tự tử (suicidal ideation) vốn cực kỳ nhạy cảm và đòi hỏi tính an toàn cao.
   - *Từ khóa phổ biến*: `tự tử`, `muốn chết`, `kết thúc cuộc đời`, `biến mất`, `gánh nặng`, `vô dụng`, `bế tắc hoàn toàn`, `không muốn thức dậy`.

6. **Bạo hành (Abuse/Violence)**:
   - *Đặc trưng*: Nạn nhân của bạo lực gia đình, quấy rối hoặc bắt nạt học đường. Phản ứng cảm xúc của nạn nhân đan xen giữa sợ hãi cho sự an toàn (`lo_au`), uất ức buồn bã (`buon`), bế tắc (`that_vong`) và phẫn nộ/muốn phản kháng (`gian_du`).
   - *Từ khóa phổ biến*: `chồng đánh`, `bạo hành`, `tấn công`, `xâm hại`, `quấy rối`, `lạm dụng`, `đe dọa`, `bắt nạt`.
