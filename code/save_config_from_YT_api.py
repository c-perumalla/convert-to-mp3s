from googleapiclient.discovery import build
import json
import os

# Read the YouTube Data API key from the environment, e.g.
#   export YOUTUBE_API_KEY="..."
# Never commit the key itself.
API_KEY = os.environ["YOUTUBE_API_KEY"]

savepath = ""  # TODO: set local path — where to write config.json
get_link = lambda x: 'https://www.youtube.com/watch?v={}'.format(x)

def get_vidnames(playlist_id, playlist_name):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = build(api_service_name, api_version, developerKey=API_KEY)

    try:
        request = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=playlist_id, maxResults=50)
        response = request.execute()
        items = response['items']
        next_page_token = response['nextPageToken']
    except:
        print('done reading')
        return {playlist_name: {item['snippet']['title']: {'upload_date': item['snippet']['publishedAt'], 'link': get_link(item['snippet']['resourceId']["videoId"])} for item in items}}

    while True:
        try:
            request = youtube.playlistItems().list(part="snippet, contentDetails", playlistId=playlist_id, maxResults=50, pageToken=next_page_token)
            response = request.execute()
            items.append(response['items'])
            next_page_token = response['nextPageToken']
        except KeyError as e:
            print('done reading')
            break
    return {playlist_name: {item['snippet']['title']: {'upload_date': item['snippet']['publishedAt'], 'link': get_link(item['snippet']['resourceId']["videoId"])} for item in items[:-1]}}


def get_playlists():
    api_service_name = "youtube"
    api_version = "v3"

    youtube = build(api_service_name, api_version, developerKey=API_KEY)


    try:
        request = youtube.playlists().list(part="snippet,contentDetails", channelId="UCimwXNI1_dUHs1HYJTMPgLw", maxResults=50)
        response = request.execute()
        items = response['items']
        next_page_token = response['nextPageToken']
    
    except KeyError as e:
        print('done reading')
        return [(item['id'], item['snippet']['title']) for item in items]

    while True:
        try:
            response = youtube.playlists().list(part="snippet,contentDetails", channelId="UUimwXNI1_dUHs1HYJTMPgLw",  maxResults=50, pageToken=next_page_token)
            items.append(response['items'])
            next_page_token = response['nextPageToken']
        except KeyError as e:
            print('done reading')
            break

    return [(item['id'], item['snippet']['title']) for item in items]

def main():
    config = {}
    playlist_info = get_playlists()
    for id, name in playlist_info:
        config.update(get_vidnames(id, name))
    
    with open(savepath, 'w') as fp:
        json.dump(config, fp)

if __name__ == '__main__':
    main()




