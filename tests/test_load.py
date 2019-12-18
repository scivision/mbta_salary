#!/usr/bin/env python
import pytest
import urllib.request
from pathlib import Path
import subprocess
import mbtasalary as ms
import shutil

URL2014 = 'http://www.mbta.com/uploadedfiles/Smart_Forms/News,_Events_and_Press_Releases/Wages2014.pdf'

R = Path(__file__).parent

PDF2TXT = shutil.which('pdftotext')


@pytest.mark.skipif(not PDF2TXT, reason='Missing Poppler Utils pdftotext.')
def getfile(rawfn: Path):
    txtfn = rawfn.with_suffix('.txt')

    if not rawfn.is_file():
        print(f'trying to download {rawfn} from {URL2014}')
        urllib.request.urlretrieve(URL2014, rawfn)
    # %% convert to text
    subprocess.check_call([PDF2TXT, '-layout', str(rawfn)])

    assert txtfn.is_file()


def test_ld():

    rawfn = R / URL2014.split('/')[-1]

    txtfn = rawfn.with_suffix('.txt')

    if not txtfn.is_file():
        getfile(rawfn)

    stats, data = ms.parsefilt(txtfn, 2014)

    assert data.shape == (6331, 5)


if __name__ == '__main__':
    pytest.main([__file__])
