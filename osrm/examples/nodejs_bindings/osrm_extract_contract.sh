wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf
node_modules/osrm/lib/binding/osrm-extract berlin-latest.osm.pbf -p node_modules/osrm/profiles/car.lua
node_modules/osrm/lib/binding/osrm-contract berlin-latest.osrm