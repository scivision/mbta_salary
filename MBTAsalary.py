#!/usr/bin/env python
"""
Example of using 2014 MBTA salary data extracted from PDF with pandas for quick analysis

First you must download http://www.mbta.com/uploadedfiles/Smart_Forms/News,_Events_and_Press_Releases/Wages2014.pdf
to this directory and run
pdftotext -layout Wages2014.pdf

there are more efficient ways to index, but this is a rather small dataset.

examples: see README

Michael Hirsch
"""
from argparse import ArgumentParser
import pandas as pd

try:
    from matplotlib.pyplot import show
except ImportError:
    show = None

import mbtasalary as ms


def main():

    p = ArgumentParser(description="MBTA salary data plotter/parser")
    p.add_argument('fn', help='type filename to analyze e.g. wages2014.txt')
    p.add_argument('year', help='type year of data [2013 2014] so we can pick the right parser', type=int, nargs='?', default=2014)
    p.add_argument('-l', '--lowerthreshold', help='[dollars] lower salary threshold', type=float, default=0)
    p = p.parse_args()

    stats, data = ms.parsefilt(p.fn, p.year, p.lowerthreshold)

    with pd.option_context('precision', 0):
        print(stats)

    if show is not None:
        show()


if __name__ == '__main__':
    main()
