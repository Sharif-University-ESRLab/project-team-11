import cv2
import numpy as np
import dlib
import os
from matplotlib import pyplot as plt
import front_view_with_symmetric_distance
import imageio


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


def get_landmarks(img, detector, predictor, show = False):
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
        scale_factor = w/500
        (x, y, w, h) = rect_to_bb(rect)
        x=int(x*scale_factor)
        y=int(y*scale_factor)
        w=int(w*scale_factor)
        h=int(h*scale_factor)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # show the face number
        # loop over the (x, y)-coordinates for the facial landmarks
        # and draw them on the image
        for (x, y) in shape:
            x = int(x * scale_factor)
            y = int(y * scale_factor)
            cv2.circle(img, (x, y), int(2 * scale_factor), (0, 0, 255), -1)
        # cv2.imshow("Output", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    return shape


def get_template_coords(path_to_dataset, detector, predictor):
    img = cv2.imread(path_to_dataset + "/Leila_Hatami/Leila_Hatami_0004.jpg")
    return get_landmarks(img, detector, predictor)


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


def find_best_rotation(a, b):
    H = np.dot(np.transpose(a), b)
    u, s, vh = np.linalg.svd(H)
    return np.dot(np.transpose(vh), np.transpose(u))


def l2(a, b):
    return ((a - b)**2).sum()/len(a)


def distance_from_temp(img, temp, detector, predictor, show):
    landmarks = get_landmarks(img, detector, predictor, show)
    if landmarks is None:
        return "face not found"
    landmarks = landmarks.astype(np.float)
    zero_mean(landmarks)
    orient_ear_to_ear(landmarks)
    normalize_scale(landmarks)
    r = find_best_rotation(landmarks, temp)
    for i in range(len(landmarks)):
        landmarks[i] = np.dot(r, landmarks[i])
    return l2(landmarks, temp)


def main():
    path_to_dataset = "C:\\Users\\ahmad\\Desktop\\ILFW"

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    temp = get_template_coords(path_to_dataset, detector, predictor).astype(np.float)
    zero_mean(temp)
    orient_ear_to_ear(temp)
    normalize_scale(temp)
    list_of_pics_with_score = []
    for name in os.listdir(path_to_dataset):
        for img_name in os.listdir(path_to_dataset + "\\" + name):
            img = cv2.imread(path_to_dataset + "\\" + name + "\\" + img_name)
            dist = distance_from_temp(img, temp, detector, predictor, False)
            if  dist == "face not found":
                dist = 100000
            list_of_pics_with_score.append((dist, name, img_name))
    list_of_pics_with_score = sorted(list_of_pics_with_score, key=lambda x: x[0])
    # for name in os.listdir(path_to_dataset):
    #     print(name)
    #     for img_name in os.listdir(path_to_dataset + "\\" + name):
    #         print(img_name)
    for i, (d, name, img_name) in enumerate(list_of_pics_with_score):
            img = cv2.imread(path_to_dataset + "\\" + name + "\\" + img_name)
            line_dist, point_dist = front_view_with_symmetric_distance.symmetric_distance(img, detector, predictor, False)
            dist = distance_from_temp(img, temp, detector, predictor, True)
            plt.imshow(img[..., ::-1])
            plt.axis("off")
            # plt.tight_layout()
            if dist != "face not found" and line_dist != "face not found":
                plt.title("Old method: {}\n New method:   Line distance: {}  -  Point distance: {}".format(round(dist, 3), round(line_dist, 3), round(point_dist, 3)))
            else:
                plt.title("face not found")
            plt.savefig("distances\\"+str(i)+".jpg")


def real_time():
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("vid.mp4")

    path_to_dataset = "C:\\Users\\ahmad\\Desktop\\ILFW"

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    temp = get_template_coords(path_to_dataset, detector, predictor).astype(np.float)
    zero_mean(temp)
    orient_ear_to_ear(temp)
    normalize_scale(temp)
    frames = []
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
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
        dist = distance_from_temp(frame, temp, detector, predictor, False)
        line_dist, point_dist = front_view_with_symmetric_distance.symmetric_distance(frame, detector, predictor, False)
        a, b, thresh = 0.09076017506713725, 0.0017837412579896899, 7.3362696629644395
        if dist != "face not found":
            # cv2.putText(frame, "Distance: {}".format(round(dist, 3)), (20, 20),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            combination_dist = a * dist + b * point_dist
            if combination_dist < thresh:
                cv2.putText(frame, "Front View", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (9, 110, 19), 6)
            else:
                cv2.putText(frame, "Not Front View", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (9, 9, 110), 6)
        else:
            cv2.putText(frame, "Face Not Found", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (110, 9, 9), 8)
        # show the image
        cv2.imshow(winname="Face", mat=frame)
        frames.append(frame[..., ::-1])


        # Exit when escape is pressed
        if cv2.waitKey(delay=1) == 27:
            break

    # When everything done, release the video capture and video write objects
    cap.release()

    # Close all windows
    cv2.destroyAllWindows()
    # imageio.mimwrite('vid_frontview.gif', frames, fps=14.8)


if __name__ == '__main__':
    # main()
    real_time()
