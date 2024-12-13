import os
import cv2
import argparse

# Sử dụng argparse để nhận các tham số từ dòng lệnh
parser = argparse.ArgumentParser(description="Thu thập hình ảnh cho các lớp ngôn ngữ ký hiệu mới.")
parser.add_argument("--class_name", type=str, required=True, help="Tên lớp ngôn ngữ ký hiệu mới.")
parser.add_argument("--size", type=int, default=100, help="Số lượng ảnh cho lớp mới.")
parser.add_argument("--data_dir", type=str, default='./data', help="Thư mục lưu trữ dữ liệu.")
args = parser.parse_args()

DATA_DIR = args.data_dir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class_name = args.class_name
dataset_size = args.size

# Check if directory already exists, find the last class number
existing_classes = [int(d) for d in os.listdir(DATA_DIR) if d.isdigit()]
if existing_classes:
  next_class_number = max(existing_classes) + 1
else:
  next_class_number = 0

class_dir = os.path.join(DATA_DIR, str(next_class_number))
if not os.path.exists(class_dir):
  os.makedirs(class_dir)

print('Collecting data for class {}'.format(class_name))

# cài cap là webcam
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    cv2.putText(frame, 'Ready? Press "Q" ! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                cv2.LINE_AA)
    cv2.imshow('frame', frame)
    if cv2.waitKey(25) == ord('q'):
        break

counter = 0
while counter < dataset_size:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    cv2.waitKey(25)
    cv2.imwrite(os.path.join(class_dir, '{}.jpg'.format(counter)), frame)
    print(f"Collected {counter + 1}/{dataset_size} images for class {class_name}")  # Hiển thị số ảnh đã thu thập

    counter += 1

cap.release()
cv2.destroyAllWindows()