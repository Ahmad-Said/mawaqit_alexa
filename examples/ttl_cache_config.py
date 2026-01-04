# --- Configuration ---
import os

from mawaqit_alexa.util import ttl_cache

def config_ex_cache():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_path = project_root + "/data/cache"

    ttl_cache.configure_cache(cache_path)
