import cv2
import sys, glob, os
import tqdm
import subprocess
import time
import pathlib
import time

class Time:
    
    @staticmethod
    def to_seconds(h, m, s):
        return h * 3600 + m * 60 + s 
    
    # As 1st arguments it expectes the stirng HH:mm:ss
    def __init__(self, *args):
        self.seconds = 0

        if len(args) > 0:
            t = time.strptime(args[0], "%H:%M:%S")
            self.seconds = Time.to_seconds(t.tm_hour, t.tm_min, t.tm_sec)

    def increment(self, seconds):
        self.seconds = self.seconds + seconds

    def to_str(self):
        h = int(self.seconds / 60 / 60)
        m = int(self.seconds / 60) - h * 60
        s = self.seconds - h * 60 * 60 - m * 60

        return "{:02}:{:02}:{:02}".format(h, m, s)

class Width:
    # It expects formats "1 mm" or "50 um" or "
    def __init__(self, text):

        # Get the last 2 characters
        self.units = text[-2:]
        self.full_text = text

        # Convert to meters. The substring will be either "4.7" or
        # "4.7 ". It's ok for conversion to float
        val = float(text[:-2])
        if self.units == "mm":
            val = val * 10e-3
        elif self.units == "um":
            val = val * 10e-6
        elif self.units == "cm":
            val = val * 10e-2
        else:
            print("Unkown units: \"{}\".".format(text))
                
        self.width = val

    def text(self):
        return self.full_text

    def value(self):
        return self.width

    def __gt__(self, other):
        if (self.width > other.width):
            return True
        else:
            return False


def generate_img_to_video(folder : str,
                          observable_width : Width,
                          capture_interval_s : float,
                          video_time_s : float,
                          start_time : str,
                          scale_bar_width : Width,
                          check_if_stop_requested,
                          observer = None):
    
    assert observable_width > scale_bar_width
    
    print("Folder to process: {}.".format(folder))
    print("Observable width: {}.".format(observable_width.text))
    print("Scale bar width: {}.".format(scale_bar_width.text))
    print("Capture interval, s: {}.".format(capture_interval_s))
    print("Video time, s: {}.".format(video_time_s))

    # The folder should contain files of only one extension, but extensions
    # can be different.
    extensions = ('*.TIF', '*.tif', '*.JPG', '*.jpg', '*.JPEG', '*.jpeg')
    files = []
    for e in extensions:
        files.extend(glob.glob(folder + "/" + e))

    if len(files) == 0:
        print("No files found")
        observer.done()
        return

    files.sort()
    
    # Get image resolution
    img = cv2.imread((files[0]))
    height, width, layers = img.shape
    print("Image size: {}x{}.".format(width, height))
    
    # Calculate desired video resolution.
    dwidth = 1024
    scale_ration = dwidth / width
    dheight = int(height * scale_ration)

    # Calculate the width of a scale bar
    
    scale_bar_width_px = round((dwidth / observable_width.value()) *
                               scale_bar_width.value())
                  
    print("{} takes {} pixels.".format(scale_bar_width.text(),
                                       scale_bar_width_px))
          

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

    # Create a time stamp object which serves as a source for
    # time stamp text on the image
    time_stamp = Time(start_time)

    # Create tqdm bar (works in console)
    pbar = None
    if observer is None:
        pbar = tqdm.tqdm(total = len(files))

    # Compute FPS to correspond the requested video time
    fps = int(round(len(files) / video_time_s))
    fps = min(fps, 60)
    print("FPS: {}.".format(fps))
        
    # well as text positions
    p = pathlib.Path(folder)
    video_filename = str(p.with_suffix('.mp4'))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video=cv2.VideoWriter(video_filename,
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
        pt1 = (dwidth - scale_bar_width_px - h_margin,
               dheight - v_margin + scale_bar_height)
        pt2 = (pt1[0] + scale_bar_width_px,
               pt1[1] - scale_bar_height)
        # dwidth - h_margin, dheight - v_margin)
        img = cv2.rectangle(img, pt1, pt2, color, cv2.FILLED)

        # Draw the unit text below the bar
        text_size, _ = cv2.getTextSize(scale_bar_width.text(), font, fontscale * 0.5, 1)
        text_w, text_h = text_size

        org = (dwidth - int(scale_bar_width_px / 2) - int(text_w / 2) - h_margin,
               pt1[1] + scale_bar_height + text_h)
        
        img = cv2.putText(img, scale_bar_width.text(), org, font, fontscale * 0.5, color, 1, cv2.LINE_AA)

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

        if check_if_stop_requested():
            break

    video.release()

    end = time.time()
    print("Processing time: {}.".format(end-start))
    print("Video file: {}.".format(video_filename))
    
    # Notify it's done
    observer.done()

#if __name__ == '__main__':
#    path = sys.argv[1]
#    dwidth = float(sys.argv[2])
#    frame_interval = int(sys.argv[3])

#    sys.exit(generate_img_to_video(path, dwidth, frame_interval))
