#!/usr/bin/env python3
import sys
import os
import re

if len(sys.argv) < 3:
    print("Prepares a mapnik xml style for get-veloroad.")
    print("Usage: {} <input.xml> <output.xml> [<before_layer>]".format(sys.argv[0]))
    sys.exit(1)

if len(sys.argv) > 3:
    before_layer = sys.argv[3]
else:
    before_layer = 'places|nepopulated'

BEFORE_LAYERS = re.compile('^\s*<Style[^>]*name="(?:{})"'.format(before_layer))
ROUTE_LAYER = '''
<Style name="route" filter-mode="first">
  <Rule>
    <MinScaleDenominator>750000</MinScaleDenominator>
    <LineSymbolizer stroke-width="4" stroke="#012d64" stroke-linejoin="round" stroke-linecap="round" />
  </Rule>
  <Rule>
    <MaxScaleDenominator>750000</MaxScaleDenominator>
    <LineSymbolizer stroke-width="5" stroke="#012d64" stroke-linejoin="round" stroke-linecap="round" />
  </Rule>
</Style>
<Layer name="route" status="off" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
  <StyleName>route</StyleName>
  <Datasource>
    <Parameter name="type"><![CDATA[ogr]]></Parameter>
    <Parameter name="file"><![CDATA[${{route:{}/route.gpx}}]]></Parameter>
    <Parameter name="layer"><![CDATA[tracks]]></Parameter>
    <Parameter name="all_layers"><![CDATA[route_points,routes,track_points,waypoints]]></Parameter>
  </Datasource>
</Layer>
'''.format(os.path.abspath(os.path.dirname(sys.argv[0])))

wrote = False
with open(sys.argv[1], 'r') as f:
    with open(sys.argv[2], 'w') as ff:
        for line in f:
            if not wrote and BEFORE_LAYERS.match(line):
                ff.write(ROUTE_LAYER)
                wrote = True
            ff.write(line)
