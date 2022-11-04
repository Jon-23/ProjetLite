import getpass

clear_chaine = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
class InterfacePublic():

    Dao = None
    def __init__(self,Dao):
        print("Interface Public")
        print(clear_chaine)
        self.Dao = Dao
        self.page_acceuil()

    def page_acceuil(self):
        print("--------------")
        print("Page Acceuil")
        print("Bienvenu dans MaBank")
        print("Auteur: Jonathan NEVEU")
        print("--------------")
        actions_disponibles = ['connexion','creer un compte']
        saisie = ""
        while not saisie in actions_disponibles :
            
            saisie = input(f"Actions disponibles : {actions_disponibles}\n>")
        
        print(clear_chaine)
        if saisie == 'connexion':
            self.page_connexion()
        elif saisie == 'creer un compte':
            self.page_creation_compte()
            
    def page_creation_compte(self):
        print("Page Création de compte")
        login = "login"
       
        while True:
            login = input("Login: ")
            if len(login) <3:
                print("Le login doit comporter au moins 3 caractères.")
            elif login.find(" ")>=0:
                print("Le login ne doit pas comporter d'espace.")
            elif self.Dao.client_existe(login):
                print("Le login existe déjà.")
            else:
                break
        try:
            password = getpass.getpass("Password: ")
            confirm_password = getpass.getpass("Confirm password: ")
        except:
            password = input("Password: ")
            confirm_password = input("Confirm password: ")

        while password != confirm_password:
            print("Mots de passes differents")
            try:
                password = getpass.getpass("Password: ")
                confirm_password = getpass.getpass("Confirm password: ")
            except:
                password = input("Password: ")
                confirm_password = input("Confirm password: ")

        IntPrive = InterfacePrive(self.Dao.cree_client(login,password),self.Dao)
        IntPrive = None

    def page_connexion(self):
        print("Page d'identification")
        tentatives_max = 3
        nombre_essais = 0
        while tentatives_max > nombre_essais:
            nombre_essais += 1
            # client_id = Dao.connexion_client(input("Login: "),input("Password: "))
            try:
                client_id = self.Dao.connexion_client(input("Login: "),getpass.getpass("Password: "))
            except:
                client_id = self.Dao.connexion_client(input("Login: "),input("Password: "))
            if client_id:
                IntPrive = InterfacePrive(client_id,self.Dao)
                IntPrive = None
                break
            else:
                print("Identification impossible")
        self.page_acceuil()

class InterfacePrive():
    nom = str()
    client_id = int()
    Dao = None
    def __init__(self,client_id,Dao):
        print(clear_chaine)
        self.client_id = client_id
        self.Dao = Dao 
        self.nom = self.Dao.informations_client(client_id)
        self.page_acceuil()

    def page_acceuil(self):
        print("------------------")
        print("Interfaction Privé")
        print(f"Client : {self.nom}")
        print("------------------")
        actions_disponibles = ['deconnexion',"deposer de l'argent",'consulter le solde','consulter les operations',"retirer de l'argent"]
        saisie = ""
        while not saisie in actions_disponibles :
            saisie = input(f"Actions disponibles : {actions_disponibles}\n>")
        print(clear_chaine)
        if saisie == 'deconnexion':
            self.deconnexion()
        elif saisie == 'consulter le solde':
            self.page_consulter_le_solde()
        elif saisie == "deposer de l'argent":
            self.page_deposer_argent()
        elif saisie == "retirer de l'argent":
            self.page_retirer_argent()
            
    def page_consulter_le_solde(self):
        print(clear_chaine)
        print("Page solde")
        print(f"Solde actuel: {self.Dao.get_solde(self.client_id)}")
        self.page_acceuil()

    def page_deposer_argent(self):
        print("Page deposer de l'argent")
        print(f"Solde actuel: {self.Dao.get_solde(self.client_id)}")
        nouveau_montant = 0 
        while True:
            try:
                nouveau_montant = float(input("Montant: "))
                if nouveau_montant <= 0:
                    print("Le montant doit être supérieur à 0")
                    continue
            except:
                print("Le montant doit être un nombre réel.")
                continue
            self.Dao.add_argent_solde(self.client_id,"Dépos d'argent", nouveau_montant )
            break
        self.page_consulter_le_solde()

    def page_retirer_argent(self):
        print("Page retirer de l'argent")
        print(f"Solde actuel: {self.Dao.get_solde(self.client_id)}")
        nouveau_montant = 0 
        while True:
            try:
                nouveau_montant = float(input("Montant: "))
                if nouveau_montant <= 0:
                    print("Le montant doit être supérieur à 0")
                    continue
            except:
                print("Le montant doit être un nombre réel.")
                continue
            self.Dao.drop_argent_solde(self.client_id,  "Retrait d'argent",nouveau_montant)
            break
        self.page_consulter_le_solde()

    def page_consulter_les_operations(self,page_actuel=1):
        print(clear_chaine)
        print("Page Consultations des operations")
        retour_operations = self.Dao.get_operations(self.client_id,page_actuel,5)
        total_operations = retour_operations['total_operations']
        page_max = retour_operations['nombre_pages']
        operations_affichees = retour_operations['operations']
        print(f"Opérations total : {total_operations}")
        print(f"Page : {page_actuel}/{page_max}")
        chaine = "Opérations : \n"
        type_affiches = ['type','description','montant','date']
        chaine += " | ".join(type_affiches)
        
        if len(operations_affichees) >  0:
            for i in range(len(operations_affichees)):
                chaine += "\n"
                chaine += " | ".join([str(operations_affichees[i][n]) for n in range(len(type_affiches))])
        else:
            chaine += "\n Aucune operations"
        
        print(chaine)

        actions_disponibles = ['deconnexion','acceuil',"actualiser",'suivant','precedent',"aller a la page"]
        saisie = ""
        while not saisie in actions_disponibles :
            saisie = input(f"Actions disponibles : {actions_disponibles}\n>")
        
        if saisie == "deconnexion":
            self.deconnexion()
        elif saisie == "acceuil":
            self.page_acceuil()
        elif saisie == "actualiser":
            self.page_consulter_les_operations(page_actuel)
        elif saisie == "suivant":
            if page_max > page_actuel :
                self.page_consulter_les_operations(page_actuel+1)
            else:
                self.page_consulter_les_operations(page_actuel)
        elif saisie == "precedent":
            if page_actuel > 1:
                self.page_consulter_les_operations(page_actuel-1)
            else:
                self.page_consulter_les_operations(page_actuel)
        elif saisie == "aller a la page":
            numero_page_saisie = int()
            while True:
                try:
                    numero_page_saisie = int(input("Page numéro : "))
                    if numero_page_saisie >page_max:
                        numero_page_saisie = page_max
                    elif numero_page_saisie < 1:
                        numero_page_saisie = 1
                    break
                except:
                    print("Cela doit être un nombre entier.")
            self.page_consulter_les_operations(numero_page_saisie)
                          
    def deconnexion(self):
        print("Deconnexion")


