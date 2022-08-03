import cv2
import sys, glob, os
import tqdm
import subprocess

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

def main(folder, los_width, frame_interval_s):
    print("Folder to process: {}.".format(folder))
    print("Width of the image, mm: {}.".format(los_width))
    print("Time interval: {} seconds".format(frame_interval_s))

    files = glob.glob(folder + '/*.JPG')
    files.sort()

    # Calculate the width of a scale bar
    img = cv2.imread((files[0]))
    height, width, layers = img.shape
    scale_bar_width = round(width / los_width) # num. of pixel that 1 mm takes
    print("Image size: {}x{}.".format(width, height))
    print("1 mm takes {} pixels.".format(scale_bar_width))

    # Margins for drawings
    h_margin = 20
    v_margin = 100
    scal_bar_heigh = 10

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 48
    thickness = 2
    font_scale = 1
    color = (255, 255, 255)
    color_bg = (0, 0, 0)

    # Create a temporal folder for modified images
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    time_stamp = Time()

    index = 0

    with tqdm.tqdm(total = len(files)) as pbar:
        for file_name in files:
            img = cv2.imread(file_name)

            # Draw the scale bar.
            # pt1 and pt2 can be calculated outside
            pt1 = (width - scale_bar_width - h_margin, height - v_margin + scal_bar_heigh)
            pt2 = (width - h_margin, height - v_margin)
            img = cv2.rectangle(img, pt1, pt2, color, cv2.FILLED)

            # Draw the unit text below the bar
            org = (width - int(scale_bar_width / 2) - h_margin, height - v_margin - scal_bar_heigh + font_size + 10)
            img = cv2.putText(img, '1 mm', org, font, font_scale, color, thickness, cv2.LINE_AA)

            # Draw the time
            org = (0 + h_margin, 0 + v_margin)
            x, y = org
            text_size, _ = cv2.getTextSize(time_stamp.to_str(), font, 2, thickness)
            text_w, text_h = text_size
            img = cv2.rectangle(img, org, (x + text_w, y -  text_h), color_bg, cv2.FILLED)
            img = cv2.putText(img, time_stamp.to_str(), org, font, 2, color, thickness, cv2.LINE_AA)

            cv2.imwrite("tmp/{}.JPG".format(index), img)
            index += 1

            time_stamp.increment(frame_interval_s)

            # Updated status bar
            pbar.update(1)
    
    # Run ffmpeg to generate video
    subprocess.call(['ffmpeg', '-r', '24', '-i', 'tmp/%d.JPG', 'out.mp4'])

    # Delete all images
    for file in glob.glob('tmp/*'):
        os.remove(file)
    os.rmdir('tmp')

if __name__ == '__main__':
    path = sys.argv[1]
    width = float(sys.argv[2])
    frame_interval = int(sys.argv[3])

    sys.exit(main(path, width, frame_interval))
