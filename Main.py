import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Label
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import sqlite3
import locale
from docx import Document
from docxtpl import DocxTemplate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
from pathlib import Path
from appdirs import user_data_dir
import tkinter.simpledialog as simpledialog

def resource_path(relative_path):
    try:
        # For PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # For normal development
        base_path = os.path.abspath(".")

    if "Data/main.db" in relative_path:
        # Define app-specific directory in user data folder
        app_name = "CRSS_Nabeul_Carbu"
        data_dir = user_data_dir(app_name)  # Cross-platform user data directory
        os.makedirs(data_dir, exist_ok=True)  # Ensure directory exists
        return os.path.join(data_dir, os.path.basename(relative_path))

    return os.path.join(base_path, relative_path)

# Initialize the SQLite database
def init_db():
    try:
        # Connect to the database
        db_path = resource_path('Data/main.db')
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging for safety
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicule (
            vehicule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_immatriculation TEXT,
            marque TEXT,
            type_carburant TEXT,
            prix_carburant REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conducteur (
            conducteur_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_conducteur TEXT,
            prenom_conducteur TEXT,
            role TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS saisie (
            saisie_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_saisie TEXT,
            objet_mission TEXT,
            type_charge TEXT,
            date_sortie TEXT,
            date_arrivee TEXT,
            lieux_depart TEXT,
            lieux_arrivee TEXT,
            nom_conducteur TEXT,
            Prenom_conducteur TEXT,
            role TEXT,
            nbre_acc INTEGER,
            immatriculation TEXT,
            marque_vehicule TEXT,
            type_carburant TEXT,
            prix_carburant REAL,
            indice_depart REAL,
            indice_arrivee REAL,
            distance REAL,
            numero_bon TEXT,
            nombre_bon INTEGER,
            prix_bon REAL,
            prix_total REAL
        )
        ''')

        # Commit changes and close the connection
        conn.commit()
        print(f"Base de données initialiser à : {db_path}")

    except sqlite3.Error as e:
        print(f"Error pour initialisation de base de données: {e}")

    finally:
        if conn:
            conn.close()

def check_tables():
    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:", tables)
    conn.close()


# Functions for handling login, signup, and logout
def check_login():
    username = username_entry.get()
    password = password_entry.get()

    # Vérifier si les champs sont vides
    if not username or not password:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
        return

    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Connexion réussie", f"Bienvenue, {username}!")
        show_main_buttons_frame()
    else:
        messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")


def add_user():
    username = signup_username_entry.get()
    password = signup_password_entry.get()
    confirm_password = confirm_password_entry.get()

    # Vérifier si les champs sont vides
    if not username or not password:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
        return

    # Vérifier si les mots de passe compatible
    if password != confirm_password:
        messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
        return

    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo("Réussie", "Compte créé avec succès !")
        show_login_frame()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", "Ce nom d'utilisateur existe déjà.")
    finally:
        conn.close()
        clear_user_entries()

def clear_user_entries():
    signup_username_entry.delete(0, tk.END)
    signup_password_entry.delete(0, tk.END)
    confirm_password_entry.delete(0, tk.END)


def clear_logout_entries():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)


def logout():
    show_login_frame()
    clear_logout_entries()


# Functions for managing frames
def show_login_frame():
    signup_frame.grid_forget()
    main_buttons_frame.grid_forget()
    car_management_frame.grid_forget()
    rapports_frame.grid_forget()
    person_management_frame.grid_forget()
    login_frame.grid()


def show_signup_frame():
    login_frame.grid_forget()
    signup_frame.grid()


def show_main_buttons_frame():
    login_frame.grid_forget()
    signup_frame.grid_forget()
    main_buttons_frame.grid()


def open_car_management():
    main_buttons_frame.grid_forget()
    car_management_frame.grid()


def car_management(event=None):
    car_management_frame.grid()


def person_management(event=None):
    person_management_frame.grid()


def open_rapport_frame():
    main_buttons_frame.grid_forget()
    rapports_frame.grid()


def open_person_management():
    main_buttons_frame.grid_forget()
    person_management_frame.grid()


# Fonction pour ajouter un Conducteur
def ajouter_conducteur():
    nom_conducteur = entry_nom_conducteur.get()
    prenom_conducteur = entry_prenom_conducteur.get()
    role = entry_role_conducteur.get()

    if nom_conducteur and prenom_conducteur and role:
        conn = sqlite3.connect(resource_path('Data/main.db'))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conducteur (nom_conducteur, prenom_conducteur, role)
            VALUES (?, ?, ?)
            ''', (nom_conducteur, prenom_conducteur, role))
        conn.commit()
        # # Récupérer l'ID du conducteur ajouté
        # conducteur_id = cursor.lastrowid
        conn.close()
        load_all_conducteurs()
        messagebox.showinfo("Info", "Conducteur ajouté avec succès")

        clear_entries_conducteur()
        root.update_idletasks()  # Forcer la mise à jour de l'interface
    else:
        messagebox.showerror("Erreur", "Tous les champs doivent être remplis")


# Fonction pour supprimer un Conducteur
def supprimer_conducteur():
    # Vérifier si un élément est sélectionné dans le Treeview
    selected_item = tree_conducteur.selection()
    if not selected_item:
        messagebox.showwarning("Avertissement", "Sélectionnez un conducteur à supprimer.")
        return

    # Récupérer l'ID du conducteur sélectionné
    item = tree_conducteur.item(selected_item)
    conducteur_id = item['values'][0]  # L'ID est le premier élément dans les valeurs

    try:
        # Demander le mot de passe à l'utilisateur
        mot_de_passe = simpledialog.askstring(
            "Mot de passe requis",
            "Veuillez entrer votre mot de passe pour confirmer la suppression :",
            show="*"
        )

        if not mot_de_passe:
            messagebox.showwarning("Avertissement", "La suppression a été annulée car le mot de passe n'a pas été fourni.")
            return

        # Vérifier si le mot de passe est correct
        mot_de_passe_correct = "admin"
        if mot_de_passe != mot_de_passe_correct:
            messagebox.showerror("Erreur", "Mot de passe incorrect. La suppression a été annulée.")
            return

        # Confirmation de suppression
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce conducteur ?"):
            with sqlite3.connect(resource_path('Data/main.db')) as conn:
                cursor = conn.cursor()
                # Supprimer le conducteur de la base de données
                cursor.execute('''
                DELETE FROM conducteur
                WHERE conducteur_id = ?
                ''', (conducteur_id,))
                conn.commit()

                # Réindexer les ID des conducteurs restants
                cursor.execute('''
                UPDATE conducteur
                SET conducteur_id = (
                    SELECT rowid
                    FROM (
                        SELECT rowid, ROW_NUMBER() OVER(ORDER BY conducteur_id) AS new_id
                        FROM conducteur
                    )
                    WHERE rowid = conducteur.rowid
                )
                ''')

                # Réinitialiser l'auto-incrémentation de l'ID
                cursor.execute('DELETE FROM sqlite_sequence WHERE name="conducteur"')
                conn.commit()

            # Recharger les conducteurs dans le Treeview
            load_all_conducteurs()
            root.update_idletasks()  # Forcer la mise à jour de l'interface

            # Afficher une confirmation
            messagebox.showinfo("Info", "Conducteur supprimé avec succès.")
            clear_entries_conducteur()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression du conducteur : {e}")

# Fonction pour mettre à jour un Conducteur
def mettre_a_jour_conducteur():
    conducteur_id = entry_id_conducteur.get()
    nom_conducteur = entry_nom_conducteur.get()
    prenom_conducteur = entry_prenom_conducteur.get()
    role = entry_role_conducteur.get()

    if conducteur_id:
        try:
            conducteur_id = int(conducteur_id)  # Convertir l'ID en entier
            with sqlite3.connect(resource_path('Data/main.db')) as conn:
                cursor = conn.cursor()

                # Récupérer l'état actuel dans la base de données
                cursor.execute('''
                    SELECT nom_conducteur, prenom_conducteur, role
                    FROM conducteur
                    WHERE conducteur_id = ?
                ''', (conducteur_id,))
                conducteur_actuel = cursor.fetchone()

                if not conducteur_actuel:
                    messagebox.showwarning("Info", "Aucun conducteur trouvé avec cet ID.")
                    return

                # Vérifier si des modifications ont été apportées
                if (nom_conducteur, prenom_conducteur, role) == conducteur_actuel:
                    messagebox.showinfo("Info", "Aucune modification détectée.")
                    return

                # Mise à jour uniquement si des modifications existent
                cursor.execute('''
                    UPDATE conducteur
                    SET nom_conducteur = ?, prenom_conducteur = ?, role = ?
                    WHERE conducteur_id = ?
                ''', (nom_conducteur, prenom_conducteur, role, conducteur_id))

                conn.commit()
                load_all_conducteurs()
                messagebox.showinfo("Info", "Conducteur mis à jour avec succès.")
                clear_entries_conducteur()
        except ValueError:
            messagebox.showerror("Erreur", "L'ID doit être un nombre entier.")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du conducteur : {e}")
    else:
        messagebox.showerror("Erreur", "L'ID du conducteur est requis.")

# Fonction pour vider les champs d'un Conducteur
def clear_entries_conducteur():
    entry_id_conducteur.delete(0, tk.END)
    entry_nom_conducteur.delete(0, tk.END)
    entry_prenom_conducteur.delete(0, tk.END)
    entry_role_conducteur.delete(0, tk.END)

def load_all_conducteurs():
    tree_conducteur.delete(*tree_conducteur.get_children())  # Effacer les anciennes données du Treeview
    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT conducteur_id, nom_conducteur, prenom_conducteur, role FROM conducteur")
    conducteurs = cursor.fetchall()
    conn.close()

    for conducteur in conducteurs:
        tree_conducteur.insert("", tk.END, values=(conducteur[0], conducteur[1], conducteur[2], conducteur[3]))
        combobox_ids['values'] = [str(conducteur[0]) for conducteur in conducteurs]

def on_combobox_select(event):
    conducteur_id = combobox_ids.get()
    load_conducteur_details(conducteur_id)

def on_tree_select(event):
    item = tree_conducteur.selection()[0]
    conducteur_id = tree_conducteur.item(item, "values")[0]
    load_conducteur_details(conducteur_id)

def load_conducteur_details(conducteur_id):
    try:
        conducteur_id = int(conducteur_id)
        conn = sqlite3.connect(resource_path('Data/main.db'))
        cursor = conn.cursor()
        cursor.execute("SELECT nom_conducteur, prenom_conducteur, role FROM conducteur WHERE conducteur_id = ?",
                       (conducteur_id,))
        conducteur = cursor.fetchone()
        conn.close()

        if conducteur:
            entry_nom.config(state="normal")
            entry_nom.delete(0, tk.END)
            entry_nom.insert(0, conducteur[0])
            entry_nom.config(state="disabled")

            entry_prenom.config(state="normal")
            entry_prenom.delete(0, tk.END)
            entry_prenom.insert(0, conducteur[1])
            entry_prenom.config(state="disabled")

            entry_role.config(state="normal")
            entry_role.delete(0, tk.END)
            entry_role.insert(0, conducteur[2])
            entry_role.config(state="disabled")

        else:
            messagebox.showerror("Erreur", f"Aucun conducteur trouvé avec l'ID {conducteur_id}")
    except ValueError:
        messagebox.showerror("Erreur", "L'ID du conducteur doit être un nombre entier")


# Fonction pour selectioner un Conducteur
def on_tree_selected(event):
    selected_item = tree_conducteur.selection()
    if selected_item:
        item = tree_conducteur.item(selected_item)
        conducteur_id = item['values'][0]
        nom_conducteur = item['values'][1]
        prenom_conducteur = item['values'][2]
        role_conducteur = item['values'][3]

        # Remplir les champs avec les informations du conducteur sélectionné
        entry_id_conducteur.delete(0, tk.END)
        entry_id_conducteur.insert(0, conducteur_id)
        entry_nom_conducteur.delete(0, tk.END)
        entry_nom_conducteur.insert(0, nom_conducteur)
        entry_prenom_conducteur.delete(0, tk.END)
        entry_prenom_conducteur.insert(0, prenom_conducteur)
        entry_role_conducteur.delete(0, tk.END)
        entry_role_conducteur.insert(0, role_conducteur)

# ----------------------------------- Véhicule Fonctions ------------------------------------------------------------- #
# Fonction pour ajouter un véhicule
def ajouter_vehicule():
    numero_immatriculation = entry_immatriculation.get()
    marque = entry_marque.get()
    type_carburant = type_var.get()
    prix_carburant = entry_prix_carburant.get()

    if numero_immatriculation and marque and type_carburant and prix_carburant:
        conn = sqlite3.connect(resource_path('Data/main.db'))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicule (numero_immatriculation, marque, type_carburant, prix_carburant)
            VALUES (?, ?, ?, ?)
            ''', (numero_immatriculation, marque, type_carburant, prix_carburant))
        conn.commit()
        conn.close()
        load_all_vehicules()
        update_combobox()
        messagebox.showinfo("Info", "Véhicule ajouté avec succès")

        clear_entries_vehicule()
        root.update_idletasks()
    else:
        messagebox.showerror("Erreur", "Tous les champs doivent être remplis")

# Fonction pour vider les champs d'une Véhicule
def clear_entries_vehicule():
    entry_id_vehicule.delete(0, tk.END)
    entry_immatriculation.delete(0, tk.END)
    entry_marque.delete(0, tk.END)
    type_var.set("")
    entry_prix_carburant.delete(0, tk.END)

def load_all_vehicules():
    tree_vehicule.delete(*tree_vehicule.get_children())  # Effacer les anciennes données du Treeview
    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT vehicule_id, numero_immatriculation, marque, type_carburant, prix_carburant FROM vehicule")
    vehicules = cursor.fetchall()
    conn.close()

    for vehicule in vehicules:
        tree_vehicule.insert("", tk.END, values=(vehicule[0], vehicule[1], vehicule[2], vehicule[3], vehicule[4]))
        combobox_ids['values'] = [str(vehicule[0]) for vehicule in vehicules]

# Fonction pour supprimer une véhicule
def supprimer_véhicule():
    # Vérifier si un élément est sélectionné dans le Treeview
    selected_item = tree_vehicule.selection()
    if not selected_item:
        messagebox.showwarning("Avertissement", "Sélectionnez un véhicule à supprimer.")
        return

    # Récupérer l'ID du véhicule sélectionné
    item = tree_vehicule.item(selected_item)
    vehicule_id = item['values'][0]  # L'ID est le premier élément dans les valeurs

    try:
        # Demander le mot de passe à l'utilisateur
        mot_de_passe = simpledialog.askstring(
            "Mot de passe requis",
            "Veuillez entrer votre mot de passe pour confirmer la suppression :",
            show="*"
        )

        if not mot_de_passe:
            messagebox.showwarning("Avertissement", "La suppression a été annulée car le mot de passe n'a pas été fourni.")
            return

        # Vérifier si le mot de passe est correct
        mot_de_passe_correct = "admin"
        if mot_de_passe != mot_de_passe_correct:
            messagebox.showerror("Erreur", "Mot de passe incorrect. La suppression a été annulée.")
            return

        # Confirmation de suppression
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce véhicule ?"):
            with sqlite3.connect(resource_path('Data/main.db')) as conn:
                cursor = conn.cursor()
                # Supprimer le véhicule de la base de données
                cursor.execute('''
                DELETE FROM vehicule
                WHERE vehicule_id = ?
                ''', (vehicule_id,))
                conn.commit()

                # Réindexer les ID des véhicules restants
                cursor.execute('''
                UPDATE vehicule
                SET vehicule_id = (
                    SELECT rowid
                    FROM (
                        SELECT rowid, ROW_NUMBER() OVER(ORDER BY vehicule_id) AS new_id
                        FROM vehicule
                    )
                    WHERE rowid = vehicule.rowid
                )
                ''')

                # Réinitialiser l'auto-incrémentation de l'ID
                cursor.execute('DELETE FROM sqlite_sequence WHERE name="vehicule"')
                conn.commit()

            # Recharger les véhicules dans le Treeview
            load_all_vehicules()
            update_combobox()
            root.update_idletasks()  # Forcer la mise à jour de l'interface

            # Afficher une confirmation
            messagebox.showinfo("Info", "Véhicule supprimé avec succès.")
            clear_entries_vehicule()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression du véhicule : {e}")

# Fonction pour mettre à jour un véhicule
def mettre_a_jour_vehicule():
    # Récupérer les valeurs saisies
    vehicule_id = entry_id_vehicule.get()
    numero_immatriculation = entry_immatriculation.get()
    marque = entry_marque.get()
    type_carburant = type_var.get()
    prix_carburant = entry_prix_carburant.get()

    if not vehicule_id:
        messagebox.showerror("Erreur", "L'ID du véhicule est requis.")
        return

    try:
        # Convertir l'ID en entier
        vehicule_id = int(vehicule_id)
    except ValueError:
        messagebox.showerror("Erreur", "L'ID doit être un nombre entier.")
        return

    try:
        with sqlite3.connect(resource_path('Data/main.db')) as conn:
            cursor = conn.cursor()

            # Récupérer l'état actuel du véhicule dans la base de données
            cursor.execute('''
                SELECT numero_immatriculation, marque, type_carburant, prix_carburant
                FROM vehicule
                WHERE vehicule_id = ?
            ''', (vehicule_id,))
            vehicule_actuel = cursor.fetchone()

            if not vehicule_actuel:
                messagebox.showwarning("Info", "Aucun véhicule trouvé avec cet ID.")
                return

            # Normaliser les valeurs actuelles (remplacer None par des chaînes vides)
            vehicule_actuel = tuple(str(v).strip() if v is not None else '' for v in vehicule_actuel)

            # Normaliser les valeurs saisies
            valeurs_saisies = (
                numero_immatriculation.strip(),
                marque.strip(),
                type_carburant.strip(),
                prix_carburant.strip(),
            )

            # Comparer les valeurs saisies avec celles actuelles
            if valeurs_saisies == vehicule_actuel:
                messagebox.showinfo("Info", "Aucune modification détectée.")
                return

            # Mise à jour uniquement si des modifications existent
            cursor.execute('''
                UPDATE vehicule
                SET numero_immatriculation = ?, marque = ?, type_carburant = ?, prix_carburant = ?
                WHERE vehicule_id = ?
            ''', (*valeurs_saisies, vehicule_id))

            conn.commit()

            # Rafraîchir les données dans l'interface
            load_all_vehicules()
            update_combobox()

            # Afficher le message de succès
            messagebox.showinfo("Info", "Véhicule mis à jour avec succès.")

            # Nettoyer les champs
            clear_entries_vehicule()

    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du véhicule : {e}")

# Fonction pour selectioner une véhicule
def on_vehicule_selected(event):
    selected_item = tree_vehicule.selection()
    if selected_item:
        item = tree_vehicule.item(selected_item)
        vehicule_id = item['values'][0]
        numero_immatriculation = item['values'][1]
        marque = item['values'][2]
        type_carburant = item['values'][3]
        prix_carburant = item['values'][4]

        # Remplir les champs avec les informations du véhicule sélectionné
        entry_id_vehicule.delete(0, tk.END)
        entry_id_vehicule.insert(0, vehicule_id)
        entry_immatriculation.delete(0, tk.END)
        entry_immatriculation.insert(0, numero_immatriculation)
        entry_marque.delete(0, tk.END)
        entry_marque.insert(0, marque)
        type_var.set(type_carburant)
        entry_prix_carburant.delete(0, tk.END)
        entry_prix_carburant.insert(0, prix_carburant)

def remplir_champs(event):
    numero_immatriculation = immatriculation.get()

    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()

    # Récupérer les informations du véhicule (marque, type de carburant, prix du carburant)
    cursor.execute("SELECT marque, type_carburant, prix_carburant FROM vehicule WHERE numero_immatriculation=?",
                   (numero_immatriculation,))
    vehicule_info = cursor.fetchone()

    # Récupérer les derniers indices de départ et d'arrivée associés au numéro d'immatriculation
    cursor.execute(
        "SELECT indice_depart, indice_arrivee FROM saisie WHERE immatriculation = ? ORDER BY saisie_id DESC LIMIT 1",
        (numero_immatriculation,)
    )
    indices_info = cursor.fetchone()

    conn.close()

    if vehicule_info:
        marque.config(state="normal")
        marque.delete(0, tk.END)
        marque.insert(0, vehicule_info[0])
        marque.config(state="disabled")

        carburant.config(state="normal")
        carburant.delete(0, tk.END)
        carburant.insert(0, vehicule_info[1])
        carburant.config(state="disabled")

        prix_carburant.config(state="normal")
        prix_carburant.delete(0, tk.END)
        prix_carburant.insert(0, vehicule_info[2])
        prix_carburant.config(state="disabled")
    else:
        # Affiche une boîte de dialogue si aucun véhicule n'est trouvé pour cet immatriculation
        messagebox.showerror("Erreur", "Aucun véhicule trouvé pour cet immatriculation.")
        marque.delete(0, tk.END)
        carburant.delete(0, tk.END)
        prix_carburant.delete(0, tk.END)

    # Remplir les champs d'indice de départ et d'arrivée si les informations sont disponibles
    if indices_info:
        entry_indice_depart.delete(0, tk.END)
        entry_indice_depart.insert(0, indices_info[0])

        entry_indice_arrivee.delete(0, tk.END)
        entry_indice_arrivee.insert(0, indices_info[1])
    else:
        # Effacer les champs si aucun indice n'est trouvé pour cet immatriculation
        entry_indice_depart.delete(0, tk.END)
        entry_indice_arrivee.delete(0, tk.END)

def update_combobox():
    # Met à jour le combobox d'immatriculation
    immatriculation['values'] = charger_immatriculations()
    immatriculation.set('')

def charger_immatriculations():
    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()

    cursor.execute("SELECT numero_immatriculation FROM vehicule")
    immatriculations = [row[0] for row in cursor.fetchall()]

    conn.close()
    return immatriculations

# Fonction pour calculer la distance du véhicule
def calculer_distance(event=None):
    try:
        # Récupérer les valeurs des entrées
        indice_depart = float(entry_indice_depart.get()) if entry_indice_depart.get() else 0
        indice_arrivee = float(entry_indice_arrivee.get()) if entry_indice_arrivee.get() else 0

        # Calculer la distance
        distance = abs(indice_arrivee - indice_depart)  # Utiliser la valeur absolue pour éviter les distances négatives

        # Afficher le résultat dans le champ de distance
        entry_distance.delete(0, tk.END)  # Vider l'entrée avant d'afficher le nouveau résultat
        entry_distance.insert(0, f"{distance:.2f}")  # Afficher la distance avec deux décimales

    except ValueError:
        # Gérer les erreurs de conversion
        entry_distance.delete(0, tk.END)
        messagebox.showerror("Erreur", "Veuillez saisir des valeurs numériques valides pour les indices.")

# ------------------------------------- Fonctions pour Carburant -------------------------------------------#

def calculer_prix_total(event=None):
    try:
        nombre_bon = int(entry_nombre_bon.get())
        prix_bon = float(entry_prix_bon.get())
        prix_total = nombre_bon * prix_bon
        entry_total.delete(0, tk.END)
        entry_total.insert(0, str(prix_total))
    except ValueError:
        entry_total.delete(0, tk.END)
        entry_total.insert(0, "Erreur")

# --------------------------------- Fonctions pour Apercu et Imprission ------------------------------------#

# Pour faire une apercu avant d'imprimer le document
def afficher_apercu():
    selected_item = tree_saisie.selection()
    if not selected_item:
        tk.messagebox.showwarning("Sélection requise", "Veuillez sélectionner une ligne dans le Tableaux.")
        return

    # Récupérer les données de l'item sélectionné
    item_data = tree_saisie.item(selected_item)["values"]

    # Créer une nouvelle fenêtre pour l'aperçu
    apercu_window = tk.Toplevel(data_entry_frame)
    apercu_window.iconphoto(False, tk.PhotoImage(file=resource_path('Images/CRSS_Carbu.png')))
    apercu_window.title("Aperçu les données")

    # Créer un widget Text pour afficher les données
    text_apercu = tk.Text(apercu_window, wrap=tk.WORD)
    text_apercu.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    # Afficher les données dans le widget Text, en excluant "saisie_id"
    columns = tree_saisie["columns"]
    for col, data in zip(columns, item_data):
        if col != "saisie_id":  # Exclure le champ "saisie_id"
            text_apercu.insert(tk.END, f'{col}: {data}\n')

    # Image du bouton
    doc_image = Image.open(resource_path("Images/doc.png"))
    doc_image = doc_image.resize((35, 35), Image.LANCZOS)
    doc_photo = ImageTk.PhotoImage(doc_image)
    apercu_window.doc_photo = doc_photo

    # Ajouter un bouton pour enregistrer dans un document Word
    save_button = tk.Button(apercu_window, text="Enregistrer en Word", image=doc_photo, compound="left",
                            command=lambda: save_to_word(item_data, apercu_window), padx=10)
    save_button.pack(pady=10)

def save_to_word(item_data, apercu_window):
    try:
        # Charger le modèle Word
        template_path = resource_path("Docs/Ordre_Mission.docx")
        document = DocxTemplate(template_path)

        # Préparer le contexte
        context = {
            'variable0': item_data[0],
            'variable1': item_data[1],
            'variable2': item_data[2],
            'variable3': item_data[8],
            'variable4': item_data[9],
            'variable5': item_data[10],
            'variable6': item_data[13],
            'variable7': item_data[12],
            'variable8': item_data[7],
            'variable9': item_data[4],
            'variable10': item_data[5],
            'variable11': item_data[11],
            'variable12': item_data[3],
            'variable13': item_data[18],
            'variable14': item_data[22]
        }

        # Rendre le document avec les données
        document.render(context)

        # Déterminer le chemin de sauvegarde dans le dossier "Bureau" (Desktop) de l'utilisateur
        desktop_path = Path.home() / "Desktop" / "CRSS_Nabeul_Carbu"  # Change "Documents" to "Desktop"
        desktop_path.mkdir(parents=True, exist_ok=True)

        word_file_path = desktop_path / "New_Ordre_Mission.docx"
        document.save(word_file_path)

        messagebox.showinfo("Enregistrement réussi", f"Les données ont été enregistrées dans {word_file_path}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de l'enregistrement : {e}")
    finally:
        # Fermer la fenêtre d'aperçu
        apercu_window.destroy()

# ----------------------------------------------------------------------------------------------------#
#                                Fonctions pour Enregistrer les données saisie
# ----------------------------------------------------------------------------------------------------#
def enregistrer_donnees():
    date_saisie = entry_date.get()
    obj_mission = objet_mission.get()
    charge = type_charge.get()
    date_sortie_value = date_sortie.get()
    date_arrivee_value = date_arrivee.get()
    lieux_dep = lieux_depart.get()
    lieux_arr = lieux_arrivee.get()
    nom_conducteur = entry_nom.get()
    prenom_conducteur = entry_prenom.get()
    role_conducteur = entry_role.get()
    nbre_acc = nbr_acc.get()
    immat = immatriculation.get()
    marque_vehicule = marque.get()
    type_carburant = carburant.get()
    prix_carburant_val = prix_carburant.get()
    indice_depart = entry_indice_depart.get()
    indice_arrivee = entry_indice_arrivee.get()
    distance = entry_distance.get()
    numero_bon = entry_numero_bon.get()
    nombre_bon = entry_nombre_bon.get()
    prix_bon = entry_prix_bon.get()
    prix_total = entry_total.get()

    # Vérifier que tous les champs requis sont remplis
    if date_saisie and obj_mission and charge and date_sortie_value and date_arrivee_value and lieux_dep and lieux_arr and nom_conducteur and prenom_conducteur and role_conducteur and nbre_acc and immat and marque_vehicule and type_carburant and prix_carburant_val and numero_bon and nombre_bon and prix_bon and prix_total:
        try:
            # Validation des types pour indice_depart et indice_arrivee
            indice_depart = float(indice_depart)  # Convertit en float
            indice_arrivee = float(indice_arrivee)  # Convertit en float

            # Se connecter à la base de données
            conn = sqlite3.connect(resource_path('Data/main.db'))
            cursor = conn.cursor()

            # Insérer les données
            cursor.execute('''
                INSERT INTO saisie (date_saisie, objet_mission, type_charge, date_sortie, date_arrivee, lieux_depart, lieux_arrivee, nom_conducteur, prenom_conducteur, role, nbre_acc, immatriculation, marque_vehicule, type_carburant, prix_carburant, indice_depart, indice_arrivee, distance, numero_bon, nombre_bon, prix_bon, prix_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                date_saisie, obj_mission, charge, date_sortie_value, date_arrivee_value, lieux_dep, lieux_arr,
                nom_conducteur,
                prenom_conducteur, role_conducteur, nbre_acc, immat, marque_vehicule, type_carburant,
                prix_carburant_val,
                indice_depart, indice_arrivee, distance, numero_bon, nombre_bon, prix_bon, prix_total))

            conn.commit()
            conn.close()

            # Recharger les données et réinitialiser les champs
            load_all_saisie()
            update_comboboxes()

            messagebox.showinfo("Succès", "Les données ont été enregistrées avec succès.")
            clear_donnees()
            root.update_idletasks()
        except ValueError:
            # Lever une erreur si les indices ne sont pas des nombres réels ou entiers
            messagebox.showerror("Erreur",
                                 "Les indices de départ et d'arrivée doivent être des nombres réels ou entiers.")
    else:
        messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")

def clear_donnees():
    # Liste des champs à effacer avec leur état initial
    fields = [
        (entry_date, entry_date.cget("state")),
        (objet_mission, objet_mission.cget("state")),
        (type_charge, type_charge.cget("state")),
        (date_sortie, date_sortie.cget("state")),
        (date_arrivee, date_arrivee.cget("state")),
        (lieux_depart, lieux_depart.cget("state")),
        (lieux_arrivee, lieux_arrivee.cget("state")),
        (entry_nom, entry_nom.cget("state")),
        (entry_prenom, entry_prenom.cget("state")),
        (entry_role, entry_role.cget("state")),
        (nbr_acc, nbr_acc.cget("state")),
        (combobox_ids, combobox_ids.cget("state")),
        (immatriculation, immatriculation.cget("state")),
        (marque, marque.cget("state")),
        (carburant, carburant.cget("state")),
        (prix_carburant, prix_carburant.cget("state")),
        (entry_indice_depart, entry_indice_depart.cget("state")),
        (entry_indice_arrivee, entry_indice_arrivee.cget("state")),
        (entry_distance, entry_distance.cget("state")),
        (entry_numero_bon, entry_numero_bon.cget("state")),
        (entry_nombre_bon, entry_nombre_bon.cget("state")),
        (entry_prix_bon, entry_prix_bon.cget("state")),
        (entry_total, entry_total.cget("state")),
    ]

    # Effacer les champs en les activant temporairement si nécessaire
    for field, original_state in fields:
        field.config(state=tk.NORMAL)
        field.delete(0, tk.END)
        field.config(state=original_state)

def mettre_a_jour_donnees():
    try:
        # Vérifier qu'une ligne est bien sélectionnée dans le TreeView
        if not tree_saisie.selection():
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un enregistrement dans la liste.")
            return

        # Récupérer les valeurs actuelles de la ligne sélectionnée
        selected_item = tree_saisie.selection()[0]
        values = tree_saisie.item(selected_item, 'values')
        saisie_id = values[0]  # ID unique de l'enregistrement

        # Récupérer les données actuelles affichées dans les champs
        champs_actuels = {
            "date_saisie": values[1].strip(),
            "objet_mission": values[2].strip(),
            "type_charge": values[3].strip(),
            "date_sortie": values[4].strip(),
            "date_arrivee": values[5].strip(),
            "lieux_depart": values[6].strip(),
            "lieux_arrivee": values[7].strip(),
            "nbre_acc": values[11].strip(),
            "indice_depart": values[16].strip(),
            "indice_arrivee": values[17].strip(),
            "distance": values[18].strip(),
            "numero_bon": values[19].strip(),
            "nombre_bon": values[20].strip(),
            "prix_bon": values[21].strip(),
            "prix_total": values[22].strip(),
        }

        # Récupérer les nouvelles données saisies dans les champs
        champs_nouveaux = {
            "date_saisie": entry_date.get().strip(),
            "objet_mission": objet_mission.get().strip(),
            "type_charge": type_charge.get().strip(),
            "date_sortie": date_sortie.get().strip(),
            "date_arrivee": date_arrivee.get().strip(),
            "lieux_depart": lieux_depart.get().strip(),
            "lieux_arrivee": lieux_arrivee.get().strip(),
            "nbre_acc": nbr_acc.get().strip(),
            "indice_depart": entry_indice_depart.get().strip(),
            "indice_arrivee": entry_indice_arrivee.get().strip(),
            "distance": entry_distance.get().strip(),
            "numero_bon": entry_numero_bon.get().strip(),
            "nombre_bon": entry_nombre_bon.get().strip(),
            "prix_bon": entry_prix_bon.get().strip(),
            "prix_total": entry_total.get().strip(),
        }

        # Validation des types pour indice_depart et indice_arrivee
        try:
            champs_nouveaux["indice_depart"] = float(champs_nouveaux["indice_depart"])  # Convertit en float
            champs_nouveaux["indice_arrivee"] = float(champs_nouveaux["indice_arrivee"])  # Convertit en float
        except ValueError:
            messagebox.showerror("Erreur", "Les indices de départ et d'arrivée doivent être des nombres réels ou entiers.")
            return

        # Identifier les modifications
        champs_modifies = [
            champ for champ in champs_actuels
            if champs_actuels[champ] != str(champs_nouveaux[champ])  # Convertir en str pour comparer
        ]

        # Si aucun champ n'a été modifié
        if not champs_modifies:
            messagebox.showinfo("Information", "Aucune modification détectée.")
            return

        # Sinon, mettre à jour les données
        conn = sqlite3.connect(resource_path('Data/main.db'))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE saisie 
            SET date_saisie = ?, objet_mission = ?, type_charge = ?, date_sortie = ?, date_arrivee = ?, lieux_depart = ?, 
                lieux_arrivee = ?, nbre_acc = ?, indice_depart = ?, indice_arrivee = ?, distance = ?, numero_bon = ?, 
                nombre_bon = ?, prix_bon = ?, prix_total = ? 
            WHERE saisie_id = ?
        ''', (
            champs_nouveaux["date_saisie"], champs_nouveaux["objet_mission"], champs_nouveaux["type_charge"],
            champs_nouveaux["date_sortie"], champs_nouveaux["date_arrivee"], champs_nouveaux["lieux_depart"],
            champs_nouveaux["lieux_arrivee"], champs_nouveaux["nbre_acc"], champs_nouveaux["indice_depart"],
            champs_nouveaux["indice_arrivee"], champs_nouveaux["distance"], champs_nouveaux["numero_bon"],
            champs_nouveaux["nombre_bon"], champs_nouveaux["prix_bon"], champs_nouveaux["prix_total"], saisie_id
        ))
        conn.commit()
        conn.close()

        # Recharger les données du TreeView
        load_all_saisie()
        messagebox.showinfo(
            "Succès",
            f"Les données ont été mises à jour avec succès.\nChamps modifiés : {', '.join(champs_modifies)}"
        )
        clear_donnees()
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {str(e)}")

def on_saisie_selected(event):
    try:
        selected_item = tree_saisie.selection()[0]
        values = tree_saisie.item(selected_item, 'values')

        # Remplir les champs avec les valeurs sélectionnées
        entry_date.delete(0, tk.END)
        entry_date.insert(0, values[1])

        objet_mission.delete(0, tk.END)
        objet_mission.insert(0, values[2])
        type_charge.delete(0, tk.END)
        type_charge.insert(0, values[3])
        date_sortie.delete(0, tk.END)
        date_sortie.insert(0, values[4])
        date_arrivee.delete(0, tk.END)
        date_arrivee.insert(0, values[5])
        lieux_depart.delete(0, tk.END)
        lieux_depart.insert(0, values[6])
        lieux_arrivee.delete(0, tk.END)
        lieux_arrivee.insert(0, values[7])
        entry_nom.delete(0, tk.END)
        entry_nom.insert(0, values[8])
        entry_prenom.delete(0, tk.END)
        entry_prenom.insert(0, values[9])
        entry_role.delete(0, tk.END)
        entry_role.insert(0, values[10])
        nbr_acc.delete(0, tk.END)
        nbr_acc.insert(0, values[11])
        immatriculation.delete(0, tk.END)
        immatriculation.insert(0, values[12])
        marque.delete(0, tk.END)
        marque.insert(0, values[13])
        carburant.delete(0, tk.END)
        carburant.insert(0, values[14])
        prix_carburant.delete(0, tk.END)
        prix_carburant.insert(0, values[15])
        entry_indice_depart.delete(0, tk.END)
        entry_indice_depart.insert(0, values[16])
        entry_indice_arrivee.delete(0, tk.END)
        entry_indice_arrivee.insert(0, values[17])
        entry_distance.delete(0, tk.END)
        entry_distance.insert(0, values[18])
        entry_numero_bon.delete(0, tk.END)
        entry_numero_bon.insert(0, values[19])
        entry_nombre_bon.delete(0, tk.END)
        entry_nombre_bon.insert(0, values[20])
        entry_prix_bon.delete(0, tk.END)
        entry_prix_bon.insert(0, values[21])
        entry_total.delete(0, tk.END)
        entry_total.insert(0, values[22])
    except IndexError:
        pass

# Fonction pour charger les données dans le tableaux de saisie
def load_all_saisie():
    tree_saisie.delete(*tree_saisie.get_children())
    conn = sqlite3.connect(resource_path('Data/main.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saisie")
    saisies = cursor.fetchall()
    conn.close()

    for saisie in saisies:
        tree_saisie.insert("", tk.END, values=(
        saisie[0], saisie[1], saisie[2], saisie[3], saisie[4], saisie[5], saisie[6], saisie[7], saisie[8], saisie[9],
        saisie[10], saisie[11], saisie[12], saisie[13], saisie[14], saisie[15], saisie[16], saisie[17], saisie[18],
        saisie[19], saisie[20], saisie[21], saisie[22]))


# Supprimer les données
def supprimer_donnees():
    # Vérifier si un élément est sélectionné dans le Treeview
    selected_item = tree_saisie.selection()
    if not selected_item:
        messagebox.showwarning("Avertissement", "Sélectionnez un saisie à supprimer.")
        return

    # Récupérer l'ID du véhicule sélectionné
    item = tree_saisie.item(selected_item)
    saisie_id = item['values'][0]

    try:
        # Demander le mot de passe à l'utilisateur
        mot_de_passe = simpledialog.askstring(
            "Mot de passe requis",
            "Veuillez entrer votre mot de passe pour confirmer la suppression :",
            show="*"
        )

        if not mot_de_passe:
            messagebox.showwarning("Avertissement", "La suppression a été annulée car le mot de passe n'a pas été fourni.")
            return

        # Vérifier si le mot de passe est correct
        mot_de_passe_correct = "admin"
        if mot_de_passe != mot_de_passe_correct:
            messagebox.showerror("Erreur", "Mot de passe incorrect. La suppression a été annulée.")
            return

        # Confirmation de suppression
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce saisie ?"):
            with sqlite3.connect(resource_path('Data/main.db')) as conn:
                cursor = conn.cursor()
                # Supprimer le saisie de la base de données
                cursor.execute('''
                DELETE FROM saisie
                WHERE saisie_id = ?
                ''', (saisie_id,))
                conn.commit()

                # Réindexer les ID des saisies restants
                cursor.execute('''
                UPDATE saisie
                SET saisie_id = (
                    SELECT rowid
                    FROM (
                        SELECT rowid, ROW_NUMBER() OVER(ORDER BY saisie_id) AS new_id
                        FROM saisie
                    )
                    WHERE rowid = saisie.rowid
                )
                ''')

                # Réinitialiser l'auto-incrémentation de l'ID
                cursor.execute('DELETE FROM sqlite_sequence WHERE name="saisie"')
                conn.commit()

            # Recharger les données dans le Treeview
            load_all_saisie()
            root.update_idletasks()

            # Afficher une confirmation
            messagebox.showinfo("Info", "Saisie supprimée avec succès.")
            clear_donnees()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression du saisie : {e}")

# --------------------------------------------------------------------------------------------------------------------------------------------#
#                                                Fonctions pour Consommations
# --------------------------------------------------------------------------------------------------------------------------------------------#
def connect_to_db():
    try:
        conn = sqlite3.connect(resource_path('Data/main.db'))
        return conn
    except sqlite3.Error as e:
        print("Erreur de connexion à la base de données:", e)
        return None

def fetch_immatriculations(conn):
    query = "SELECT DISTINCT immatriculation FROM saisie"
    cursor = conn.cursor()
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def fetch_conducteur_ids(conn):
    query = "SELECT conducteur_id FROM conducteur"
    cursor = conn.cursor()
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def fetch_years(conn):
    query = """
    SELECT DISTINCT strftime('%Y', date(substr(date_sortie, 7, 4) || '-' || substr(date_sortie, 4, 2) || '-' || substr(date_sortie, 1, 2))) 
    FROM saisie
    WHERE date_sortie IS NOT NULL
    """
    cursor = conn.cursor()
    cursor.execute(query)
    years = [row[0] for row in cursor.fetchall()]
    print("Années récupérées:", years)
    return years

MONTH_NUMBER_TO_NAME = {
    "01": "Janvier",
    "02": "Février",
    "03": "Mars",
    "04": "Avril",
    "05": "Mai",
    "06": "Juin",
    "07": "Juillet",
    "08": "Août",
    "09": "Septembre",
    "10": "Octobre",
    "11": "Novembre",
    "12": "Décembre"
}

def fetch_months(conn, year):
    query = """
    SELECT DISTINCT substr(date_sortie, 4, 2) AS month
    FROM saisie
    WHERE substr(date_sortie, 7, 4) = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (year,))
    months_numbers = [row[0] for row in cursor.fetchall()]
    months_names = [MONTH_NUMBER_TO_NAME.get(mois) for mois in months_numbers]
    print(f"Année sélectionnée: {year}")
    print(f"Numéros de mois récupérés: {months_numbers}")
    print(f"Noms des mois récupérés: {months_names}")
    return months_names

def consommation_mensuelle(conn, annee, mois_nom):
    MONTH_NAME_TO_NUMBER = {v: k for k, v in MONTH_NUMBER_TO_NAME.items()}
    mois = MONTH_NAME_TO_NUMBER.get(mois_nom)

    print(f"Année: {annee}, Mois: {mois}")

    if mois:
        query = """
        SELECT 
        -- Consommation totale en litres calculée à partir des indices d'arrivée et de départ
        ROUND(SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance), 0) AS total_litres,
        
        -- Distance totale parcourue
        SUM(distance) AS total_distance,
        
        -- Consommation moyenne en litres par 100 km
        ROUND((SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) / SUM(distance)) * 100, 2) AS consommation_L_100km,
        
        -- Nombre total de bons consommés
        SUM(nombre_bon) AS total_bons_consommes,
        
        -- Coût total de carburant
        SUM(prix_total) AS cout_total_carburant
        FROM saisie
        WHERE strftime('%Y', date(substr(date_sortie, 7, 4) || '-' || substr(date_sortie, 4, 2) || '-' || substr(date_sortie, 1, 2))) = ?
        AND strftime('%m', date(substr(date_sortie, 7, 4) || '-' || substr(date_sortie, 4, 2) || '-' || substr(date_sortie, 1, 2))) = ?
        """
        cursor = conn.cursor()
        cursor.execute(query, (annee, mois))
        result = cursor.fetchone()
        print(f"Résultat de la requête: {result}")
        return result
    else:
        return (0, 0)

def consommation_par_voiture(conn, immatriculation):
    query = """
    SELECT 
        -- Consommation totale en litres calculée à partir des indices d'arrivée et de départ
        SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) AS total_litres,
        
        -- Distance totale parcourue
        SUM(distance) AS total_distance,
        
        -- Consommation moyenne en litres par 100 km
        ROUND((SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) / SUM(distance)) * 100, 2) AS consommation_L_100km,
        
        -- Nombre total de bons consommés
        SUM(nombre_bon) AS total_bons_consommes,
        
        -- Coût total de carburant
        SUM(prix_total) AS cout_total_carburant
    FROM saisie
    WHERE immatriculation = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (immatriculation,))
    return cursor.fetchone()

def consommation_annuelle(conn, annee):
    query = """
    SELECT 
        -- Consommation totale en litres calculée à partir des indices d'arrivée et de départ
        SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) AS total_litres,
        
        -- Distance totale parcourue
        SUM(distance) AS total_distance,
        
        -- Consommation moyenne en litres par 100 km
        ROUND((SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) / SUM(distance)) * 100, 2) AS consommation_L_100km,
        
        -- Nombre total de bons consommés
        SUM(nombre_bon) AS total_bons_consommes,
        
        -- Coût total de carburant
        SUM(prix_total) AS cout_total_carburant
    FROM saisie
    WHERE strftime('%Y', date(substr(date_sortie, 7, 4) || '-' || substr(date_sortie, 4, 2) || '-' || substr(date_sortie, 1, 2))) = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (annee,))
    return cursor.fetchone()

def consommation_par_conducteur(conn, id_conducteur):
    query = """
    SELECT 
        -- Consommation totale en litres calculée à partir des indices d'arrivée et de départ
        SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) AS total_litres,
        
        -- Distance totale parcourue
        SUM(distance) AS total_distance,
        
        -- Consommation moyenne en litres par 100 km
        ROUND((SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) / SUM(distance)) * 100, 2) AS consommation_L_100km,
        
        -- Nombre total de bons consommés par le conducteur
        SUM(nombre_bon) AS total_bons_consommes,
        
        -- Coût total de carburant
        SUM(prix_total) AS cout_total_carburant
    FROM saisie
    WHERE nom_conducteur = (SELECT nom_conducteur FROM conducteur WHERE conducteur_id = ?)
    """
    cursor = conn.cursor()
    cursor.execute(query, (id_conducteur,))
    return cursor.fetchone()

def consommation_par_dates(conn, date_debut, date_fin):
    query = """
    SELECT 
        -- Consommation totale en litres calculée à partir des indices d'arrivée et de départ
        SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) AS total_litres,
        
        -- Distance totale parcourue
        SUM(distance) AS total_distance,
        
        -- Consommation moyenne en litres par 100 km
        ROUND((SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) / SUM(distance)) * 100, 2) AS consommation_L_100km,
        
        -- Nombre total de bons consommés
        SUM(nombre_bon) AS total_bons_consommes,
        
        -- Coût total de carburant
        SUM(prix_total) AS cout_total_carburant
    FROM saisie
    WHERE date_sortie BETWEEN ? AND ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (date_debut, date_fin))
    return cursor.fetchone()

def update_comboboxes():
    conn = connect_to_db()

    immatriculations = fetch_immatriculations(conn)
    conducteur_ids = fetch_conducteur_ids(conn)
    years = fetch_years(conn)

    immatriculation_combobox['values'] = immatriculations
    conducteur_id_combobox['values'] = conducteur_ids
    annee_combobox['values'] = years

    # Initialiser le mois_combobox avec les mois pour la première année sélectionnée
    if years:
        selected_year = years[0]
        months = fetch_months(conn, selected_year)
        mois_combobox['values'] = months

    conn.close()

    # Bind the year selection to update months
    annee_combobox.bind('<<ComboboxSelected>>', on_year_selected)

def on_year_selected(event):
    selected_year = annee_combobox.get()
    if selected_year:
        conn = connect_to_db()
        if conn:
            months = fetch_months(conn, selected_year)
            mois_combobox['values'] = months
            conn.close()

# Déclaration des variables globales
resultats_window = None
tree = None

def afficher_resultats():
    global resultats_window, tree

    # Vérification et réinitialisation si la fenêtre a été détruite
    if resultats_window is not None and not resultats_window.winfo_exists():
        resultats_window = None

    if resultats_window is None:
        resultats_window = tk.Toplevel(rapports_frame)
        resultats_window.title("Résultats de Consommation")
        resultats_window.iconphoto(False, tk.PhotoImage(file=resource_path('Images/CRSS_Carbu.png')))

        columns = ("Type de consommation", "Total Litres (L)", "Total Distance (km)", "Consommation moyenne (L/100 km)", "Nombre total de bons", "Coût total de carburant (TND)")
        tree = ttk.Treeview(resultats_window, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col, anchor="center")
            tree.column(col, anchor="center", width=200)

        tree.grid(row=0, column=0, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(resultats_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Image du bouton
        doc_image = Image.open(resource_path("Images/doc.png"))
        doc_image = doc_image.resize((35, 35), Image.LANCZOS)
        imp_doc = ImageTk.PhotoImage(doc_image)
        resultats_window.imp_doc = imp_doc

        close_img = Image.open(resource_path("Images/close.png"))
        close_img = close_img.resize((35, 35), Image.LANCZOS)
        close_imp = ImageTk.PhotoImage(close_img)
        resultats_window.close_imp = close_imp

        # Ajouter un bouton pour enregistrer dans un document Word
        imprimer_button = tk.Button(resultats_window, text="Enregistrer en Word", image=imp_doc, compound="left",
                                    command=imprimer_treeview, padx=10)
        imprimer_button.grid(row=1, column=0)

        # Ajouter un label vide pour l'espace
        espace = tk.Label(resultats_window, text="")
        espace.grid(row=2, column=0)

        quitter_button = tk.Button(resultats_window, text="Quitter", image=close_imp, compound="left",
                                   command=resultats_window.destroy, padx=10)
        quitter_button.grid(row=3, column=0)

    else:
        # Vérifier si `tree` existe avant de tenter de le vider
        if tree.winfo_exists():
            tree.delete(*tree.get_children())

    # Connexion à la base de données et remplissage du treeview
    conn = connect_to_db()
    if conn:
        def ajouter_resultat(titre, litres, distance, consommation_L_100km, Nombre_total_bons,
                             Coût_total_carburant):
            tree.insert("", "end", values=(
                titre,
                litres if litres else 0,
                distance if distance is not None else "",
                consommation_L_100km,
                Nombre_total_bons,
                Coût_total_carburant
            ))

        # Récupérer la marque d'un véhicule
        def get_marque_par_immatriculation(conn, immatriculation):
            cursor = conn.cursor()
            cursor.execute("SELECT marque_vehicule FROM saisie WHERE immatriculation = ?", (immatriculation,))
            result = cursor.fetchone()
            return result[0] if result else None

        # Ajouter les différentes consommations
        if var_voiture.get():
            immatriculation = immatriculation_combobox.get()
            marque = get_marque_par_immatriculation(conn, immatriculation)

            litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant = consommation_par_voiture(
                conn, immatriculation)

            titre = f"Consommation par véhicule ({marque})" if marque else f"Consommation par véhicule ({immatriculation})"

            ajouter_resultat(titre, litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant)

        if var_annuelle.get():
            annee = annee_combobox.get()
            litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant = consommation_annuelle(conn, annee)
            ajouter_resultat(f"Consommation annuelle ({annee})", litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant)

        if var_mensuelle.get():
            annee = annee_combobox.get()
            mois = mois_combobox.get()
            litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant = consommation_mensuelle(conn, annee, mois)
            ajouter_resultat(f"Consommation mensuelle ({mois} - {annee})", litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant)

        if var_conducteur.get():
            id_conducteur = conducteur_id_combobox.get()
            litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant = consommation_par_conducteur(conn, id_conducteur)
            ajouter_resultat(f"Consommation par conducteur ({id_conducteur})", litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant)

        if var_dates.get():
            date_debut = date_debut_entry.get()
            date_fin = date_fin_entry.get()
            litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant = consommation_par_dates(conn, date_debut, date_fin)
            ajouter_resultat(f"Consommation entre {date_debut} et {date_fin}", litres, distance, consommation_L_100km, Nombre_total_bons, Coût_total_carburant)

        conn.close()

def imprimer_treeview():
    try:
        # Charger le modèle Word
        doc = Document(resource_path('Docs/Consommation.docx'))
        tableau = doc.tables[0]

        # Remplir le tableau avec les données de Treeview
        for row_id in tree.get_children():
            row_values = tree.item(row_id, 'values')
            row_cells = tableau.add_row().cells
            for i, value in enumerate(row_values):
                row_cells[i].text = str(value)

        # Déterminer le chemin de sauvegarde dans le dossier "Documents" de l'utilisateur
        documents_path = Path.home() / "Desktop" / "CRSS_Nabeul_Carbu"
        documents_path.mkdir(parents=True, exist_ok=True)  # Crée le dossier s'il n'existe pas

        # Sauvegarder le document modifié dans un emplacement permanent
        output_path = documents_path / "Résultat_Consommation.docx"
        doc.save(output_path)

        messagebox.showinfo("Succès", f"Les données ont été enregistrées dans {output_path}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de l'enregistrement du document : {e}")

def fetch_consumption_by_vehicle(conn):
    query = """
    SELECT immatriculation, SUM((CAST(indice_arrivee AS REAL) - CAST(indice_depart AS REAL)) / 100.0 * distance) AS total_litres
    FROM saisie
    GROUP BY immatriculation
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# le dashboard
def afficher_dashboard():
    conn = connect_to_db()  # Connexion à la base de données

    # Création d'une nouvelle fenêtre pour le tableau de bord
    dashboard_window = tk.Toplevel()
    dashboard_window.title("Dashboard")
    dashboard_window.iconphoto(False, tk.PhotoImage(file=resource_path('Images/CRSS_Carbu.png')))

    # Créer un frame pour les options de sélection de graphique
    options_frame = tk.Frame(dashboard_window)
    options_frame.pack(pady=20)

    # Liste des options pour les graphiques
    options = [
        ("Consommation par Véhicule", tk.BooleanVar()),
        ("Nombre de Sorties par Conducteur", tk.BooleanVar()),
        ("Nombre de Sorties par Véhicule", tk.BooleanVar())
    ]

    # Liste pour stocker les variables des Checkbuttons
    check_vars = []

    # Créer un frame pour les checkbuttons
    check_frame = tk.Frame(options_frame)
    check_frame.pack(side=tk.LEFT)

    # Combobox pour sélectionner un conducteur
    selected_conducteur = tk.StringVar()
    conducteur_combo = ttk.Combobox(options_frame, textvariable=selected_conducteur, values=[])
    conducteur_combo.pack(side=tk.LEFT)
    conducteur_combo.set("Sélectionner un conducteur")  # Valeur par défaut

    # Récupérer la liste des conducteurs pour la combobox
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT nom_conducteur FROM saisie")
    conducteurs = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Mettre à jour la Combobox avec les conducteurs récupérés
    conducteur_combo['values'] = conducteurs

    # Créer les checkbuttons à partir des options
    for text, var in options:
        var = tk.BooleanVar()
        check_vars.append(var)  # Ajoute la variable à la liste
        checkbutton = tk.Checkbutton(check_frame, text=text, variable=var,
                                     font=("Helvetica", 12))  # Taille de texte définie ici
        checkbutton.pack(anchor=tk.W)  # Alignement à gauche

    # Frame pour contenir les graphiques
    graph_frame = tk.Frame(dashboard_window)
    graph_frame.pack(pady=20)

    def afficher_graphiques():
        conn_local = connect_to_db()  # Connexion à la base de données
        cursor = conn_local.cursor()  # Créer le curseur

        # Effacer le contenu précédent du graph_frame
        for widget in graph_frame.winfo_children():
            widget.destroy()

        # Afficher le graphique de consommation par véhicule si sélectionné
        if check_vars[0].get():  # Consommation par véhicule
            consommation_vehicules = fetch_consumption_by_vehicle(conn_local)
            vehicules = [row[0] for row in consommation_vehicules]
            consommation = [row[1] for row in consommation_vehicules]

            fig1, ax1 = plt.subplots(figsize=(5, 4))  # Taille personnalisée en pouces
            ax1.bar(vehicules, consommation, color=['blue', 'green', 'orange'])
            ax1.set_title("Consommation par Véhicule")
            ax1.set_ylabel("Litres")
            chart1 = FigureCanvasTkAgg(fig1, master=graph_frame)
            chart1.draw()
            chart1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

        # Afficher le graphique de sorties par conducteur si sélectionné
        if check_vars[1].get():  # Nombre de sorties par conducteur
            conducteur = selected_conducteur.get()  # Récupérer le conducteur sélectionné
            if conducteur != "Sélectionner un conducteur":
                cursor.execute("""
                    SELECT 
                        nom_conducteur, 
                        COUNT(*) AS nombre_sorties
                    FROM saisie
                    WHERE nom_conducteur = ?
                """, (conducteur,))
                data_conducteur = cursor.fetchall()
                nombre_sorties_conducteur = [row[1] for row in data_conducteur]

                fig2, ax2 = plt.subplots(figsize=(5, 4))
                ax2.bar([conducteur], nombre_sorties_conducteur, color='purple')
                ax2.set_title(f"Nombre de Sorties pour {conducteur}")
                ax2.set_xlabel("Les Conducteur")
                ax2.set_ylabel("Nombre de Sorties")

                # S'assurer que l'axe y affiche des entiers
                ax2.set_yticks(range(1, max(nombre_sorties_conducteur) + 1))

                chart2 = FigureCanvasTkAgg(fig2, master=graph_frame)
                chart2.draw()
                chart2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

        # Afficher le graphique de sorties par véhicule si sélectionné
        if check_vars[2].get():  # Nombre de sorties par véhicule
            cursor.execute("""
                SELECT 
                    immatriculation, 
                    COUNT(*) AS nombre_sorties
                FROM saisie
                GROUP BY immatriculation
            """)
            data_vehicule = cursor.fetchall()
            vehicules = [row[0] for row in data_vehicule]
            nombre_sorties_vehicule = [int(row[1]) for row in data_vehicule]  # Conversion en entier

            fig3, ax3 = plt.subplots(figsize=(5, 4))
            ax3.bar(vehicules, nombre_sorties_vehicule, color='teal')
            ax3.set_title("Nombre de Sorties par Véhicule")
            ax3.set_xlabel("Les Véhicules")
            ax3.set_ylabel("Nombre de Sorties")
            ax3.set_xticks(range(len(vehicules)))

            # Forcer l'affichage des entiers sur l'axe des ordonnées
            ax3.yaxis.get_major_locator().set_params(integer=True)

            chart3 = FigureCanvasTkAgg(fig3, master=graph_frame)
            chart3.draw()
            chart3.get_tk_widget().grid(row=0, column=2, padx=10, pady=10)

        # Fermer le curseur et la connexion après utilisation
        cursor.close()
        conn_local.close()

    graph_img = Image.open(resource_path("Images/graph.png"))
    graph_img = graph_img.resize((35, 35), Image.LANCZOS)
    graph_imp = ImageTk.PhotoImage(graph_img)
    dashboard_window.graph_imp = graph_imp

    close_img = Image.open(resource_path("Images/close.png"))
    close_img = close_img.resize((35, 35), Image.LANCZOS)
    close_imp = ImageTk.PhotoImage(close_img)
    dashboard_window.close_imp = close_imp

    # Bouton pour afficher les graphiques sélectionnés
    tk.Button(dashboard_window, text="Afficher les Graphiques", image=graph_imp, compound="top", command=afficher_graphiques).pack(pady=10)

    # Bouton pour quitter le dashboard window
    tk.Button(dashboard_window, text="Quitter", image=close_imp, compound="left", command=dashboard_window.destroy).pack(pady=10)

# Fonction pour rechercher dans le Treeview lorsque l'utilisateur appuie sur Entrée
def rechercher_dans_treeview(event=None):
    saisie_id = search_entry.get().strip()

    if not saisie_id:
        # Si le champ est vide, réinitialiser le Treeview
        recharger_treeview()
        return

    # Récupérer tous les éléments du Treeview
    items = tree_saisie.get_children()

    # Parcourir les éléments pour trouver ceux qui correspondent
    correspondance_trouvee = False
    for item in items:
        valeurs = tree_saisie.item(item, "values")

        # Si une correspondance est trouvée avec l'ID saisie
        if valeurs[0] == saisie_id:  # Assurez-vous que l'ID Saisie est dans la première colonne
            # Supprimer tous les éléments actuels
            for i in items:
                tree_saisie.delete(i)

            # Réinsérer uniquement la ligne correspondante
            tree_saisie.insert("", "end", values=valeurs)
            correspondance_trouvee = True
            break

    # Si aucune correspondance n'est trouvée
    if not correspondance_trouvee:
        messagebox.showinfo("Résultat", "Aucun résultat trouvé pour l'ID saisi.")

# Fonction pour réinitialiser automatiquement le Treeview
def recharger_treeview():
    # Supprimer toutes les lignes actuelles du Treeview
    for item in tree_saisie.get_children():
        tree_saisie.delete(item)

    # Recharger toutes les données initiales
    load_all_saisie()

# Fonction pour gérer les touches spécifiques (Retour arrière ou Supprimer)
def gerer_touches_specifiques(event):
    # Réinitialiser si Retour arrière ou Supprimer est pressé et le champ est vide
    if event.keysym in ("BackSpace", "Delete") and not search_entry.get().strip():
        recharger_treeview()

def show_data_entry_frame():
    main_buttons_frame.grid_forget()
    data_entry_frame.grid()

# Définir la locale en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Initialize database
init_db()

# Main application
root = tk.Tk()
root.state('zoomed')
root.title("CRSS Nabeul Carbu")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.iconphoto(False, tk.PhotoImage(file=resource_path('Images/CRSS_Carbu.png')))

# Login Frame
login_frame = tk.Frame(root, padx=10, pady=10)

image_login = Image.open(resource_path("Images/utss.png"))
image_login = image_login.resize((500, 150), Image.Resampling.LANCZOS)
photo_login = ImageTk.PhotoImage(image_login)
logo_label = tk.Label(login_frame, image=photo_login)
logo_label.grid(row=0, columnspan=2, pady=10)

login_label = tk.Label(login_frame, text="Connexion", font=("Helvetica", 20))
login_label.grid(row=1, columnspan=2, pady=10, sticky='nsew')

# Login icon
login_image = Image.open(resource_path("Images/login.png"))
login_image = login_image.resize((35, 35), Image.LANCZOS)
login_photo = ImageTk.PhotoImage(login_image)

# Signup icon
signup_image = Image.open(resource_path("Images/compte.png"))
signup_image = signup_image.resize((35, 35), Image.LANCZOS)
signup_photo = ImageTk.PhotoImage(signup_image)

username_label = tk.Label(login_frame, text="Nom d'utilisateur :")
username_label.grid(row=2, column=0, sticky='e', padx=10, pady=10)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)

password_label = tk.Label(login_frame, text="Mot de passe :")
password_label.grid(row=3, column=0, sticky='e', padx=10, pady=10)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=3, column=1, sticky='w', padx=10, pady=10)
password_entry.bind('<Return>', lambda event: check_login())

login_button = tk.Button(login_frame, text="Se connecter", image=login_photo, compound=tk.TOP, command=check_login)
login_button.grid(row=4, column=0, sticky="ew", padx=10, pady=10)

signup_button = tk.Button(login_frame, text="Créer un compte", image=signup_photo, compound=tk.TOP,
                          command=show_signup_frame)
signup_button.grid(row=4, column=1, sticky="ew", padx=10, pady=10)

# Signup Frame
signup_frame = tk.Frame(root, padx=10, pady=10)

image_signup = Image.open(resource_path("Images/utss.png"))
image_signup = image_signup.resize((500, 150), Image.Resampling.LANCZOS)
photo_signup = ImageTk.PhotoImage(image_signup)
image_label_signup = tk.Label(signup_frame, image=photo_signup)
image_label_signup.grid(row=0, columnspan=2, pady=10)

signup_label = tk.Label(signup_frame, text="Créer un Compte", font=("Helvetica", 20))
signup_label.grid(row=1, columnspan=2, pady=10, sticky='nsew')

# Retour icon
retour_image = Image.open(resource_path("Images/retour.png"))
retour_image = retour_image.resize((35, 35), Image.LANCZOS)
retour_photo = ImageTk.PhotoImage(retour_image)

signup_username_label = tk.Label(signup_frame, text="Nom d'utilisateur :")
signup_username_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
signup_username_entry = tk.Entry(signup_frame)
signup_username_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)

signup_password_label = tk.Label(signup_frame, text="Mot de passe :")
signup_password_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)
signup_password_entry = tk.Entry(signup_frame, show="*")
signup_password_entry.grid(row=3, column=1, sticky="w", padx=10, pady=10)

confirm_password_label = tk.Label(signup_frame, text="Confirmer mot de passe :")
confirm_password_label.grid(row=4, column=0, sticky="e", padx=10, pady=10)
confirm_password_entry = tk.Entry(signup_frame, show="*")
confirm_password_entry.grid(row=4, column=1, sticky="w", padx=10, pady=10)
confirm_password_entry.bind('<Return>', lambda event: add_user())

create_account_button = tk.Button(signup_frame, text="Créer un compte", image=signup_photo, compound=tk.TOP,
                                  command=add_user)
create_account_button.grid(row=5, column=0, sticky="ew", padx=10, pady=10)

back_to_login_button = tk.Button(signup_frame, text="Retour", image=retour_photo, compound=tk.TOP,
                                 command=show_login_frame)
back_to_login_button.grid(row=5, column=1, sticky="ew", padx=10, pady=10)

# Main Buttons Frame
main_buttons_frame = tk.Frame(root, padx=10, pady=10)

# Load and place the logo
logo = Image.open(resource_path("Images/CRSS_Carbu.png"))
logo = logo.resize((200, 150), Image.Resampling.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(main_buttons_frame, image=logo_photo)
logo_label.grid(row=0, columnspan=2, pady=10)

welcome_label = tk.Label(main_buttons_frame, text="Menu du Navigation", font=("Helvetica", 20))
welcome_label.grid(row=1, columnspan=2, pady=10)

# Button icons
car_image = Image.open(resource_path("Images/car.png"))
car_image = car_image.resize((35, 35), Image.LANCZOS)
car_photo = ImageTk.PhotoImage(car_image)

rapport_img = Image.open(resource_path("Images/rapport.png"))
rapport_img = rapport_img.resize((35, 35), Image.LANCZOS)
rapport_photo = ImageTk.PhotoImage(rapport_img)

person_image = Image.open(resource_path("Images/conducteur.png"))
person_image = person_image.resize((35, 35), Image.LANCZOS)
person_photo = ImageTk.PhotoImage(person_image)

saisie_image = Image.open(resource_path("Images/saisie.jpg"))
saisie_image = saisie_image.resize((35, 35), Image.LANCZOS)
saisie_photo = ImageTk.PhotoImage(saisie_image)

logout_image = Image.open(resource_path("Images/logout.png"))
logout_image = logout_image.resize((35, 35), Image.LANCZOS)
logout_photo = ImageTk.PhotoImage(logout_image)

# Create buttons with images and place them using grid
tk.Button(main_buttons_frame, text="Saisie les données", image=saisie_photo, compound=tk.TOP,
          command=show_data_entry_frame).grid(row=2, column=0, sticky="ew", padx=10, pady=10)
tk.Button(main_buttons_frame, text="Gestion des véhicules", image=car_photo, compound=tk.TOP,
          command=open_car_management).grid(row=2, column=1, sticky="ew", padx=10, pady=10)
tk.Button(main_buttons_frame, text="Les Rapports", image=rapport_photo, compound=tk.TOP,
          command=open_rapport_frame).grid(row=3, column=0, sticky="ew", padx=10, pady=10)
tk.Button(main_buttons_frame, text="Gestion des conducteurs", image=person_photo, compound=tk.TOP,
          command=open_person_management).grid(row=3, column=1, sticky="ew", padx=10, pady=10)
logout_button = tk.Button(main_buttons_frame, text="Se déconnecter", image=logout_photo, compound=tk.LEFT,
                          command=logout)
logout_button.config(padx=10)
logout_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

# --------------------------------------------------Cadre de saisie les données -------------------------------------- #
# Cadre principale
data_entry_frame = tk.Frame(root, padx=20, pady=10)

# Titre principal
data_entry_label = tk.Label(data_entry_frame, text="Saisie des Données", font=("Helvetica", 20))
data_entry_label.grid(row=0, column=0, columnspan=2, pady=10)

# Quitter icon
quitter_image = Image.open(resource_path("Images/close.png"))
quitter_image = quitter_image.resize((35, 35), Image.LANCZOS)
quitter_photo = ImageTk.PhotoImage(quitter_image)

# Ajouter icon
ajout_image = Image.open(resource_path("Images/ajouter.png"))
ajout_image = ajout_image.resize((35, 35), Image.LANCZOS)
ajout_photo = ImageTk.PhotoImage(ajout_image)

# MAJ icon
maj_image = Image.open(resource_path("Images/boucler.png"))
maj_image = maj_image.resize((35, 35), Image.LANCZOS)
maj_photo = ImageTk.PhotoImage(maj_image)

# Supprimer icon
sup_image = Image.open(resource_path("Images/supprimer.png"))
sup_image = sup_image.resize((35, 35), Image.LANCZOS)
sup_photo = ImageTk.PhotoImage(sup_image)

# Enregistrer icon
eng_image = Image.open(resource_path("Images/enregistrer.png"))
eng_image = eng_image.resize((35, 35), Image.LANCZOS)
eng_photo = ImageTk.PhotoImage(eng_image)

# Apercu icon
apr_image = Image.open(resource_path("Images/apercu.png"))
apr_image = apr_image.resize((35, 35), Image.LANCZOS)
apr_photo = ImageTk.PhotoImage(apr_image)

# MAJ icon
mettre_image = Image.open(resource_path("Images/boucler.png"))
mettre_image = mettre_image.resize((35, 35), Image.LANCZOS)
mettre_photo = ImageTk.PhotoImage(mettre_image)

date_frame = tk.LabelFrame(data_entry_frame, text="Détails de la Mission")
date_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

tk.Label(date_frame, text="Date de Saisie :").grid(row=0, column=1, sticky="e")
entry_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, locale='fr_FR')
entry_date.grid(row=0, column=2, padx=10, pady=10)

tk.Label(date_frame, text="Objet de la Mission :").grid(row=1, column=0, sticky="e")
objet_mission = tk.Entry(date_frame)
objet_mission.grid(row=1, column=1, padx=10, pady=10)

tk.Label(date_frame, text="Type de Charge :").grid(row=1, column=2, sticky="e")
type_charge = tk.Entry(date_frame)
type_charge.grid(row=1, column=3, padx=10, pady=10)

tk.Label(date_frame, text="Date de Sortie :").grid(row=2, column=0, sticky="e")
date_sortie = DateEntry(date_frame, width=12, background='green', foreground='white', borderwidth=2, locale='fr_FR')
date_sortie.grid(row=2, column=1, padx=10, pady=10)

tk.Label(date_frame, text="Date D'arrivée :").grid(row=2, column=2, sticky="e")
date_arrivee = DateEntry(date_frame, width=12, background='red', foreground='white', borderwidth=2, locale='fr_FR')
date_arrivee.grid(row=2, column=3, padx=10, pady=10)

tk.Label(date_frame, text="Lieux de Départ :").grid(row=3, column=0, sticky="e")
lieux_depart = tk.Entry(date_frame)
lieux_depart.grid(row=3, column=1, padx=10, pady=10)

tk.Label(date_frame, text="Lieux D'arrivée :").grid(row=3, column=2, sticky="e")
lieux_arrivee = tk.Entry(date_frame)
lieux_arrivee.grid(row=3, column=3, padx=10, pady=10)

# Cadre pour le véhicule frame
vehicule_frame = tk.Frame(data_entry_frame)
vehicule_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ns")

# Véhicule frame
data_entry_vehicule_frame = tk.LabelFrame(vehicule_frame, text="Véhicule")
data_entry_vehicule_frame.grid(row=0, column=1, padx=10, pady=10)

# Configuration des colonnes pour centrer
for i in range(4):
    data_entry_vehicule_frame.grid_columnconfigure(i, weight=1)

tk.Label(data_entry_vehicule_frame, text="Numéro d'Immatriculation :").grid(row=0, column=2, sticky="e")
# Créer un Combobox normal (modifiable)
immatriculation = ttk.Combobox(data_entry_vehicule_frame, state="normal")
immatriculation.grid(row=0, column=3, sticky="w")

# Remplir le Combobox avec les valeurs
immatriculation['values'] = charger_immatriculations()

# Lier l'événement <<ComboboxSelected>> pour remplir d'autres champs
immatriculation.bind("<<ComboboxSelected>>", remplir_champs)

# Lier l'événement <Double-1> pour ouvrir le gestionnaire de voitures (car_management)
immatriculation.bind('<Double-1>', car_management)

# Ajouter une validation pour empêcher la modification du texte, tout en maintenant l'action double-clic
def on_focus_in(event):
    current_value = immatriculation.get()
    immatriculation.set(current_value)  # Restaure la valeur initiale pour éviter les modifications

# Appliquer la validation lors de la mise au point (focus)
immatriculation.bind('<FocusIn>', on_focus_in)

# Pour mettre a jour le combobox
update_combobox()

tk.Label(data_entry_vehicule_frame, text="Marque du Véhicule :").grid(row=1, column=0, sticky="e")
marque = tk.Entry(data_entry_vehicule_frame, state="disabled")
marque.grid(row=1, column=1)

tk.Label(data_entry_vehicule_frame, text="Type du Carburant :").grid(row=1, column=2, sticky="e")
carburant = tk.Entry(data_entry_vehicule_frame, state="disabled")
carburant.grid(row=1, column=3)

tk.Label(data_entry_vehicule_frame, text="Prix du Carburant/Litre :").grid(row=1, column=4, sticky="e")
prix_carburant = tk.Entry(data_entry_vehicule_frame, state="disabled")
prix_carburant.grid(row=1, column=5)

tk.Label(data_entry_vehicule_frame, text="Indice de Départ :").grid(row=2, column=0, sticky="e")
entry_indice_depart = tk.Entry(data_entry_vehicule_frame)
entry_indice_depart.grid(row=2, column=1)

tk.Label(data_entry_vehicule_frame, text="Indice D'arrivée :").grid(row=2, column=2, sticky="e")
entry_indice_arrivee = tk.Entry(data_entry_vehicule_frame)
entry_indice_arrivee.grid(row=2, column=3)

tk.Label(data_entry_vehicule_frame, text="Distance en (KM) :").grid(row=2, column=4, sticky="e")
entry_distance = tk.Entry(data_entry_vehicule_frame)
entry_distance.grid(row=2, column=5)
entry_distance.bind("<Return>", calculer_distance)

carburant_frame = tk.LabelFrame(data_entry_frame, text="Carburant")
carburant_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ns")

tk.Label(carburant_frame, text="Numéro du Bon :").grid(row=0, column=0)
entry_numero_bon = tk.Entry(carburant_frame)
entry_numero_bon.grid(row=0, column=1)

tk.Label(carburant_frame, text="Nombre du Bon :").grid(row=1, column=0)
entry_nombre_bon = tk.Spinbox(carburant_frame, from_=0, to=1000, increment=1)
entry_nombre_bon.grid(row=1, column=1)

tk.Label(carburant_frame, text="Prix du Bon (TND) :").grid(row=2, column=0)
entry_prix_bon = tk.Entry(carburant_frame)
entry_prix_bon.grid(row=2, column=1)

tk.Label(carburant_frame, text="Prix Total du Bon (TND) :").grid(row=3, column=0)
entry_total = tk.Entry(carburant_frame)
entry_total.grid(row=3, column=1)
entry_total.bind("<Return>", calculer_prix_total)

# Frame pour le conducteur
data_entry_conducteur_frame = tk.LabelFrame(data_entry_frame, text="Conducteur")
data_entry_conducteur_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

tk.Label(data_entry_conducteur_frame, text="ID Conducteur :").grid(row=0, column=0)
combobox_ids = ttk.Combobox(data_entry_conducteur_frame, width=18, state="readonly")
combobox_ids.grid(row=0, column=1, padx=10)
combobox_ids.bind("<<ComboboxSelected>>", on_combobox_select)

tk.Label(data_entry_conducteur_frame, text="Prénom du Conducteur :").grid(row=1, column=0)
entry_nom = tk.Entry(data_entry_conducteur_frame, state="disabled")
entry_nom.grid(row=1, column=1)
entry_nom.bind("<Double-Button-1>", person_management)

tk.Label(data_entry_conducteur_frame, text="Nom du Conducteur :").grid(row=2, column=0)
entry_prenom = tk.Entry(data_entry_conducteur_frame, state="disabled")
entry_prenom.grid(row=2, column=1)

tk.Label(data_entry_conducteur_frame, text="Rôle du Conducteur :").grid(row=3, column=0)
entry_role = tk.Entry(data_entry_conducteur_frame, state="disabled")
entry_role.grid(row=3, column=1)

tk.Label(data_entry_conducteur_frame, text="Nombre d'accompagnateurs :").grid(row=4, column=0)
nbr_acc = tk.Spinbox(data_entry_conducteur_frame, from_=0, to=50, increment=1)
nbr_acc.grid(row=4, column=1)

# Frame pour les boutons
button_frame = tk.LabelFrame(data_entry_frame, text="Les Boutons")
button_frame.grid(row=3, column=0, padx=(10, 20), pady=10, sticky="ns")

# Configuration des boutons
buttons = [
    {"text": "Enregistrer", "image": eng_photo, "command": enregistrer_donnees},
    {"text": "Mettre à jour", "image": mettre_photo, "command": mettre_a_jour_donnees},
    {"text": "Supprimer", "image": sup_photo, "command": supprimer_donnees},
    {"text": "Aperçu", "image": apr_photo, "command": afficher_apercu},
    {"text": "Quitter", "image": quitter_photo, "command": lambda: [data_entry_frame.grid_forget(),
                                                                   main_buttons_frame.grid(row=0, column=0, pady=20)]},
]

# Placement des boutons dans le frame
for col, btn in enumerate(buttons):
    button = tk.Button(button_frame, text=btn["text"], image=btn["image"], compound=tk.LEFT, command=btn["command"])
    button.config(padx=5)
    button.grid(row=0, column=col, padx=5, pady=5, sticky="ew")

# Frame pour la recherche/filtrage
search_frame = tk.LabelFrame(data_entry_frame, text="Filtrer")
search_frame.grid(row=3, column=1, padx=(20, 10), pady=10, sticky="ns")

# Configurer la colonne pour permettre l'expansion
search_frame.grid_columnconfigure(0, weight=2, uniform="equal")
search_frame.grid_columnconfigure(1, weight=0)

# Label pour la recherche
search_label = tk.Label(search_frame, text="ID :", wraplength=150)
search_label.grid(row=0, column=0, padx=5, sticky="w")

# Champ d'entrée pour saisir l'ID (plus large, avec un ratio d'expansion)
search_entry = tk.Entry(search_frame, width=20)
search_entry.grid(row=0, column=1, padx=5, sticky="ew")

# Ajouter un binding pour détecter la touche Entrée (recherche)
search_entry.bind("<Return>", rechercher_dans_treeview)

# Ajouter un binding pour détecter Retour arrière ou Supprimer (réinitialisation)
search_entry.bind("<KeyRelease>", gerer_touches_specifiques)

# Rechercher icon
rech_image = Image.open(resource_path("Images/rechercher.png"))
rech_image = rech_image.resize((35, 35), Image.LANCZOS)
rech_photo = ImageTk.PhotoImage(rech_image)

# Bouton pour exécuter la recherche
search_button = tk.Button(search_frame, text="Rechercher", image=rech_photo, compound=tk.LEFT, command=rechercher_dans_treeview)
search_button.grid(row=0, column=2, padx=5, sticky="w")
search_button.config(padx=10)

# Créer un cadre pour le Treeview et la scrollbar
tree_frame = tk.Frame(data_entry_frame)
tree_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

# Ajouter la barre de défilement verticale
scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
scrollbar_y.pack(side="right", fill="y")

# Ajouter la barre de défilement horizontale
scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")
scrollbar_x.pack(side="bottom", fill="x")

# Créer le Treeview avec des colonnes appropriées
tree_saisie = ttk.Treeview(tree_frame, columns=(
"saisie_id", "Date de saisie", "Objet Mission", "Type Charge", "Date de sortie", "Date d'arrivée", "Lieux de départ",
"Lieux d'arrivée", "Prénom Conducteur", "Nom Conducteur", "Role Conducteur", "Nbre Accompagnateurs", "Immatriculation",
"Marque de véhicule", "Type du Carburant", "Prix Carburant", "Indice de départ", "Indice d'arrivée", "Distance",
"Numéro du bon", "Nombre du bon", "Prix du bon", "Prix total du bon"),
                           show='headings',  # Afficher uniquement les en-têtes de colonnes
                           yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Configurer les en-têtes des colonnes
tree_saisie.heading("saisie_id", text="ID Saisie")
tree_saisie.heading("Date de saisie", text="Date de saisie")
tree_saisie.heading("Objet Mission", text="Objet Mission")
tree_saisie.heading("Type Charge", text="Type Charge")
tree_saisie.heading("Date de sortie", text="Date de sortie")
tree_saisie.heading("Date d'arrivée", text="Date d'arrivée")
tree_saisie.heading("Lieux de départ", text="Lieux de départ")
tree_saisie.heading("Lieux d'arrivée", text="Lieux d'arrivée")
tree_saisie.heading("Prénom Conducteur", text="Prénom Conducteur")
tree_saisie.heading("Nom Conducteur", text="Nom Conducteur")
tree_saisie.heading("Role Conducteur", text="Role Conducteur")
tree_saisie.heading("Nbre Accompagnateurs", text="Nbre Accompagnateurs")
tree_saisie.heading("Immatriculation", text="Immatriculation")
tree_saisie.heading("Marque de véhicule", text="Marque de véhicule")
tree_saisie.heading("Type du Carburant", text="Type du Carburant")
tree_saisie.heading("Prix Carburant", text="Prix Carburant")
tree_saisie.heading("Indice de départ", text="Indice de départ")
tree_saisie.heading("Indice d'arrivée", text="Indice d'arrivée")
tree_saisie.heading("Distance", text="Distance")
tree_saisie.heading("Numéro du bon", text="Numéro du bon")
tree_saisie.heading("Nombre du bon", text="Nombre du bon")
tree_saisie.heading("Prix du bon", text="Prix du bon")
tree_saisie.heading("Prix total du bon", text="Prix total du bon")

# Configurer la largeur des colonnes si nécessaire
tree_saisie.column("saisie_id", width=50)
tree_saisie.column("Date de saisie", width=150)
tree_saisie.column("Objet Mission", width=150)
tree_saisie.column("Type Charge", width=150)
tree_saisie.column("Date de sortie", width=150)
tree_saisie.column("Date d'arrivée", width=150)
tree_saisie.column("Lieux de départ", width=150)
tree_saisie.column("Lieux d'arrivée", width=150)
tree_saisie.column("Prénom Conducteur", width=150)
tree_saisie.column("Nom Conducteur", width=150)
tree_saisie.column("Role Conducteur", width=150)
tree_saisie.column("Nbre Accompagnateurs", width=150)
tree_saisie.column("Immatriculation", width=200)
tree_saisie.column("Marque de véhicule", width=150)
tree_saisie.column("Type du Carburant", width=150)
tree_saisie.column("Prix Carburant", width=150)
tree_saisie.column("Indice de départ", width=150)
tree_saisie.column("Indice d'arrivée", width=150)
tree_saisie.column("Distance", width=150)
tree_saisie.column("Numéro du bon", width=200)
tree_saisie.column("Nombre du bon", width=100)
tree_saisie.column("Prix du bon", width=100)
tree_saisie.column("Prix total du bon", width=100)

# Ajouter le Treeview dans le cadre
tree_saisie.pack(side="left", fill="both", expand=True)
# Configurer les barres de défilement
scrollbar_y.config(command=tree_saisie.yview)
scrollbar_x.config(command=tree_saisie.xview)

load_all_saisie()

# Personnaliser les barres de défilement
style = ttk.Style()
style.configure("Vertical.TScrollbar",
                gripcount=0,
                background="#c0c0c0",
                troughcolor="#f0f0f0",
                bordercolor="#d0d0d0",
                arrowcolor="#000000")

style.configure("Horizontal.TScrollbar",
                gripcount=0,
                background="#c0c0c0",
                troughcolor="#f0f0f0",
                bordercolor="#d0d0d0",
                arrowcolor="#000000")

tree_saisie.bind("<<TreeviewSelect>>", on_saisie_selected)

# Pour donner un space entre les élements d'une frame
for frame in data_entry_vehicule_frame.winfo_children():
    frame.grid_configure(padx=10, pady=5)

for frame in carburant_frame.winfo_children():
    frame.grid_configure(padx=10, pady=5)

for frame in data_entry_conducteur_frame.winfo_children():
    frame.grid_configure(padx=10, pady=5)

for frame in button_frame.winfo_children():
    frame.grid_configure(padx=20, pady=5)

data_entry_frame.columnconfigure(0, weight=1)
data_entry_frame.columnconfigure(1, weight=1)
data_entry_frame.rowconfigure(4, weight=1)
# ----------------------------------------------- Véhicule ----------------------------------------------------------- #

# Cadre pour la gestion des véhicules
car_management_frame = tk.Frame(root, padx=10, pady=10)

# Charger et redimensionner l'image
car_management_image = Image.open(resource_path("Images/car.png"))
resized_image = car_management_image.resize((100, 100))
header_image = ImageTk.PhotoImage(resized_image)

# Ajouter l'image en haut du cadre
header_label = tk.Label(car_management_frame, image=header_image)
header_label.grid(row=0, column=0, columnspan=4)

# Titre
tk.Label(car_management_frame, text="Gestion des Véhicules", font=("Helvetica", 20)).grid(row=1, column=0, columnspan=4,
                                                                                          pady=10)

# Saisie du véhicule
véhicule_frame = tk.LabelFrame(car_management_frame, text="Véhicule")
véhicule_frame.grid(row=2, column=0, columnspan=4, pady=10)

tk.Label(véhicule_frame, text="ID du Véhicule :").grid(row=0, column=0)
entry_id_vehicule = tk.Entry(véhicule_frame)
entry_id_vehicule.grid(row=0, column=1)

tk.Label(véhicule_frame, text="Numéro d'Immatriculation :").grid(row=1, column=0)
entry_immatriculation = tk.Entry(véhicule_frame)
entry_immatriculation.grid(row=1, column=1)

tk.Label(véhicule_frame, text="Marque du Véhicule :").grid(row=2, column=0)
entry_marque = tk.Entry(véhicule_frame)
entry_marque.grid(row=2, column=1)

tk.Label(véhicule_frame, text="Type de Carburant :").grid(row=3, column=0)
type_var = tk.StringVar()
type_choix = ttk.Combobox(véhicule_frame, textvariable=type_var)
type_choix['values'] = ('Essence', 'Diesel', 'Électrique')
type_choix.grid(row=3, column=1)

tk.Label(véhicule_frame, text="Prix du Carburant/Litre :").grid(row=4, column=0)
entry_prix_carburant = tk.Entry(véhicule_frame)
entry_prix_carburant.grid(row=4, column=1)

# Créer un cadre pour le Treeview et la scrollbar
tree_frame = tk.Frame(car_management_frame)
tree_frame.grid(row=3, column=0, columnspan=4, pady=5, sticky="nsew")

# Ajouter la barre de défilement verticale
scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
scrollbar_y.pack(side="right", fill="y")

# Ajouter la barre de défilement horizontale
scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")
scrollbar_x.pack(side="bottom", fill="x")

# Créer le Treeview avec des colonnes appropriées
tree_vehicule = ttk.Treeview(tree_frame, columns=(
"vehicule_id", "Immatriculation", "Marque", "Type du Carburant", "Prix du Carburant"),
                             show='headings',  # Afficher uniquement les en-têtes de colonnes
                             yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Configurer les en-têtes des colonnes
tree_vehicule.heading("vehicule_id", text="ID Véhicule")
tree_vehicule.heading("Immatriculation", text="Numéro d'Immatriculation")
tree_vehicule.heading("Marque", text="Marque")
tree_vehicule.heading("Type du Carburant", text="Type du Carburant")
tree_vehicule.heading("Prix du Carburant", text="Prix du Carburant")

# Configurer la largeur des colonnes si nécessaire
tree_vehicule.column("vehicule_id", width=100)
tree_vehicule.column("Immatriculation", width=200)
tree_vehicule.column("Marque", width=150)
tree_vehicule.column("Type du Carburant", width=150)
tree_vehicule.column("Prix du Carburant", width=150)

# Ajouter le Treeview dans le cadre
tree_vehicule.pack(side="left", fill="both", expand=True)
# Configurer les barres de défilement
scrollbar_y.config(command=tree_vehicule.yview)
scrollbar_x.config(command=tree_vehicule.xview)

load_all_vehicules()

# Personnaliser les barres de défilement
style = ttk.Style()
style.configure("Vertical.TScrollbar",
                gripcount=0,
                background="#c0c0c0",
                troughcolor="#f0f0f0",
                bordercolor="#d0d0d0",
                arrowcolor="#000000")

style.configure("Horizontal.TScrollbar",
                gripcount=0,
                background="#c0c0c0",
                troughcolor="#f0f0f0",
                bordercolor="#d0d0d0",
                arrowcolor="#000000")

# Associer la fonction de sélection à l'événement de sélection du Treeview
tree_vehicule.bind('<<TreeviewSelect>>', on_vehicule_selected)

# Button Ajouter
button_ajouter = tk.Button(car_management_frame, text="Ajouter", image=ajout_photo, compound=tk.LEFT,
                           command=ajouter_vehicule)
button_ajouter.config(padx=10)
button_ajouter.grid(row=4, column=0, pady=10, sticky="ns")

# Button MAJ
button_maj = tk.Button(car_management_frame, text="Mettre à jour", image=maj_photo, compound=tk.LEFT,
                       command=mettre_a_jour_vehicule)
button_maj.config(padx=10)
button_maj.grid(row=4, column=1, pady=10, sticky="ns")

# Button Supprimer
button_ajouter = tk.Button(car_management_frame, text="Supprimer", image=sup_photo, compound=tk.LEFT,
                           command=supprimer_véhicule)
button_ajouter.config(padx=10)
button_ajouter.grid(row=4, column=2, pady=10, sticky="ns")

# Bouton pour revenir au menu principal
button_quitter = tk.Button(car_management_frame, text="Quitter", image=quitter_photo, compound=tk.LEFT,
                           command=lambda: [car_management_frame.grid_forget(),
                                            main_buttons_frame.grid(row=0, column=0, pady=20)])
button_quitter.config(padx=10)
button_quitter.grid(row=4, column=3, pady=10, sticky="ns")

# Configure column weights to center buttons horizontally
for i in range(4):
    car_management_frame.columnconfigure(i, weight=1)

# Configure row weights to center buttons vertically
car_management_frame.rowconfigure(4, weight=1)

# Pour un espace dans le conducteur frame
for frame in véhicule_frame.winfo_children():
    frame.grid_configure(padx=10, pady=5)

# -------------------------------------------------------------------Conducteur -----------------------------------------------------------------------------------------

# Cadre pour la gestion des conducteurs
person_management_frame = tk.Frame(root, padx=10, pady=10)

# Charger et redimensionner l'image
person_management_image = Image.open(resource_path("Images/conducteur.png"))
con_image = person_management_image.resize((100, 100))
conducteur_image = ImageTk.PhotoImage(con_image)

# Ajouter l'image en haut du cadre
header_label = tk.Label(person_management_frame, image=conducteur_image)
header_label.grid(row=0, column=0, columnspan=4)

# Titre
tk.Label(person_management_frame, text="Gestion des Conducteurs", font=("Helvetica", 20)).grid(row=1, column=0,
                                                                                               columnspan=4, pady=10)

# Saisie du Conducteur
conducteur_frame = tk.LabelFrame(person_management_frame, text="Conducteur")
conducteur_frame.grid(row=2, column=0, columnspan=4, pady=10)

tk.Label(conducteur_frame, text="ID du Conducteur :").grid(row=0, column=0)
entry_id_conducteur = tk.Entry(conducteur_frame)  # Renommer l'entrée pour l'ID
entry_id_conducteur.grid(row=0, column=1)

tk.Label(conducteur_frame, text="Prénom du Conducteur :").grid(row=1, column=0)
entry_nom_conducteur = tk.Entry(conducteur_frame)  # Renommer l'entrée pour le nom
entry_nom_conducteur.grid(row=1, column=1)

tk.Label(conducteur_frame, text="Nom du Conducteur :").grid(row=2, column=0)
entry_prenom_conducteur = tk.Entry(conducteur_frame)  # Renommer l'entrée pour le prénom
entry_prenom_conducteur.grid(row=2, column=1)

tk.Label(conducteur_frame, text="Rôle du Conducteur :").grid(row=3, column=0)
entry_role_conducteur = tk.Entry(conducteur_frame)
entry_role_conducteur.grid(row=3, column=1)

# Créer un cadre pour le Treeview et la scrollbar
tree_frame = tk.Frame(person_management_frame)
tree_frame.grid(row=3, column=0, columnspan=4, pady=5, sticky="nsew")

# Ajouter la barre de défilement verticale
scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
scrollbar_y.pack(side="right", fill="y")

# Ajouter la barre de défilement horizontale
scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")
scrollbar_x.pack(side="bottom", fill="x")

# Créer le Treeview avec des colonnes appropriées
tree_conducteur = ttk.Treeview(tree_frame, columns=(
"conducteur_id", "Prénom du conducteur", "Nom du conducteur", "Role du conducteur"),
                               show='headings',
                               yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Configurer les en-têtes des colonnes
tree_conducteur.heading("conducteur_id", text="ID Conducteur")
tree_conducteur.heading("Prénom du conducteur", text="Prénom du conducteur")
tree_conducteur.heading("Nom du conducteur", text="Nom du conducteur")
tree_conducteur.heading("Role du conducteur", text="Role du conducteur")

# Configurer la largeur des colonnes si nécessaire
tree_conducteur.column("conducteur_id", width=100)
tree_conducteur.column("Prénom du conducteur", width=150)
tree_conducteur.column("Nom du conducteur", width=150)
tree_conducteur.column("Role du conducteur", width=150)

# Ajouter le Treeview dans le cadre
tree_conducteur.pack(side="left", fill="both", expand=True)
# Configurer les barres de défilement
scrollbar_y.config(command=tree_conducteur.yview)
scrollbar_x.config(command=tree_conducteur.xview)

load_all_conducteurs()

# Personnaliser les barres de défilement
style = ttk.Style()
style.configure("Vertical.TScrollbar",
                gripcount=0,
                background="#c0c0c0",
                troughcolor="#f0f0f0",
                bordercolor="#d0d0d0",
                arrowcolor="#000000")

style.configure("Horizontal.TScrollbar",
                gripcount=0,
                background="#c0c0c0",
                troughcolor="#f0f0f0",
                bordercolor="#d0d0d0",
                arrowcolor="#000000")

# Associer la fonction de sélection à l'événement de sélection du Treeview
tree_conducteur.bind('<<TreeviewSelect>>', on_tree_selected)

# Button Ajouter
button_ajouter = tk.Button(person_management_frame, text="Ajouter", image=ajout_photo, compound=tk.LEFT,
                           command=ajouter_conducteur)
button_ajouter.config(padx=10)
button_ajouter.grid(row=4, column=0, pady=10, sticky="ns")

# Button MAJ
button_maj = tk.Button(person_management_frame, text="Mettre à jour", image=maj_photo, compound=tk.LEFT,
                       command=mettre_a_jour_conducteur)
button_maj.config(padx=10)
button_maj.grid(row=4, column=1, pady=10, sticky="ns")

# Button Supprimer
button_sup = tk.Button(person_management_frame, text="Supprimer", image=sup_photo, compound=tk.LEFT,
                           command=supprimer_conducteur)
button_sup.config(padx=10)
button_sup.grid(row=4, column=2, pady=10, sticky="ns")

# Bouton pour revenir au menu principal
button_quitter = tk.Button(person_management_frame, text="Quitter", image=quitter_photo, compound=tk.LEFT,
                           command=lambda: [person_management_frame.grid_forget(),
                                            main_buttons_frame.grid(row=0, column=0, pady=20)])
button_quitter.config(padx=10)
button_quitter.grid(row=4, column=3, pady=10, sticky="ns")

# Configure column weights to center buttons horizontally
for i in range(4):
    person_management_frame.columnconfigure(i, weight=1)

# Configure row weights to center buttons vertically
person_management_frame.rowconfigure(3, weight=1)

# Pour un espace dans le conducteur frame
for frame in conducteur_frame.winfo_children():
    frame.grid_configure(padx=10, pady=5)

# ---------------------------------------------------------------------------Rapports------------------------------------------------------------------------------------

# Cadre pour la gestion des carburant
rapports_frame = tk.Frame(root, padx=10, pady=10)

# Load and place the logo
rapport = Image.open(resource_path("Images/rapport.png"))
rapport = rapport.resize((200, 150), Image.Resampling.LANCZOS)
rap = ImageTk.PhotoImage(rapport)
rapport_label = tk.Label(rapports_frame, image=rap)
rapport_label.grid(row=0, column=0, columnspan=3, pady=10)

# Le nom du l'interface
welcome_label = tk.Label(rapports_frame, text="Les Rapports", font=("Helvetica", 25))
welcome_label.grid(row=1, column=0, columnspan=3, pady=10)

# Configuration de la grille
for col in range(3):
    rapports_frame.grid_columnconfigure(col, weight=1)

# Variables pour les cases à cocher
var_voiture = tk.BooleanVar()
var_annuelle = tk.BooleanVar()
var_mensuelle = tk.BooleanVar()
var_conducteur = tk.BooleanVar()
var_dates = tk.BooleanVar()

# Entrées pour l'immatriculation, année, mois, et ID conducteur
tk.Checkbutton(rapports_frame, text="Consommation par Voiture : ", font=("Helvetica", 15), variable=var_voiture).grid(
    row=6, column=0, sticky="w", padx=5, pady=2)
immatriculation_combobox = ttk.Combobox(rapports_frame)
immatriculation_combobox.grid(row=6, column=1, columnspan=2, sticky="ew", padx=5)

tk.Checkbutton(rapports_frame, text="Consommation Annuelle : ", font=("Helvetica", 15), variable=var_annuelle).grid(
    row=7, column=0, sticky="w", padx=5, pady=2)
annee_combobox = ttk.Combobox(rapports_frame)
annee_combobox.grid(row=7, column=1, columnspan=2, sticky="ew", padx=5)

tk.Checkbutton(rapports_frame, text="Consommation Mensuelle : ", font=("Helvetica", 15), variable=var_mensuelle).grid(
    row=8, column=0, sticky="w", padx=5, pady=2)
mois_combobox = ttk.Combobox(rapports_frame)
mois_combobox.grid(row=8, column=1, columnspan=2, sticky="ew", padx=5)

tk.Checkbutton(rapports_frame, text="Consommation par Conducteur : ", font=("Helvetica", 15), variable=var_conducteur).grid(
    row=9, column=0, sticky="w", padx=5, pady=2)
conducteur_id_combobox = ttk.Combobox(rapports_frame)
conducteur_id_combobox.grid(row=9, column=1, columnspan=2, sticky="ew", padx=5)

tk.Checkbutton(rapports_frame, text="Consommation entre les dates : ", font=("Helvetica", 15), variable=var_dates).grid(
    row=10, column=0, sticky="w", padx=5, pady=2)

# Champs de dates alignés
date_debut_entry = DateEntry(rapports_frame, width=12, background='darkgreen',
                             foreground='white', borderwidth=2, locale='fr_FR')
date_debut_entry.grid(row=10, column=1, sticky="e", padx=5)

label_et = Label(rapports_frame, text="et", font=("Helvetica", 15))
label_et.grid(row=10, column=2, sticky="w", padx=10)

date_fin_entry = DateEntry(rapports_frame, width=12, background='darkred',
                           foreground='white', borderwidth=2, locale='fr_FR')
date_fin_entry.grid(row=10, column=3, sticky="w", padx=5)

# Résultat icon
resultat_img = Image.open(resource_path("Images/carbucons.png"))
resultat_img = resultat_img.resize((35, 35), Image.LANCZOS)
resultat_photo = ImageTk.PhotoImage(resultat_img)

# Dashboard icon
dash_img = Image.open(resource_path("Images/dashboard.png"))
dash_img = dash_img.resize((35, 35), Image.LANCZOS)
dash_photo = ImageTk.PhotoImage(dash_img)

# Retour icon
retour_image = Image.open(resource_path("Images/retour.png"))
retour_image = retour_image.resize((35, 35), Image.LANCZOS)
retour_rapport_photo = ImageTk.PhotoImage(retour_image)

# Bouton pour afficher les consommations
tk.Button(rapports_frame, text="Afficher les Consommations", image=resultat_photo, compound=tk.TOP,
          command=afficher_resultats).grid(row=11, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

tk.Button(rapports_frame, text="Afficher le Dashboard", image=dash_photo, compound=tk.TOP,
          command=afficher_dashboard).grid(row=12, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

# Bouton Retour
bouton_retour = tk.Button(rapports_frame, text="Retour", image=retour_rapport_photo, compound=tk.LEFT,
                          padx=10, command=lambda: [rapports_frame.grid_forget(),
                                           main_buttons_frame.grid(row=0, column=0, pady=20)])
bouton_retour.grid(row=13, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

# Mise à jour initiale des comboboxes
update_comboboxes()

annee_combobox.bind('<<ComboboxSelected>>', on_year_selected)

# check_tables
check_tables()

# Afficher l'interface de login
show_login_frame()

root.mainloop()