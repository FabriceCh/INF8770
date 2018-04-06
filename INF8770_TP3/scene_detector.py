import cv2
import numpy as np
import matplotlib.pyplot as plt

# Inspiration : https://bcastell.com/posts/scene-detection-tutorial-part-1/
def main():
    video = cv2.VideoCapture("Toots.avi")

    if not video.isOpened():
        print("Error - could not open video Toots.avi.")
        return
    else:
        print("Parsing video Toots.avi...")

    # Do stuff with cap here
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("Video resolution: %d x %d" % (width, height))

    last_hist = []
    diff = []
    while True:
        (rv, im) = video.read()
        if not rv:
            break
        if len(last_hist) == 0 :
            last_bhist, _ = np.histogram(im[:, :, 0].flatten(), 16, (0, 255))
            last_ghist, _ = np.histogram(im[:, :, 1].flatten(), 16, (0, 255))
            last_rhist, _ = np.histogram(im[:, :, 2].flatten(), 16, (0, 255))
            last_hist = np.concatenate((last_bhist, last_ghist, last_rhist))
        else:
            bhist, _ = np.histogram(im[:, :, 0].flatten(), 16, (0, 255))
            ghist, _ = np.histogram(im[:, :, 1].flatten(), 16, (0, 255))
            rhist, _ = np.histogram(im[:, :, 2].flatten(), 16, (0, 255))
            hist = np.concatenate((bhist, ghist, rhist))
            diff.append(np.linalg.norm(last_hist - hist))
            last_hist = hist

    plt.plot(diff)
    plt.xlabel('Frame number')
    plt.ylabel('Difference')
    plt.show()

    frame_count = video.get(cv2.CAP_PROP_POS_FRAMES)
    print("Read %d frames from video." % frame_count)


    video.release()


if __name__ == '__main__' :
    main()
