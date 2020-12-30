# Read svg file and convert splines to arcs

# Read SVG into a list of path objects and list of dictionaries of attributes
import sys
import argparse
import numpy as np
import svgpathtools as spt
import logging
import warnings

def get_parser():
    parser = argparse.ArgumentParser(description="Bezier curve to Arc converter")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--convert", action="store_true", default=False, dest="convert")
    group.add_argument("--list", action="store_true", default=False, dest="list")
    group.add_argument("--color", action="store_true", default=False, dest="color")

    parser.add_argument("-i", "--infile", action="store", dest="infile", help="input file")
    parser.add_argument("-o", "--outfile", action="store", dest="outfile", help="output file")
    parser.add_argument("-l", "--logfile", action="store", dest="logfile", default="log.txt", help="log file")
    parser.add_argument("-n", "--nb_arcs", action="store", dest="nb_arcs", help="number of arcs per segment")

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


def _bezier_to_arc(segment):
    p1 = segment.start
    p2 = segment.point(0.5)
    p3 = segment.end

    # if they are collinear, cannot fit circle, fit straight line instead
    # if p1, p2, p3 are collinear, then
    # (p1-p3)/(p3-p2) is real
    tol = 1.e-5
    _ratio = (p1-p3)/(p3-p2)
    if np.abs(np.imag(_ratio)) < tol:
        a = spt.Line(start=p1, end=p3)
    else:
        # magic to determine sweep
        v_mid = p2 - p1
        v_end = p3 - p1
        a_mid, a_end = np.angle([v_mid, v_end])
        b_sweep = a_mid < a_end

        center, radius = circle_from_points(p1, p2, p3)
        # rotation parameter does not matter for a circle
        a = spt.Arc(p1, radius=complex(radius, radius), rotation=0, large_arc=False, sweep=b_sweep, end=p3)
    return a


def convert_bezier_to_arcs(input_file, nb_arcs):

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
                    a = _bezier_to_arc(segment)
                except Warning:
                    logging.info("error in path {} segment {}".format(idx, jdx))
                    logging.info(segment)
                    raise
                new_path.append(a)
                logging.info("Found Bezier curve in Path {} segment {}".format(idx, jdx))
            else:
                logging.error("segment type {} is not supported".format(type(segment)))
                sys.exit()
        new_paths.append(new_path)

    return new_paths, svg_attributes

def list_paths(args):

    input_file = ""
    nb_arcs = 1

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
    pass


def convert_file(args):
    input_file = ""
    output_file = ""
    nb_arcs = 1

    input_file = args.infile
    output_file = args.outfile
    nb_arcs = args.nb_arcs

    if input_file == "" or output_file == "":
        logging.error("Input or output file names are missing")
        raise ValueError("Input and output files are needed")

    logging.info("input file {} output file {} nb arcs {}".format(input_file, output_file, nb_arcs))

    new_paths, svg_attributes = convert_bezier_to_arcs(input_file, nb_arcs)

    for idx, path in enumerate(new_paths):
        logging.info('=== new path {}'.format(idx))
        for jdx, segment in enumerate(path):
            logging.info("   === segment {}".format(jdx))
            logging.info(segment)

    spt.wsvg(new_paths, svg_attributes=svg_attributes, filename=output_file)

    logging.info("End")



