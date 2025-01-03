from dotenv import load_dotenv
import os
import base64
from requests import get, post
import json
import cv2
load_dotenv()
from deepface import DeepFace

client_id=os.getenv("CLIENT_ID")
client_secret=os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64=str(base64.b64encode(auth_bytes), 'utf-8')

    url="https://accounts.spotify.com/api/token"
    headers={
        "authorization":"Basic " + auth_base64,
        "Content-Type":"application/x-www-form-urlencoded"
    }    
    data={"grant_type": "client_credentials"}
    result=post(url, headers=headers, data=data)
    json_result=json.loads(result.content)
    token=json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization":"Bearer " + token}

def extract_audio_features(track_ids, token):
    url=f"https://api.spotify.com/v1/audio-features"
    headers=get_auth_header(token)
    params={"ids": ",".join(track_ids)}
    result=get(url, headers=headers, params=params)
    audio_features=json.loads(result.content)["audio_features"]
    return audio_features

def tracks_by_moods(audio_features, moods):
    mood_map={
        "happy": {"danceability": 0.7, "energy": 0.7, "tempo": 120},
        "sad": {"danceability": 0.3, "energy": 0.3, "tempo": 70},
        "calm": {"danceability": 0.5, "energy": 0.5, "tempo": 80},
        "excited": {"danceability": 0.8, "energy": 0.9, "tempo": 130},
    }
    selected_tracks=[]
    for track in audio_features:
        mood_criteria=mood_map[mood]
        if track["danceability"] >= mood_criteria["danceability"] and track["energy"] >= mood_criteria["energy"] and track["tempo"] >= mood_criteria["tempo"]:
            selected_tracks.append(track)
    return selected_tracks  

    user_feelings=input("What mood are you in? (happy, sad, calm, excited): ").lower()
    moods=["happy", "sad", "calm", "excited"]
    if user_feelings not in moods:
        print("Invalid mood")

def detect_mood():
    cap=cv2.VideoCapture(0)
    mood="neutral"
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    while True:
        ret, frame=cap.read()
        if not ret:
            print("Can't receive frame")
            break
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces=face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            face_roi=frame[y:y+h, x:x+w]
            try:
                analysis=DeepFace.analyze(face_roi, actions=["emotion"])
                emotion=analysis["dominant_emotion"]
                if emotion in ["happy", "joyful", "amusement"]:
                    mood="happy"
                elif emotion in ["sad", "angry", "disgust"]:
                    mood="sad"
                elif emotion in ["calm", "relaxed", "neutral"]:
                    mood="calm"
                elif emotion in ["excited", "surprised", "happy"]:
                    mood="excited"
                break
            except Exception as e:
                print(f"Can't detect emotion: {e}")
                mood="neutral"
                break
        if mood != "neutral":
            break
        
    cap.release()
    cv2.destroyAllWindows()
    return mood

    user_mood=detect_mood()

    def make_playlist_by_mood(user_id, token,name,description,):
        url=f"https://api.sporify.com/i/v1/users/{user_id}/playlists"
        headers=get_auth_header(token)
        data={
            "name":name,
            "description":description,
            "public":True
        }
        result=post(url, headers=headers, json=data)
        playlist_id=json.loads(result.content)["id"]
        return playlist_id
        
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        

        

    


token=get_token()

    
    




    
#def search_for_artist(token, artist_name):
 #   url="https://api.spotify.com/v1/search"
  #  headers=get_auth_header(token)
   # query=f"?q={artist_name}&type=artist&limit=1"

    #query_url=url + query
    #result= get(query_url,headers=headers)
    #json_result=json.loads(result.content)["artists"]["items"]
    
    #if len(json_result) == 0:
     #   print("No artist with this name exists...")
      #  return None
        
    #return json_result[0]

#def get_songs_by_artist(token, artist_id):
 #   url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
  #  headers=get_auth_header(token)    
   # result=get(url, headers=headers)  
    #json_result=json.loads(result.content)["tracks"]
    #return json_result
        

#result=search_for_artist(token, "ACDC")
#artist_id=result["id"]
#songs=get_songs_by_artist(token, artist_id)
#for idx,song in enumerate(songs):
#    print(f"{idx+1}. {song['name']}") 



