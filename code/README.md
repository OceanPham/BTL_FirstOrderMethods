# Code demo – Các phương pháp tối ưu bậc một (First-Order Methods)

Đề tài 3: Gradient Descent – Mini-batch GD – Stochastic GD
Môn: Tối ưu hóa ứng dụng (Cao học CNTT – Đại học Thủy lợi)

## Cài đặt

Yêu cầu Python 3.10 trở lên.

```bash
pip install -r requirements.txt
```

Nếu chỉ cần chạy script 01–04 thì không cần PyTorch (`pip install numpy matplotlib scikit-learn`).

## Các script

| File | Nội dung | Thư viện | Hình sinh ra (thư mục `../hinh`) |
|---|---|---|---|
| `01_vi_du_tinh_tay.py` | In từng bước lặp của các ví dụ tính tay trong báo cáo | NumPy | – |
| `02_gd_ham_hai_bien.py` | GD trên hàm f = 3x₁² + 2x₁x₂ + 4x₂² + 10: ảnh hưởng của tốc độ học; bước cố định / chính xác theo tia / quay lui Armijo | NumPy, Matplotlib | `hinh1`, `hinh2` |
| `03_so_sanh_gd_sgd_minibatch.py` | Tự cài đặt Batch GD, SGD, Mini-batch GD cho hồi quy tuyến tính; khảo sát kích thước lô | NumPy, Matplotlib | `hinh3`, `hinh4`, `hinh5` |
| `04_thu_vien_sklearn.py` | `SGDRegressor`, `SGDClassifier`, `partial_fit`, `MLPClassifier(solver="sgd")` | scikit-learn | `hinh6` |
| `05_pytorch_mang_no_ron.py` | Huấn luyện mạng MLP bằng `torch.optim.SGD` với batch size = N / 1 / 32 | PyTorch | `hinh7` |

## Cách chạy

```bash
python 01_vi_du_tinh_tay.py
python 02_gd_ham_hai_bien.py
python 03_so_sanh_gd_sgd_minibatch.py
python 04_thu_vien_sklearn.py
python 05_pytorch_mang_no_ron.py
```

Mỗi script chạy độc lập, in kết quả ra màn hình và lưu hình vào `../hinh`.
Các bộ dữ liệu đều được sinh ngẫu nhiên (có cố định seed) hoặc có sẵn trong scikit-learn nên không cần tải từ Internet.
Thời gian chạy in ra phụ thuộc vào máy; script 05 mất khoảng nửa phút vì phần SGD (b = 1) thực hiện hơn 43 000 lần cập nhật.
