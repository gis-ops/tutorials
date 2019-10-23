# WordPress Plugin development - Enable spatial capabilities

This tutorial will give an introduction into enabling WordPress with spatial capabilities via a custom plugin and expose those functionalities via the built-in REST API.

It will make use of the excellent [WP GeoMeta plugin](https://github.com/BrilliantPlugins/wp-geometa) by [Michael Moore](https://twitter.com/stuporglue). It hasn't been maintained for a while, however it's still running strong with the newest WordPress version (5.2.x at the time of writing). It will serve as the basis for the plugin you'll develop.

**Note**, that the final result of this tutorial is only useful if you deploy WordPress as a backend and use a frontend framework (e.g. React, AngularJS) to access WordPress via its REST API, see also [Motivation](#Motivation). However, the steps included to get to the final result can also be helpful when using WordPress as frontend.

The final plugin can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/wordpress/examples/metageo_plugin/gisops_wp_spatial).

![GeoMeta Plugin example](https://github.com/gis-ops/tutorials/raw/master/wordpress/img/wp_geometa_example.png)
*WP GeoMeta Plugin example with a bunch of polygons*

### Motivation

WordPress is powerful. Very powerful. Most people only know it for its fool-proof CMS capabilities to build blogs and websites. However, unless you want to build static sites, WordPress is actually not a good solution. For more complex and/or dynamic websites proper frontend frameworks, like React or AngularJS, are a far better choice. But even then there's no need to ditch WordPress.

Its real power lies in its backend. WordPress core provides complete user management out-of-the-box and mighty plugins like WooCommerce make very complex web shop setups a breeze. And the best thing: it all comes with a well-documented and reeeaaally easily extendable **REST API**. You start to see its real merits?

However, we're immediately missing spatial capabilities and likely you are too, if you landed here. What if you want to query the geographical location of users (provided you have their locations)? Or what if you set up a web shop for vector print maps and want to query your WooCommerce store by bounding box to intersect the map products available within the lateral extent of a web map app (*Spoiler*: that's how we actually got here!)? Fear not, read on and learn how to do just that. All contained within your very own WordPress installation, no PostGIS server and even fully functional on shared hosts.

**Goals**:

- Get familiar with the [WP GeoMeta Plugin](https://github.com/BrilliantPlugins/wp-geometa) by [Michael Moore](https://twitter.com/stuporglue)
- Create a WordPress plugin from scratch
- Extend existing WordPress REST API routes with new fields
- Extend WordPress REST API with custom routes
- Add `ST_Intersects` functionality to WordPress

**Plugin functionality**:

You will create a custom route with the WordPress REST API, which will be able to receive a bounding box and return a list of users which are located within this bounding box.

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **WordPress <= v5.2.1**

## Prerequisites

- WordPress >= v5.0.0
- MySQL >= 5.7
- Basic understanding of WordPress and ideally PHP

## 1 General setup

Your WordPress installation can be remote on a server or local and natively on the host or in a Docker container. That's entirely up to you. However, we do recommend doing it locally with Docker, as you'll need to do quite a bit of PHP programming in the `wp-content/plugins` folder. So you'll need the files offline, plus you don't want to litter your precious environment with the likes of PHP ;)

For convenience, we include a `docker-compose.yml` which you can run to setup a bare-metal WordPress installation and exposes the `wp-content` directory, so you can start developing instantly with the IDE of your choice. Upon `docker-compose up -d`, a new directory `./wp-content` will be available, which contains most WordPress files and most importantly the `plugins` directory.

To be able to develop in this directory, you'll need to change the permissions of `wp-content`: `sudo chmod -R 777 wp-content` (no worries, it's just localhost!).

WordPress is now available on http://localhost:8090. If you haven't done so already, go through the installation process now. Once installed, you need to **change the permalinks settings** to enable "normal" access to the REST API. In *Settings* ► *Permalinks*, switch to the *Post name* URL structure. Just to see if it works, call http://localhost:8090/wp-json, which should give you the full API specifications.

## 2 WP GeoMeta Plugin

[Michael Moore](https://twitter.com/stuporglue) developed this plugin back in 2017 when he presented it on the Boston 2017 FOSS4G conference. Since then it's unfortunately been fairly quiet on the project. However, it's still alive and kicking on WordPress v5.2.x. So, let's get started.

### Details

The GeoMeta plugin enables your WordPress installation to save and query spatial features. This is not really helpful unless there are other plugins making use of this functionality. This is what you'll do during this tutorial.

GeoMeta Plugin enables other plugins to:
- insert spatial data in spatially enabled tables via WordPress meta queries
- use spatial functions to query the spatial tables via WordPress meta queries, also passing geometries as arguments

**TL;DR**
Upon installation, it creates 4 new databases which are spatially enabled and complement their respective WordPress `meta` counterparts with a `_geo` extension in the table name:

- `wp_commentmeta_geo`: Holding spatial metadata for the comment table.
- `wp_postmeta_geo`: Holding spatial metadata for the posts table.
- `wp_termmeta_geo`: Holding spatial metadata for the term table.
- `wp_usermeta_geo`: Holding spatial metadata for the users table. This one you'll use in this tutorial.

So, you see, it's only mimicking the `meta` tables. Those are the tables which store all kinds of additional information about their core counterparts. E.g. the core `wp_users` table only stores the basic information like email, login name, hashed password etc. Its `meta` equivalent `wp_usermeta` stores uncritical optional information, like first name, last name etc in `key` and `value` columns. WP GeoMeta clones that database model to the `wp_usermeta_geo` table and extends the table with spatial functionality and a spatial index. That enables the plugin to interact with common WP meta queries, which other plugins can use to their advantage. WP meta queries request the core features (posts, users etc.) by its related metadata. You'll shortly see the general meta query syntax and you'll understand better.

And now comes the magic: WP GeoMeta auto-detects when a plugin inserts a GeoJSON to one of the above `meta` tables via a WP meta query. It then converts the GeoJSON in its \*`_geo` equivalent table to the data model a WP meta query would expect and converts the GeoJSON geometry to the spatial format MySQL understands. Thus you can now use all MySQL spatial functions to query posts, users, comments or terms from within other plugins. Love it!

### Setup

First, clone the plugin repository to `./wp-content/plugins` and change the ownership to apache's `www-data` user:

```bash
cd wp-content/plugins

git clone https://github.com/BrilliantPlugins/wp-geometa

cd wp-geometa

git submodule update --init --recursive

cd ..

sudo chown -R www-data:www-data wp-geometa
```

Now you can go into your WordPress Administration page and activate the plugin. Upon successful activation, you'll see a *WP-GeoMeta* entry in the *Tools* menu:

![Plugin activate](https://github.com/gis-ops/tutorials/raw/master/wordpress/img/wp_geometa_activate.png)

### Usage

If you skip over to the UI of the plugin in *Tools* ► *Wp-GeoMeta*, you'll see quite a few tabs. A few of them are really helpful for sanity checks:

***Your Data*** displays a Leaflet map visualizing the data loaded in the database.
***System Status*** shows you the current status of your plugin and spatial data. The entries ***Geo Tables Exist!***, ***Geo Tables Indexed!*** and ***All Spatial Data Loaded!*** should all be green, otherwise there's a critical problem.
***Your Functions*** is a quick reference for the functions your MySQL installation holds available.

In theory, you should be able use the ***Import Data*** functionality. However, we could not get it working on `localhost` and suspect it's using deprecated WordPress functionalities. Anyways, it's of very limited use as we're aiming to add spatial data through a custom POST endpoint, not manually one-by-one.

## 3 Plugin skeleton

WordPress plugins are far less verbose and intimidating than most other plugin architectures we've seen. Believe us, we didn't have a single clue about PHP before starting out on this and we managed to get the entire job done within 2 days. It's unbelievably easy, so kudos to the WordPress core team. Amazing work.

That being said, this section is for sure not a best-practice guide for WordPress plugin development, but rather a working and practical solution.

### Setup

First, create a new plugin directory in `./wp-content/plugins` with your plugin name (e.g. `gis_ops_spatial`;)) and give it the right permissions. While you're at it, also setup the other necessary folders:

```bash
mkdir -p ./wp-content/plugins/gis_ops_spatial/includes/spatial
sudo chown -R www-data:www-data ./wp-content/plugins/gis_ops_spatial
```

### Add plugin base

Create a new file in `wp-content/plugins/gis_ops_spatial` and call it `gis_ops.php` (or whatever you like). This will be the entrypoint of the plugin and call all other PHP classes you will define:

```php
<?php
/**
 * Plugin Name: GIS-OPS Spatial
 * Description: Add spatial functionalities to WordPress and expose API to interact with them.
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
```

The header in this file is how you let WordPress know of its existence. It has to comply with the [WordPress header requirements](https://developer.wordpress.org/plugins/the-basics/header-requirements/) and at the very minimum contain the entry `* Plugin Name: xxx`.  

After you saved the file you can go back to the WordPress Administration site and activate the (still unfunctional) plugin. In the next sections you'll add functionality.

## 4 Add location to users

Let's dive into adding a new REST API route. After this section, you'll have spatial data in your MySQL `wordpress` database that you can view in the GeoMeta plugin dashboard. This is one of the sections that only makes sense if you access the WordPress backend from a frontend technology.

Here's the catch though: if you want a painless way to insert data to the `user` table to quickly show results, you need to do things a little differently from what you'd actually do (or we'd recommend) in a production scenario. Those standard WordPress tables are protected against unauthenticated API calls to update or insert records. For quite obvious reasons. Since you don't want to do deal with WordPress authentication at this point, we'll show you both ways: a bad and hacky way and the way you'd normally go about this.

### Add a new API route - hacky workaround

First, you'll see the hacky way. **Note**, this is bypassing built-in WordPress security features and should only be implemented for demonstration.

Add a new file in `wp-content/plugins/gis_ops_spatial/includes/spatial`, name it `gis_ops-spatial-data-wp-api.php` and add the following content:

```php
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
}
```
WordPress made the genius design decision to make it ridiculously easy to extend its functionality. This is usually done via [`action`](https://codex.wordpress.org/Plugin_API/Action_Reference) and [`filter`](https://codex.wordpress.org/Plugin_API/Filter_Reference) hooks, with which you can insert arbitrary functions into core WP functions where they will be executed. A comprehensive list is available on [Adam Browns's blog](https://adambrown.info/p/wp_hooks/version/5.1), albeit only up to v5.1.

In the constructor of the `GisOpsSpatialData` class, you add your custom function `register_routes` to the WP core function `rest_api_init` as an `action`, which is responsible for initializing the WP REST API.

The `register_routes` function only calls the core WP function [`register_rest_route`](https://developer.wordpress.org/reference/functions/register_rest_route/), which will add a custom route to the REST API. Its arguments are as follows:

- `namespace`: this is the the base URL you want this route to be accessible in, i.e. everything which comes in between `http://localhost:8090/wp-json/` and the `route` name. In this class it's built from the plugin's base `namespace`, i.e. `gisops/v1` plus `/spatial`
- `route`: the name of the route plus optional path parameter(s). The path parameter follows the pattern `(?P<param_name>regex)`, so you can define any regular expression after the parameter name. Multiple path parameters are allowed. **Note**, the regular expression **has to be valid**. So, in this example the final API route would be `http://localhost:8090/gisops/v1/spatial/user/1` for the first user.
- `args`: named array of arguments. It usually includes the arguments `methods` and `callback`:
  - `methods`: string of comma-separated HTTP methods. E.g. `'POST,PATCH'` or just `'POST'`
  - `callback`: the function to be called when the HTTP method(s) was triggered
  - (options) `permission_callback`: can be used to determine who's allowed to access the resource. Usually using WordPress built-in `current_user_can(arg)` where `arg` is a [WordPress role or capability](https://wordpress.org/support/article/roles-and-capabilities/). In your case, don't specify it, as the whole point of the hacky workaround is to circumvent authorization.

So, when our new route receives a POST request the function `update_user` is executed. That method takes the full `request` parameters as input and just inserts the location information as-is to the `wp_usermeta` MySQL table via an update meta query. If the user wasn't found, it will return a 404.

### Add to plugin skeleton - hacky workaround

For this new functionality to take effect, you need to instantiate the class in the plugin base. So, you `require` it in `gis_ops.php` and create an instance. Remember, the constructor of our new class includes a `rest_api_init` action hook. So, only by instantiating the class you already tell WordPress to add your custom endpoint.

To do so, add the following bit to `/wp-content/plugins/gis_ops_spatial/gis_ops.php` at the very bottom:

```php
// Import custom spatial api endpoint classes
require_once GISOPS_PLUGIN_PATH . '/includes/spatial/gis_ops-spatial-data-wp-api.php';

// Instantiate the class
$gisopsSpatialData = new GisOpsSpatialData($baseNamespace);
```

### Try it out - hacky workaround

Finally you can see all this actually worked. If you didn't do so yet, activate now your plugin on the WordPress Administration site. Then flip over to your favorite HTTP handler (we recommend [Postman](https://www.getpostman.com), but `curl` will also do) and fire against your new endpoint. For convenience, this should work from your terminal:

```bash
curl -X POST \
  http://localhost:8090/wp-json/gisops/v1/spatial/user/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "location": {
        "type": "feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                29.024402,
                40.981047
            ]
        }
    }
}'
```

If you don't get a HTTP 200 and a message similar to `"Successfully added a location to user nils"`, there's something wrong and you better review all steps again.

### Add a new API route - the right way

With the hacky workaround just about everyone can add or edit a specific user's location. No authentication required. This is usually not what you'd like. The admin, or the user the change concerns, should be the only ones being allowed to update the location. So, here we present what we'd do for a live site. Code-wise this is actually the easier solution.

First, forget about all the changes you did to `gis_ops-spatial-data-wp-api.php`. Instead, create a new file in `./wp-content/plugins/gis_ops_spatial/includes` and call it `spatial-events-listener.php`. The new method will be to add a new field to an existing endpoint: the built-in `/users`. BTW, you'll have to do some of this work in the next section anyways, since so far, you're only able to update a user's location, but you can't pull that information yet by any GET request.

Paste the following code into the new file:

```php
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
```

The `addGeojsonFieldCallback` function only calls the WP core `register_rest_field` function, which ... well, you get the idea. It takes as arguments:

- `object_type`: the type of object whose route response you'd like to customize, here `user`. Could also be `post`, `comment` or `term` etc.
- `attribute`: the name of the attribute you'd like to register, here `location` (you should be confident it's not conflicting with existing fields for that endpoint)
- `something`: an array defining
  - `get_callback`: the function which will be called when the route gets a GET request
  - `update_callback`: the function which will be called when the route gets a POST/PUT/PATCH HTTP request
  - (optional) `schema`: set the expected schema for this data field. Only informational purpose

The API callback function `updateGeojsonField` couldn't be any easier: all you do is `update` the meta data entry for your field with the WordPress integrated function [`update_user_meta`](https://developer.wordpress.org/reference/functions/update_user_meta/). The parameters are added during the callback by WordPress.

### Add to plugin skeleton - The right way

Also here, since the `register_rest_field` function is executed during the `__construct`ion of the new listener class, you only have to instantiate it in the plugin base by adding the following lines to the very bottom in `gis_ops.php`:

```php
// Import custom spatial listeners starters
require_once GISOPS_PLUGIN_PATH . '/includes/spatial/spatial-events-listener.php';

// Start the hook listener
$spatialEventsListener = new SpatialEventsListener();
```

### Try it out - The right way

That's not so easy, since POSTing to the `users` endpoint is restricted to certain privileges, so you can't just `curl` or use `Postman` easily. WordPress comes with cookie authentication out-of-the-box. Which is cumbersome to implement client-side if you're using a frontend framework. And the problem is: that's the **only** authentication WordPress allows by default.

Thanks to the rich plugin world around WordPress (which clearly can be a curse too..), there are [several alternative ways of authentication](https://wordpress.org/plugins/tags/authentication/) to choose from, including social login, basic authentication, LDAP and many more. However, our favorite which works very well with client frameworks: [JWT Authentication](https://wordpress.org/plugins/jwt-authentication-for-wp-rest-api/). The documentation is straight-forward, so the setup won't be part of this tutorial.

## 5 Get locations from users

So far, you can only *add* a location to user entries. And actually that would suffice for our goal of being able to intersect its geometries with a user-provided polygon. But maybe you'd like to just display the location somewhere in the user profile. For that purpose, you'd need to be able to retrieve the location GeoJSON. If you already added a user following the [*Try it out - hacky workaround*](#try-it-out-hacky-workaround) section, you can see what happens right now when you try to retrieve the user you added a location to: [http://localhost:8090/wp-json/wp/v2/users/1](http://localhost:8090/wp-json/wp/v2/users/1). Yep, there's no `location` field being returned. Let's fix that.

### Add a new field for GET requests

If you worked through the *"- The right way"* sections to update the `location` for a user, the code needed for this will look all too familiar.

If not, create a new file in `./wp-content/plugins/gis_ops_spatial/includes` and call it `spatial-events-listener.php`. Paste the following contents (or update the relevant code in case you worked through the previous sections):

```php
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
}
```

For a more thorough explanation of the process, refer to [*Add a new API route - the right way*](#add-a-new-api-route-the-right-way). Here you just use `get_callback` and `get_user_meta` instead of their `update_` equivalents.

### Try it out

That's already enough to now also retrieve the `location` field when GETting users from WordPress. Try the same query again: [http://localhost:8090/wp-json/wp/v2/users/1](http://localhost:8090/wp-json/wp/v2/users/1).

## 6 Filter users by bounding box

The final step in this tutorial: implement functionality by which to spatially filter users by polygon. To keep things simple it will only be a bounding box.

After this section you will be able to call a new REST API endpoint called `/user/<id>/intersect` with a `bbox` query parameter and it will return a list of users whose `location` intersects with the passed `bbox`. This could be helpful if you (for what reason soever) want to display a [leaflet](https://leafletjs.com) map with the locations of your users in your frontend framework.

### Add route for spatial intersection

At this point, you only have to add a REST API route, which executes a function spatially intersecting a supplied bounding box with the users' locations.

The code build on top of what you've done in [Add a new API route - hacky workaround](#add-a-new-api-route-hacky-workaround), so we won't explain all the nitty-gritty details, but focus on the new stuff:

```php
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
        register_rest_route( $this->get_namespace(), 'user/(?P<id>\d+)/intersect', array(  // <== new stuff
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
    function get_intersected($request) {  // <== new stuff
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
```

So, you'll go about this in a very similar way as you did when adding the workaround API endpoint to update a user's location: you register a new route with `register_rest_route`, where you add a callback specifying what should be done, when the route is called. In this case, you'll add a `GET` endpoint which listens on the route `user/(?P<id>\d+)/intersect`.

The callback expects a parameter called `bbox` in the request. Since this is a GET request, you'll add the parameter as a query string parameter to our requests. The `bbox` parameter is also expected to follow a certain format, i.e. `min_lon,min_lat,max_lon,max_lat` which is equivalent to the X/Y comma-separated coordinates of a SE and NW point spanning a bounding box. The callback then builds a GeoJSON object from the bounding box (possibly more verbose than necessary).

The GeoJSON object is then used in a WordPress meta query using [`get_users`](https://developer.wordpress.org/reference/functions/get_users/). The `meta_compare` argument is the operator which is used to compare the `meta_value` with all values of the `meta_key` stored in the `wp_usermeta` table. Usually the `meta_compare` operator is a standard SQL comparison operator, like `=`, `>` or `IN`. And here is the magic again: WP GeoMeta automatically detects when the `meta_value` is a GeoJSON (object or even string) and allows you to use MySQL's spatial functions to be utilized as a `meta_compare` operator. So, this little piece of code accomplishes the whole spatial functionality: it returns the list of users whose location is intersecting with the provided bounding box from the API call.

At the very end, it just constructs the response using built-in `WP_REST_Users_Controller` functions. As the class name says, that class controls the users REST behavior.

### Try it out

Finally, you're at the step that should feel really good: experiencing that the above code actually works.

The new GET endpoint to filter users by bounding box is available on `http://localhost:8090/wp-json/gisops/v1/spatial/user/<user_id>/intersect`. As explained above, the code expects a `bbox` parameter in a certain format. Gladly, that format happens to be the export format of the most user-friendly bounding box generator by [Klokantech](https://www.klokantech.com): https://boundingbox.klokantech.com.

In the example above you used our office location at [Friedrichstraße 123, 10117 Berlin](https://www.openstreetmap.org/node/1552051608). Just search for the address in Klokantech's UI, zoom there and use the bounding box drawer in the upper left to draw a bbox around your address. In the lower left, you can choose `CSV` format and copy the CSV-style bounding box:

![Plugin activate](https://github.com/gis-ops/tutorials/raw/master/wordpress/img/wp_geometa_bbox_selector.png)

Then use that bounding box value to add to your GET request:

http://localhost:8090/wp-json/gisops/v1/spatial/user/1/intersect?bbox=13.3860517669,52.525561967,13.3885284622,52.5271369451

Hopefully, you also get one single user returned. If there's any other response, you likely did something wrong in the code, the bounding box or the user's location(s).

To additionally confirm that it's working as intended, try to add a bounding box where you're sure there will be no user intersected or add new users with different locations and try different bounding boxes.

## 7 Final plugin

Your final plugin structure should look like this:

```bash
├── gisops_wp_spatial
│   ├── gis_ops.php
│   └── includes
│       └── spatial
│           ├── gis_ops-spatial-data-wp-api.php
│           └── spatial-events-listener.php
```

If you want to verify your results, you can find the code for the final plugin in our [repository](https://github.com/gis-ops/tutorials/tree/master/examples/metageo_plugin/gisops_wp_spatial).

To get you started right away, we have included a `docker-compose.yml`. Go through the [General Setup](#1-general-setup) if you're having trouble with `docker-compose`.

To include the full plugin to WordPress, just copy the `gisops_wp_spatial` folder to `./wp-content/plugins` and activate it in the WordPress Admin site.
