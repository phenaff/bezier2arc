# Read svg file and convert splines to arcs

# Read SVG into a list of path objects and list of dictionaries of attributes
import sys
import os
import argparse
import numpy as np
import svgpathtools as spt
import logging
import warnings
import ezdxf
from ezdxf import units
import cmath
from scipy.optimize import fminbound


def get_parser():
    parser = argparse.ArgumentParser(description="Bezier curve to Arc converter")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--convert", action="store_true", default=False, dest="convert")
    group.add_argument("--list", action="store_true", default=False, dest="list")
    group.add_argument("--color", action="store_true", default=False, dest="color")

    parser.add_argument("-i", "--infile", action="store", dest="infile", help="input file")
    parser.add_argument("-o", "--outfile", action="store", dest="outfile", help="output file")
    parser.add_argument("-l", "--logfile", action="store", dest="logfile", default="log.txt", help="log file")
    parser.add_argument("-r", "--min_radius", action="store", dest="min_radius", type=float, help="minimum arc radius", default=50)
    parser.add_argument("-d", "--max_dist", action="store", dest="max_dist", type=float, help="max distance from arc to spline", default=2)

    return parser


def circle_from_points(p1, p2, p3):
    """"
    Given three points in the complex plane, find center and radius of circle through these three points
    Source:
    https: //math.stackexchange.com/questions/1141830/
    how-to-find-the-center-of-the-circle-that-contains-three-given-complex-numbers
    """

    # center is intersection of bisectors of segments p1-p2 and p2-p3

    s = np.real((p3-p1)*np.conj(p3-p2)) / np.imag((p3-p1)*np.conj(p3-p2))
    center = (p1+p2)/2 + np.complex(0, s)*(p1-p2)/2
    radius = abs(p1-center)

    return center, radius


def c2t(c):
    return c.real, c.imag


def max_distance(cb_segment, arc):

    path1 = cb_segment
    path2 = arc

    def dist(t):
        return -path1.radialrange(path2.point(t))[0][0]
    t2 = fminbound(dist, 0, 1)

    pt2 = path2.point(t2)
    d = path1.radialrange(pt2)[0][0]

    return d


def fit_arc(cb, t_start, t_end, tol_dist, min_radius):
    t_arc = (t_end - t_start) * 2
    max_dist = np.inf
    a = None
    print(cb)
    while max_dist > tol_dist:
        t_arc = t_arc / 2
        p1 = cb.point(t_start)
        p3 = cb.point(t_start + t_arc)
        p2 = cb.point(t_start + t_arc / 2)

        center, radius = circle_from_points(p1, p2, p3)
        print("t_start: {} t_arc: {} radius: {}".format(t_start, t_arc, radius))
        if radius < min_radius:
            t_arc *= 2
            break
        v_start = p1-center
        v_end = p3-center
        is_ccw = np.diff(np.angle([v_start, v_end]))[0] > 0
        a = spt.Arc(p1, radius=complex(radius, radius), rotation=0, large_arc=False, sweep=is_ccw, end=p3)

        max_dist = max_distance(cb, a)

    if a is None:
        raise ValueError("Arc radius less than min radius")

    return a, t_arc


def _bezier_to_dxf_arc(segment):
    p1 = segment.start
    p2 = segment.point(0.5)
    p3 = segment.end

    tol = 1.e-5
    _ratio = (p1-p3)/(p3-p2)
    if np.abs(np.imag(_ratio)) < tol:
        a = ezdxf.math.ConstructionLine(c2t(p1), c2t(p3))
    else:
        # magic to determine sweep
        v_mid = p2 - p1
        v_end = p3 - p1
        a_mid, a_end = np.angle([v_mid, v_end])
        b_sweep = a_mid < a_end

        center, radius = circle_from_points(p1, p2, p3)
        # rotation parameter does not matter for a circle
        a = ezdxf.math.ConstructionArc(center=c2t(center), radius=radius, start_angle=cmath.phase(p1-center),
                                       end_angle=cmath.phase(p3-center), is_counter_clockwise=b_sweep)

    return a


def _bezier_to_svg_arc(segment, max_dist, min_radius):
    p1 = segment.start
    p2 = segment.point(0.5)
    p3 = segment.end

    p = []
    # if p1, p2, p3 are collinear, then
    # (p1-p3)/(p3-p2) is real
    tol = 1.e-5
    _ratio = (p1-p3)/(p3-p2)
    if np.abs(np.imag(_ratio)) < tol:
        a = spt.Line(start=p1, end=p3)
        p.append(a)
    else:
        t_start = 0
        t_end = 1
        while t_start < t_end:
            a, t_arc = fit_arc(segment, t_start, t_end, max_dist, min_radius)
            p.append(a)
            t_start += t_arc
    return p


def convert_to_dxf(input_file):
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    msp = doc.modelspace()

    paths, attributes, svg_attributes = spt.svg2paths2(input_file)

    for idx, path in enumerate(paths):
        logging.info('=== path {}'.format(idx))
        logging.info(path)
        for jdx, segment in enumerate(path):
            logging.info("   === segment {}".format(jdx))
            logging.info(segment)
            if isinstance(segment, spt.Line):
                # export as is
                msp.add_line(c2t(segment.start), c2t(segment.end))
                logging.info("Found line in Path {} segment {}".format(idx, jdx))
            elif isinstance(segment, spt.CubicBezier):
                try:
                    a = _bezier_to_dxf_arc(segment)
                except Warning:
                    logging.info("error in path {} segment {}".format(idx, jdx))
                    logging.info(segment)
                    raise
                if isinstance(a, ezdxf.math.ConstructionLine):
                    msp.add_line(a.start, a.end)
                elif isinstance(a, ezdxf.math.ConstructionArc):
                    msp.add_arc(center=a.center, radius=a.radius, start_angle=a.start_angle, end_angle=a.end_angle)
                    logging.info("Found Bezier curve in Path {} segment {}".format(idx, jdx))
                else:
                    logging.error("segment type {} is not supported".format(type(segment)))
            else:
                logging.error("segment type {} is not supported".format(type(segment)))

    return doc


def convert_to_svg(input_file, max_dist, min_radius):

    # to handle numpy warnings as errors
    warnings.filterwarnings("error")
    paths, attributes, svg_attributes = spt.svg2paths2(input_file)

    new_paths = []
    for idx, path in enumerate(paths):
        logging.info('=== path {}'.format(idx))
        new_path = spt.Path()
        logging.info(path)
        for jdx, segment in enumerate(path):
            logging.info("   === segment {}".format(jdx))
            logging.info(segment)
            if isinstance(segment, spt.Line):
                # export as is
                new_path.append(segment)
                logging.info("Found line in Path {} segment {}".format(idx, jdx))
            elif isinstance(segment, spt.CubicBezier):
                # approximate cubic Bezier by NB_ARCS
                try:
                    a = _bezier_to_svg_arc(segment, max_dist, min_radius)
                except Warning:
                    logging.info("error in path {} segment {}".format(idx, jdx))
                    logging.info(segment)
                    raise
                new_path  += a
                logging.info("Found Bezier curve in Path {} segment {}".format(idx, jdx))
            else:
                logging.error("segment type {} is not supported".format(type(segment)))
                sys.exit()
        new_paths.append(new_path)

    return new_paths, svg_attributes


def list_paths(args):

    input_file = args.infile

    if input_file == "":
        logging.error("Input file name is missing")
        raise ValueError("Input file are needed")

    logging.info("input file {}".format(input_file))

    paths, attributes, svg_attributes = spt.svg2paths2(input_file)

    for idx, path in enumerate(paths):
        print('=== new path {}'.format(idx))
        for jdx, segment in enumerate(path):
            print("   === segment {}".format(jdx))
            print(segment)

    logging.info("End")


def colorize(args):
    input_file = args.infile
    output_file = args.outfile

    if input_file == "" or output_file == "":
        logging.error("Input or output file names are missing")
        raise ValueError("Input and output files are needed")

    logging.info("input file {} output file {}".format(input_file, output_file))

    paths, attributes, svg_attributes = spt.svg2paths2(input_file)

    # each segment must be a path in order to assign a color

    new_paths = []
    for path in paths:
        for segment in path:
            new_paths.append(spt.Path(segment))

    nb_segments = len(new_paths)
    col = ['r', 'g', 'b', 'k']
    segment_col = ''.join([col[i % len(col)] for i in range(nb_segments)])

    spt.wsvg(new_paths, colors=segment_col, stroke_widths=[2] * nb_segments, filename=output_file)


def convert_file(args):
    print(args)
    input_file = args.infile
    output_file = args.outfile
    min_radius = args.min_radius
    max_dist = args.max_dist

    if input_file == "" or output_file == "":
        logging.error("Input or output file names are missing")
        raise ValueError("Input and output files are needed")

    logging.info("input file {} output file {} min radius {}".format(input_file, output_file, min_radius))

    file_name, file_extension = os.path.splitext(output_file)
    if file_extension == '.svg':
        new_paths, svg_attributes = convert_to_svg(input_file, max_dist, min_radius)

        for idx, path in enumerate(new_paths):
            logging.info('=== new path {}'.format(idx))
            for jdx, segment in enumerate(path):
                logging.info("   === segment {}".format(jdx))
                logging.info(segment)
        spt.wsvg(new_paths, svg_attributes=svg_attributes, filename=output_file)
    elif file_extension == '.dxf':
        raise ValueError("convert to dxf not yet implemented.")
        # doc = convert_to_dxf(input_file, max_dist, min_radius)
        # doc.saveas(output_file)
    logging.info("End")
