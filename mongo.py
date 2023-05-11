from pymongo import MongoClient
import gridfs

def mongo_conn():
    try:
        conn = MongoClient("mongodb://root:example@localhost:27017/")
        return conn.grid_file
    except Exception as e:
        print("error", e)

db = mongo_conn()
print("connection réussie")

def enregistrer_video(filepath, filename, db = db):

    file_data = open(filepath, "rb")
    data = file_data.read()
    fs = gridfs.GridFS(db)
    fs.put(data, filename = filename)
    print("upload complete")

# def choper_image(nom):


# def uploaded_video()