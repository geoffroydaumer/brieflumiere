# briefincendie

Detection incendies
Geoffroy Daumer, Amadou Diaby, David Scanu

Dans ce brief, nous appliquons un apprentissage supervisé pour détecter les incendies à partir d’une vidéo ou image.

Partie 1 : Labellisation des données
Nous avons labelisé un DataSet fourni pour le modèle Yolo. Outil : https://www.makesense.ai
Données labelisées dans Teams Sujet – 24 février

Partie 2 : Transfer Learning
Cette deuxième partie est réservée pour réaliser un Transfer Learning sur l’architecture de Yolov5.
Pour avoir les explications concernant l'entraînement du modèle sur google colab : voir le fichier TRAIN_YOLO_V5_ON_YOUR_CUSTOM_DATASET.ipynb

Partie 3 : Application
Application Streamlit qui permet de :
Charger et exécuter la détection d'incendie et de fumée à partir d’une image, vidéo ou d’une webcam.
Permettre de stocker les détections dans une bdd mongodb

Pour lancer l'app : lancer streamlit run app.py dans le bon path.
Changer les path dans app.py car ils ne seront pas adaptés à votre arborescence.
