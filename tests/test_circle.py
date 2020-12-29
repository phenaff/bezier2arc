import pytest
import numpy as np
import bezier2arc as b2a


@pytest.fixture
def _points():
    p1 = np.complex(real=0, imag=0)
    p2 = np.complex(real=1, imag=1)
    p3 = np.complex(real=2, imag=0)
    return [p1, p2, p3]


def test_radius(_points):
    center, radius = b2a.circle_from_points(_points[0], _points[1], _points[2])
    assert radius == 1.0


def test_center(_points):
    center, radius = b2a.circle_from_points(_points[0], _points[1], _points[2])
    assert center == np.complex(1, 0)
