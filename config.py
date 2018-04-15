import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PYTHON = 'python3.5'

DEBUG = False

# Override these (and anything else) in config_local.py
NIK4 = '/home/zverik/progr/git/nik4/nik4.py'
STYLES = {
    'veloroad': '/home/zverik/maps/brevet/veloroad.xml',
    'osm': '/home/zverik/osm/krym/carto/osm.xml'
}
PARAMETRIC = True
ROUTE = 'route'
SCALE = 'scale'
FORMATS = {
    'png': 'image/png',
    'svg': 'image/svg+xml',
    'pdf': 'application/pdf'
}

try:
    from config_local import *
except ImportError:
    pass
