# Kế hoạch xử lý `review_2nd_opinion.csv` (Đã cập nhật)

Mày nói đúng, góc nhìn của tao hơi cứng nhắc. Nếu một câu ("thấy bản thân mk ở đây") có thể dùng ở cả video vui lẫn buồn, thì tức là bản thân câu chữ đó **không mang cảm xúc cố định**, đưa về `trung_tinh` là hợp lý nhất để tránh model bị nhiễu.
Đồng thời, ý tưởng thêm lệnh `remove` cho những câu dọa dẫm trêu đùa/vô nghĩa ("anh chiến oánh cho bây h") là **cực kỳ xuất sắc** để làm sạch rác trong data.

Dựa trên feedback đó, tao cập nhật lại Plan như sau:

## 1. Phương hướng xử lý 659 dòng

**A. Nhóm Đổi về Trung Tính (359 dòng):**
- **Đồng ý với AI 2:** Chấp nhận toàn bộ 359 dòng này. Các câu mập mờ, thiếu ngữ cảnh, đa nghĩa sẽ được chuyển về `trung_tinh` đúng như AI 2 gợi ý.

**B. Nhóm Đổi sang Cảm Xúc Khác (117 dòng):**
*(Gồm 56 `that_vong`, 23 `gian_du`, 21 `hy_vong`, 14 `vui`, 3 `buon`)*
- AI 2 có vẻ gán nhãn rất ảo cho nhóm này (ví dụ: gán `that_vong` cho các câu đùa cợt). 
- **Giải pháp:** Áp dụng lệnh `remove` (xoá khỏi tập train) cho phần lớn nhóm này nếu chúng chỉ là chat nhảm/vô nghĩa.

**C. Nhóm Giữ Nguyên - Keep (180 dòng):**
- AI 2 đồng ý với Human. Ta sẽ tiếp tục giữ nguyên.

## 2. Các bước hành động (Action Items)

Để tiết kiệm thời gian cho mày, tao sẽ không bắt mày đọc tay 659 dòng. Tao sẽ:
1. Viết script **tự động duyệt** lại file `review_2nd_opinion.csv`.
2. Giữ nguyên các dòng `action = change` và `new_label = trung_tinh`.
3. Đổi toàn bộ các dòng mà AI 2 gợi ý gán sang các cảm xúc vô lý (nhóm 117 dòng) thành `action = remove` (để lọc bỏ hoàn toàn).
4. Áp dụng các thay đổi này (bao gồm cả việc xóa dòng khỏi tập data chính thức `emotion_training.csv`).

## 3. Câu hỏi cho mày (Open Question)
Đối với **117 dòng** mà AI 2 gợi ý đổi sang cảm xúc khác (vui, buồn, thất vọng...), tao có nên **quét sạch (đổi action thành `remove` hết)** luôn không? Hay mày muốn tao xuất riêng 117 dòng đó ra một file nhỏ để mày lướt qua xem có câu nào cứu được không?

*(Bấm Proceed hoặc comment lựa chọn của mày nhé)*
