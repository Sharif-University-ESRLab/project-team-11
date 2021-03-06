import cv2
import dlib
import numpy as np
import pose_estimation
from scipy.spatial import Delaunay


d_isa = "mamad"

def preprocess(points):
    pose_estimation.zero_mean(points)
    pose_estimation.orient_ear_to_ear(points)
    pose_estimation.normalize_scale(points)
    return points


def calc_triangle_area(points):
    a = np.array([[points[0, 0], points[0, 1], 1], [points[1, 0], points[1, 1], 1], [points[2, 0], points[2, 1], 1]])
    return np.abs(np.linalg.det(a))

def PolyArea(x,y):  # x is the vector of xs of points and y is the vector of ys of the points
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def calc_ratio_lr(img, detector, predictor):
    w, h = len(img[0]), len(img)
    img = cv2.resize(img, (500, int(h * 500 / w)))

    left_ids = [0, 1, 2, 3, 4, 5, 6, 7, 17, 18, 19, 20, 21, 36, 37, 38, 39, 40, 41, 31, 32, 48, 49, 50, 60, 61, 67, 58, 59]
    midd_ids = [27, 28, 29, 30, 33, 51, 62, 66, 57, 8]
    right_ids = [16, 15, 14, 13, 12, 11, 10, 9, 26, 25, 24, 23, 22, 45, 44, 43, 42, 47, 46, 35, 34, 54, 53, 52, 64, 63, 65, 56,
         55]

    points = pose_estimation.get_landmarks(img, detector, predictor)
    if points is not None:
        points = points.astype(float)
    else:
        return np.array([0, 0, 0])
    normalized_points = preprocess(points.copy())

    tri = Delaunay(normalized_points[left_ids + midd_ids])

    left_areas, right_areas = [], []
    for ids in tri.simplices:
        left_areas.append(calc_triangle_area((points[left_ids + midd_ids])[ids]))
        right_areas.append(calc_triangle_area((points[right_ids + midd_ids])[ids]))
    return np.array(left_areas)/np.array(right_areas)


def calc_ratio_ud(img, detector, predictor, temp):
    w, h = len(img[0]), len(img)
    img = cv2.resize(img, (500, int(h * 500 / w)))

    up_ids = [0, 1, 2] + [x for x in range(14, 48)]
    down_ids = [x for x in range(2, 15)] + [x for x in range(31, 36)] + [x for x in range(48, 68)]

    points = pose_estimation.get_landmarks(img, detector, predictor)
    if points is not None:
        points = points.astype(np.float)
    else:
        img = cv2.resize(img, (w, h))
        return 0, img
    normalized_points = preprocess(points.copy())
    r = pose_estimation.find_best_rotation(normalized_points, temp)
    for i in range(len(normalized_points)):
        normalized_points[i] = np.dot(r, normalized_points[i])
    l = 0
    for id in range(1, 6):
        if abs(normalized_points[id, 1] - normalized_points[33, 1]) < abs(normalized_points[l, 1] - normalized_points[33, 1]):
            l = id
    r = 11
    for id in range(12, 17):
        if abs(normalized_points[id, 1] - normalized_points[33, 1]) < abs(
                normalized_points[r, 1] - normalized_points[33, 1]):
            r = id

    up_polygon_ids = [x for x in range(16, r-1, -1)] + [35, 34, 33, 32, 31] + [x for x in range(l, -1, -1)] + [x for x in range(17, 27)]
    face_polygon_ids = [x for x in range(16, -1, -1)] + [x for x in range(17, 27)]

    up_area = PolyArea(points[up_polygon_ids, 0], points[up_polygon_ids, 1])
    mask_img = np.zeros_like(img)
    cv2.fillPoly(mask_img, [(points[up_polygon_ids]).astype(np.int32)], (255, 255, 255))
    img = img.astype(int)
    face_area = PolyArea(points[face_polygon_ids, 0], points[face_polygon_ids, 1])
    img[img > 255] = 255
    img = img.astype(np.uint8)
    img = cv2.resize(img, (w, h))
    return up_area/face_area, img



detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
path_to_dataset = "ILFW"
temp = pose_estimation.get_template_coords(path_to_dataset, detector, predictor).astype(np.float)
preprocess(temp)



def get_frame_direction(frame):
    lr_ratio = calc_ratio_lr(frame, detector, predictor)
    median = round(np.median(lr_ratio), 2)

    ud_ratio, frame = calc_ratio_ud(frame, detector, predictor, temp)
    ud_ratio = round(ud_ratio, 2)

    # frame[:40, :, :] = 0
    # cv2.putText(frame, "Ratio:{}".format(ratio), (20, 20),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # cv2.putText(frame, "ratio: {}".format(ratio), (20, 20),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    l_thresh, r_thresh = 0.70, 1.30
    u_thresh, d_thresh = 0.52, 0.65
    if len(lr_ratio)==3:
        text = "Face not Found"
    elif median < l_thresh:
        text = "Left"
    elif median > r_thresh:
        text = "Right"
    elif ud_ratio < u_thresh:
        text = "Up"
    elif ud_ratio > d_thresh:
        text = "Down"
    else:
        text = "Front"

    global d_isa
    d_isa = text
    return text



def real_time():
    cap = cv2.VideoCapture(0)
    frames = []
    while True:
        ret, frame = cap.read()
        if ret == False:
            break


        get_frame_direction(frame)

        text = d_isa
        cv2.putText(frame, text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 6)

        # cv2.putText(frame, str(median), (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 6)
        # cv2.putText(frame, str(ud_ratio), (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 6)


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
    # imageio.mimwrite('vid_full_labeld.mp4', frames, fps=14.8)


if __name__ == '__main__':
    real_time()
