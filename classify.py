# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified by Sicheng Zeng

"""A demo which runs a tflite model on camera frames.
python3 classify.py
"""

import argparse
import collections
import common
import gstreamer
import numpy as np
import operator
import os
import re
import svgwrite
import time
import sys

Category = collections.namedtuple('Category', ['id', 'score'])

def clamp(v, l, r):
    return max(min(v, r), l)

# Draw stuff to the screen
def generate_svg(size, text_lines):
    font_size = '20'
    red = svgwrite.rgb(255,0,0,'%')
    grey = svgwrite.rgb(15,15,15,'%')

    dwg = svgwrite.Drawing('', size=size)

    dwg.add(dwg.text("Boxes:", insert=(11, 21), fill='white', font_size=font_size))

    x = size[0]
    y = size[1]

    # Draw boxes and text
    box_i = 0
    for box in text_lines:
        top = clamp(int(box[0] * x), 0, x)
        left = clamp(int(box[1] * y), 0, y)
        bottom = clamp(int(box[2] * x), 0, x)
        right = clamp(int(box[3] * y), 0, y)

        # Write text
        dwg.add(dwg.text(((top, left), (bottom, right)), 
                         insert=(11, 20*(box_i+2) + 1), 
                         fill='white', 
                         font_size=font_size))

        # Draw box
        if box_i == 0:
            color=red
        else:
            color=grey
        dwg.add(dwg.rect((left, top), (right-left, bottom-top),
                         stroke=color,
                         fill='none'))

        # Draw circle
        if box_i == 0:
            x_avg = int((left + right)/2)
            y_avg = int((top + bottom)/2)
            dwg.add(dwg.circle(center=(x_avg, y_avg),
                               r=10,
                               stroke=red,
                               fill='red'))

        box_i += 1

    return dwg.tostring()

# Print output to stdout
def get_output(interpreter):
    threshold = .6

    boxes = common.output_tensor(interpreter, 0)
    classes = common.output_tensor(interpreter, 1)
    scores = common.output_tensor(interpreter, 2)
    count = int(common.output_tensor(interpreter, 3))

    hand_detections = []
    for i in range(count):
        if scores[i] > threshold:
            hand_detections.append(boxes[i])
    print(hand_detections)
    sys.stdout.flush()

    return hand_detections

def main():

    # Flag to also show video 
    show_display = True

    # Model path parameter
    model_path = '/home/mendel/handdetection_ssdmobilenetv1.tflite'

    #####

    print('Loading {} with {} labels.'.format(model_path, ""))
    interpreter = common.make_interpreter(model_path)
    interpreter.allocate_tensors()

    w, h, _  = common.input_image_size(interpreter)
    inference_size = (w, h)
    # Average fps over last 30 frames.
    fps_counter = common.avg_fps_counter(30)

    print(inference_size)

    def user_callback(input_tensor, src_size, inference_box):

      nonlocal fps_counter
      start_time = time.monotonic()
      common.set_input(interpreter, input_tensor)
      interpreter.invoke()
      # For larger input image sizes, use the edgetpu.classification.engine for better performance
      results = get_output(interpreter)
      end_time = time.monotonic()

      if show_display:
          return generate_svg(src_size, results)
      return

    result = gstreamer.run_pipeline(user_callback,
                                    src_size=(640, 480),
                                    appsink_size=inference_size,
                                    show_display=show_display)

if __name__ == '__main__':
    main()
