# commandHelper

Fournit une autre méthode d'exécution de scripts pour les personnes qui ont des difficultés à appuyer sur des combinaisons de clavier compliquées. 

### Mode d'utilisation 

Vous devez d'abord configurer une méthode pour invoquer l'assistant. Vous pouvez attribuer un raccourci clavier dans le menu Préférences de NVDA > Gestes de commandes. Vous pouvez également configurer la touche contrôle dans les préférences de l'extension (voir ci-dessous).

Lorsque l'assistant est invoqué une couche de commandes clavier est activée avec les options suivantes: 

* Flèches gauche et droite pour choisir une catégorie. 
* Toute lettre de A à Z pour sauter à la catégorie avec cette initiale. 
* Flèches haut et bas pour sélectionner une commande de la catégorie choisie. 
* Barre d'espace pour appliquer un filtre par la voix. 
* Entrée pour exécuter la commande. 
* Majuscule+entrée pour exécuter la commande comme si sa combinaison de touches avait été appuyée deux fois rapidement. 
* Contrôle+entrée pour exécuter la commande comme si sa combinaison de touches avait été appuyée trois fois. 
* F1 pour informer du geste correspondant à la commande sélectionnée. 
* Échap abandonne la couche de commandes et restaure la fonctionnalité normale du clavier. 

### Configuration 

La combinaison de touches permettant d'activer l'assistant de commandes peut être modifiée dans le menu Préférences de NVDA > Gestes de Commandes. 

Certaines autres touches peuvent être personnalisées dans le menu Préférences de NVDA > Paramètres > Assistant de commandes. 

* Activer/désactiver l'utilisation de la touche contrôle pour invoquer l'assistant de commandes. 
* Sélectionner avec quelle touche l'assistant est abandonné. 
* Sélectionner avec quelle touche le geste associé à une commande est annoncé.
* Activer/désactiver la gestion de l'assistant via le pavé numérique. 

#### Utilisation de la  touche contrôle pour invoquer l'assistant 

Avec cette option activée, l'assistant est invoqué en appuyant cinq fois rapidement  la touche contrôle. Ceci est utile pour les personnes qui ont du mal à appuyer sur des combinaisons de plusieurs touches à la fois. Cependant, il peut parfois causer l'activation involontaire de l'assistant en appuyant sur la touche contrôle pour d'autres utilisations, par exemple contrôle+C et contrôle+V pour copier et coller. Pour l'éviter, vous devez réduire la fréquence de répétition  du clavier. Ceci est fait dans le Panneau de configuration de Windows. Dans le dialogue Préférences de l'extension vous trouverez un bouton qui en appuyant  sur lui vous amènera directement à ce dialogue. Il peut également être ouvert en appuyant sur la touche Windows+R et en tapant control.exe keyboard dans le dialogue "Exécuter" de Windows. Dans le potentiomètre "Fréquence de répétition" vous devez mettre une valeur aussi bas que possible. Le mettre à zéro, nous nous assurons que nous n'aurons pas de problèmes, mais  cela cessera de fonctionner l'activation de l'assistant en maintenant enfoncée la touche contrôle, ce qui pourrait être un inconvénient pour certains utilisateurs avec une mobilité réduite à ceux qui ont du mal à faire des appuis rapides répétées et préfèrent l'activer de cette façon. Il n'y a pas de configuration universelle, chaque utilisateur doit trouver le plus approprié pour ses besoins ou leurs préférences. 

#### Pavé numérique 

Avec cette option activée, vous pouvez utiliser l'assistant avec les touches du pavé numérique. 

* 4 et 6 pour choisir une catégorie. 
* 2 et 8 pour sélectionner une commande de la catégorie choisie. 
* 5 pour informer du geste correspondant à la commande sélectionnée. 
* Entrée pour exécuter la commande. 
* Signe plus pour exécuter la commande comme si sa combinaison de touches avait été appuyée deux fois rapidement. 
* signe moins pour exécuter la commande comme si sa combinaison de touches avait été appuyée trois fois. 
* Effacement abandonne la couche de commandes et restaure la fonctionnalité normale du clavier. 

#### Filtre par la voix 
 
Dans le menu virtuel, appuyer sur la barre d'espace et parler au microphone. Le menu ne montrera que les commandes correspondant aux mots parlés. Si le résultat n'est pas satisfaisant, appuyez à nouveau sur espace pour effectuer une autre recherche ou échap  pour revenir au menu complet.
 
Pour qu'il fonctionne, il est nécessaire d'avoir une connexion Internet. 

Remarque sur la compatibilité: L'extension est prête à fonctionner avec les versions précédentes de NVDA. La plus ancienne avec laquelle il a été testée est la 2018.1 mais cela devrait fonctionner avec d'autres même plus anciennes. Cependant ne sera pas fourni le support futur pour des problèmes spécifiques pouvant survenir dans ces versions. 

