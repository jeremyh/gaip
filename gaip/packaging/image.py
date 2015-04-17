import glob
import logging
import os
import shutil
from subprocess import check_call
import math
import tempfile

import gdalconst
import gdal
import numpy
from pathlib import Path

from gaip.packaging.type import BrowseMetadata


GDAL_CACHE_MAX_MB = 512

_LOG = logging.getLogger(__name__)


def run_command(command, work_dir):
    _LOG.debug('Running %r', command)
    check_call(command, cwd=work_dir)
    _LOG.debug('Finished %s', command[0])


def _calculate_scale_offset(nodata, band):
    nbits = gdal.GetDataTypeSize(band.DataType)
    dfScaleDstMin, dfScaleDstMax = 0.0, 255.0
    if nbits == 16:
        count = 32767 + nodata
        histogram = band.GetHistogram(-32767, 32767, 65536)
    else:
        count = 0
        histogram = band.GetHistogram()
    total = 0
    cliplower = int(0.01 * (sum(histogram) - histogram[count]))
    clipupper = int(0.99 * (sum(histogram) - histogram[count]))
    while total < cliplower and count < len(histogram) - 1:
        count += 1
        total += int(histogram[count])
        dfScaleSrcMin = count
    if nbits == 16:
        count = 32767 + nodata
    else:
        count = 0
    total = 0
    while total < clipupper and count < len(histogram) - 1:
        count += 1
        total += int(histogram[count])
        dfScaleSrcMax = count
    if nbits == 16:
        dfScaleSrcMin -= 32768
        dfScaleSrcMax -= 32768

    # Determine gain and offset
    dfScale = (dfScaleDstMax - dfScaleDstMin) / (dfScaleSrcMax - dfScaleSrcMin)
    dfOffset = -1 * dfScaleSrcMin * dfScale + dfScaleDstMin

    return dfScale, dfOffset


def create_thumbnail(red_file, green_file, blue_file, thumb_image,
                     outcols=None, nodata=-999, work_dir=None, overwrite=True):
    """
    Create JPEG thumbnail image using individual R, G, B images.

    :param red_file: red band data file
    :param green_file: green band data file
    :param blue_file: blue band data file
    :param thumb_image: thumbnail file to write to.
    :param outcols: thumbnail width (if not full resolution)
    :param nodata: null/fill data value
    :param work_dir: temp/work directory to use.
    :param overwrite: overwrite existing thumbnail?

    Thumbnail height is adjusted automatically to match the aspect ratio
    of the input images.

    """
    nodata = int(nodata)

    # GDAL calls need absolute paths.
    thumbnail_path = Path(thumb_image).absolute()

    if thumbnail_path.exists() and not overwrite:
        _LOG.warning('File already exists. Skipping creation of %s', thumbnail_path)
        return

    # thumbnail_image = os.path.abspath(thumbnail_image)

    work_dir = os.path.abspath(work_dir) if work_dir else tempfile.mkdtemp('-gaip-package')

    # working files
    file_to = os.path.join(work_dir, 'rgb.vrt')
    warp_to_file = os.path.join(work_dir, 'rgb-warped.vrt')
    outtif = os.path.join(work_dir, 'thumbnail.tif')

    # file_to = os.path.abspath(file_to)

    # Build the RGB Virtual Raster at full resolution
    run_command(
        [
            "gdalbuildvrt",
            "-overwrite", "-separate",
            file_to,
            str(red_file), str(green_file), str(blue_file)
        ],
        work_dir
    )
    assert os.path.exists(file_to), "VRT must exist"

    # Determine the pixel scaling to get the correct width thumbnail
    vrt = gdal.Open(file_to)
    intransform = vrt.GetGeoTransform()
    inpixelx = intransform[1]
    # inpixely = intransform[5]
    inrows = vrt.RasterYSize
    incols = vrt.RasterXSize

    # If a specific resolution is asked for.
    if outcols:
        outresx = inpixelx * incols / outcols
        _LOG.info('Input pixel res %r, output pixel res %r', inpixelx, outresx)

        outrows = int(math.ceil((float(inrows) / float(incols)) * outcols))

        run_command([
            "gdalwarp",
            "--config", "GDAL_CACHEMAX", str(GDAL_CACHE_MAX_MB),
            "-of", "VRT",
            "-tr", str(outresx), str(outresx),
            "-r", "near",
            "-overwrite", file_to,
            warp_to_file
        ], work_dir)
    else:
        # Otherwise use a full resolution browse image.
        outrows = inrows
        outcols = incols
        warp_to_file = file_to
        outresx = inpixelx

    _LOG.debug('Current GDAL cache max %rMB. Setting to %rMB', gdal.GetCacheMax() / 1024 / 1024, GDAL_CACHE_MAX_MB)
    gdal.SetCacheMax(GDAL_CACHE_MAX_MB * 1024 * 1024)

    # Open VRT file to array
    vrt = gdal.Open(warp_to_file)
    driver = gdal.GetDriverByName("GTiff")
    outdataset = driver.Create(outtif, outcols, outrows, 3, gdalconst.GDT_Byte)

    # Loop through bands and apply Scale and Offset
    for band_number in (1, 2, 3):
        band = vrt.GetRasterBand(band_number)

        scale, offset = _calculate_scale_offset(nodata, band)

        # Apply gain and offset
        outdataset.GetRasterBand(band_number).WriteArray(
            (numpy.ma.masked_less_equal(band.ReadAsArray(), nodata) * scale) + offset
        )
        _LOG.debug('Scale %r, offset %r', scale, offset)

    # Must close dataset to flush to disk.
    # noinspection PyUnusedLocal
    outdataset = None

    # GDAL Create doesn't support JPEG so we need to make a copy of the GeoTIFF
    run_command(
        [
            "gdal_translate",
            "--config", "GDAL_CACHEMAX", str(GDAL_CACHE_MAX_MB),
            "-of", "JPEG",
            outtif,
            str(thumbnail_path)
        ],
        work_dir)

    _LOG.debug('Cleaning work files')
    # Clean up work files
    shutil.rmtree(work_dir)

    return outcols, outrows, outresx


def create_browse(red_band, green_band, blue_band, destination_file, constrain_horizontal_res=None):
    """

    :type red_band: gaip.packaging.type.BandMetadata
    :type green_band: gaip.packaging.type.BandMetadata
    :type blue_band: gaip.packaging.type.BandMetadata
    :param destination_file:
    :return:
    """
    cols, rows, output_res = create_thumbnail(
        red_band.path,
        green_band.path,
        blue_band.path,
        destination_file,
        outcols=constrain_horizontal_res
    )

    return BrowseMetadata(
        path=destination_file,
        file_type='image/jpg',
        cell_size=output_res,
        red_band=red_band.number,
        green_band=green_band.number,
        blue_band=blue_band.number
    )


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    import sys

    # Create thumb from the given image directory.
    _dir = sys.argv[1]

    create_thumbnail(
        glob.glob(_dir + '/*_B7.TIF')[0],
        glob.glob(_dir + '/*_B5.TIF')[0],
        glob.glob(_dir + '/*_B1.TIF')[0],
        thumb_image='test-thumb.jpg'
    )