# pgRouting performance tuning made easy

> **Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04 as well as Ubuntu 20.04. Windows compatibility cannot be guaranteed.

## Motivation

[pgRouting](https://pgrouting.org/), the popular routing extension for the open source RDBMS Postgres has been around for quite some time now, preceding most other open source routing engines.
And while its flexibility has often been praised, pgRouting's performance is usually not what it's been known for. In this tutorial however, we want to show you that 
the opposite is true: with the right tweaks and tricks, pgRouting can provide blazingly fast routing even on large road data sets!


## Prerequisites & Dependencies

- PostgreSQL instance with **PostGIS and pgRouting enabled**, we recommend [Kartoza](kartoza.com)'s [docker image]([Kartoza](https://github.com/kartoza/docker-postgis)) (see [this tutorial](https://gis-ops.com/postgrest-tutorial-installation-and-setup/))
- osmconvert ([installation instructions](https://wiki.openstreetmap.org/wiki/Osmconvert)): easily clip OSM files
- [osm2po](http://osm2po.de/): create pgRouting topology from raw OSM data

## Step 1 – Preparing the OpenStreetMap Data

For our example, we will be working with OpenStreetMap data for Northern California.
