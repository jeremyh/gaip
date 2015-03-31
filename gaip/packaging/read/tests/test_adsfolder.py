import os
import unittest

import datetime

import gaip.packaging.read.adsfolder as adsfolder
from gaip.packaging.read.tests import write_files
import gaip.packaging.type as ptype


class AdsFolderExtractionTest(unittest.TestCase):

    def test_directory(self):
        d = write_files({
            'LANDSAT-8.11308': {
                'LC80880750762013254ASA00': {
                    '446.000.2013254233714881.ASA': 'a',
                    '447.000.2013254233711482.ASA': 'a',
                    'LC80880750762013254ASA00_IDF.xml': 'a',
                    'LC80880750762013254ASA00_MD5.txt': 'a',
                }
            }
        })

        # Read orbit from folder name
        d = os.path.join(d, 'LANDSAT-8.11308')
        ds = ptype.DatasetMetadata()
        metadata = adsfolder.extract_md(ds, d)
        self.assertEqual(metadata.acquisition.platform_orbit, 11308)

        # Read orbit from parent folder name.
        d = os.path.join(d, 'LC80880750762013254ASA00')
        ds = ptype.DatasetMetadata()
        metadata = adsfolder.extract_md(ds, d)
        self.assertEqual(metadata.acquisition.platform_orbit, 11308)



if __name__ == '__main__':
    import doctest

    doctest.testmod(mdf)
    unittest.main()