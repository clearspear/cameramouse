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
from PIL import Image
from gi.repository import Gst

Category = collections.namedtuple('Category', ['id', 'score'])

def clamp(v, l, r):
    return max(min(v, r), l)

# Draw stuff to the screen
def generate_svg(size, detection_results, classification_results):
    font_size = '20'
    red = svgwrite.rgb(255,0,0,'%')
    grey = svgwrite.rgb(15,15,15,'%')

    dwg = svgwrite.Drawing('', size=size)

    dwg.add(dwg.text("Boxes:", insert=(11, 21), fill='white', font_size=font_size))

    x = size[0]
    y = size[1]

    command = ""

    # Draw boxes and text for detection
    box_i = 0
    for box in detection_results:
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

            # Print out box center to stdout
            command += str(x_avg) + " " + str(y_avg)

        box_i += 1

    # Write classification results to screen and stdout
    classification_threshold = .7
    if classification_results[0] > classification_threshold:
        hand_pos = 'fist'
    elif classification_results[1] > classification_threshold:
        hand_pos = 'palm'
    else: 
        hand_pos = 'unknown'
    dwg.add(dwg.text("Hand position: " + hand_pos,
                     insert=(11, 20*(box_i+2)),
                     fill='white',
                     font_size=font_size))
    command += " " + hand_pos

    # Print command to stdout
    print(command)
    sys.stdout.flush()

    return dwg.tostring()

# Print detection output to stdout
def get_detection_output(interpreter):
    threshold = .6

    boxes = common.output_tensor(interpreter, 0)
    classes = common.output_tensor(interpreter, 1)
    scores = common.output_tensor(interpreter, 2)
    count = int(common.output_tensor(interpreter, 3))

    hand_detections = []
    for i in range(count):
        if scores[i] > threshold:
            hand_detections.append(boxes[i])
    #print(hand_detections)
    #sys.stdout.flush()

    return hand_detections

# Print classification output to stdout
def get_classification_output(interpreter):
    scores = common.output_tensor(interpreter, 0)
    #print(scores)
    #sys.stdout.flush()
    return scores

def main():

    # Flag to also show video 
    show_display = True

    # Model path parameter
    detection_model_path = '/home/mendel/handdetection_ssdmobilenetv1.tflite'
    classification_model_path = '/home/mendel/handclassification_mobilenet_v2_1.0_224_quant_edgetpu.tflite'

    #####

    print('Loading {} for hand detection.'.format(detection_model_path))
    detection_interpreter = common.make_interpreter(detection_model_path)
    detection_interpreter.allocate_tensors()
    
    print('Loading {} for hand classification.'.format(classification_model_path))
    classification_interpreter = common.make_interpreter(classification_model_path)
    classification_interpreter.allocate_tensors()

    w, h, _  = common.input_image_size(detection_interpreter)
    inference_size = (w, h)
    print("Inference size {},{}".format(w, h))

    # Average fps over last 30 frames.
    fps_counter = common.avg_fps_counter(30)

    def user_callback(input_tensor, src_size, inference_box):
      nonlocal fps_counter
      start_time = time.monotonic()

      # Run hand detection
      common.set_input(detection_interpreter, input_tensor)
      detection_interpreter.invoke()
      detection_results = get_detection_output(detection_interpreter)

      # Resize image and set as input
      buf = input_tensor
      _, map_info = buf.map(Gst.MapFlags.READ)
      np_input = np.ndarray(shape=(h,w,3),
                           dtype=np.uint8,
                           buffer=map_info.data)
      pil_input = Image.fromarray(np_input)
      pil_input = pil_input.resize((224,224), Image.NEAREST)
      np_input = np.asarray(pil_input)
      common.input_tensor(classification_interpreter)[:, :] = np_input

      # Run hand classification
      classification_interpreter.invoke()
      classification_results = get_classification_output(classification_interpreter)

      end_time = time.monotonic()
      
      if show_display:
          return generate_svg(src_size, detection_results, classification_results)
      return

    result = gstreamer.run_pipeline(user_callback,
                                    src_size=(640, 480),
                                    appsink_size=inference_size,
                                    show_display=show_display)

if __name__ == '__main__':
    main()
