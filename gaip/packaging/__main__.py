import os
import logging

import click
from pathlib import Path

from gaip.packaging.package import get_dataset, generate_raw_metadata, generate_ortho_metadata, generate_nbar_metadata, do_package


_DATASET_PACKAGERS = {
    'raw': (generate_raw_metadata, None),
    'ortho': (generate_ortho_metadata, 'raw'),
    'nbar': (generate_nbar_metadata, 'ortho'),
}


@click.command()
@click.option('--parent', type=click.Path(exists=True, readable=True, writable=False), multiple=True)
@click.option('--debug', is_flag=True)
@click.option('--in-place', is_flag=True)
@click.argument('type', type=click.Choice(_DATASET_PACKAGERS.keys()))
@click.argument('dataset', type=click.Path(exists=True, readable=True, writable=False), nargs=-1)
@click.argument('destination', type=click.Path(exists=True, readable=True, writable=True), nargs=1)
def run_packaging(parent, debug, in_place, type, dataset, destination):
    """
    :type parent: str
    :type debug: bool
    :type in_place: bool
    :type type: str
    :type dataset: list of str
    :type destination: str
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger('gaip.packaging').setLevel(logging.INFO)

    parent_datasets = {}

    extract_metdata, parent_name = _DATASET_PACKAGERS[type]

    # TODO: Multiple parents?
    if parent:
        parent_datasets.update({parent_name: get_dataset(Path(parent[0]))})

    if in_place:
        dataset.append(destination)
        destination = None

    for dataset_path in dataset:
        if in_place:
            target_folder = dataset_path
        else:
            target_folder = os.path.join(destination, type)
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)

        do_package(
            extract_metdata,
            dataset_path,
            target_folder,
            source_datasets=parent_datasets
        )

run_packaging()