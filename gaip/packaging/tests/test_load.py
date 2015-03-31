import unittest

from pathlib import PosixPath

import gaip.packaging.load as load
from gaip.packaging.read.tests import write_files
from gaip.packaging.type import *


BASIC_BANDS = {
    '11': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B11.TIF'),
        number='11',
    ),
    '10': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B10.TIF'),
        number='10',
    ),
    '1': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B1.TIF'),
        number='1',
    ),
    '3': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B3.TIF'),
        number='3',
    ),
    '2': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B2.TIF'),
        number='2',
    ),
    '5': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B5.TIF'),
        number='5',
    ),
    '4': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B4.TIF'),
        number='4',
    ),
    '7': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B7.TIF'),
        number='7',
    ),
    '6': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B6.TIF'),
        number='6',
    ),
    '9': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B9.TIF'),
        number='9',
    ),
    '8': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B8.TIF'),
        number='8',
    ),
    'quality': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_BQA.TIF'),
        number='quality',
    )
}

EXPANDED_BANDS = {
    '11': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B11.TIF'),
        type=u'thermal',
        label=u'Thermal Infrared 2',
        number='11',
        cell_size=25.0
    ),
    '10': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B10.TIF'),
        type=u'thermal',
        label=u'Thermal Infrared 1',
        number='10',
        cell_size=25.0
    ),
    '1': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B1.TIF'),
        type=u'reflective',
        label=u'Coastal Aerosol',
        number='1',
        cell_size=25.0
    ),
    '3': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B3.TIF'),
        type=u'reflective',
        label=u'Visible Green',
        number='3',
        cell_size=25.0
    ),
    '2': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B2.TIF'),
        type=u'reflective',
        label=u'Visible Blue',
        number='2',
        cell_size=25.0
    ),
    '5': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B5.TIF'),
        type=u'reflective',
        label=u'Near Infrared',
        number='5',
        cell_size=25.0
    ),
    '4': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B4.TIF'),
        type=u'reflective',
        label=u'Visible Red',
        number='4',
        cell_size=25.0
    ),
    '7': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B7.TIF'),
        type=u'reflective',
        label=u'Short-wave Infrared 2',
        number='7',
        cell_size=25.0
    ),
    '6': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B6.TIF'),
        type=u'reflective',
        label=u'Short-wave Infrared 1',
        number='6',
        cell_size=25.0
    ),
    '9': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B9.TIF'),
        type=u'atmosphere',
        label=u'Cirrus',
        number='9',
        cell_size=25.0
    ),
    '8': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_B8.TIF'),
        type=u'panchromatic',
        label=u'Panchromatic',
        number='8',
        cell_size=12.5
    ),
    'quality': BandMetadata(
        path=PosixPath('/tmp/fake-folder/LC81010782014285LGN00_BQA.TIF'),
        type=u'quality',
        label=u'Quality',
        number='quality',
        cell_size=25.0
    )
}


class TestBandExpansion(unittest.TestCase):
    def test_expand_band(self):
        # Create fake image file.
        image_file = write_files({'LC81010782014285LGN00_B6.TIF': 'test'})
        image_file = os.path.join(image_file, 'LC81010782014285LGN00_B6.TIF')

        md = load.expand_band_information(
            'LANDSAT_8', 'OLI_TIRS',
            BandMetadata(path=PosixPath(image_file), number='6')
        )

        expected = BandMetadata(
            path=PosixPath(image_file),
            type=u'reflective',
            label=u'Short-wave Infrared 1',
            number='6',
            # MD5 of image contents ('test')
            checksum_md5='098f6bcd4621d373cade4e832627b4f6',
            cell_size=25.0
        )
        self.assertEqual(md, expected)

    def test_expand_all_bands(self):
        for number, band_metadata in BASIC_BANDS.items():
            load.expand_band_information('LANDSAT_8', 'OLI_TIRS', band_metadata, checksum=False)

        self.assertEqual(BASIC_BANDS, EXPANDED_BANDS)