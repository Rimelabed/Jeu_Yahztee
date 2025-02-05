# Projet Yahtzee - Jeu de Dès en Réseau


Ce projet propose une implémentation complète du jeu de dés Yahtzee, également connu sous le nom de Yam’s. Il est développé en plusieurs versions, chacune correspondant à une branche distincte sur le dépôt GitHub. Chaque version apporte de nouvelles fonctionnalités et améliorations, permettant d'explorer différentes approches en programmation réseau et en gestion du multithreading.

## Version 1 : Yam’s Simple

Dans cette première version, une seule partie est organisée à la fois. Un serveur centralisé héberge et gère le jeu des clients connectés.

Fonctionnalités

Gestion d'une partie unique entre plusieurs joueurs

Un serveur qui lance et relance les dés

Comptabilisation des points pour chaque joueur

Présentation du tableau des scores en fin de partie

Technologies et Bibliothèques

Python 3

Socket (sockets TCP/IP) pour la communication client-serveur

Threading pour gérer plusieurs connexions simultanées

Random pour simuler les lancers de dés

Pickle pour sérialiser les données entre serveur et clients

Lancer la version

Démarrer le serveur : python server.py

Démarrer un client : python client.py
