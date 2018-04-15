import cv2
import numpy as np
import matplotlib.pyplot as plt

COLOUR_DIFF_THRESHOLD = 8000
GRADIENT_SCENE_CHANGE_THRESHOLD = 1050
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
    last_edges = []
    edges_diff = []
    frame = 0

    # Kernel defines how thick the dilation is. e.g. (2,2), (4,4)
    kernel = np.ones((2,2),np.uint8)

    # Calculate the histograms
    while True:
        (rv, im) = video.read()
        if not rv:
            break
        frame += 1
        if len(last_hist) == 0 :
            # First frame
            last_bhist, _ = np.histogram(im[:, :, 0].flatten(), 16, (0, 255))
            last_ghist, _ = np.histogram(im[:, :, 1].flatten(), 16, (0, 255))
            last_rhist, _ = np.histogram(im[:, :, 2].flatten(), 16, (0, 255))
            last_hist = np.concatenate((last_bhist, last_ghist, last_rhist))

            im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            # Canny is the edge detection thing
            # I have no idea what the other arguments are but it seems to work
            # TODO: Figure out what the arguments are
            edges = cv2.Canny(im_gray, 100, 200)
            # Make edges thicc
            dilated = cv2.dilate(edges, kernel, iterations=1)
            last_edges_img = dilated
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
            edges = cv2.Canny(im_gray, 100, 200)
            dilated = cv2.dilate(edges, kernel, iterations=1)

            # Add one to all values in the previous image because we
            # don't want to get negative values in the difference image.
            one = np.ones((last_edges_img.shape[0],last_edges_img.shape[1]),np.uint8)

            # Divide the images by 255 so that white is represented by 1
            edges_diff_img = (last_edges_img/255) + one - dilated/255

            edges_diff_values, _ = np.histogram(edges_diff_img.flatten(), 3, (0, 2))

            # Add the number of 0s and 2s because those are the pixels
            # that were different
            sum_differences = edges_diff_values[0] + edges_diff_values[2]
            edges_diff.append(sum_differences)

            # Use the code below to print a certain frame in the vid
            if frame == 228:
                plt.subplot(2,3,1),plt.imshow(last_edges,cmap = 'gray')
                plt.title('Last_edges'), plt.xticks([]), plt.yticks([])
                plt.subplot(2,3,2),plt.imshow(dilated,cmap = 'gray')
                plt.title('Current_edges'), plt.xticks([]), plt.yticks([])
                plt.subplot(2,3,3),plt.imshow(last_edges - dilated, cmap = 'gray')
                plt.title('Difference'), plt.xticks([]), plt.yticks([])

            last_edges = dilated

    # Colour changes - Detect the scene changes
    is_scene_change = False
    start_change_frame = 0
    end_change_frame = 0
    for idx, diff in enumerate(colour_diff, start=1):
        is_scene_change_start = (abs(diff) > COLOUR_SCENE_CHANGE_THRESHOLD) \
                                    and (not is_scene_change)
        is_scene_change_end = (abs(diff) < COLOUR_SCENE_CHANGE_THRESHOLD) \
                                and is_scene_change

        if is_scene_change_start:
            is_scene_change = True
            start_change_frame = idx
        if is_scene_change_end:
            is_scene_change = False
            end_change_frame = idx

            scene_change_length = end_change_frame - start_change_frame
            if scene_change_length == 1:
                print('CUT: ' + str(start_change_frame))
            else:
                print('FADE: ' + str(start_change_frame) + ' to '
                        + str(end_change_frame))

    edges_diff_derivative = np.gradient(edges_diff)
    # Edge changes - Detect the scene changes
    for idx, diff in enumerate(edges_diff_derivative, start=1):
        if idx == 1:
            # The start of the video will produce a spike on the graph
            # because the histogram is initialized with black
            continue

        is_scene_change = False
        is_scene_change_start = abs(diff) > GRADIENT_SCENE_CHANGE_THRESHOLD \
                                    and not is_scene_change
        is_scene_change_end = abs(diff) < GRADIENT_SCENE_CHANGE_THRESHOLD \
                                and is_scene_change

        if is_scene_change_start:
            is_scene_change = True
        if is_scene_change:
            print('EDGE: ' + str(idx) + ' ' + str(diff))
        if is_scene_change_end:
            is_scene_change = False

    plt.subplot(2,3,4), plt.plot(edges_diff)
    plt.xlabel('Frame number')
    plt.ylabel('Edge Differences')
    plt.subplot(2,3,5), plt.plot(edges_diff_derivative)
    plt.xlabel('Frame number')
    plt.ylabel('Edge Diff Derivative')
    plt.subplot(2,3,6), plt.plot(colour_diff, 'b-', thresh_exceed, 'rx')
    plt.xlabel('Frame number')
    plt.ylabel('Colour Difference')
    plt.show()

    frame_count = video.get(cv2.CAP_PROP_POS_FRAMES)
    print("Read %d frames from video." % frame_count)
    video.release()


if __name__ == '__main__' :
    main()
