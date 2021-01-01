import pytest
import numpy as np
import bezier2arc as b2a
import svgpathtools as spt

def test_convert_file():
    input_file = "../data/gabarit-table-1.svg"
    nb_arcs = 1
    new_paths, svg_attributes = b2a.convert_bezier_to_arcs(input_file, nb_arcs)

    for idx, path in enumerate(new_paths):
        print('=== new path {}'.format(idx))
        for jdx, segment in enumerate(path):
            print("   === segment {}".format(jdx))
            print(segment)

    assert True

def test_convert_svg():
    parser = b2a.get_parser()
    args = parser.parse_args(['-i', '../data/table-1-spline.svg', '-o', '../data/test_1.svg'])
    b2a.convert_file(args)
    assert True

def test_convert_dxf():
    parser = b2a.get_parser()
    args = parser.parse_args(['-i', '../data/table-1-spline.svg', '-o', '../data/test_1.dxf'])
    b2a.convert_file(args)
    assert True

def test_list_1():
    parser = b2a.get_parser()
    args = parser.parse_args(['-i', '../data/gabarit-table-1.svg'])
    b2a.list_paths(args)
    assert True

def test_colorize():
    parser = b2a.get_parser()
    args = parser.parse_args(['-i', '../data/table-1-spline.svg', "-o", "../data/table-1-spline-colors.svg"])
    b2a.colorize(args)
    assert True
