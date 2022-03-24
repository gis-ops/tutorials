<?php

/**
 * GIS-OPS Spatial Data Wp Api
 *
 * @package gis_ops_spatial\GisOpsSpatialData
 */


class GisOpsSpatialData {

    private $baseNamespace;

    public function __construct($baseNamespace)
    {
        $this->baseNamespace = $baseNamespace;
        add_action('rest_api_init', array( $this, 'register_routes'));
    }

    /**
     * Get plugin namespace.
     * @return string
     */
    public function get_namespace() {
        return $this->baseNamespace."/spatial";
    }

    /**
     * Register boundless api routes for WP API v2.
     */
    public function register_routes() {
        register_rest_route( $this->get_namespace(), 'user/(?P<id>\d+)', array(
            'methods' => 'POST',
            'callback' => [$this, 'update_user']
        ));
        register_rest_route( $this->get_namespace(), 'user/(?P<id>\d+)/intersect', array(
            'methods' => 'GET',
            'callback' => [$this, 'get_intersected']
        ));
    }

    /**
     * Updater for /spatial/user POST endpoint. Inserts location into user_meta_data.
     *
     * @param WP_REST_Request $request Full request data.
     * @return WP_REST_Response|WP_Error Either user data is returned or HTTP 404
     */
    function update_user($request) {
        $user = get_user_by('id', $request['id']);
        if ($user) {
            update_user_meta($request['id'], 'location', $request['location']);
            return new WP_REST_Response("Successfully added a location to user ".$user->display_name, 200);
        }
        else {
            return new WP_Error('no_user', 'Invalid User ID', array('status' => 404));
        }
    }

    /**
     * Gets the list of users whose location intersects with the passed bounding box.
     *
     * @param WP_REST_Request $request Full request data.
     * @return WP_REST_Response List of users
     */
    function get_intersected($request) {
        list($min_x, $min_y, $max_x, $max_y) = explode(',', $request->get_param('bbox'));
        $min_x = floatval($min_x);
        $max_x = floatval($max_x);
        $min_y = floatval($min_y);
        $max_y = floatval($max_y);

        $coordinates = array(array(
            array($min_x, $min_y),
            array($max_x, $min_y),
            array($max_x, $max_y),
            array($min_x, $max_y),
            array($min_x, $min_y)
        )) ;
        $bounding_box = array(
            "type" => "Feature",
            "geometry" => array(
                "type" => "Polygon",
                "coordinates" => $coordinates
            ),
            "properties" => array(
                "id" => "undefined"
            )
        );

        $users_matches = get_users(array(
            'users_per_page' => -1,
            'meta_key'   => 'location',
            'meta_value' => $bounding_box,
            'meta_compare' => 'ST_Intersects'
        ));

        $controller = new WP_REST_Users_Controller();
        $users_response = [];
        foreach ( $users_matches as $user ) {
            $data = $controller->prepare_item_for_response($user, $request);
            $users_response[] = $controller->prepare_response_for_collection($data);
        }

        return new WP_REST_Response($users_response, 200);
    }
}
