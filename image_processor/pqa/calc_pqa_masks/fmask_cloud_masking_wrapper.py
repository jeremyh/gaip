'''
Created on 08/01/2013

@author: u76345
'''
import os
from glob import glob
import logging

from ULA3.dataset import SceneDataset
from ULA3.common.pqa_result import PQAResult
from ULA3.image_processor import ProcessorConfig
from ULA3 import DataManager
from ULA3.utils import dump_array
import fmask_cloud_masking as _fmask

logger = logging.getLogger('root.' + __name__)

def process(subprocess_list=[], resume=False):
    ''' Because fmask_cloud_masking.py was translated from Matlib code, it is covered by GPL so it
    will need to be re-released as a stand-alone module.
    This module wraps the fmask_cloud_masking.py module to allow it to be used in the NBAR/PQA execution
    framework.
    '''

    CONFIG = ProcessorConfig()
    DATA = DataManager()

    l1t_input_dataset = DATA.get_item(CONFIG.input['l1t']['path'], SceneDataset)
    assert l1t_input_dataset, 'Unable to retrieve SceneDataset object for L1T input scene dataset'
    logger.debug( 'SceneDataset object for %s retrieved', l1t_input_dataset.pathname)

    result = DATA.get_item('result.tif', PQAResult)
    assert result, 'Unable to retrieve PQAResult object for result'
    logger.debug( 'PQAResult object for result retrieved')

    pqa_temp_output = DATA.get_item('pqa_temp_output.dat', str)
    assert pqa_temp_output, 'Unable to retrieve string object for pqa_temp_output'
    logger.debug( 'string object for pqa_temp_output retrieved')

    def FMaskCloudMask(mtl, null_mask=None, cloud_prob=None, wclr_max=None):
        cloud_prob = cloud_prob or CONFIG.pqa_param['fmask_cloudprob']
        wclr_max = wclr_max or CONFIG.pqa_param['fmask_wclr_max']

        try: # Need to change directory to ensure log files are written to the right place
            current_dir = os.curdir
            os.chdir(os.path.join(pqa_temp_output, 'scene01'))

            (_,_,_,_,_,_,_,_,fmask_byte,_,_,_,_,_) = _fmask.plcloud_1_6sav(filename=mtl,
                                                                       cldprob=cloud_prob,
                                                                       mask=null_mask,
                                                                       wclr_max=wclr_max)
        finally:
            os.chdir(current_dir)

        return (fmask_byte != 1).astype('bool') # Invert to a 'land mask'

    #===========================================================================
    # contiguity_mask = DATA.get_item('contiguity_mask', numpy.ndarray)
    # assert contiguity_mask is not None, 'Unable to retrieve ndarray object for contiguity_mask'
    # logger.debug( 'ndarray object for contiguity_mask retrieved')
    #===========================================================================
    assert CONFIG.pqa_test_index['CONTIGUITY'] in result.test_set, 'Contiguity test not yet run'
    contiguity_mask = (result.array & (1 << CONFIG.pqa_test_index['CONTIGUITY'])) > 0

    mtl = glob(os.path.join(l1t_input_dataset.pathname, 'scene01/*_MTL.txt'))[0] # Crude but effective
    mask = FMaskCloudMask(mtl, null_mask=contiguity_mask)

    bit_index = CONFIG.pqa_test_index['FMASK']
    result.set_mask(mask, bit_index)
    if CONFIG.debug:
        dump_array(mask,
                   os.path.join(CONFIG.work_path, 'mask_%02d.tif' % bit_index),
                   l1t_input_dataset)


