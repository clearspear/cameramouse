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

"""A demo which runs object classification on camera frames.

Run default object detection:
python3 classify.py

Choose different camera and input encoding
python3 classify.py --videosrc /dev/video1 --videofmt jpeg
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
from gi.repository import Gst
import matplotlib.image

Category = collections.namedtuple('Category', ['id', 'score'])

def load_labels(path):
    print(path)
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def generate_svg(size, text_lines):
    dwg = svgwrite.Drawing('', size=size)
    for y, line in enumerate(text_lines, start=1):
      dwg.add(dwg.text(line, insert=(11, y*20+1), fill='black', font_size='20'))
      dwg.add(dwg.text(line, insert=(10, y*20), fill='white', font_size='20'))
    return dwg.tostring()

def get_output(interpreter):
    """Returns no more than top_k categories with score >= score_threshold."""
    top_k = 3
    score_threshold = 0.1

    scores = common.output_tensor(interpreter, 0)
    categories = [
        Category(i, scores[i])
        for i in np.argpartition(scores, -top_k)[-top_k:]
        if scores[i] >= score_threshold
    ]
    return sorted(categories, key=operator.itemgetter(1), reverse=True)

def main():
    model_path = '/home/mendel/all_models/mobilenet_v2_1.0_224_quant_edgetpu.tflite'
    labels_path = '/home/mendel/all_models/imagenet_labels.txt'

    print('Loading {} with {} labels.'.format(model_path, labels_path))
    interpreter = common.make_interpreter(model_path)
    interpreter.allocate_tensors()
    labels = load_labels(labels_path)

    w, h, _  = common.input_image_size(interpreter)
    inference_size = (w, h)
    # Average fps over last 30 frames.
    fps_counter = common.avg_fps_counter(30)

    def user_callback(input_tensor, src_size, inference_box):
      print(input_tensor)
      print(src_size)
      print(inference_box)

      buffer = input_tensor
      success, map_info = buffer.map(Gst.MapFlags.READ)
      if not success:
          raise RuntimeError("Could not map Buffer data!")

      nparray = np.ndarray(
              shape=(h, w, 3),
              dtype=np.uint8,
              buffer=map_info.data)
      nparray = nparray[28:-28,:,:] # Trim black from top and bottom
      print(nparray.shape)
      # nparray contains the image now...

    
      output_details = interpreter.get_output_details()
      print(output_details)


      nonlocal fps_counter
      start_time = time.monotonic()
      common.set_input(interpreter, input_tensor)
      interpreter.invoke()
      # For larger input image sizes, use the edgetpu.classification.engine for better performance
      results = get_output(interpreter)
      end_time = time.monotonic()
      text_lines = [
          ' ',
          'Inference: {:.2f} ms'.format((end_time - start_time) * 1000),
          'FPS: {} fps'.format(round(next(fps_counter))),
      ]
      for result in results:
          text_lines.append('score={:.2f}: {}'.format(result.score, labels.get(result.id, result.id)))
      print(' '.join(text_lines))
      return #generate_svg(src_size, text_lines)

    result = gstreamer.run_pipeline(user_callback,
                                    src_size=(640, 480),
                                    appsink_size=inference_size)

if __name__ == '__main__':
    main()
