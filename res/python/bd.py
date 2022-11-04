import sqlite3
import hashlib
from math import ceil

class Dao():
    db = None

    #Internes
    def __init__(self,filepath_db="Mabank.bd"):
        self.conn = sqlite3.connect(filepath_db)
        self.db = self.conn.cursor()
        sql_verification_tables = """
        CREATE TABLE IF NOT EXISTS clients (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                login VARCHAR(64) UNIQUE,
                password VARCHAR(255),
                bank_details VARCHAR(200) UNIQUE
        );
        
        """
        sql_verification_table_operations = """
        CREATE TABLE IF NOT EXISTS operations(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_Id INTEGER,
            type VARCHAR(64),
            description VARCHAR(64),
            montant REAL,
            date datetime default CURRENT_TIMESTAMP
        );

        """
        sql_verification_table_soldes = """
        CREATE TABLE IF NOT EXISTS soldes(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_Id INTEGER,
            montant REAL,
            date datetime default CURRENT_TIMESTAMP
        );"""
        sql_verification_table_beneficiaires = """
        CREATE TABLE IF NOT EXISTS beneficiaires(
            client_Id INTEGER,
            associate_client_Id INTEGER
        )
        """
        self.db.execute(sql_verification_tables)
        self.db.execute(sql_verification_table_operations)
        self.db.execute(sql_verification_table_soldes)
        self.db.execute(sql_verification_table_beneficiaires)

    def _sauvegarde(self):
        self.conn.commit()
    
    def _hash(self, string):
        return hashlib.sha224(string.encode('utf-8')).hexdigest()

    #Clients
    def connexion_client(self,login,password):
        sql_client_connect = "SELECT Id FROM clients WHERE login = :login AND password = :password LIMIT 1"
        sql_client_connect_test = "SELECT * FROM clients WHERE 1"
        statement2 = self.db.execute(sql_client_connect_test)
        statement = self.db.execute(sql_client_connect,{'login':login,'password':self._hash(password)})
        resultat = statement.fetchall()
        if len(resultat) == 1:
            return resultat[0][0]
        else:
            return False
    
    def change_mot_de_passe(self,client_id,new_password):
        sql_client_update = "UPDATE clients SET password = :new_password WHERE Id = :client_id"
        statement = self.db.execute(sql_client_update,{'client_id':client_id, 'new_password':self._hash(new_password)})
        self._sauvegarde()
        return True

    def informations_client(self,client_id):
        sql_client_info = "SELECT login FROM clients WHERE Id = :client_id"
        statement = self.db.execute(sql_client_info,{'client_id':client_id})
        resultat = statement.fetchall()
        if len(resultat) == 1:
            return resultat[0][0]
        else:
            return False

    def client_existe(self,login):
        sql_client_exist = "SELECT Id FROM clients WHERE login = :login"
        statement = self.db.execute(sql_client_exist,{'login':login})
        resultat = statement.fetchall()
        return len(resultat) >0  
    
    def cree_client(self,login,password):
        if self.client_existe(login):
            print("Ce login existe déjà")
        else:
            sql_client_create = f"INSERT INTO clients (login,password) VALUES (:login,:password)"
            # sql_client_create = "INSERT INTO clients (login,password) VALUES (:login,:password)"
            sql_solde_create = "INSERT INTO soldes (client_Id,montant) VALUES (:client_id,:montant)"
            statement = self.db.execute(sql_client_create,{'login':login,'password':self._hash(password)})
            statement2 = self.db.execute(sql_solde_create,{'client_id':statement.lastrowid,'montant':0})
            lastrowid_client = statement.lastrowid
            sql_client_update = f"UPDATE clients SET bank_details = 'FAUXRIB{lastrowid_client*1000}' WHERE Id = :client_id"
            statement3 = self.db.execute(sql_client_update,{'client_id':lastrowid_client})
            # print(statement.lastrowid)
            if lastrowid_client == self.connexion_client(login,password):
                self._sauvegarde()
                return self.connexion_client(login,password)
            else:
                raise "Erreur BD"
    
    def supprime_client(self,client_id,login,password):
        sql_c_toi_le_client = "SELECT Id FROM clients WHERE Id = :Id AND login = :login AND password = :password LIMIT 1"
        statement = self.db.execute(sql_c_toi_le_client,{'client_id':client_id,'login':login,'password':self._hash(password)})
        resultat = statement.fetchall()
        if len(resultat) == 1:
            print("TODO : supprime_client")
            # self._sauvegarde()
            return True
        else:
            return False

    def add_argent_solde(self,client_id,type_op,montant):
        solde_actuel = self.get_solde(client_id) + montant
        sql_solde_update = "UPDATE soldes SET montant = :solde_actuel WHERE client_Id = :client_id"
        statement = self.db.execute(sql_solde_update,{'client_id':client_id,'solde_actuel':solde_actuel})
        self.add_operations(client_id,type_op, type_op,montant)
        self._sauvegarde()

    def drop_argent_solde(self,client_id,type_op,montant):
        solde_actuel = self.get_solde(client_id) - montant
        sql_solde_update = "UPDATE soldes SET montant = :solde_actuel WHERE client_Id = :client_id"
        statement = self.db.execute(sql_solde_update,{'client_id':client_id,'solde_actuel':solde_actuel})
        self.add_operations(client_id,type_op, type_op,0-montant)
        self._sauvegarde()


    def get_solde(self,client_id):
        sql_solde_select = "SELECT montant FROM soldes WHERE client_Id = :client_id"
        statement = self.db.execute(sql_solde_select,{'client_id':client_id})
        resultat = statement.fetchall()
        if len(resultat) == 1:
            # print(resultat[0][0])
            return resultat[0][0]
        else:
            raise "Impossible de consulter le solde."
    
    def get_operations(self,client_id,page,elements_max=10):
        sql_operations_select = "SELECT type, description, montant, date FROM operations WHERE client_Id = :client_id ORDER BY date DESC LIMIT :elements_max OFFSET :elements_saute "
        statement = self.db.execute(sql_operations_select,{'client_id':client_id,'elements_saute':(page-1)*elements_max,'elements_max':elements_max})
        resultat = {}
        resultat['operations'] = statement.fetchall()
        sql_operations_count = "SELECT count(*) as count FROM operations WHERE client_Id = :client_id"
        statement2 = self.db.execute(sql_operations_count,{'client_id':client_id})
        resultat['total_operations'] = statement2.fetchall()[0][0]
        resultat['nombre_pages'] = ceil(resultat['total_operations']/elements_max)
        return resultat
        
    def add_operations(self,client_id,type_op,description,montant):
        sql_operations_insert = "INSERT INTO operations (client_Id,type, description, montant) VALUES (:client_id, :type, :description, :montant)"
        statement = self.db.execute(sql_operations_insert,{'client_id':client_id,'type':type_op,'description':description,'montant':montant})
    
