<?php
/**
 * Plugin Name: GIS-OPS Spatial
 * Description: Add spatial functionalities to Wordpress and expose API to interact with them.
 * Version:     0.0.1
 *
 * Author:      Nils Nolde
 * Author URI:  https://gis-ops.com
 *
 * Text Domain: gis_ops_spatial
 *
 * @package GisOpsSpatial
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly
}

define('GISOPS_PLUGIN_PATH', dirname( __FILE__ ));

// Base api namespace that represents also the url
$baseNamespace = 'gisops/v1';

// Import custom spatial api endpoint classes
require_once GISOPS_PLUGIN_PATH . '/includes/spatial/gis_ops-spatial-data-wp-api.php';

// Instantiate the class
$gisopsSpatialData = new GisOpsSpatialData($baseNamespace);

// Import custom spatial listeners starters
require_once GISOPS_PLUGIN_PATH . '/includes/spatial/spatial-events-listener.php';

// Start the hook listener
$spatialEventsListener = new SpatialEventsListener();

