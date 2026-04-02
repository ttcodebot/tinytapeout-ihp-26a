#!/usr/bin/env python3
"""Collect Magic's generate_fill.py output into a single GDS.

Magic's -dist mode produces multiple tt_ihp_wrapper_fill_pattern_X_Y.gds files.
Non-dist mode produces a single tt_ihp_wrapper_fill_pattern.gds.gz.
This script finds all fill pattern files and merges them into one GDS.
"""
import glob
import gzip
import os
import sys

import gdstk


def main(fill_dir, output_gds):
    # Find fill pattern files (dist mode: multiple .gds, non-dist: single .gds.gz)
    patterns = sorted(glob.glob(os.path.join(fill_dir, '*_fill_pattern*.gds')))
    patterns_gz = sorted(glob.glob(os.path.join(fill_dir, '*_fill_pattern*.gds.gz')))

    if not patterns and not patterns_gz:
        print(f"ERROR: No fill pattern files found in {fill_dir}")
        sys.exit(1)

    lib = gdstk.Library()
    top = lib.new_cell('tt_ihp_wrapper_fill')

    for gds_path in patterns:
        print(f"  Loading {os.path.basename(gds_path)}")
        fill_lib = gdstk.read_gds(gds_path)
        for cell in fill_lib.top_level():
            top.add(gdstk.Reference(cell))
            lib.add(cell, *cell.dependencies(True))

    for gz_path in patterns_gz:
        # Decompress and load
        gds_path = gz_path[:-3]
        print(f"  Decompressing {os.path.basename(gz_path)}")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(gds_path, 'wb') as f_out:
                f_out.write(f_in.read())
        fill_lib = gdstk.read_gds(gds_path)
        for cell in fill_lib.top_level():
            top.add(gdstk.Reference(cell))
            lib.add(cell, *cell.dependencies(True))

    print(f"  Writing {output_gds} ({len(top.references)} fill references)")
    lib.write_gds(output_gds)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <fill_dir> <output.gds>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
