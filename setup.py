# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    print "Please install python-setuptools."
    sys.exit(0)

setup(
    name='claritick',
    description='Ticketing system written in django, and much more',
    version='1.0',
    author='Laurent Coustet',
    author_email='ed@zehome.com',
    url='http://github.com/zehome/claritick',
    license='License :: OSI Approved :: BSD License',
    platforms=['OS Independent'],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'django>=1.3',
        'django-debug-toolbar',
        'django-extensions',
        'django-desktop-notifications>=0.3',
        'elixir',
        'psycopg2',
        'setproctitle',
        'python-dateutil'
    ],
)
