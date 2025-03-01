import socket
import threading
import random

class ServeurJeu:
    def __init__(self, hote='localhost', port=2410):
        self.hote = hote
        self.port = port
        self.socket_serveur = None
        self.jeu_commence = False
        self.lock = threading.Lock()
        self.noms_joueurs = []
        self.joueurs_ids = {}
        self.prochain_id_joueur = 1
        self.nombre_clients_connectes = 0  
        self.tours_termines = 0
        self.scores = {}
        self.sockets = {}

    def lancer_des(self):
        """Lance 5 dés et retourne une liste de résultats."""
        return [random.randint(1, 6) for _ in range(5)]

    def relancer_des(self, des, valeur_gardee):
        """Relance les dés qui ne correspondent pas à la valeur gardée."""
        for i in range(len(des)):
            if des[i] != valeur_gardee:
                des[i] = random.randint(1, 6) 
        return des

    def tour_de_jeu(self, socket_client, nom):
        """Gère un tour de jeu avec 3 lancers maximum."""
        des = self.lancer_des()
        print(f"{nom} commence un tour avec les dés : {des}")
        socket_client.send(f"{nom}, Premier lancer : {des}\n".encode())

        lancers = 1
        valeur_gardee = None

        while lancers < 3:
            socket_client.send(f"{nom}, Entrez la valeur des dés à garder ou tapez 'fin' pour ne pas relancer : ".encode())
            choix = socket_client.recv(1024).decode().strip()

            if choix.lower() == "fin":
                break
            try:
                valeur_gardee = int(choix)
                if valeur_gardee in des:
                    des = self.relancer_des(des, valeur_gardee)
                    lancers += 1
                    print(f"{nom} a relancé les dés et obtenu : {des}")
                    socket_client.send(f"{nom}, Lancer suivant : {des}\n".encode())
                else:
                    socket_client.send(f"Entrée non valide, la valeur {valeur_gardee} ne fait pas partie des dés {des}.\n".encode())
            except ValueError:
                socket_client.send(f"Entrée non valide, veuillez entrer un chiffre valide.\n".encode())

        points = des.count(valeur_gardee) * valeur_gardee if valeur_gardee else sum(des)
        print(f"{nom} termine le tour avec {points} points.")
        socket_client.send(f"{nom}, Vous avez marqué {points} points pour ce tour.\n".encode())
        socket_client.send("\n".encode())
        return points

    def partie(self, socket_client, nom, id_joueur):
        """Gère une partie complète pour un joueur."""
        print(f"Début de la partie pour {nom} (ID: {id_joueur})")
        socket_client.send(f"Joueur {id_joueur} ({nom}), vous avez commencé la partie.\n".encode())
        points_totaux = 0

        for tour in range(6):
            points = self.tour_de_jeu(socket_client, nom)
            points_totaux += points

        print(f"{nom} a terminé la partie avec un score total de {points_totaux}.")
        socket_client.send(f"{nom}, Partie terminée ! Score total : {points_totaux}\n".encode())
        return points_totaux

    def gerer_client(self, socket_client, nom_client, id_joueur):
        """Gère les interactions avec un client et la progression du jeu."""
        try:
            score_total = self.partie(socket_client, nom_client, id_joueur)
            self.scores[nom_client] = score_total
            self.sockets[nom_client] = socket_client

            with self.lock:
                self.tours_termines += 1
                print(f"Nombre de tours terminés : {self.tours_termines}/{len(self.noms_joueurs)}")
                if self.tours_termines == len(self.noms_joueurs):
                    self.terminer_jeu()
                else:
                    socket_client.send(f"{nom_client}, vous avez terminé vos tours. Veuillez attendre les autres joueurs.\n".encode())

        except (ConnectionResetError, BrokenPipeError):
            print(f"Le client {nom_client} s'est déconnecté.")
        finally:
            pass

    def terminer_jeu(self):
        """Clôture le jeu et informe les joueurs du gagnant."""
        gagnant = max(self.scores, key=self.scores.get)
        print(f"Le gagnant est {gagnant} avec un score de {self.scores[gagnant]} points !")

        for nom_client, socket_client in self.sockets.items():
            try:
                if nom_client == gagnant:
                    # Message to the winner
                    socket_client.send(f"Félicitations {nom_client}, vous avez gagné avec un score de {self.scores[nom_client]} points !\n".encode())
                else:
                    # Message to the players who lost
                    socket_client.send(f"Désolé {nom_client}, vous avez perdu. Le gagnant est {gagnant} avec un score de {self.scores[gagnant]} points.\n".encode())
            finally:
                socket_client.close()

        print("Le jeu est terminé et tous les clients ont été déconnectés.")


    def gerer_connexion_client(self, socket_client):
        """Traite la connexion des clients."""
        with self.lock:
            if self.jeu_commence:
                socket_client.send("Désolé, le jeu a déjà commencé. Vous ne pouvez pas rejoindre.\n".encode())
                socket_client.close()
                print("Connexion refusée : le jeu a déjà commencé.")
                return

            self.nombre_clients_connectes += 1
            print(f"Nouveau client connecté. Nombre total de clients : {self.nombre_clients_connectes}")

        socket_client.send("Bienvenue au jeu de Yahtzee ! Veuillez entrer votre nom : ".encode())
        nom_client = socket_client.recv(1024).decode().strip()

        with self.lock:
            id_joueur = self.prochain_id_joueur
            self.joueurs_ids[nom_client] = id_joueur
            self.noms_joueurs.append(nom_client)
            self.prochain_id_joueur += 1
            print(f"Client {nom_client} a rejoint le jeu avec l'ID {id_joueur}.")

            if not self.jeu_commence:
                self.jeu_commence = True
                print("Le jeu commence !")

        self.gerer_client(socket_client, nom_client, id_joueur)

    def demarrer_serveur(self):
        """Démarre le serveur et gère les clients."""
        self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_serveur.bind((self.hote, self.port))
        self.socket_serveur.listen(5)
        print("Le serveur attend des connexions...")

        while True:
            socket_client, adresse_client = self.socket_serveur.accept()
            print(f"Connexion acceptée de l'adresse {adresse_client}")
            threading.Thread(target=self.gerer_connexion_client, args=(socket_client,)).start()

if __name__ == "__main__":
    serveur = ServeurJeu()
    serveur.demarrer_serveur()
