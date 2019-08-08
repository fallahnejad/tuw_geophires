#!/usr/bin/env python
# -*- coding: utf-8 -*-

from create_template import template_generator

import sys
import os
import numpy as np

if __name__ == "__main__":
    if len(sys.argv) != 20:
        print("usage: %s <path> <param1> ... <param18>" % sys.argv[0])
        sys.exit(1)

    output_path = sys.argv[1]
    user_input_list = [int(x) for x in sys.argv[2:]]
    user_input = np.array(user_input_list)

    warehouse = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data_warehouse"
    )
    template_generator(warehouse, output_path, user_input)
