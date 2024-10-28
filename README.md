1. Service d'Authentification

    Rôle : Gérer l'authentification des utilisateurs via OAuth 2.0 (avec 42).
    Fonctionnalités :
        Inscription et connexion des utilisateurs.
        Gestion des tokens d'authentification OAuth.
        Vérification et renouvellement des sessions.
    Communications :
        Communique avec le Service Utilisateurs pour récupérer et enregistrer des données de profil.
        Envoie des tokens sécurisés au Service Frontend.

2. Service Utilisateurs

    Rôle : Gérer les profils utilisateurs et leurs données.
    Fonctionnalités :
        Stockage et mise à jour des informations utilisateur (nom, avatar, statistiques, etc.).
        Gestion des amis, historique des matchs.
    Communications :
        Connexion avec le Service d'Authentification pour identifier les utilisateurs.
        Envoie et reçoit des requêtes au Service Matchmaking pour organiser les jeux.

3. Service Matchmaking

    Rôle : Gérer l’appariement des joueurs pour les parties.
    Fonctionnalités :
        Algorithme d'appariement pour trouver des adversaires en fonction de leur niveau.
        Création de sessions de jeu et gestion de la file d'attente des joueurs.
    Communications :
        Interagit avec le Service Utilisateurs pour récupérer les informations de profil.
        Envoie les sessions de jeu au Service Jeu et au Service IA.

4. Service Jeu (Core Game)

    Rôle : Gérer la logique de jeu Pong pour les parties en temps réel.
    Fonctionnalités :
        Gérer les parties en temps réel pour les joueurs distants.
        Mise à jour de l'état du jeu (position de la balle, score, etc.).
    Communications :
        Utilise WebSockets pour une connexion en temps réel avec le Service Frontend.
        Connexion avec le Service IA pour l’intégration de l’adversaire IA.

5. Service IA Adversaire

    Rôle : Fournir une IA pour jouer contre les utilisateurs.
    Fonctionnalités :
        Calcul de mouvements en temps réel pour simuler un adversaire humain.
        Gestion des actions en fonction des mouvements et règles du jeu.
    Communications :
        Reçoit les informations de l'état du jeu du Service Jeu.
        Retourne les actions prévues pour l’IA au Service Jeu.

6. Service de Stockage des Scores

    Rôle : Gérer la persistance des scores de jeu.
    Fonctionnalités :
        Stocker les scores et résultats des parties.
        Gérer l’historique des parties pour chaque joueur.
    Communications :
        Enregistre les scores fournis par le Service Jeu après chaque partie.
        Permet au Service Utilisateurs d'afficher l'historique des parties et des scores.

7. Service Graphiques 3D

    Rôle : Gérer les rendus et effets graphiques 3D du jeu.
    Fonctionnalités :
        Utiliser Three.js/WebGL pour rendre les animations du jeu Pong en 3D.
    Communications :
        Interagit avec le Service Jeu pour synchroniser l'affichage 3D en fonction des actions en temps réel.

8. Service de Monitoring

    Rôle : Surveiller l'état et la performance des microservices.
    Fonctionnalités :
        Collecte de métriques pour chaque service (latence, nombre de requêtes, erreurs).
        Gestion d’alertes en cas de défaillances ou d'anomalies.
    Communications :
        Connecte tous les microservices pour collecter des métriques et offrir une vue d'ensemble de l'application.
