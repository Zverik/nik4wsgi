import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PYTHON = 'python3.6'

DEBUG = False

# Override these (and anything else) in config_local.py
NIK4 = '/home/zverik/progr/git/nik4/nik4.py'

# Style descriptions: slug, name, path to xml, parametric?
STYLES = [
    ['veloroad', 'Veloroad', '/home/zverik/maps/brevet/veloroad.xml', True],
    ['osm', 'OSM-Carto', '/home/zverik/osm/krym/carto/osm.xml', False],
]
FORMATS = [
    ['png', 'PNG', 'image/png'],
    ['svg', 'SVG', 'image/svg+xml'],
    ['pdf', 'PDF', 'application/pdf'],
]
TILES = {
    'veloroad': ['http://tile.osmz.ru/veloroad/{z}/{x}/{y}.png',
                 'Map &copy; OpenStreetMap | Tiles &copy Ilya Zverev'],
    'osm': ['https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            'Map &copy; OpenStreetMap'],
}

# Parameter names for parametric styles
ROUTE = 'route'
SCALE = 'scale'

try:
    from config_local import *
except ImportError:
    pass
