#!/usr/bin/env python
# -*- coding: utf-8 -*-

from run import call_tuw_geophires
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s <output_path> <uploaded_json_file>" % sys.argv[0])
        sys.exit(1)

    output_path = sys.argv[1]
    uploaded_json_file = sys.argv[2]
    call_tuw_geophires(output_path, uploaded_json_file)
