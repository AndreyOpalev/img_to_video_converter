# Script to convert microscope images to a video file

It also adds:
   1. A scale bar (of 1 mm)
   2. A time stamp (real time of measumrenets)

## Prerequisites:

  1. python 3.7+
  2. opencv2
  3. ffmpeg (as a installed utility)

## Usage

To run a script on a folder with images:

    python img_to_video.py path/to/image_folder real_captured_width_mm time_interval_s

Example

    python img_to_video.py ./30_min 4.7 10

The script would generate video vased on a images stored in the local folder '30_min'. The
scale bar is to be computed considering the full image covers 4.7 mm of real surface. And
the time stamp would be incremented by 10 seconds for every frame (of the video).

## Known problems

The script is pretty simple and the core work is done by the 'ffmpeg' utility which generates
a video file based on images. The python code only adds to every image correct time stamp
text and a scale bar before runnig ffmpeg utility.
Note that this approach uses disk memory, since it creates copies of every image, but then it
deletes them.