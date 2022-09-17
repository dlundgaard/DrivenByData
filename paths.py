import os

FF1_CACHE_DIR = os.path.expanduser("~/Documents/ff1_cache")
os.makedirs(FF1_CACHE_DIR, exist_ok=True)

package_directory = os.path.dirname(os.path.abspath(__file__))
analysis_directory = os.path.join(package_directory, "analysis")

cache_directory = "caches"

telemetry_cache_directory = os.path.join(cache_directory, "telemetry")
laps_cache_directory = os.path.join(cache_directory, "laps")

f1_logo_path = os.path.join(package_directory, "assets", "images", "f1_logo.png")
d_logo_path = os.path.join(package_directory, "assets", "images", "d_logo_2021.png")
signature = os.path.join(package_directory, "assets", "images", "drivenbydata_signature.png")
social_tag = os.path.join(package_directory, "assets", "images", "social_tag.png")
