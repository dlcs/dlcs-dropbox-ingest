import os
import distutils.util

DEBUG = bool(distutils.util.strtobool(os.getenv("DEBUG", "True")))
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
DLCS_API_BASE = os.getenv("DLCS_API_BASE")
DLCS_CUSTOMER_ID = os.getenv("DLCS_CUSTOMER_ID")
DLCS_SPACE_ID = os.getenv("DLCS_SPACE_ID")
DLCS_API_KEY_ID = os.getenv("DLCS_API_KEY_ID")
DLCS_API_SECRET_KEY = os.getenv("DLCS_API_SECRET_KEY")
PARENT_FOLDER = os.getenv("PARENT_FOLDER")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", default="10"))
