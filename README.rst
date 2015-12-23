====================
MBTA Salary Analysis
====================

An example of extracting text tables from PDF, then loading with Pandas to look
for interesting aspects of the data.

For example, in 2014, the top MBTA earner was a Technician with an estimated $145 K of overtime on top of an $89 K salary.
Excessive overtime can be a concern for worker performance and safety in any field, with possible drastic consequences
for the public when working in sensitive areas like transportation and medicine.

The `Washingtonian published a 9 Dec 2015 article <http://www.washingtonian.com/blogs/capitalcomment/transportation/why-does-metro-suck-dangerous-accidents-escalator-outages.php>`_ 
by Luke Mullins and Michael Gaynor that explores at length issues with WMATA and 
overtime abuses.

.. contents::

.. image:: plots/2015hist.png
    :alt: MBTA salary histogram by category

.. image:: plots/2015cat.png
    :alt: MBTA salary by category


Examples of MBTA Salary Plots and Statistics
============================================
We currently have 2013-2015 salary data. Other trend analyses may find it useful to request prior years data.

2015 MBTA Salary
----------------
::

    python salary.py EMP-2015-Gross-Bpay-Ovt.xlsx 2015

2014 MBTA Salary
----------------
::
    
    python salary.py Wages2014.txt 2014

yields the output:

Highest earning MBTA staff $235194 in 2014 was a Technician,Power Equip.

======  ======  ======  ======  ======  ====
type       max  median    90th  subtot   num
======  ======  ======  ======  ======  ====
signal  179689  110775  127210   2e+07   155
police  221910  107261  165080   3e+07   259
maint   235194   95772  131344   2e+08  1727
ops     138506   93504  115208   1e+07   131
heavy   224458   90492  120647   6e+07   670
bus-ft  196809   88447  109504   1e+08  1337
subway  185242   84203  111710   4e+07   576
bus-pt   66435   33326   52231   1e+07   345
rest    220000   86463  129061   1e+08  1132
all     235194   89251  123618   5e+08  6332
======  ======  ======  ======  ======  ====

MBTA 2013 Salary
----------------
::
    
    python salary.py "FOIA 14-11 final.txt" 2013



Obtaining Salary Data
=====================
You will need to download and convert the salary data first. Each year's format is a little
different.

2015 Salary Data
----------------
I obtained this data from Matthew Rocheleau, the Boston Globe staff reporter on the `22 Dec 2015 MBTA overtime article. <http://www.bostonglobe.com/2015/12/21/mbta-employees-who-will-make-more-than-this-year/u6BUkDr6EawQ7dlHx9bZQP/story.html>`_
We anticipate a request for the whole year 2015 data once we're into 2016.

2014 Salary Data
----------------

1. `Download 2014 MBTA salary data <http://www.mbta.com/uploadedfiles/Smart_Forms/News,_Events_and_Press_Releases/Wages2014.pdf>`_

2. Extract text from PDF, using `pdftotext <https://en.wikipedia.org/wiki/Poppler_%28software%29#poppler-utils>`_::

    pdftotext -layout Wages2014.pdf

2013 Salary Data
----------------

1. `Download 2013 MBTA salary data <http://www.mbta.com/uploadedfiles/Smart_Forms/News,_Events_and_Press_Releases/FOIA%2014-11%20final.pdf>`_

2. Extract text from PDF, using `pdftotext <https://en.wikipedia.org/wiki/Poppler_%28software%29#poppler-utils>`_::

    pdftotext -layout "FOIA 14-11 final.pdf"

3. The last three lines of this .txt file are missing a space between the salary and "2013". 
Just open in a text editor and manually add one additional space before 2013 in these last three lines.

