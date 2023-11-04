import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Get a value from the configuration file
cached_folder = config.get('data', 'cached_folder')
api_key = config.get('openai','api_key')

__all__ = [
    'cached_folder',
    'api_key'
]