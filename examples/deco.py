# --- Configuration ---
import os

from mawaqit_alexa.util.ttl_cache import persistent_ttl_cache

WEEK_IN_SECONDS = 604800

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- Your Function ---
@persistent_ttl_cache(seconds=WEEK_IN_SECONDS, logger_callback=print, cache_dir=project_root+"/data/cache")
def get_masjid_config(masjid_url):
    # Simulate a slow database or network call
    # This print will only show up once per week!
    print(f"Connecting to DB for {masjid_url}...")

    return {"name": "Central Masjid", "capacity": 500}


# --- Testing it ---

# 1. First call: Runs the function
data1 = get_masjid_config("http://masjid-1.com")
# Output: 🐢 Fetching fresh data...

# 2. Second call (Immediate): Returns instantly from RAM
data2 = get_masjid_config("http://masjid-1.com")
# Output: ⚡ Returning cached data...

# 3. Different argument: Runs the function again (new key)
data3 = get_masjid_config("http://masjid-2.com")
# Output: 🐢 Fetching fresh data...
