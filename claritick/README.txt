Claritick est une application de gestion de tiquets, il peut gérer des hierarchie de clients ainsi que leur infrastructure

Note: cette interface est en français et sans les options d'internationnalisation.

C'est une application Django, web utilisée notament par clarisys (http://www.clarisys.fr) pour avoir une interface plus adaptée et plus simple que celle de mantise et intégrer la gestion de parc et des clients.

Ce logiciel est testé en production avec ces dépendences:
zlib 1.2.5 (--shared et CFLAGS=-fPIC)
bzip2 1.0.5
Python 2.6.5 (configuré avec --without-pymalloc)
PostgreSql 8.4.3
egenix-base 3.0.0
psycopg2 2.0.14
Django 1.2.3
Django-extentions 0.4.1
gdata 2.0.9
setuptools
python-dateutils
py-setproctitle
pyftpdlib

(Pours les internes clarisys, un utilitaire à jour permétant de compiler un environnement avec ces packets est disponible sous le nom de clarideploy)

Pour les développeurs, un fichier local_settings.py permet d'écraser les variables du fichier settings par défaut, il est automatiquement ignoré par svn.

Une fois que vous avez une base de donnée postgres de configurée, un utilisateur/administrateur
Dans le dossier media, décompressez le package dojo

le reste du déploiement est classique pour un site django: http://www.djangobook.com/en/2.0/chapter12/

Note: il peut être nécessaire d'importer le dossier parent dans le path python.
