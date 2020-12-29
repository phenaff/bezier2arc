# bezier2arc

A program to modify an SVG file containing line segments and cubic Bezier curves.
Each cubic Bezier curve is approximated by one or several Arcs.

This conversion is useful when dealing with CNC programs that cannot handle Bezier curves.

## Usage

```bash
$ bezier2arc -i <input file> -o <output file> -n <number of arcs>

```

