import cv2
import sys, glob, os
import tqdm
import subprocess
import time

class Time:
    def __init__(self):
        self.seconds = 0
    
    def increment(self, seconds):
        self.seconds = self.seconds + seconds

    def to_str(self):
        h = int(self.seconds / 60 / 60)
        m = int(self.seconds / 60) - h * 60
        s = self.seconds - h * 60 * 60 - m * 60

        return "{:02}:{:02}:{:02}".format(h, m, s)

def generate_img_to_video(folder, pixels_per_cm, capture_interval_s, video_time_s, observer = None):
    print("Folder to process: {}.".format(folder))
    print("Width of the image, mm: {}.".format(pixels_per_cm))
    print("Capture interval, s: {}.".format(capture_interval_s))
    print("Video time, s: {}.".format(video_time_s))

    files = glob.glob(folder + '/*.JPG')
    files.sort()
    
    # Get image resolution
    img = cv2.imread((files[0]))
    height, width, layers = img.shape
    print("Image size: {}x{}.".format(width, height))
    
    # Calculate desired video resolution.
    dwidth = 1024
    scale_ration = dwidth / width
    dheight = int(height * scale_ration)

    # TODO: Consider different length of scale bars    
    # Calculate the width of a scale bar
    scale_bar_width = round(dwidth / pixels_per_cm) # num. of pixel that 1 mm takes    
    print("1 mm takes {} pixels.".format(scale_bar_width))

    # Margins for drawings
    h_margin = 20
    v_margin = 50
    scale_bar_height = 2

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 10 # 48
    thickness = 1
    fontscale = 1
    color = (255, 255, 255)
    color_bg = (0, 0, 0)

    # Create a temporal folder for modified images
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    time_stamp = Time()

    pbar = None
    if observer is None:
        pbar = tqdm.tqdm(total = len(files))

    # Compute FPS to correspond the requested video time
    fps = int(len(files) / video_time_s)
    fps = min(fps, 60)
    print("FPS: {}.".format(fps))
        
    # well as text positions
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video=cv2.VideoWriter('video.mp4',
                          fourcc,
                          fps,
                          (dwidth, dheight))

    start = time.time()
    for file_name in files:
        print("Proccessing: {}.".format(file_name));
        
        img = cv2.imread(file_name)
        img = cv2.resize(img, (dwidth, dheight))

        # Draw the scale bar.
        # pt1 and pt2 can be calculated outside
        pt1 = (dwidth - scale_bar_width - h_margin,
               dheight - v_margin + scale_bar_height)
        pt2 = (pt1[0] + scale_bar_width,
               pt1[1] - scale_bar_height)
        # dwidth - h_margin, dheight - v_margin)
        img = cv2.rectangle(img, pt1, pt2, color, cv2.FILLED)

        # Draw the unit text below the bar
        text_size, _ = cv2.getTextSize('1 mm', font, fontscale * 0.5, 1)
        text_w, text_h = text_size

        org = (dwidth - int(scale_bar_width / 2) - int(text_w / 2) - h_margin,
               pt1[1] + scale_bar_height + text_h)
        
        img = cv2.putText(img, '1 mm', org, font, fontscale * 0.5, color, 1, cv2.LINE_AA)

        # Draw the time
        org = (0 + h_margin, 0 + v_margin)
        x, y = org
        text_size, _ = cv2.getTextSize(time_stamp.to_str(), font, fontscale, thickness)
        text_w, text_h = text_size
        img = cv2.rectangle(img, org, (x + text_w, y - text_h), color_bg, cv2.FILLED)
        img = cv2.putText(img, time_stamp.to_str(), org, font, fontscale, color, thickness, cv2.LINE_AA)

        video.write(img)

        time_stamp.increment(capture_interval_s)

        # Updated status bar
        if pbar is not None:
            pbar.update(1)

    video.release()

    end = time.time()
    print("Processing time: {}.".format(end-start))

    # Notify it's done
    observer.done()

if __name__ == '__main__':
    path = sys.argv[1]
    dwidth = float(sys.argv[2])
    frame_interval = int(sys.argv[3])

    sys.exit(generate_img_to_video(path, dwidth, frame_interval))
