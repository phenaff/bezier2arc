import pytest
import getopt
import numpy as np
import bezier2arc as b2a

def test_convert_file():
    input_file = "../data/table-1-spline.svg"
    nb_arcs = 1
    new_paths, svg_attributes = b2a.convert_bezier_to_arcs(input_file, nb_arcs)

    for idx, path in enumerate(new_paths):
        print('=== new path {}'.format(idx))
        for jdx, segment in enumerate(path):
            print("   === segment {}".format(jdx))
            print(segment)

    assert True

def test_convert_1():
    args = ['-i', '../data/table-1-spline.svg', '-o', '../data/test_1.svg']
    b2a.convert_file(args)
    assert True

def test_convert_2():
    args = ['--convert', '-i', '../data/table-1-spline.svg', '-o', '../data/test_1.svg']
    b2a.main(args)

def test_getopt():
    print(getopt.getopt(["--list", '-i', '-o'], 'l', ['list'] ))
    assert True