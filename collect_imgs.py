import os
import cv2
import time

# Tạo thư mục lưu dữ liệu hình ảnh
DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Định nghĩa số lớp ảnh và số lượng ảnh của mỗi lớp
number_of_classes = 8
dataset_size = 200

# Cài cap là webcam
cap = cv2.VideoCapture(0)


for j in range(number_of_classes):
    if not os.path.exists(os.path.join(DATA_DIR, str(j))):
        os.makedirs(os.path.join(DATA_DIR, str(j)))

    print('Collecting data for class {}'.format(j))

    # Thu thập dữ liệu cho từng lớp
    while True:
        ret, frame = cap.read()
        cv2.putText(frame, 'Ready? Press "Q" ! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                    cv2.LINE_AA)
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) == ord('q'):
            break

    # Đếm ngược và thu thập ảnh
    for i in range(3, 0, -1):
        ret, frame = cap.read()
        cv2.putText(frame, f'Collecting in {i} seconds...', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                    cv2.LINE_AA)
        cv2.imshow('frame', frame)
        cv2.waitKey(1000)  # Đợi 1 giây

    # Thu thập và lưu ảnh
    counter = 0
    while counter < dataset_size:
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        cv2.waitKey(25)
        cv2.imwrite(os.path.join(DATA_DIR, str(j), '{}.jpg'.format(counter)), frame)

        counter += 1

# Đóng webcam và cửa sổ
cap.release()
cv2.destroyAllWindows()