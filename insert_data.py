import psycopg2
import spotipy
from datetime import datetime
from dateutil import tz
from psycopg2.extensions import AsIs
from json import loads

# Connection to database
conn = psycopg2.connect(database="spotify", user="postgres", password="password", host="127.0.0.1", port="5432")
cursor = conn.cursor()

# Listening files
files = [
    '/Users/muhammadsohail/Desktop/MyData-7/endsong_0.json',
    '/Users/muhammadsohail/Desktop/MyData-7/endsong_1.json',
    '/Users/muhammadsohail/Desktop/MyData-7/endsong_2.json'
    ]

# Function to insert listening histroy into table
def insert_listens():

    # Time zones for timestamp conversion
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # Function to filter columns I don't need
    def removeCols(col):
        return col not in [
            'username',
            'ip_addr_decrypted',
            'user_agent_decrypted',
            'episode_name',
            'episode_show_name',
            'spotify_episode_uri',
            ]

    for filename in files:
        with open(filename, 'r') as file:
            data = loads(file.read())   # Load the JSON array for each file


        columns = list(filter(removeCols, data[0].keys()))  # Filtering out unwanted columns

        for song in data:
            if song['episode_name']:    # I don't care about podcasts sadly
                continue

            song = dict(filter(removeCols, song.items()))   # Filtering out unwanted data
            song['ts'] = datetime.fromisoformat(song['ts'][:-1]) \
                .replace(tzinfo=from_zone) \
                .astimezone(to_zone) \
                .isoformat()    # Converting to local timezone

            try:
                values = [song[column] for column in columns]
                insert_statement = 'insert into listens (%s) values %s'
                cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))  # Inserting into 'listens' table
            except Exception as e:
                print(e, song)
                break

    conn.commit()   # Commiting changes to DB

# Function to insert genres into table
def insert_genres():
    client_id = ''
    client_secret = ''  # API constants

    # Spotipy clients
    ccm = spotipy.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, cache_handler=spotipy.MemoryCacheHandler())
    sp = spotipy.Spotify(client_credentials_manager=ccm, requests_timeout=10)


    songs = {}
    artists = {}
    genres = {}

    # Iterating through listens and determining the number of streams for each song
    for filename in files:
        with open(filename, 'r') as file:
            data = loads(file.read())

            for song in data:
                if not song['spotify_track_uri']:
                    continue

                if not songs.get(song['spotify_track_uri']):
                    songs[song['spotify_track_uri']] = 0

                songs[song['spotify_track_uri']] += 1

    # Getting all the song URIs
    song_uris = list(songs.keys())

    # Iterating through the tracks and determining the number of streams for each artist
    for i in range(0, len(song_uris), 50):
        print(round(i / len(song_uris) * 100, 2), end='\t\r')

        try:
            tracks = sp.tracks(song_uris[i:i + 50])['tracks']

            for track in tracks:
                for artist in track['artists']:
                    if not artists.get(artist['id']):
                        artists[artist['id']] =  0

                    artists[artist['id']] += songs[track['uri']]

        except Exception as e:
            print(e, i, i + 50)

    print()

    # Getting artist URIs
    artist_uris = list(artists.keys())

    # Iterating through the artists and determining the number of streams for each genre
    for i in range(0, len(artist_uris), 50):
        print(round(i / len(artist_uris) * 100, 2), end='\t\r')

        try:
            api_artists = sp.artists(artist_uris[i:i + 50])['artists']

            for artist in api_artists:
                for genre in artist['genres']:
                    if not genres.get(genre):
                        genres[genre] = 0

                    genres[genre] += artists[artist['id']]

        except Exception as e:
            print(e, i, i + 50)


    print()

    # Mapping to appropriate dictionary structure
    genre_data = [{ 'genre': g, 'listens': genres[g] } for g in genres]
    columns = ['genre', 'listens']

    # Inserting genre streams into table
    for genre in genre_data:
        try:
            values = [genre[column] for column in columns]
            insert_statement = 'insert into genres (%s) values %s'
            cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
        except Exception as e:
            print(e, genre)
            break

    # Commiting changes to the DB
    conn.commit()

insert_listens()
insert_genres()

# Closing the connection
conn.close()
