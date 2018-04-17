import cv2
import matplotlib.pyplot as plt
import numpy as np

COLOUR_DIFF_THRESHOLD = 8000
GRADIENT_SIGN_THRESHOLD = 0.05
COLOUR_SCENE_CHANGE_THRESHOLD = 8000

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
    thresh_exceed = []
    colour_diff = []
    edges_enter = []
    edges_exit = []
    edges_variation = []
    frame = 0

    # Kernel defines how thick the dilation is. e.g. (2,2), (4,4)
    kernel = np.ones((8, 8), np.uint8)

    # Calculate the histograms
    while True:
        (rv, im) = video.read()
        if not rv:
            break
        frame += 1
        if len(last_hist) == 0:
            # First frame
            last_bhist, _ = np.histogram(im[:, :, 0].flatten(), 16, (0, 255))
            last_ghist, _ = np.histogram(im[:, :, 1].flatten(), 16, (0, 255))
            last_rhist, _ = np.histogram(im[:, :, 2].flatten(), 16, (0, 255))
            last_hist = np.concatenate((last_bhist, last_ghist, last_rhist))

            im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            # Canny is the edge detection thing
            # 75 low threshold, 100 high threshold seems to work pretty well with L2 norm
            gray_mean = im_gray.mean()
            edges = cv2.Canny(im_gray, gray_mean * 0.5, gray_mean * 1, L2gradient=True)
            last_edges_img = edges
            # Make edges thicc
            dilated = cv2.dilate(edges, kernel, iterations=1)
            last_dilated_img = dilated
        else:
            # COLOUR DIFF
            bhist, _ = np.histogram(im[:, :, 0].flatten(), 16, (0, 255))
            ghist, _ = np.histogram(im[:, :, 1].flatten(), 16, (0, 255))
            rhist, _ = np.histogram(im[:, :, 2].flatten(), 16, (0, 255))
            hist = np.concatenate((bhist, ghist, rhist))
            difference = np.linalg.norm(last_hist - hist)
            if difference > COLOUR_DIFF_THRESHOLD:
                thresh_exceed.append(difference)
            else:
                thresh_exceed.append(None)

            colour_diff.append(difference)
            last_hist = hist

            # EDGES DIFF
            im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            gray_mean = im_gray.mean()
            edges = cv2.Canny(im_gray, gray_mean * 0.5, gray_mean * 1, L2gradient=True)
            dilated = cv2.dilate(edges, kernel, iterations=1)

            pin = 1 - np.sum(np.multiply(last_dilated_img.flatten() // 255, edges.flatten() // 255)) / np.sum(
                edges.flatten() // 255)
            pout = 1 - np.sum(np.multiply(last_edges_img.flatten() // 255, dilated.flatten() // 255)) / np.sum(
                last_edges_img.flatten() // 255)
            edges_enter.append(pin)
            edges_exit.append(pout)
            edges_variation.append(pin - pout)

            # Use the code below to print a certain frame in the vid
            if frame == 1442:
                plt.subplot(2, 3, 1), plt.imshow(last_edges_img, cmap='gray'), plt.imshow(last_dilated_img, cmap='gray', alpha=0.5)
                plt.title('Last_edges'), plt.xticks([]), plt.yticks([])
                plt.subplot(2, 3, 2), plt.imshow(edges, cmap='gray'), plt.imshow(dilated, cmap='gray', alpha=0.5)
                plt.title('Current_edges'), plt.xticks([]), plt.yticks([])
                plt.subplot(2, 3, 3), plt.imshow(last_edges_img - edges, cmap='gray', alpha = 0.5), plt.imshow(last_dilated_img - dilated, cmap='gray', alpha=0.5)
                plt.title('Difference'), plt.xticks([]), plt.yticks([])

            last_edges_img = edges
            last_dilated_img = dilated

    # Detect the scene changes
    is_scene_change = False
    start_change_frame = 0
    end_change_frame = 0
    previous_sign = 0

    edges_variation_diff = edges_variation

    for idx, diff in enumerate(colour_diff):
        is_scene_change_start = (abs(diff) > COLOUR_SCENE_CHANGE_THRESHOLD) \
                                and (not is_scene_change)
        is_scene_change_end = (abs(diff) < COLOUR_SCENE_CHANGE_THRESHOLD) \
                              and is_scene_change

        if is_scene_change_start:
            is_scene_change = True
            start_change_frame = idx
            previous_sign = np.sign(edges_variation_diff[idx])
            continue
        elif is_scene_change and (not is_scene_change_end):
            current_sign = np.sign(edges_variation_diff[idx])

            if current_sign != previous_sign and (abs(edges_variation_diff[idx]) > GRADIENT_SIGN_THRESHOLD):
                is_scene_change_end = True

        if is_scene_change_end:
            is_scene_change = False
            end_change_frame = idx

            scene_change_length = end_change_frame - start_change_frame
            if scene_change_length == 1:
                # -1 to count the first frame that's not differentiated
                print('CUT: ' + str(start_change_frame - 1))
            else:
                print('FADE: ' + str(start_change_frame - 1) + ' to '
                      + str(end_change_frame - 1))

    plt.subplot(2, 3, 4), plt.plot(edges_enter, 'g-', edges_exit, 'r-')
    plt.xlabel('Frame number')
    plt.ylabel('Edge Differences')
    plt.subplot(2, 3, 5), plt.plot(edges_variation_diff)
    plt.xlabel('Frame number')
    plt.ylabel('Edge Diff "Sum"')
    plt.subplot(2, 3, 6), plt.plot(colour_diff, 'b-', thresh_exceed, 'rx')
    plt.xlabel('Frame number')
    plt.ylabel('Colour Difference')
    plt.show()

    frame_count = video.get(cv2.CAP_PROP_POS_FRAMES)
    print("Read %d frames from video." % frame_count)
    video.release()


if __name__ == '__main__':
    main()
