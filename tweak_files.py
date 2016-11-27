import os
import sys
import traceback
import json
from PIL import Image
import piexif
from datetime import datetime, timedelta

"""
Swap month and year that are separated by underscore. Quick hack, no smarts.
"""
def fix_date_in_filename(config):
   basedir = config['media_source_dir']
   print('Basedir: %s' % basedir)
   for entry in os.listdir(basedir):
      origname = entry
      p = origname.split('_')
      dumb_date = p[0].split('-')
      date = '%s-%s' % (dumb_date[1], dumb_date[0])
      newname = '%s_%s' % (date, p[1])
      origname_path = os.path.join(basedir, origname)
      newname_path = os.path.join(basedir, newname)
      print('%s -> %s' % (newname_path, newname_path))
      os.rename(origname_path, newname_path)

"""
19xx-yy-film_002.jpg
"""
def fix_date_in_filename_2(config):
   basedir = config['media_source_dir']
   print('Basedir: %s' % basedir)
   for entry in os.listdir(basedir):
      origname = entry
      p = origname.split('_')
      suffix = p[1]
      prefix = '1983-07-%s' % config['media_type']
      newname = '%s_%s' % (prefix, suffix)
      origname_path = os.path.join(basedir, origname)
      newname_path = os.path.join(basedir, newname)
      print('%s -> %s' % (newname_path, newname_path))
      os.rename(origname_path, newname_path)

def parse_date(date_str):
   dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
   return dt

def format_date(dt):
   str = datetime.strftime(dt, '%Y:%m:%d %H:%M:%S')
   return str

def make_target_dir_based_on_date(config):
   parentdir = os.path.split(config['media_source_dir'])[0]
   dt = parse_date(config['date_time_original'])
   targetdirname = '%04d-%02d-%02d - %s' % (dt.year, dt.month, dt.day, config['media_type'])
   targetdir = os.path.join(parentdir, targetdirname)
   n = 0
   while (os.path.exists(targetdir)):
      n += 1
      targetdirname = '%04d-%02d-%02d - %s_%03d' % (dt.year, dt.month, dt.day, config['media_type'], n)
      targetdir = os.path.join(parentdir, targetdirname)
   print('Making targetdir: %s' % targetdir)
   os.mkdir(targetdir)
   return (targetdir)

def rename_and_move(config, targetdir):
   sourcedir = config['media_source_dir']
   dt = parse_date(config['date_time_original'])
   prefix = '%04d-%02d-%02d' % (dt.year, dt.month, dt.day)
   print('Moving sourcedir: %s\ntargetdir: %s\nprefix: %s' % (sourcedir, targetdir, prefix))
   sequence_counter = 0
   for entry in os.listdir(sourcedir):
      sequence_counter += 1
      if (len(entry.split('_')) > 1):
         # Underscore expected to precede the sequence counter in a filename.
         suffix = entry.split('_')[1]
         if config['resequence']:
            # Replace existing sequence
            suffix = '%03d%s' % (sequence_counter, suffix[-4:])
      else:
         # No underscore found in filename. Assume no sequence exists. Add one to filename.
         suffix = '%03d%s' % (sequence_counter, suffix[-4:])

      newname = '%s_%s' % (prefix, suffix)
      origname_path = os.path.join(sourcedir, entry)
      newname_path = os.path.join(targetdir, newname)
      print('%s -> %s' % (newname_path, newname_path))
      os.rename(origname_path, newname_path)

"""
 Windows 0th attrs {
   270: b'The Title of Photo', 
   271: b'Camera Make', 
   272: b'Camera Model', 
   315: b'Author Name', 
   34665: 2138, 40091: (84, 0, 104, 0, 101, 0, 32, 0, 84, ...), 
   40092: (67, 0, 111, 0, 109, 0, 109, 0, 101, ...), 
   40093: (67, 0, 101, 0, 99, 0, 105, 0, 108, ...), 
   40094: (116, 0, 97, 0, 103, 0, 45, 0, 111, ...), 
   40095: (83, 0, 111, 0, 109, 0, 101, 0, 32, ...)
 }

 Windows exif attrs {
   36867: b'1983:11:11 09:44:53', 
   36868: b'1983:11:11 09:44:53', 
   37521: b'79', 
   37522: b'79'
 }

 Attrs currently set by this method {
   'Exif': {
      36867: b'1983:05:01 12:00:00'},
   '0th': {
      305: b'piexif', 
      34665: 281, 
      40092: (255, 254, 83, 0, 99, 0, 97, 0, 110, 0, 110, 0, 101, 0, 100, 0, 32, 0, 102, 0, 114, 0, 111, 0, 109, 0, 32, 0, 115, 0, 108, 0, 105, 0, 100, 0, 101, 0, 115, 0, 32, 0, 98, 0, 121, 0, 32, 0, 82, 0, 83, 0, 76, 0, 105, 0, 110, 0, 102, 0, 111, 0, 114, 0, 100, 0, 46, 0, 32, 0, 68, 0, 97, 0, 116, 0, 101, 0, 32, 0, 116, 0, 97, 0, 107, 0, 101, 0, 110, 0, 32, 0, 105, 0, 115, 0, 32, 0, 97, 0, 112, 0, 112, 0, 114, 0, 111, 0, 120, 0, 105, 0, 109, 0, 97, 0, 116, 0, 101, 0, 46, 0), 
      40093: (255, 254, 67, 0, 101, 0, 99, 0, 105, 0, 108, 0, 101, 0, 32, 0, 76, 0, 105, 0, 110, 0, 102, 0, 111, 0, 114, 0, 100, 0), 
      270: b'1983-05-film003', 
      271: b"Mom's Trusty Camera"}, 
   'GPS': {}, 
   '1st': {}, 
   'thumbnail': None, 
   'Interop': {}, 
   }

 Attrs after Google round trip. Retained everything; nothing was added. In Google Photos, the only 
 Windows attrs that have a visible effect are 'Date Taken' (Exif 36867) and the name of the 
 uploaded file. {
   'Exif': {
      36867: b'1983:10:22 12:00:00'}, 
   '0th': {
      305: b'piexif', 
      34665: 283, 
      40092: (255, 254, 83, 0, 99, 0, 97, 0, 110, 0, 110, 0, 101, 0, 100, 0, 32, 0, 102, 0, 114, 0, 111, 0, 109, 0, 32, 0, 51, 0, 53, 0, 109, 0, 109, 0, 32, 0, 102, 0, 105, 0, 108, 0, 109, 0, 32, 0, 98, 0, 121, 0, 32, 0, 82, 0, 83, 0, 76, 0, 105, 0, 110, 0, 102, 0, 111, 0, 114, 0, 100, 0, 46, 0, 32, 0, 68, 0, 97, 0, 116, 0, 101, 0, 32, 0, 116, 0, 97, 0, 107, 0, 101, 0, 110, 0, 32, 0, 105, 0, 115, 0, 32, 0, 97, 0, 112, 0, 112, 0, 114, 0, 111, 0, 120, 0, 105, 0, 109, 0, 97, 0, 116, 0, 101, 0, 46, 0), 
      40093: (255, 254, 67, 0, 101, 0, 99, 0, 105, 0, 108, 0, 101, 0, 32, 0, 76, 0, 105, 0, 110, 0, 102, 0, 111, 0, 114, 0, 100, 0), 
      270: b'1983-10_036', 
      271: b"Mom's Trusty Camera"},
   'GPS': {}, 
   '1st': {}, 
   'thumbnail': None, 
   'Interop': {}, 
   }
 Existing_metadata in LG G3 photo {
   'Exif': {
      36864: b'0220', 
      37121: b'\x01\x02\x03\x00', 
      40962: 4160,
      36867: b'2016:11:09 10:47:47', 
      36868: b'2016:11:09 10:47:47', 
      40965: 1158, 
      40960: b'0100', 
      37383: 2, 
      37385: 0, 
      37386: (3970, 1000),
      37520: b'273393', 
      37521: b'273393', 
      37522: b'273393', 
      40963: 3120, 
      37380: (0, 1), 
      33434: (1, 581), 
      33437: (240, 100), 
      41988: (100, 100), 
      42016: b'ee88e0edfc03cbfc0000000000000000', 
      40961: 1,
      37510: b'    FocusArea=100111111\x00\x00\x00\..., 
      34855: 50, 
      41987: 0}, 
   '0th': {
      272: b'LG-D851', 
      305: b'Picasa', 
      274: 1, 
      531: 1, 
      34853: 1108, 
      296: 2, 
      34665: 180, 
      282: (72, 1), 
      283: (72, 1), 
      271: b'LG Electronics'}, 
   'GPS': {
      0: (2, 2, 0, 0), # Exif.GPSInfo.GPSVersionID
      5: 0,            # Exif.GPSInfo.GPSAltitudeRef Indicates the altitude used as the reference altitude. If the reference is sea level and the altitude is above sea level, 0 is given. If the altitude is below sea level, a value of 1 is given and the altitude is indicated as an absolute value in the GSPAltitude tag. The reference unit is meters. Note that this tag is BYTE type, unlike other reference tags.
      6: (0, 1000)},   # Exif.GPSInfo.GPSAltitude in meters
 }
"""
def set_metadata(config, date_time_counter, fn):
   fn_sans_path_sans_ext = os.path.split(fn)[1].split('.')[0]

   zeroth_ifd = {
      piexif.ImageIFD.ImageDescription: fn_sans_path_sans_ext,
      piexif.ImageIFD.Make: config['make'],
      piexif.ImageIFD.XPAuthor: config['xp_author'].encode('utf-16'),
      piexif.ImageIFD.XPComment: config['xp_comment'].encode('utf-16'),
      piexif.ImageIFD.Software: config['software'],
      }

   exif_ifd = {
      piexif.ExifIFD.DateTimeOriginal: format_date(date_time_counter)
      }

   #gps_ifd = {
   #   piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
   #   piexif.GPSIFD.GPSAltitudeRef: 1,
   #   piexif.GPSIFD.GPSDateStamp: config['date_time_original']
   #   }

   #exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd, "GPS":gps_ifd}
   exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd}
   exif_bytes = piexif.dump(exif_dict)
   im = Image.open(fn)

   """
   PIL JPEG 'quality'
   The image quality, on a scale from 1 (worst) to 95 (best). The default is 75. 
   Values above 95 should be avoided; 100 disables portions of the JPEG compression 
   algorithm, and results in large files with hardly any gain in image quality.
   http://pillow.readthedocs.io/en/3.1.x/handbook/image-file-formats.html
   """
   im.save(fn, exif=exif_bytes, quality=85)

def print_metadata(fn):
   existing_metadata = piexif.load(fn)
   print('Existing_metadata in %s\n\t%s' % (fn, existing_metadata))

"""
Do all the stuff: 
   1) create target dir based on Date Taken
   2) rename photos based on Date Taken
   3) move photos to newly created target dir
   4) set metadata in photos including Date Taken
"""
def tweak_files(config):
   print('media_source_dir: %s' % config['media_source_dir'])
   targetdir = make_target_dir_based_on_date(config)
   rename_and_move(config, targetdir)
   date_time_counter = parse_date(config['date_time_original'])
   for entry in os.listdir(targetdir):
      try:
         ext = entry[-4:]
         if ext != '.jpg':
            continue
         fn = os.path.join(targetdir, entry)
         print('set metadata %s' % fn)
         set_metadata(config, date_time_counter, fn)
         date_time_counter += timedelta(minutes = 1)
      except ValueError as ve:
         print('%s\n\t%s' % (fn, ve))


################# BEGIN Main Template With Config ######################

def print_config_file(config):
   print('Config file located at:\n\t%s\nPoint "media_source_dir" path to your files. Use fully qualified path or relative path. Current working directory:\n\t%s' \
      % (config['config_file_name'], os.getcwd()))
   print('Current config contents:')
   with open(config['config_file_name'], 'r') as f:
      for line in f:
         print(line)

def save_config(config):
   with open(config['config_file_name'], 'w') as f:
      json.dump(config, f)

def normalize_config(config):
   config['config_file_name'] = config.get('config_file_name', r'edit_video_config.json')
   config['media_source_dir'] = config.get('media_source_dir', 'your_media_source_dir')
   config['make'] = config.get('make', 'Cannon')
   config['xp_author'] = config.get('xp_author', 'Some Author')
   config['xp_comment'] = config.get('xp_comment', 'Some Comment')
   config['software'] = config.get('software', 'piexif')
   config['date_time_original'] = config.get('date_time_original', '1970:01:01 12:00:00')
   config['media_type'] = config.get('media_type', 'film')
   config['resequence'] = config.get('resequence', False)

def create_default_config(config_file_name):
   config = {'config_file_name':config_file_name}
   normalize_config(config)
   save_config(config)
   print('New config file created.')
   print_config_file(config)

def load_config(config_file_name):
   with open(config_file_name, 'r') as f:
      config = json.load(f)
   config['config_file_name'] = config_file_name
   return config

def main():
   config_file_name = r'media_meta_tweak_settings.json'

   try:
      config = load_config(config_file_name)
      if not os.path.isdir(config['media_source_dir']):
         print('media_source_dir is not a file:\n\t%s' % config['media_source_dir'])
         print_config_file(config)
         return 1
      normalize_config(config)
   except (FileNotFoundError):
      create_default_config(config_file_name)
      raise

   tweak_files(config)

if __name__ == '__main__':
   try:
      main()
      print('\n[Normal Exit]')
   except (KeyboardInterrupt):
      print('\n[User Exit]')
   except (SystemExit):
      print('\n[System Exit]')
