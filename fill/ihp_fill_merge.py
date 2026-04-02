#!/usr/bin/env python3
"""Replace KLayout small M2/M3 fill with Magic M2/M3 fill (flattened)."""
import sys
import gdstk

REMOVE_CELLS = {
    'Met2_S_FILL_CELL',
    'Met2_XS_FILL_CELL',
    'Met2_M_FILL_CELL',
    'Met3_S_FILL_CELL',
    'Met3_M_FILL_CELL',
}

MAGIC_KEEP_LAYERS = {(10, 22), (30, 22)}


def main(argv0, klayout_gds, magic_gds, output_gds):
    lib = gdstk.read_gds(klayout_gds)
    top = lib.top_level()[0]
    print(f"Design: {len(top.polygons)} polys, {len(top.references)} refs")

    # Remove KLayout small M2/M3 fill refs
    to_remove = [r for r in top.references if r.cell_name in REMOVE_CELLS]
    for r in to_remove:
        top.remove(r)
    # Remove orphaned cell definitions
    for cname in REMOVE_CELLS:
        try:
            lib.remove(lib[cname])
        except (KeyError, ValueError):
            pass
    print(f"Removed {len(to_remove)} KLayout M2/M3 fill refs")

    # Load Magic fill and flatten M2/M3 into top cell
    flib = gdstk.read_gds(magic_gds)
    ftop = flib.top_level()[0]
    
    added = 0
    for poly in ftop.get_polygons(depth=-1):
        if (poly.layer, poly.datatype) in MAGIC_KEEP_LAYERS:
            top.add(poly)
            added += 1
    print(f"Added {added} Magic M2/M3 fill polygons (flattened)")

    # Remove Magic wrapper cells to avoid multiple topcells
    for cell in list(flib.cells):
        if cell.name in {c.name for c in lib.cells}:
            continue
        # Don't add any magic cells to lib - we flattened everything

    lib.write_gds(output_gds)
    print(f"Output: {output_gds} ({len(top.polygons)} polys, {len(top.references)} refs)")


if __name__ == '__main__':
    main(*sys.argv)
