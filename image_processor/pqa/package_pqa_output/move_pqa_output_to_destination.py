'''
Created on Jun 14, 2012

@author: Alex Ip (alex.ip@ga.gov.au)
Code adapted from NbarProcessor.py and main.py

Create composite preview thumbnail from RGB product files
'''

import logging
from ULA3 import DataManager
from ULA3.utils import log_multiline
from ULA3.image_processor import ProcessorConfig
from ULA3.utils import execute

logger = logging.getLogger('root.' + __name__)

def process(subprocess_list=[], resume=False):
    logger.info('%s.process(%s, %s) called', __name__, subprocess_list, resume)

    CONFIG = ProcessorConfig()
    DATA = DataManager()

    pqa_temp_output = DATA.get_item('pqa_temp_output.dat', str)
    assert pqa_temp_output, 'Unable to retrieve pqa_temp_output string'
    logger.debug('string for pqa_temp_output retrieved')

    pqa_output_path = DATA.get_item('pqa_output_path.dat', str)
    assert pqa_output_path, 'Unable to retrieve pqa_output_path string'
    logger.debug('string for pqa_output_path retrieved')

    if pqa_temp_output != pqa_output_path: # Moving is actually required (i.e. temp directory used)
        # N.B: Move files rather than copying them - may change later
        command_string = 'rm -rf %s; mkdir -p %s; mv -f %s/* %s' % (pqa_output_path, pqa_output_path, pqa_temp_output, pqa_output_path)

        logger.info('Invoking: %s', command_string)

        result = execute(command_string=command_string,
            cwd=CONFIG.work_path
            )

        if result['stdout']:
            log_multiline(logger.info, result['stdout'], command_string + ' in ' + pqa_temp_output, '\t')

        if result['returncode']:
            log_multiline(logger.error, result['stderr'], 'stderr from ' + command_string, '\t')
            raise Exception('%s failed', command_string)
    else:
        logger.info('PQA output already in final destination directory %s. No files moved', pqa_output_path)
