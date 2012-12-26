CLARITICK Systèem de gestion
============================

Author: Laurent Coustet <ed@zehome.com>

QUICK INSTALL
-------------

```
# Install the dependencies
root@machine:~# apt-get install python-virtualenv python-setuptools
# Create the virtual env
claritick@machine:~$ virtualenv claritick_env
# Activate virtual env
claritick@machine:~$ . claritick_env/bin/activate
# Checkout sources in src
claritick@machine:~$ mkdir src
claritick@machine:src$ cd src
# Cloning the master git repository
claritick@machine:src$ git clone https://github.com/zehome/claritick.git
claritick@machine:src/claritick$ cd claritick
# Install dependencies
claritick@machine:src/claritick$ pip install -e .
# Link to ~/claritick
claritick@machine:src/claritick$ cd ..
claritick@machine:src$ ln -s claritick ~
# Unzip dojo sources
claritick@machine:~$ cd claritick/dojango/dojo-media/release
claritick@machine:claritick/dojango/dojo-media/release$ tar xzf custom_build_161.tar.gz
# Deploy static files
claritick@machine:claritick/dojango/dojo-media/release$ cd ~/claritick
claritick@machine:claritick$ python manage.py collectstatic
```

Now, you must configure claritick using local_settings.py (DATABASE, CACHES, ...).
Please don't modify settings or you will experience merge issues with upgrades.

```
# syncdb
claritick@machine:claritick$ python manage.py syncdb
```

UPGRADES
--------
Please follow instructions in **UPGRADING** file.
