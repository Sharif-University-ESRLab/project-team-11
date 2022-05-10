import cv2
import numpy as np
import dlib
import os
from matplotlib import pyplot as plt


def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    # return a tuple of (x, y, w, h)
    return (x, y, w, h)


def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # return the list of (x, y)-coordinates
    return coords


def get_landmarks(img, detector, predictor, show=False):
    w, h = len(img[0]), len(img)
    img_resized = cv2.resize(img, (500, int(h * 500 / w)))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    if rects is None or len(rects) == 0:
        return None
    # determine the facial landmarks for the face region, then
    # convert the facial landmark (x, y)-coordinates to a NumPy
    # array
    rect = rects[0]
    shape = predictor(gray, rect)
    shape = shape_to_np(shape)

    if show:
        (x, y, w, h) = rect_to_bb(rect)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # show the face number
        # loop over the (x, y)-coordinates for the facial landmarks
        # and draw them on the image
        for (x, y) in shape:
            cv2.circle(img, (x, y), 2, (0, 0, 255), -1)
        cv2.imshow("Output", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return shape


def plot_points(a):
    n = len(a)
    plt.scatter(a[:, 0], -a[:, 1], 10, range(n))
    plt.scatter([0], [0], 30, [(0, 0, 0)])
    # plt.axis([-100, 100, -100, 100])
    plt.show()


def zero_mean(a):
    a[:, 0] -= int(a[:, 0].sum() / len(a))
    a[:, 1] -= int(a[:, 1].sum() / len(a))


def get_rotation_matrix(deg):
    rad = np.deg2rad(deg)
    return np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])


def rotate(a, deg):
    r = get_rotation_matrix(deg)
    n = len(a)
    for i in range(n):
        a[i] = np.dot(r, a[i])


def orient_ear_to_ear(a):
    x1 = a[0]
    x2 = a[16]
    theta = np.arctan2(x2[1] - x1[1], x2[0] - x1[0])
    rotate(a, -np.rad2deg(theta))


def normalize_scale(a):
    w = a[16, 0] - a[0, 0]
    h = a[8, 1] - a[19, 1]
    a[:, 0] *= 200 / w
    a[:, 1] *= 200 / h


def l2(a, b):
    return ((a - b)**2).sum()/len(a)


def point_to_line_dist(m, b, x, y):
    return (m * x + b - y)**2 / (m**2 + 1)


def reflect_point_to_line(m, b, x, y):
    new_x = ((1 - m**2) * x + 2 * m * y - 2 * m * b) / (m**2 + 1)
    new_y = ((m**2 - 1) * y + 2 * m * x + 2 * b) / (m**2 + 1)
    return new_x, new_y


def symmetric_distance(img, detector, predictor, show):
    landmarks = get_landmarks(img, detector, predictor, show)
    if landmarks is None:
        return "face not found", "face not found"
    landmarks = landmarks.astype(np.float)
    zero_mean(landmarks)
    orient_ear_to_ear(landmarks)
    normalize_scale(landmarks)
    left_ids = np.array([0, 1, 2, 3, 4, 5, 6, 7, 17, 18, 19, 20, 21, 36, 37, 38, 39, 40, 41, 31, 32, 48, 49, 50, 60, 61, 67, 58, 59], dtype=int)
    midd_ids = np.array([27, 28, 29, 30, 33, 51, 62, 66, 57, 8], dtype=int)
    right_ids = np.array([16, 15, 14, 13, 12, 11, 10, 9, 26, 25, 24, 23, 22, 45, 44, 43, 42, 47, 46, 35, 34, 54, 53, 52, 64, 63, 65, 56, 55], dtype=int)

    m, b = np.polyfit(landmarks[midd_ids, 0], landmarks[midd_ids, 1], 1)

    dist_to_line = 0
    for x, y in landmarks[midd_ids]:
        dist_to_line += point_to_line_dist(m, b, x, y) / len(midd_ids)

    left_points = landmarks[left_ids]
    right_points = landmarks[right_ids]
    right_points_predicted = []
    for (x, y) in left_points:
        right_points_predicted.append(reflect_point_to_line(m, b, x, y))
    return dist_to_line, l2(right_points, right_points_predicted)


def main():
    path_to_dataset = "C:\\Users\\ahmad\\Desktop\\ILFW"

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    # temp = get_template_coords(path_to_dataset, detector, predictor).astype(np.float)
    # zero_mean(temp)
    # orient_ear_to_ear(temp)
    # normalize_scale(temp)
    img = cv2.imread(path_to_dataset + "\\Leila_Hatami\\Leila_Hatami_0004.jpg")
    print(symmetric_distance(img, detector, predictor, False))

    # for name in os.listdir(path_to_dataset):
    #     print(name)
    #     for img_name in os.listdir(path_to_dataset + "\\" + name):
    #         print(img_name)
    #         img = cv2.imread(path_to_dataset + "\\" + name + "\\" + img_name)
    #         dist = distance_from_temp(img, temp, detector, predictor, False)
    #
    #         # w, h = len(img[0]), len(img)
    #         # img = cv2.resize(img, (500, int(h * 500 / w)))
    #         # cv2.putText(img, "Distance: {}".format(round(dist, 3)), (20, 20),
    #         #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    #         # cv2.imshow("output", img)
    #         # cv2.waitKey()
    #         # cv2.destroyAllWindows()
    #         plt.imshow(img[..., ::-1])
    #         plt.axis("off")
    #         # plt.tight_layout()
    #         if dist != "face not found":
    #             plt.title("Distance: {}".format(round(dist, 3)))
    #         else:
    #             plt.title(dist)
    #         plt.savefig("distances\\"+img_name)


def real_time():
    cap = cv2.VideoCapture(0)
    path_to_dataset = "C:\\Users\\ahmad\\Desktop\\ILFW"

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    # temp = get_template_coords(path_to_dataset, detector, predictor).astype(np.float)
    # zero_mean(temp)
    # orient_ear_to_ear(temp)
    # normalize_scale(temp)
    while True:
        _, frame = cap.read()
        # # Convert image into grayscale
        # gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
        #
        # # Use detector to find landmarks
        # faces = detector(gray)
        #
        # for face in faces:
        #     x1 = face.left()  # left point
        #     y1 = face.top()  # top point
        #     x2 = face.right()  # right point
        #     y2 = face.bottom()  # bottom point
        #
        #     # Create landmark object
        #     landmarks = predictor(image=gray, box=face)
        #
        #     # Loop through all the points
        #     for n in range(0, 68):
        #         x = landmarks.part(n).x
        #         y = landmarks.part(n).y
        #
        #         # Draw a circle
        #         cv2.circle(img=frame, center=(x, y), radius=3, color=(0, 255, 0), thickness=-1)

        # i added them
        line_dist, point_dist = symmetric_distance(frame, detector, predictor, False)
        thresh = 50
        if line_dist != "face not found":
            cv2.putText(frame, "Line distance: {}".format(round(line_dist, 3)), (20, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, "Point distance: {}".format(round(point_dist, 3)), (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            # cv2.putText(frame, str(dist < thresh), (20, 20),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            cv2.putText(frame, line_dist, (20, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        # show the image
        cv2.imshow(winname="Face", mat=frame)

        # Exit when escape is pressed
        if cv2.waitKey(delay=1) == 27:
            break

    # When everything done, release the video capture and video write objects
    cap.release()

    # Close all windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # main()
    real_time()
