from setuptools import setup
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, 'bezier2arc', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='bezier2arc',
    version=version['__version__'],
    description=('Convert Bezier curves to arcs in an SVG file.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Patrick Hénaff',
    author_email='pa.henaff@gmail.com',
    url='https://github.com/phenaff/bezier2arc',
    license='MIT',
    install_requires=['numpy', 'svgpathtools'],
    requires=['numpy','svgpathtools'],
    packages=['bezier2arc'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8'],
    )
