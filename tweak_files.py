import os
import json

def tweak_files(config):
   print('Tweak stuff here')
   print_config_file(config)
   
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
      if not os.path.isfile(config['media_source_dir']):
         print('media_source_dir is not a file:\n\t%s' % config['media_source_dir'])
         print_config_file(config)
         return 1
      normalize_config(config)
      tweak_files(config)
   except (FileNotFoundError):
      create_default_config(config_file_name)

if __name__ == '__main__':
   try:
      main()
      print('\n[Normal Exit]')
   except (KeyboardInterrupt):
      print('\n[User Exit]')
   except (SystemExit):
      print('\n[System Exit]')
