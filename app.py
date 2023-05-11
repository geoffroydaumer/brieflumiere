import streamlit as st
import torch
import torchvision.models as models
import cv2
import os
import io
from io import BytesIO
import tempfile
from torchvision import transforms
from torch.utils.data import DataLoader
import numpy as np
import time
import gridfs
import asyncio
from tqdm import tqdm
from PIL import Image
import time
import imghdr
import subprocess
from mongo import mongo_conn, enregistrer_video
from pymongo import MongoClient
from moviepy.video.io.VideoFileClip import VideoFileClip

# Connection mongodb
db = mongo_conn()

# Barre de choix
selectbox = st.sidebar.selectbox(
    "Choisissez votre type de détection",
    ("Webcam", "Vidéo",  "Photo"))


# Chemins (destination d'enregistrement de prédiction)
final_path = r"C:\VS_Progs\Projets\ecole\brief\2023_04_14detecteur_fumee\app\yolov5\runs\detect"
detect_path = r"C:\VS_Progs\Projets\ecole\brief\2023_04_14detecteur_fumee\app\yolov5\detect.py"
weights_path = r"C:\VS_Progs\Projets\ecole\brief\2023_04_14detecteur_fumee\app\modele_amadou.pt"

def get_last_predict():

    """Récupère le lien de la dernière prédiction et le lien sans le nom du fichier """

    contents_exp = os.listdir(final_path)
    contents_exp = sorted(contents_exp, key=lambda x: os.path.getctime(os.path.join(final_path, x)), reverse=True)
    path = final_path + "\\" + contents_exp[0]
    contents_img = os.listdir(path)
    video = path + "\\" + contents_img[-1]
    return video, path

if selectbox == "Vidéo":

    uploaded_file = st.file_uploader("Sélectionnez votre vidéo")

    if uploaded_file is not None:
        
        # Créer un fichier temporaire et enregistrer la vidéo dessus
        tmp_file = tempfile.NamedTemporaryFile(delete=False,suffix='.mp4')
        tmp_file.write(uploaded_file.read())
            
        # Récupérer le chemin du fichier temporaire
        temp_file_path = tmp_file.name

        # Exécution de la ligne de commande pour la prédiction de fumée
        command = f"python {detect_path} --weights {weights_path} --source {temp_file_path}"
        output = subprocess.run(command, shell=True)

        # Récupère le lien de la dernière prédiction et l'affiche en vidéo
        filepath, path = get_last_predict()
        st.video(filepath)

        # Remplace le nom temporaire de la dernière prédiction dans le dossier de destination par le bon nom du fichier uploadé
        old_name = filepath
        new_name = path + "\\" + uploaded_file.name
        os.rename(old_name, new_name)
       
        # Enregistre la vidéo dans mongodb
        enregistrer_video(filepath = new_name, filename = uploaded_file.name)
  
    # Affiche la liste des vidéos prédites
    st.write("Liste des vidéos :")
    videos = db.fs.files.find()
    video_names = [video["filename"] for video in videos if ".mp4" in video["filename"]]
    selected_video = st.selectbox("Sélectionnez une vidéo :", video_names)

    if st.button("Visionner la vidéo"):
        fs = gridfs.GridFS(db)
        # Trouve la vidéo dans la bdd
        video = db.fs.files.find_one({"filename": selected_video})
        # Prend son id pour la récupérer
        id_video = video['_id']
        outputdata = fs.get(id_video).read()
        download_location = r"C:\VS_Progs\Projets\ecole\brief\2023_04_14detecteur_fumee\app\download" + "\\" + str(id_video) +".mp4"
        output = open(download_location, "wb")
        # .read() c'est que pour les vidéos, pour les images, c'est différent à ce moment là,
        #  pour mettre l'image en fichier temporaire, et pour aller la chercher dans mongodb
        output.write(outputdata)
        output.close()
        print("download complete")
        st.video(download_location)

if selectbox == "Photo":

    uploaded_file = st.file_uploader("Déposez votre image, nous vous dirons si il s'agit d'un incendie")

    if uploaded_file is not None:

        # Créer un fichier temporaire
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')

        # Enregistre l'image dans le fichier temp (process différent de la vidéo)
        image = Image.open(uploaded_file)
        image.save(tmp_file.name)

        # Récupérer le chemin du fichier temporaire
        temp_file_path = tmp_file.name

        # Exécution de la ligne de commande pour la prédiction de fumée
        command = f"python {detect_path} --weights {weights_path} --source {temp_file_path}"
        output = subprocess.run(command, shell=True)
    
        # Récupère le lien de la dernière prédiction et l'affiche en vidéo
        filepath, path = get_last_predict()
        st.text(filepath + "\n" + path)
        image = Image.open(filepath)
        st.image(image)

        # Remplace le nom temporaire de la dernière prédiction dans le dossier de destination par le bon nom du fichier uploadé (permet de savoir quel fichier est quoi quand on envoie dans la bdd)
        old_name = filepath
        new_name = path + "\\" + uploaded_file.name
        os.rename(old_name, new_name)
       
        # Enregistre la vidéo dans mongodb
        enregistrer_video(filepath = new_name, filename = uploaded_file.name)

  
    # Affiche la liste des vidéos prédites
    st.write("Liste des photos :")
    photos = db.fs.files.find()
    photos_names = [photo["filename"] for photo in photos if ".jpg" in photo["filename"]]
    selected_photo = st.selectbox("Sélectionnez une photo :", photos_names)


    def fonction_bouton():
        fs = gridfs.GridFS(db)
        photo = db.fs.files.find_one({"filename": selected_photo})
        id_photo = photo['_id']
        outputdata = fs.get(id_photo).read()
        outputdata = BytesIO(outputdata)
        download_location = r"C:\VS_Progs\Projets\ecole\brief\2023_04_14detecteur_fumee\app\download" + "\\" + str(id_photo) +".jpg"
        output = open(download_location, "wb")
        output.write(outputdata.getvalue())
        output.close()
        print("download complete")
        image = Image.open(download_location)
        st.image(image)

    # Va chercher l'image dans la base
    if st.button("Visionner la photo"):

        fonction_bouton()

if selectbox == "Webcam":

    # Import du modèle pour la cam ?
    # model = torch.hub.load("ultralytics/yolov5", "custom", path=r"C:\VS_Progs\Projets\ecole\brief\2023_04_14detecteur_fumee\best.pt")

    # Il faut couper le script et le relancer pour aller dans une autre section
    if st.button("mettre la webcam"):

        command = f"python {detect_path} --weights {weights_path} --source 0"
        output = subprocess.run(command, shell=True)

    # Le bouton ne fonctionne pas
    if st.button("detruiree fenetre"):

        cv2.destroyAllWindows()
