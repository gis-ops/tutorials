<?php
/**
 * GIS-OPS spatial listener to add new fields to existing endpoints.
 *
 * @package gis_ops_spatial\SpatialEventsListener
 */


class SpatialEventsListener {
    function __construct() {
     // Add GeoJSON field to Users schema
     add_action('rest_api_init', array( $this, 'addGeojsonFieldCallback'));
    }

    /**
    * Register hook to add a GeoJSON field to the /users endpoint.
    */
    public function addGeojsonFieldCallback() {
        register_rest_field(
            'user',
            'location',
            array(
                'get_callback' => [ $this, 'getGeojsonField'],
                'update_callback' => [ $this, 'updateGeojsonField'],
                'schema' => array(
                    'description' => 'User location in GeoJSON format.',
                    'type' => 'object',
                    'context' => array('view', 'edit')
                )
            )
        );
    }

    /**
    * Get GeoJSON data from /users endpoint
    *
    * @param Wp_User  $user GeoJSON as object
    * @param string   $field_name
    * @return Object  Value of GeoJSON field to be added to response
    */
    function getGeojsonField($user, $field_name) {
        return get_user_meta($user['id'], $field_name, true);
    }

    /**
     * Update GeoJSON data from User endpoint
     *
     * @param Object  $geojson
     * @param WP_Post $post
     * @param string   $field_name
     * @return bool|int  Value of GeoJSON field to be added to response
     */

    function updateGeojsonField($geojson, $post, $field_name) {
        return update_user_meta($post->id, $field_name, $geojson);
    }
}