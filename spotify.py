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
        for mood in moods:
            mood_criteria=mood_map[mood]
            if track["danceability"] >= mood_criteria["danceability"] and track["energy"] >= mood_criteria["energy"] and track["tempo"] >= mood_criteria["tempo"]:
                selected_tracks.append(track)
    return selected_tracks

def get_user_mood():
    user_feelings = input("What mood are you in? (happy, sad, calm, excited): ").lower() 
    moods = ["happy", "sad", "calm", "excited"]
    if user_feelings not in moods:
        print("Invalid mood")
        return None
    return user_feelings

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

def make_playlist_by_mood(user_id, token, name, description):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    data = {
        "name": name,
        "description": description,
        "public": True
    }
    result = post(url, headers=headers, json=data)
    playlist_id = json.loads(result.content)["id"]
    return playlist_id

def search_tracks_by_mood(token, mood):
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_header(token)
    
    # Map moods to Spotify parameters
    mood_params = {
        "happy": {"min_valence": 0.7, "min_energy": 0.7, "target_tempo": 120},
        "sad": {"min_valence": 0.1, "max_valence": 0.4, "target_tempo": 70},
        "calm": {"max_energy": 0.5, "target_tempo": 80, "max_valence": 0.6},
        "excited": {"min_energy": 0.8, "min_valence": 0.6, "target_tempo": 130}
    }
    
    params = {
        "limit": 20,
        "market": "US",
        "seed_genres": "pop,rock,hip-hop,electronic,r-n-b",
        **mood_params[mood]
    }
    
    result = get(url, headers=headers, params=params)
    json_result = json.loads(result.content)
    return [track["id"] for track in json_result["tracks"]]

def add_tracks_to_playlist(token, playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    data = {
        "uris": [f"spotify:track:{track_id}" for track_id in track_ids]
    }
    result = post(url, headers=headers, json=data)
    return result.status_code == 201

def main():
    print("Welcome to Mood-Based Music Player!")
    print("1. Detect mood from camera")
    print("2. Enter mood manually")
    choice = input("Choose an option (1/2): ")
    
    if choice == "1":
        mood = detect_mood()
        print(f"Detected mood: {mood}")
    else:
        mood = get_user_mood()
        if not mood:
            return
    
    # You need to replace this with your Spotify user ID
    user_id = input("Enter your Spotify user ID: ")
    
    # Create a new playlist
    playlist_name = f"My {mood.capitalize()} Playlist"
    playlist_description = f"A playlist generated based on {mood} mood"
    
    try:
        playlist_id = make_playlist_by_mood(user_id, token, playlist_name, playlist_description)
        print(f"Created playlist: {playlist_name}")
        
        # Get tracks based on mood
        track_ids = search_tracks_by_mood(token, mood)
        
        # Add tracks to playlist
        if add_tracks_to_playlist(token, playlist_id, track_ids):
            print("Successfully added tracks to your playlist!")
            print(f"Check your Spotify account for the playlist: {playlist_name}")
        else:
            print("Failed to add tracks to playlist")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    token = get_token()
    main()

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



