from pymongo import MongoClient
import pymongo
import certifi

def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    #CONNECTION_STRING = "mongodb+srv://tesisUser:CG3AKCe7aGs1QGoy@clusterDev.mongodb.net/weaponDetectorDB"

    ca = certifi.where()

    client = pymongo.MongoClient(
        "mongodb+srv://tesisUser:CG3AKCe7aGs1QGoy@clusterdev.pabepap.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    db = client.test

    # client devuelve la conexion y el 2do return devuelve la raiz de la bd.
    return client,client['weaponDetectorDB']

# SIRVE DE PRUEBA
# if __name__ == "__main__":
#     # Get the database
#     client, dbname = get_database()
#     collection_name = dbname["usersData"]
#     item_1 = {
#         "item_name": "Blender"
#     }
#     item_2 = {
#         "User":{
#             "username": "",
#             "password": "",
#             "detections": {
#                 "lastSecuestro": "",
#                 "lastAsalto": "",
#                 "lastTiroteo": "",
#             },
#             "cameras": [{
#                 "nombre": "",
#                 "tipo": "Web o Local",
#                 "URL": "",
#             },
#                 {
#                     "nombre": "",
#                     "tipo": "Web o Local",
#                     "URL": "",
#                 }]
#         }
#     }
#     collection_name.insert_one(item_2)
#     client.close()
#     collection_name.insert_one(item_2)