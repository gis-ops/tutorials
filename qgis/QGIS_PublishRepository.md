### QGIS Tutorials

This tutorial is part of our QGIS tutorial series:

- [QGIS 3 Plugins - Plugin 101](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/)
- [QGIS 3 Plugins - Qt Designer Explained](https://gis-ops.com/qgis-3-plugin-tutorial-qt-designer-explained/)
- [QGIS 3 Plugins - Signals and Slots in PyQt](https://gis-ops.com/qgis-3-plugin-tutorial-pyqt-signal-slot-explained/)
- [QGIS 3 Plugins - Plugin Development Part 1](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-1/)
- [QGIS 3 Plugins - Plugin Development Part 2](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-explained-part-2/)
- [QGIS 3 Plugins - Set up Plugin Repository](https://gis-ops.com/qgis-3-plugin-tutorial-set-up-a-plugin-repository-explained/)

---

# QGIS 3 Plugins - Set up Plugin Repository Explained

![Custom repos example](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/repo_front.png)

A private QGIS plugin repository can be used to distribute QGIS plugins which are not fit for purpose for the [official QGIS plugin repository](https://plugins.qgis.org).

In this tutorial you will learn how to set up your own QGIS plugin repository and register it in QGIS. You will use a simple yet powerful (the perfect combination IMHO) PHP project by the avid geospatial blogger and developer [Michel Stuyts](https://michelstuyts.be). Check out [his blog](https://stuyts.xyz) too, some very nice inspirations all around QGIS and mapping.

**Goals**:

- set up a QGIS repository, either directly on the host machine **or** via docker-compose
- set up Apache to serve the repository, optionally protected with [Basic Authentication](https://en.wikipedia.org/wiki/Basic_access_authentication)
- register private repository with QGIS

> **Disclaimer**
>
> Validity confirmed for **Ubuntu 18.04** and **QGIS <= v3.10.2**. The usage of docker-compose _should_ make this tutorial platform-independent.

## Introduction

Sometimes you simply can't adhere to QGIS [hard](https://plugins.qgis.org/publish/) requirements for its hosted public plugin repository. There are also some softer etiquette rules or project requirements like

- branding of plugins with company logos, links to paid content etc.
- intentionally restricted user base
- commercial client restrictions

And instead of distributing zipped packages to your clients, why not use QGIS amazing flexibility and offer your users/clients the comfort of installing and updating plugins directly though QGIS? Exactly, sounds great and you'll see shortly how trivial that is.

**Be sure to review the license requirements for your QGIS plugins in the case of a private plugin repository, included in [Conclusions](#conclusions).**

## Requirements

### Hard Requirements

Either

- [docker-compose](https://docs.docker.com/compose/) installed

or

- [Apache web server](https://httpd.apache.org) installed

### Recommendations

- basic knowledge of [Apache](https://httpd.apache.org) web server
- basic knowledge of [Docker](https://www.docker.com) and [docker-compose](https://docs.docker.com/compose/)

## Step 1 - Clone and decide

There are mainly two projects dedicated to set up your own QGIS plugin repository, including:

- Michel Stuyts' [phpQGISrepository](https://gitlab.com/GIS-projects/phpQGISrepository)
- Boundless Geospatial's/Planet's [qgis-plugins-xml](https://github.com/planetfederal/qgis-plugins-xml)

However, the latter is a more complex (though more flexible) solution involving a Flask app and several subcommands. You'll work with the former project which is set up quickly after cloning the repository:

```bash
git clone https://gitlab.com/GIS-projects/phpQGISrepository.git
```

From here on you'll have two options to bring up the project:

1. docker-compose
2. point the host-native (Apache) web server to the `phpQGISrepository` directory

**Advantage docker-compose option**

- No installation of external dependencies (Apache or PHP)
- Pre-configured Apache server with PHP support
- Platform independent, i.e. runs the same on Linux, Mac OS and Windows

**Advantage native option**

- Best if you have a (Apache) web server already running and PHP installed
- No virtualization of an entire OS via Docker, saving resources
- Also works for [shared hosts](https://www.hostgator.com/blog/what-is-shared-hosting/)

Which one you prefer and choose is entirely up to you. Needless to say that shared hosting is by far the cheapest option. We contributed a `docker-compose.yml` a while ago, to avoid installing PHP and configuring a web server on the host machine (also great for just trying it out). However, we'll show you both, the docker-compose and host-native web server and naturally we'll start with the harder one :wink:.

## Step 2a - Install using Apache on host machine

This section assumes that you have a working and running Apache and PHP installation on your server. Check this via:

```bash
apache2 -v  # checks if Apache is installed
service status apache2  # checks if Apache is running
php -v  # checks if PHP is installed
```

If not, execute

```bash
sudo apt-get update && sudo apt-get install php apache2
```

and follow the [instructions on Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-18-04) to initalize your Apache web server.

### Verify necessary modules

First you need to make sure that you have the required Apache and PHP modules installed on your server:

#### PHP module for Apache

This will make sure Apache can launch PHP scripts. You can check if it's already loaded and if not, install it (and restart Apache):

```bash
# verify if installed
a2query -m php7.x  # x = your minor PHP version
# install if necessary
sudo apt-get install libapache2-mod-php7.x
# load module
sudo a2enmod php7.x
# restart Apache
service apache2 restart
```

Last, check if your Apache is set up to discover and serve `index.php` files:

```bash
nano /etc/apache2/mods-enabled/dir.conf
```

It should contain a block along the lines of

```xml
<IfModule mod_dir.c>
        DirectoryIndex index.html index.cgi index.pl index.php index.xhtml index.htm
</IfModule>
```

The important part here is that `DirectoryIndex` has `index.php` in _some_ place. The order is merely for priority. So, in this case if both `index.html` and `index.php` were present, Apache would by default ignore `index.php` unless you tell it otherwise.

#### ZipArchive library for PHP

This library is a dependency of the phpQGISrepository project and sometimes needs to be installed additionally (the command won't do anything if it's installed already at the latest version):

```bash
sudo apt-get install php7.x-zip  # x = your minor PHP version
service apache2 restart
```

### Serve QGIS repository

Now all you have to do is point an Apache site configuration to the directory holding the phpQGISrepository project. You might be familiar with the how-to, in which case you can skip the rest, follow your own preferred configuration and step back in at [Step 3](#step-3-include-your-own-plugins).

#### Self-hosted Server

Whether you plan to use your server only for this QGIS repository (in which case we'd recommend the much cheaper option of a shared host) or you're running multiple domains/subdomains from your Apache, you'll have to configure it so it knows about your domain name and maps that domain to the directory holding your PHP project.

Let's not mess with Apache's default configuration and rather do one from scratch:

```bash
cd /etc/apache2/sites-available
nano qgis.example.com.conf
```

Inside `nano` paste the following configuration (and obviously adjust for your domain):

```xml
<VirtualHost *:80>
    ServerAdmin info@gis-ops.com
    ServerName qgis.example.com

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    DocumentRoot /var/www/phpQGISrepository
    DirectoryIndex index.php
</VirtualHost>
```

Once you saved this configuration you'll have to verify the configuration, copy the `phpQGISrepository` directory to `/var/www/`, change the permissions to Apache's `www-data` Linux user, enable the site and restart Apache:

```bash
sudo apache2ctl configtest  # should say "Syntax OK"
sudo cp -arf phpQGISrepository /var/www
sudo chown -R www-data /var/www/phpQGISrepository
sudo a2ensite qgis.example.com  # the name of your conf file (minus .conf extension)
service apache2 restart
```

If you now visit http://qgis.example.com you should see the QGIS repository with an example plugin. If not, you likely have some typo or other slight mistake and it's worth comparing your files with ours or checking into Apache's error log, usually located at `/var/log/apache2/error.log`.

#### Shared host

This option is not only cheaper but also much simpler, since your hosting provider takes care of all the configuration. Per FTP or SSH you can just copy the full contents of the phpQGISrepository's Gitlab repository into the web server folder (and delete whatever is there already) by following your provider's manual. You could even register a subdomain in your cPanel for `qgis.example.com` and follow the instructions to upload content for the subdomain's root. However, we never tried that and are not sure if that's supported by the majority of providers.

As soon as you did that, you should instantly see the QGIS repository on your registered (sub-)domain.

## Step 2b - Install using docker-compose

This couldn't possibly be simpler:

```bash
cd phpQGISrepository
sudo docker-compose up -d
```

Now the project is up and running on port 8082 in a container called `qgis-repo`.

If you did this locally on your machine, you can visit `http://localhost:8082` and the QGIS repository is right there. If it's on a remote server, you'll have to open port 8082 and `http://server_ip:8082` will get you there.

Of course you can change the port to anything you like in the `docker-compose.yml`.

## Step 3 - Include your own plugins

Finally you're all set up to publish your own plugins and get rid of the default example plugin.

If you've followed [our other QGIS tutorials](https://gis-ops.com/category/techtut/qgis/), you already know how to zip up a plugin to make it ready for publishing. If not, check out the [last section](https://gis-ops.com/qgis-simple-plugin/#final-plugin) of our first QGIS Plugin tutorial.

Once you have all plugins zipped up, you can copy them to the `phpQGISrepository/downloads` directory (where that is located depends on which option you chose to install the project). That's it. Your own plugins should appear in the browser!

## Step 4 - Register with QGIS

From now it's a joy ride, thanks to QGIS intuitive UI. Open the Plugin Manager and navigate to _Settings_ (_Plugins_ ► _Manage and Install Plugins_ ► _Settings_). Under _Plugin Repositories_ click on _Add_ and enter the required information:

![add qgis repository](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/repo_add.png)

Click _OK_ and once it connected, look for any of your private plugins in the sidebar's _All_ and enjoy!

![qgis repo private plugin example](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/repo_example.png)

## Step 5 - Protection via Basic authentication (optional)

In case you'd like to limit access to your splendid QGIS plugins to authorized users, you can opt to make use of Basic Authentication, which is also supported by the QGIS plugin manager.

### Server adjustments

You'll have to install the `apache2-utils` package which comes with the needed `htpasswd` utility and choose a user (here `gisops`) before entering a password:

```bash
sudo apt-get install apache2-utils
sudo htpasswd -c /etc/apache2/.htpasswd gisops  # -c only when using the utility the first time
```

The encrypted password is stored in `cat /etc/apache2/.htpasswd`.

In your site configuration file you'll need to set up the access restriction to `/var/www/phpQGISrepository`. With Apache, access restriction is set up on a directory basis. Add the following snippet to your `/etc/apache2/sites-available/qgis.example.com.conf` file within the `<VirtualHost>` block:

```xml
<Directory "/var/www/phpQGISrepository">
    AuthType Basic
    AuthName "Restricted Content"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
</Directory>
```

Again, check the configuration before restarting Apache:

```bash
sudo apache2ctl configtest  # should say "Syntax OK"
service apache2 restart
```

If you now visit http://qgis.example.com again, you should be asked for your credentials.

On a **shared host** you'll have to consult your provider if it's possible to override authentication with a `.htaccess` file. By default, Apache doesn't allow `.htaccess` overrides of any kind, but since most shared host sites are running Wordpress, which highly depends on overridable server configuration, it might even be possible. If you consult your provider, ask them which option is used in the `AllowOverride` directive. It should be `All` or at least `AuthConfig`.

With **docker-compose** you'll have to `docker exec -it qgis-repo bash` into the container and add the same block to `/opt/docker/etc/httpd/conf.d/10-server.conf` inside the `<Directory "/app">` block.

### QGIS adjustments

Now you'll have to tell QGIS about the credentials to your private plugin repository.

In the Plugin Manager's repository settings _Edit_ your previously defined repository and click on _Edit_ at the _Authentication_ settings (and set a Master password if not done before). From there click on the Plus sign to add a new Authentication setting and fill out the form according to your own settings:

![qgis repository authentication settings](https://github.com/gis-ops/tutorials/raw/master/qgis/static/img/repo_auth.png)

## Conclusions

Our recommendation is to use the host-native option if you need more than one private QGIS repository (e.g. for multiple clients) and/or have Apache and PHP installed anyways. docker-compose is great to give it a try and for one single repository on a server.

Whether or not you need a private QGIS plugin repository in the first place is of course up to you to decide. We strongly encourage you to publish your work on the [public QGIS plugin repository](https://plugins.qgis.org) so everyone has access to the functionalities and code, but at the same time we respect if there are circumstances prohibiting that. And in any case, we think it's good fun to try this out.

Also do remember that any code using the QGIS Python/C++ API **must be** licensed in terms compatible to [GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html). In practical terms you need to make the source code available to anyone using your plugin. Usually that's being done by hosting the source code in public repositories on VCS platforms (Gitlab, Github, Bitbucket etc.) and linking to it in the `metadata.txt`. However, using a private QGIS repository generally means you don't want to disclose the source code to the general public. Our recommendation is to add a line to your plugin's UI saying "Please contact us at info@example.com if you want access to the source code". Even though QGIS Python plugins are actually distributed as source code, no binaries, it might be considered too technical for a user to look up the directory your plugin was installed to. Better safe than sorry.
