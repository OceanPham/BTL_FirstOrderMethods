# Guide tự học các phương pháp tối ưu bậc một

Mở **index.html** bằng Edge, Chrome hoặc Firefox. Không cần server, Internet, npm hay Python để đọc và dùng mô phỏng.

## Lộ trình

1. Bài toán, loss, đạo hàm và gradient.
2. GD, SGD, Mini-batch: ý tưởng, mã giả, phép tính tay.
3. Mô phỏng 3 bước trên cùng ba điểm dữ liệu.
4. Python cơ bản và từng đoạn của code 01.
5. Bước cố định, chính xác theo tia, Armijo trong code 02.
6. Ma trận, NumPy và vòng huấn luyện code 03.
7. Chuẩn hóa, SGDRegressor, SGDClassifier, partial_fit, MLP trong code 04.
8. Tensor, DataLoader, backward và optimizer.step trong code 05.
9. Cách đọc kết quả và phạm vi kết luận.
10. Cài môi trường, chạy demo, xử lý lỗi, bài tập.
11. Tám câu tự kiểm tra có giải thích.
12. Toàn bộ code gốc và nguồn tham khảo.

Bấm “Đánh dấu đã hiểu” để lưu tiến độ riêng trong trình duyệt; không gửi dữ liệu đi.
Tìm mục học chỉ lọc mục lục. Có thể dùng Ctrl+F để tìm trong nội dung.
“In / lưu PDF” mở hộp thoại in của trình duyệt, tự mở các phần giải thích thu gọn.
Các mô phỏng tính trực tiếp bằng JavaScript; không phải kết quả chạy Python/PyTorch trên trình duyệt.

## Cấu trúc

- index.html: bài học tiếng Việt.
- styles.css: bố cục desktop, mobile, bản in và hỗ trợ reduced motion.
- math.js: phép tính thuần của hai mô phỏng.
- app.js: hiển thị code, thao tác mô phỏng, mục lục, tiến độ, bài kiểm tra.
- sources.js: nguyên văn 5 script Python và đoạn trích kèm số dòng/hash.
- assets/: ba hình thực nghiệm đã lưu từ bài làm.
- tools/sync_sources.py: đồng bộ code và hình từ thư mục bài làm.
- tools/check_guide.py: kiểm tra số học, nội dung và trình duyệt.

Thư mục guide tự đủ để đọc ngoại tuyến; có thể chép nguyên thư mục sang máy khác.
Các link tài liệu chính thức cần Internet.
Hướng dẫn chạy Python có đường dẫn theo máy hiện tại; đổi đường dẫn nếu chuyển máy.

## Khi sửa các file Python gốc

Từ thư mục BTL_FirstOrderMethods:

    python guide/tools/sync_sources.py

Công cụ chỉ đọc code/ và hinh/, cập nhật sources.js và các ảnh trong guide/assets/.
Đoạn trích được xác định bằng AST hoặc mốc câu lệnh. Nếu đổi tên hàm/mốc, công cụ báo lỗi thay vì trích nhầm.
Phần giải thích trong index.html là biên soạn thủ công: cần rà lại nếu thay đổi thuật toán.
Hash SHA-256 trong mục 12 đối chiếu bản file gốc tại thời điểm đồng bộ.
Code tải xuống từ guide là bản nhúng, không tự theo dõi thay đổi của file gốc.

## Kiểm tra khi bảo trì

Kiểm tra JavaScript:

    node --check guide/app.js
    node --check guide/math.js
    node --check guide/sources.js

Kiểm tra giao diện (chỉ dành cho người bảo trì, người đọc không cần cài):

    python -m pip install playwright
    python guide/tools/check_guide.py

Kiểm tra mặc định dùng Edge headless, hồ sơ trình duyệt tạm riêng.
Nếu máy không có Edge, cài Chromium của Playwright rồi dùng:

    python -m playwright install chromium
    python guide/tools/check_guide.py --browser chromium

Có thể lưu ảnh QA bằng --screenshots DUONG_DAN_THU_MUC.

