import os.path
import subprocess

try:
  VERSION = subprocess.check_output(["git", "describe", "--tags", "--always"]).decode('ascii').strip()
except Exception:
  VERSION = 'version_unknown'

AUDIO_CACHE_PATH = os.path.join(os.getcwd(), 'audio_cache')
NETEASE_DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'netease_download')
DISCORD_MSG_CHAR_LIMIT = 2000
