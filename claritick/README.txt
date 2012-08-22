Claritick est une application de gestion de tiquets, il peut gérer des hierarchie de clients ainsi que leur infrastructure

Note: cette interface est en français et sans les options d'internationnalisation.

C'est une application Django, web utilisée notament par clarisys (http://www.clarisys.fr) pour avoir une interface plus adaptée et plus simple que celle de mantise et intégrer la gestion de parc et des clients.

Ce logiciel est testé en production avec ces dépendences:
voir le fichier setup.py

(Pours les internes clarisys, un utilitaire à jour permétant de compiler un environnement avec ces packets est disponible sous le nom de clarideploy)

Pour les développeurs, un fichier local_settings.py permet d'écraser les variables du fichier settings par défaut, il est automatiquement ignoré par svn.

Une fois que vous avez une base de donnée postgres de configurée, un utilisateur/administrateur
Dans le dossier media, décompressez le package dojo

le reste du déploiement est classique pour un site django: http://www.djangobook.com/en/2.0/chapter12/

Note: il peut être nécessaire d'importer le dossier parent dans le path python.
