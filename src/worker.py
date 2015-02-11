#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# based on http://code.activestate.com/recipes/577120-julia-fractals/

import argparse
from PIL import Image
import random
import sys


class JuliaSet:

    def __init__(self, width, height, xa=-2.0, xb=2.0, ya=-1.5, yb=1.5,
                 iterations=255):
        self.xa = xa
        self.xb = xb
        self.ya = ya
        self.yb = yb
        self.iterations = iterations
        self.width = width
        self.height = height
        self.draw()

    def draw(self):
        self.image = Image.new("RGB", (self.width, self.height))
        c, z = self._set_point()
        for y in range(self.height):
            zy = y * (self.yb - self.ya) / (self.height - 1) + self.ya
            for x in range(self.width):
                zx = x * (self.xb - self.xa) / (self.width - 1) + self.xa
                z = zx + zy * 1j
                for i in range(self.iterations):
                    if abs(z) > 2.0:
                        break
                    z = z * z + c
                self.image.putpixel((x, y),
                                    (i % 8 * 32, i % 16 * 16, i % 32 * 8))

    def save(self, filename):
        self.image.save(filename, "PNG")

    def _set_point(self):
        random.seed()
        while True:
            cx = random.random() * (self.xb - self.xa) + self.xa
            cy = random.random() * (self.yb - self.ya) + self.ya
            c = cx + cy * 1j
            z = c
            for i in range(self.iterations):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            if i > 10 and i < 100:
                break

        return (c, z)


def parse_command_line_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", type=str, default="output.png",
                        help="Output filename.")
    parser.add_argument("--height", type=int, default=512,
                        help="The height of the generate image.")
    parser.add_argument("--width", type=int, default=512,
                        help="The width of the generated image.")
    parser.add_argument("--xa", type=float, default=-2.0,
                        help="Value for the parameter 'xa'.")
    parser.add_argument("--xb", type=float, default=2.0,
                        help="Value for the parameter 'xb'.")
    parser.add_argument("--ya", type=float, default=-1.5,
                        help="Value for the parameter 'ya'.")
    parser.add_argument("--yb", type=float, default=1.5,
                        help="Value for the parameter 'yb'.")
    parser.add_argument("--iterations", type=int, default=255,
                        help="The maximum number of iterations.")
    return parser.parse_args()


def main():
    args = parse_command_line_arguments()
    juliaset = JuliaSet(args.width, args.height, args.xa, args.xb,
                        args.ya, args.yb, args.iterations)
    juliaset.save(args.filename)
    return 0

if __name__ == '__main__':
    sys.exit(main())
