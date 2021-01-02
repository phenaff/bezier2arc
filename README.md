# bezier2arc

A program for modifying an SVG file containing line segments and cubic 
Bezier curves. Each cubic Bezier curve is approximated by one arc.

This conversion is useful when dealing with CNC programs that cannot handle Bezier curves.

Warning: this is work in progress!

## Usage

```bash
# list all paths and segments in original file
python -m bezier2arc --list -i input.svg
# color the segments - useful for identifying errors in input file
python -m bezier2arc --color -i input.svg -o colored-input.svg
# convert to arcs
python -m bezier2arc --convert -i with-splines.svg -o with-arcs.svg
# ... verify result
python -m bezier2arc --list -i with-arcs.svg
```

