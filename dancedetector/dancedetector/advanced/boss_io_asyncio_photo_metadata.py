# NOTE: For more examples tqdm + aiofile, search https://github.com/search?l=Python&q=aiofile+tqdm&type=Code

from __future__ import annotations

import concurrent.futures

import asyncio
import time
import aiohttp
import os
import errno
from hashlib import md5
import os
import shutil
import tempfile
import ssl
import certifi
import rich
import uritools
import aiofile
import pathlib
import functools
import gc
import aiorwlock
import requests
from tqdm.auto import tqdm
from icecream import ic
import argparse
from typing import List, Union, Optional, Tuple
import aiosqlite
from datetime import datetime
from dateutil.parser import parse as parse_date
import mimetypes
import os
import re
from subprocess import Popen, PIPE
import imghdr
import os
import shutil
from hashlib import md5
from io import StringIO

from PIL import Image

from urllib.request import urlretrieve
import pytz
import logging
from loguru import logger
from dancedetector.dbx_logger import (
    get_logger,
    intercept_all_loggers,
    global_log_config
)

global_log_config(
    log_level=logging.getLevelName("DEBUG"),
    json=False,
)


utc = pytz.utc

TEST_DB = pathlib.Path("test.db")

VERIFY_SSL = False

MIMETYPE_WHITELIST = [
    # This list is in addition to the filetypes detected by imghdr and 'dcraw -i'
    'image/heif',
    'image/heif-sequence',
    'image/heic',
    'image/heic-sequence',
    'image/avif',
    'image/avif-sequence',
]


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# ------------------------------------------------------------------------------
# db.py
# def record_photo(path, library, inotify_event_type=None):
#     logger.info(f'Recording photo {path}')

#     mimetype = get_mimetype(path)

#     if not imghdr.what(path) and not mimetype in MIMETYPE_WHITELIST and subprocess.run(['dcraw', '-i', path]).returncode:
#         logger.error(f'File is not a supported type: {path} ({mimetype})')
#         return None

#     if type(library) == Library:
#         library_id = library.id
#     else:
#         library_id = str(library)
#     try:
#         photo_file = PhotoFile.objects.get(path=path)
#     except PhotoFile.DoesNotExist:
#         photo_file = PhotoFile()

#     if inotify_event_type in ['DELETE', 'MOVED_FROM']:
#         if PhotoFile.objects.filter(path=path).exists():
#             return delete_photo_record(photo_file)
#         else:
#             return True

#     file_modified_at = datetime.fromtimestamp(os.stat(path).st_mtime, tz=utc)

#     if photo_file and photo_file.file_modified_at == file_modified_at:
#         return True

#     metadata = PhotoMetadata(path)
#     date_taken = None
#     possible_date_keys = ['Create Date', 'Date/Time Original', 'Date Time Original', 'Date/Time', 'Date Time', 'GPS Date/Time', 'File Modification Date/Time']
#     for date_key in possible_date_keys:
#         date_taken = parse_datetime(metadata.get(date_key))
#         if date_taken:
#             break
#     # If EXIF data not found.
#     date_taken = date_taken or datetime.strptime(time.ctime(os.path.getctime(path)), "%a %b %d %H:%M:%S %Y")

#     camera = None
#     camera_make = metadata.get('Make', '')[:Camera.make.field.max_length]
#     camera_model = metadata.get('Camera Model Name', '')
#     if camera_model:
#         camera_model = camera_model.replace(camera_make, '').strip()
#     camera_model = camera_model[:Camera.model.field.max_length]
#     if camera_make and camera_model:
#         try:
#             camera = Camera.objects.get(library_id=library_id, make=camera_make, model=camera_model)
#             if date_taken < camera.earliest_photo:
#                 camera.earliest_photo = date_taken
#                 camera.save()
#             if date_taken > camera.latest_photo:
#                 camera.latest_photo = date_taken
#                 camera.save()
#         except Camera.DoesNotExist:
#             camera = Camera(library_id=library_id, make=camera_make, model=camera_model,
#                             earliest_photo=date_taken, latest_photo=date_taken)
#             camera.save()

#     lens = None
#     lens_name = metadata.get('Lens ID')
#     if lens_name:
#         try:
#             lens = Lens.objects.get(name=lens_name)
#             if date_taken < lens.earliest_photo:
#                 lens.earliest_photo = date_taken
#                 lens.save()
#             if date_taken > lens.latest_photo:
#                 lens.latest_photo = date_taken
#                 lens.save()
#         except Lens.DoesNotExist:
#             lens = Lens(library_id=library_id, name=lens_name, earliest_photo=date_taken,
#                         latest_photo=date_taken)
#             lens.save()

#     photo = None
#     if date_taken:
#         try:
#             # Fix for issue 347: Photos with the same date are not imported ...
#             photo_set = Photo.objects.filter(taken_at=date_taken)
#             file_found = False
#             if photo_set:
#                 for photo_entry in photo_set:
#                     if PhotoFile.objects.get(photo_id=photo_entry).base_image_path == path:
#                         file_found = True
#                         photo = photo_entry
#                         break
#             if not file_found:
#                 photo = None
#         except Photo.DoesNotExist:
#             pass

#     latitude = None
#     longitude = None
#     if metadata.get('GPS Position'):
#         latitude, longitude = parse_gps_location(metadata.get('GPS Position'))

#     iso_speed = None
#     if metadata.get('ISO'):
#         try:
#             iso_speed = int(re.search(r'[0-9]+', metadata.get('ISO')).group(0))
#         except AttributeError:
#             pass
#     if not photo:
#         # Save Photo
#         aperture = None
#         aperturestr = metadata.get('Aperture')
#         if aperturestr:
#             try:
#                 aperture = Decimal(aperturestr)
#                 if aperture.is_infinite():
#                     aperture = None
#             except:
#                 pass

#         photo = Photo(
#             library_id=library_id,
#             taken_at=date_taken,
#             taken_by=metadata.get('Artist', '')[:Photo.taken_by.field.max_length] or None,
#             aperture=aperture,
#             exposure=metadata.get('Exposure Time', '')[:Photo.exposure.field.max_length] or None,
#             iso_speed=iso_speed,
#             focal_length=metadata.get('Focal Length') and metadata.get('Focal Length').split(' ', 1)[0] or None,
#             flash=metadata.get('Flash') and 'on' in metadata.get('Flash').lower() or False,
#             metering_mode=metadata.get('Metering Mode', '')[:Photo.metering_mode.field.max_length] or None,
#             drive_mode=metadata.get('Drive Mode', '')[:Photo.drive_mode.field.max_length] or None,
#             shooting_mode=metadata.get('Shooting Mode', '')[:Photo.shooting_mode.field.max_length] or None,
#             camera=camera,
#             lens=lens,
#             latitude=latitude,
#             longitude=longitude,
#             altitude=metadata.get('GPS Altitude') and metadata.get('GPS Altitude').split(' ')[0],
#             star_rating=metadata.get('Rating')
#         )
#         photo.save()

#         for subject in metadata.get('Subject', '').split(','):
#             subject = subject.strip()
#             if subject:
#                 tag, _ = Tag.objects.get_or_create(library_id=library_id, name=subject, type="G")
#                 PhotoTag.objects.create(
#                     photo=photo,
#                     tag=tag,
#                     confidence=1.0
#             )
#     else:
#         for photo_file in photo.files.all():
#             if not os.path.exists(photo_file.path):
#                 photo_file.delete()

#     width = metadata.get('Image Width')
#     height = metadata.get('Image Height')
#     if metadata.get('Orientation') in ['Rotate 90 CW', 'Rotate 270 CCW', 'Rotate 90 CCW', 'Rotate 270 CW']:
#         old_width = width
#         width = height
#         height = old_width

#     # Save PhotoFile
#     photo_file.photo = photo
#     photo_file.path = path
#     photo_file.width = width
#     photo_file.height = height
#     photo_file.mimetype = mimetype
#     photo_file.file_modified_at = file_modified_at
#     photo_file.bytes = os.stat(path).st_size
#     photo_file.preferred = False  # TODO
#     photo_file.save()

#     # Create task to ensure JPEG version of file exists (used for thumbnailing, analysing etc.)
#     Task(
#         type='ensure_raw_processed',
#         subject_id=photo.id,
#         complete_with_children=True,
#         library=photo.library
#     ).save()

#     return photo


# def delete_photo_record(photo_file_obj):
#     """Delete photo record if photo not exixts on library path."""
#     delete_photofile_and_photo_record(photo_file_obj)
#     Tag.objects.filter(photo_tags=None).delete()
#     Camera.objects.filter(photos=None).delete()
#     Lens.objects.filter(photos=None).delete()
#     return True


# def move_or_rename_photo(photo_old_path, photo_new_path, library_id):
#     """Rename a photoFile or change the path while moving photo in child directory."""
#     try:
#         photo_file = PhotoFile.objects.get(path=photo_old_path)
#         photo_file.path = photo_new_path
#         photo_file.save()
#         return photo_file
#     except Exception as e:
#         return True


# def delete_child_dir_all_photos(directory_path, library_id):
#     """When a child directory deleted it delete all the photo records of that directory."""
#     for photo_file_obj in PhotoFile.objects.filter(path__startswith=directory_path):
#         delete_photofile_and_photo_record(photo_file_obj)
#     Tag.objects.filter(photo_tags=None).delete()
#     Camera.objects.filter(photos=None).delete()
#     Lens.objects.filter(photos=None).delete()
#     return True


# def delete_photofile_and_photo_record(photo_file_obj):
#     """Delete photoFile object with its photo object."""
#     photo_obj = photo_file_obj.photo
#     photo_file_obj.delete()
#     if not photo_obj.files.all():
#         photo_obj.delete()
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# metadata

class PhotoMetadata(object):
    def __init__(self, path: str):
        self.data = {}
        try:
            # exiftool produces data such as MIME Type for non-photos too
            result = Popen(['exiftool', path], stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate()[0].decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            result = ''
        for line in str(result).split('\n'):
            if line:
                try:
                    k, v = line.split(':', 1)
                    self.data[k.strip()] = v.strip()
                except ValueError:
                    pass

        # Some file MIME Types can not be identified by exiftool so we fall back to Python's mimetypes library so the get_mimetype() funciton below is universal
        if not self.data.get('MIME Type'):
            self.data['MIME Type'] = mimetypes.guess_type(path)[0]

    def get(self, attribute, default=None):
        return self.data.get(attribute, default)

    def get_all(self):
        return self.data


def parse_datetime(date_str):
    if not date_str:
        return None
    if '.' in date_str:
        date_str = date_str.split('.', 1)[0]
    try:
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').replace(tzinfo=utc)
    except ValueError:
        try:
            parsed_date = parse_date(date_str)
            if not parsed_date.tzinfo:
                parsed_date = parsed_date.replace(tzinfo=utc)
            return parsed_date
        except ValueError:
            return None


def parse_gps_location(gps_str):
    # 50 deg 49' 9.53" N, 0 deg 8' 13.33" W
    regex = r'''(\d{1,3}) deg (\d{1,2})' (\d{1,2}).(\d{2})" ([N,S]), (\d{1,3}) deg (\d{1,2})' (\d{1,2}).(\d{2})" ([E,W])'''
    m = re.search(regex, gps_str)

    latitude = float(m.group(1)) + (float(m.group(2)) / 60) + (float('{}.{}'.format(m.group(3), m.group(4))) / 60 / 100)
    if m.group(5) == 'S':
        latitude *= -1

    longitude = float(m.group(6)) + (float(m.group(7)) / 60) + (float('{}.{}'.format(m.group(8), m.group(9))) / 60 / 100)
    if m.group(10) == 'W':
        longitude *= -1

    return (latitude, longitude)


def get_datetime(path):
    '''
    Tries to get date/time from EXIF data which works on JPEG and raw files.
    Failing it that it tries to find the date in the filename.
    '''
    # TODO: Use 'GPS Date/Time' if available as it's more accurate

    # First try the date in the metadata
    metadata = PhotoMetadata(path)
    date_str = metadata.get('Date/Time Original')
    if date_str:
        parsed_datetime = parse_datetime(date_str)
        if parsed_datetime:
            return parsed_datetime

    date_str = metadata.get('Create Date')
    if date_str:
        parsed_datetime = parse_datetime(date_str)
        if parsed_datetime:
            return parsed_datetime

    # If there was not date metadata, try to infer it from filename
    fn = os.path.split(path)[1]
    matched = re.search(r'((19|20)[0-9]{2})-([0-9]{2})-([0-9]{2})\D', fn)
    if not matched:
        matched = re.search(r'\D((19|20)[0-9]{2})([0-9]{2})([0-9]{2})\D', fn)
    if matched:
        date_str = '{}-{}-{}'.format(matched.group(1), matched.group(3), matched.group(4))
        return datetime.strptime(date_str, '%Y-%m-%d')

    # Otherwise get file creation time
    try:
        return datetime.fromtimestamp(os.stat(path).st_ctime).replace(tzinfo=utc)
    except:
        return None


def get_dimensions(path):
    metadata = PhotoMetadata(path)
    if metadata.data.get('Image Width') and metadata.data.get('Image Height'):
        return (int(metadata.data['Image Width']), int(metadata.data['Image Height']))
    return (None, None)


def get_mimetype(path):
    metadata = PhotoMetadata(path)
    if metadata.data.get('MIME Type'):
        return metadata.data.get('MIME Type')
    return None


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# SOURCE: https://github.com/dream2globe/CleanCodeInPython/blob/e759773c95e7485f004b629fcf7fb4a662c95794/Ch7-2_ConcurrencyTest.py
DEFAULT_FMT = "[{elapsed:0.8f}s] {name}({args}, {kwargs}) -> {result}"

BASE_DIR = str(pathlib.Path(__file__).parent.resolve())
DATA_DIR = str(pathlib.Path(BASE_DIR) / "data")
CACHE_DIR = str(pathlib.Path(DATA_DIR) / "cache")
MODEL_DIR = str(pathlib.Path(DATA_DIR) / "models")
MEDIA_ROOT = str(pathlib.Path(BASE_DIR) / "data")
THUMBNAIL_ROOT = str(pathlib.Path(CACHE_DIR) / "thumbnails")


THUMBNAIL_SIZES = [
    # Width, height, crop method, JPEG quality, whether it should be generated upon upload, force accurate gamma-aware sRGB resizing
    (256, 256, "cover", 50, True, True),  # Square thumbnails
    # We use the largest dimension for both dimensions as they won't crop and some with in portrait mode
    # (960, 960, 'contain', 75, False, False),  # 960px
    # (1920, 1920, 'contain', 75, False, False),  # 2k
    (3840, 3840, "contain", 75, False, False),  # 4k
]
PHOTO_INPUT_DIRS = [str(pathlib.Path(BASE_DIR) / "photos_to_import")]
PHOTO_OUTPUT_DIRS = [
    {
        "EXTENSIONS": ["jpg", "jpeg", "mov", "mp4", "m4v", "3gp", "png"],
        "PATH": "./data/photos",
    },
    {
        "EXTENSIONS": ["cr2"],
        "PATH": "./data/raw-photos",
    },
]
ic(
    BASE_DIR,
    DATA_DIR,
    CACHE_DIR,
    MODEL_DIR,
    MEDIA_ROOT,
    THUMBNAIL_ROOT,
    PHOTO_INPUT_DIRS,
)

# ~/dev/bossjones/sandbox/dancedetector/dancedetector/advanced feature-thread-test*
# ❯ python boss_io_asyncio_photo_metadata.py ./data/photos --urls https://i.imgur.com/kvSAxmy.png
# ic| BASE_DIR: '/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced'
#     DATA_DIR: '/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/data'
#     CACHE_DIR: '/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/data/cache'
#     MODEL_DIR: '/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/data/models'
#     MEDIA_ROOT: '/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/data'
#     THUMBNAIL_ROOT: '/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/data/cache/thumbnails'
#     PHOTO_INPUT_DIRS: ['/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/photos_to_import']

# ic| args: Namespace(data='./data/photos', urls=['https://i.imgur.com/kvSAxmy.png'])


parser = argparse.ArgumentParser(description="Asyncio io concurrency testing")
parser.add_argument(
    "data",
    metavar="DIR",
    # '?'. One argument will be consumed from the command line if possible, and produced as a single item. If no command-line argument is present, the value from default will be produced. Note that for optional arguments, there is an additional case - the option string is present but not followed by a command-line argument. In this case the value from const will be produced. Some examples to illustrate this:
    nargs="?",
    # default=f"{DEFAULT_DIR}",
    # help=f"path to dataset (default: {DEFAULT_DIR})",
)
parser.add_argument("-u", "--urls", metavar="URL", nargs="*", help="urls to download. ")
parser.add_argument(
    "--db",
    metavar="DB",
    choices=["init", "connect"],
    default="connect",
    help="Setup db"
)


async def db_init():
    async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table boss (i integer primary key asc, k integer)")
            await db.execute("insert into foo (i, k) values (1, 5)")
            await db.commit()

            cursor = await db.execute("select * from foo")
            rows = await cursor.fetchall()

def clock(fmt=DEFAULT_FMT):
    def decorate(func):
        @functools.wraps(func)
        def clocked(*_args, **_kwargs):  # clocked에서 *, ** 키워드를 통해 설정된 인수를 변수화
            t0 = time.time()
            _result = func(*_args)
            elapsed = time.time() - t0
            name = func.__name__
            args = ", ".join(repr(arg) for arg in _args)
            pairs = ["%s=%r" % (k, w) for k, w in sorted(_kwargs.items())]
            kwargs = ", ".join(pairs)
            result = repr(_result)
            print(fmt.format(**locals()))
            return _result  # clocked()는 데커레이트된 함수를 대체하므로, 원래 함수가 반환하는 값을 반환해야 한다.

        return clocked  # decorate()는 clocked()를 반환한다.

    return decorate  # clock()은 decorate()를 반환한다.


# ------------------------------------------------------------------------------
# photonix organise.py
class FileHashCache(object):
    '''
    Used with determine_same_file() function. Can keep hold of the previously
    opened orig and dest file contents. Can keep hold of all file-based and
    image-based hashes per file.
    '''
    file_hash_cache = {}
    file_data = {'orig': (None, None), 'dest': (None, None)}

    def reset(self):
        self.file_hash_cache = {}

    def get_file_hash(self, fn, hash_type):
        if fn in self.file_hash_cache and hash_type in self.file_hash_cache[fn]:
            return self.file_hash_cache[fn][hash_type]
        return None

    def set_file_hash(self, fn, hash_type, hash_val):
        if fn not in self.file_hash_cache:
            self.file_hash_cache[fn] = {}
        self.file_hash_cache[fn][hash_type] = hash_val

    def get_file(self, fn, file_type):
        if self.file_data[file_type][0] != fn:
            self.file_data[file_type] = (fn, open(fn, 'rb').read())
        return self.file_data[file_type][1]


def determine_same_file(origpath, destpath, fhc=None):
    '''
    First check if hashes of the two files match. If they don't match, they
    could still be the same image if metadata has changed so open the pixel
    data using PIL and compare hashes of that.
    '''
    if not fhc:
        fhc = FileHashCache()

    if len(fhc.file_hash_cache) > 1000:
        fhc.reset()

    orig_hash = fhc.get_file_hash(origpath, 'file')
    if not orig_hash:
        orig_hash = md5(fhc.get_file(origpath, 'orig')).hexdigest()
        fhc.set_file_hash(origpath, 'file', orig_hash)

    dest_hash = fhc.get_file_hash(destpath, 'file')
    if not dest_hash:
        dest_hash = md5(fhc.get_file(destpath, 'dest')).hexdigest()
        fhc.set_file_hash(destpath, 'file', dest_hash)

    if orig_hash == dest_hash:
        return True

    # Try matching on image data (ignoring EXIF)
    if os.path.splitext(origpath)[1][1:].lower() in ['jpg', 'jpeg', 'png', ]:
        orig_hash = fhc.get_file_hash(origpath, 'image')
        if not orig_hash:
            orig_hash = md5(Image.open(StringIO(fhc.get_file(origpath, 'orig'))).tobytes()).hexdigest()
            fhc.set_file_hash(origpath, 'image', orig_hash)

        dest_hash = fhc.get_file_hash(destpath, 'image')
        if not dest_hash:
            dest_hash = md5(Image.open(StringIO(fhc.get_file(destpath, 'dest'))).tobytes()).hexdigest()
            fhc.set_file_hash(destpath, 'image', dest_hash)

        if orig_hash == dest_hash:
            return True
    # TODO: Convert raw photos into temp jpgs to do proper comparison
    return False


def blacklisted_type(file):
    ext = file.split('.')[-1].lower()
    if ext in ['mov', 'mp4', 'mkv', 'xmp']:
        return True
    if file == '.DS_Store':
        return True
    return False

# def import_photos_from_dir(orig, move=False):
#     imported = 0
#     were_duplicates = 0
#     were_bad = 0

#     for r, d, f in os.walk(orig):
#         # if SYNOLOGY_THUMBNAILS_DIR_NAME in r:
#         #     continue
#         for fn in sorted(f):
#             filepath = os.path.join(r, fn)
#             dest = determine_destination(filepath)
#             if blacklisted_type(fn):
#                 # Blacklisted type
#                 were_bad += 1
#             elif not dest:
#                 # No filters match this file type
#                 pass
#             else:
#                 t = get_datetime(filepath)
#                 if t:
#                     destpath = '%02d/%02d/%02d' % (t.year, t.month, t.day)
#                     destpath = os.path.join(dest, destpath)
#                     mkdir_p(destpath)
#                     destpath = os.path.join(destpath, fn)

#                     if filepath == destpath:
#                         # File is already in the right place so be very careful not to do anything like delete it
#                         pass
#                     elif not os.path.exists(destpath):
#                         if move:
#                             shutil.move(filepath, destpath)
#                         else:
#                             shutil.copyfile(filepath, destpath)
#                         record_photo(destpath)
#                         imported += 1
#                         print('IMPORTED  {} -> {}'.format(filepath, destpath))
#                     else:
#                         print('PATH EXISTS  {} -> {}'.format(filepath, destpath))
#                         same = determine_same_file(filepath, destpath)
#                         print('PHOTO IS THE SAME')
#                         if same:
#                             if move:
#                                 os.remove(filepath)
#                                 were_duplicates += 1
#                                 print('DELETED FROM SOURCE')
#                         else:
#                             print('NEED TO IMPORT UNDER DIFFERENT NAME')
#                             exit(1)
#                             destpath = find_new_file_name(destpath)
#                             shutil.move(filepath, destpath)
#                             record_photo(destpath)
#                             imported += 1
#                             # print 'IMPORTED  {} -> {}'.format(filepath, destpath)

#                 else:
#                     print('ERROR READING DATE: {}'.format(filepath))
#                     were_bad += 1

#     if imported or were_duplicates:
#         print('\n{} PHOTOS IMPORTED\n{} WERE DUPLICATES\n{} WERE BAD'.format(imported, were_duplicates, were_bad))

# TODO: Get these working
# def import_photos_in_place(library_path):
#     orig = library_path.path
#     imported = 0
#     were_bad = 0

#     for r, d, f in os.walk(orig):
#         # if SYNOLOGY_THUMBNAILS_DIR_NAME in r:
#         #     continue
#         for fn in sorted(f):
#             filepath = os.path.join(r, fn)
#             if blacklisted_type(fn):
#                 # Blacklisted type
#                 were_bad += 1
#             else:
#                 modified = record_photo(filepath, library_path.library)
#                 if modified:
#                     imported += 1
#                     print('IMPORTED  {}'.format(filepath))

#     if imported:
#         print('\n{} PHOTOS IMPORTED\n{} WERE BAD'.format(imported, were_bad))


# def rescan_photo_libraries(paths=[]):
#     library_paths = LibraryPath.objects.filter(type='St', backend_type='Lo')
#     if paths:
#         library_paths = library_paths.filter(path__in=paths)

#     for library_path in library_paths:
#         print(f'Searching path for changes {library_path.path}')
#         library_path.rescan()

# ------------------------------------------------------------------------------


# ------------------------------------------------------------
# NOTE: MOVE THIS TO A FILE UTILITIES LIBRARY
# ------------------------------------------------------------
# SOURCE: https://github.com/tgbugs/pyontutils/blob/05dc32b092b015233f4a6cefa6c157577d029a40/ilxutils/tools.py
def is_file(path: str):
    """Check if path contains a file

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    if pathlib.Path(path).is_file():
        return True
    return False


def is_directory(path: str):
    """Check if path contains a dir

    Args:
        path (str): _description_

    Returns:
        _type_: _description_
    """
    if pathlib.Path(path).is_dir():
        return True
    return False


def tilda(obj):
    """wrapper for linux ~/ shell notation

    Args:
        obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    if isinstance(obj, list):
        return [
            str(pathlib.Path(o).expanduser()) if isinstance(o, str) else o for o in obj
        ]
    elif isinstance(obj, str):
        return str(pathlib.Path(obj).expanduser())
    else:
        return obj


def fix_path(path: str):
    """Automatically convert path to fully qualifies file uri.

    Args:
        path (_type_): _description_
    """

    def __fix_path(path):
        if not isinstance(path, str):
            return path
        elif "~" == path[0]:
            tilda_fixed_path = tilda(path)
            if is_file(tilda_fixed_path):
                return tilda_fixed_path
            else:
                exit(path, ": does not exit.")
        elif is_file(pathlib.Path.home() / path):
            return str(pathlib.Path().home() / path)
        elif is_directory(pathlib.Path.home() / path):
            return str(pathlib.Path().home() / path)
        else:
            return path

    if isinstance(path, str):
        return __fix_path(path)
    elif isinstance(path, list):
        return [__fix_path(p) for p in path]
    else:
        return path


def get_folder_size(filepath: str) -> int:
    """Get size of folder in bytes

    Args:
        filepath (str): path to directory

    Returns:
        int: folder size in bytes
    """
    total_size = 0
    for root, dirs, files in os.walk(filepath):
        for img in files:
            total_size += os.path.getsize(os.path.join(root, img))

    return total_size


def determine_destination(fn: str):
    ic(fn)
    extension = os.path.splitext(fn)[1][1:].lower()
    ic(extension)
    for output_filter in PHOTO_OUTPUT_DIRS:
        if extension in output_filter["EXTENSIONS"]:
            ic(output_filter["PATH"])
            return output_filter["PATH"]
    return None


def find_new_file_name(path):
    """
    If a file already exists in the same place with the same name, this
    function will find a new name to use, changing the extension to
    '_1.jpg' or similar.
    """
    counter = 1
    fn, extension = os.path.splitext(path)
    attempt = path
    while os.path.exists(attempt):
        attempt = "{}_{}{}".format(fn, counter, extension)
        counter += 1
    return attempt


def get_filename_and_dest_from_url(url: str):
    """Get filename from URL

    Args:
        url (str): url string

    Returns:
        _type_: string, string, string
    """
    dest_dir = determine_destination(url)
    fn = url.split("/")[-1]
    dest_path = str(pathlib.Path(dest_dir) / fn)

    return dest_dir, fn, dest_path


# def download_file(url, destination_path):
#     temp_path = tempfile.mktemp()
#     with requests.get(url, stream=True) as r:
#         with open(temp_path, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=32768):
#                 if chunk:
#                     f.write(chunk)
#     shutil.move(temp_path, destination_path)
#     return destination_path


def handle_download_file(url: str, destination_path: str):
    temp_path = tempfile.mktemp()
    with requests.get(url, stream=True) as r:
        with open(temp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
    shutil.move(temp_path, destination_path)
    return destination_path


async def download_and_save(url: str, dest_override=False, base_authority=""):
    rwlock = aiorwlock.RWLock()
    # SOURCE: https://github.com/aio-libs/aiohttp/issues/955
    # SOURCE: https://stackoverflow.com/questions/35388332/how-to-download-images-with-aiohttp
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=sslcontext if VERIFY_SSL else None)
    ) as http:
        url_file_api = pathlib.Path(url)
        filename = f"{url_file_api.name}"

        uri = uritools.urisplit(url)

        if not uri.authority:
            await rwlock.reader_lock.acquire()
            try:
                rich.print(
                    f"uri.authority = {uri.authority}, manually setting url variable"
                )
            finally:
                rwlock.reader_lock.release()
            url = f"{base_authority}/{url}"
            await rwlock.reader_lock.acquire()
            try:
                # rich.print(f"uri.authority = {uri.authority}, manually setting url variable")
                rich.print(f"url = {url}")
            finally:
                rwlock.reader_lock.release()

        if dest_override:
            filename = dest_override
            await rwlock.reader_lock.acquire()
            try:
                rich.print(f"filename = {dest_override}")
            finally:
                rwlock.reader_lock.release()
        # breakpoint()
        async with http.request(
            "GET", url, ssl=sslcontext if VERIFY_SSL else None
        ) as resp:
            if resp.status == 200:
                # SOURCE: https://stackoverflow.com/questions/72006813/python-asyncio-file-write-after-request-getfile-not-working
                size = 0
                try:
                    async with aiofile.async_open(filename, "wb+") as afp:
                        async for chunk in resp.content.iter_chunked(
                            1024 * 512
                        ):  # 500 KB
                            await afp.write(chunk)
                            size += len(chunk)
                except asyncio.TimeoutError:
                    # rich.print(f"A timeout ocurred while downloading '{filename}'")
                    pass

                return filename, size


def md5sum(path):
    hash_md5 = md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


#################################################################################################################################3
# Define functions to download an archived dataset and unpack it
class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url: str, filepath: str):
    directory = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(directory, exist_ok=True)
    if os.path.exists(filepath):
        print("Filepath already exists. Skipping download.")
        return

    with TqdmUpTo(
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        miniters=1,
        desc=os.path.basename(filepath),
    ) as t:
        urlretrieve(url, filename=filepath, reporthook=t.update_to, data=None)
        t.total = t.n


#################################################################################################################################3


async def go_partial(loop, urls: List[str]):
    # progress bar
    pbar = tqdm(urls)

    for url in pbar:
        pbar.set_description("Processing -> %s" % url)
        test_dest_dir, test_fn, test_dest_path = get_filename_and_dest_from_url(url)

        # handle_download_file_func = functools.partial(handle_download_file, test_images[0][0], test_images[0][1])
        handle_download_file_func = functools.partial(download_url, url, test_dest_path)

        # Run in a custom thread pool:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            dest = await loop.run_in_executor(pool, handle_download_file_func)

    return dest


def main():
    args = parser.parse_args()
    print()
    ic(args)
    print()
    return args


if __name__ == "__main__":
    start_time = time.time()

    args = main()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(go_partial(loop, args.urls))

    duration = time.time() - start_time
    print(f"Downloaded 1 site in {duration} seconds")

    # # single_file = "/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/asyncio_demo.png"
    # dd = determine_destination("https://i.imgur.com/kvSAxmy.png")
    # alt_file_path = find_new_file_name("/Users/malcolm/dev/bossjones/sandbox/dancedetector/dancedetector/advanced/asyncio_demo.png")
    # rich.print(f"dd, alt_file_path = {dd}, {alt_file_path}")

    # test_dest_dir, test_fn, test_dest_path = get_filename_and_dest_from_url("https://i.imgur.com/kvSAxmy.png")
    # ic(test_dest_dir, test_fn, test_dest_path)
