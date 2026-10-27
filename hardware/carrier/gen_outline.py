#!/usr/bin/env python3
"""Write outline.dxf: the carrier board outline for v1 (mm, origin at the bottom-left corner).
100 x 80 mm rectangle, 1.6 mm FR-4; four M3 mounting holes (3.2 mm drill) 3.5 mm in from each corner.
The ESP32 antenna keep-out (overhang or slot at one short edge) is left to the layout designer: CARRIER.md."""
import ezdxf, os
W, H, INSET, DRILL = 100.0, 80.0, 3.5, 3.2
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.MM
doc.layers.add("OUTLINE", color=7); doc.layers.add("HOLES", color=1); doc.layers.add("NOTES", color=3)
msp = doc.modelspace()
msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={"layer": "OUTLINE"})
for x in (INSET, W - INSET):
    for y in (INSET, H - INSET):
        msp.add_circle((x, y), DRILL / 2, dxfattribs={"layer": "HOLES"})
msp.add_text("PVA carrier v1 outline: 100 x 80 mm, 1.6 mm FR-4, 4 x M3 (3.2 mm) 3.5 mm from corners",
             dxfattribs={"layer": "NOTES", "height": 2.0}).set_placement((0, -6))
doc.saveas(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outline.dxf"))
print("outline.dxf written")
