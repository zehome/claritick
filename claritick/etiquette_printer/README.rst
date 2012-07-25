============================================
Installation de etiquette_printer / RabbitMQ
============================================

Install RabbitMQ
----------------

Installation::
    apt-get install rabbitmq-server

Configuration::
    rabbitmqctl add_user claritick Td2P8C2fWh6o
    rabbitmqctl add_vhost etiquetteprinter
    rabbitmqctl set_permissions -p etiquetteprinter etiquetteprinter ".*" ".*" ".*"

Configuration RabbitMQ
----------------------

Il faut faire attention a ce que tous les hosts aient leur hostname et /etc/hosts correctement configurés.


Django-celery
-------------

Installation::
    easy_install django-celery

