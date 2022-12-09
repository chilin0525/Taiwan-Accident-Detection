import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
from datetime import datetime
from typing import List


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
CHANNEL_ID = "UCiSUNo-aCw_qjMU-K84oo7w"
SECRET_PATH = "client_secret.json"


class VideoInfo():
    def __init__(
        self,
        video_id: str,
        video_published_at: datetime
    ) -> None:
        self._video_id = video_id
        self._video_published_at = video_published_at
        self._video_title = None
        self._duration = None

    @property
    def video_url(self):
        return f"https://www.youtube.com/watch?v={self._video_id}&" + \
        "ab_channel=WoWtchout-%E5%9C%B0%E5%9C%96%E5%9E%8B%E8%A1%8C" + \
        "%E8%BB%8A%E5%BD%B1%E5%83%8F%E5%88%86%E4%BA%AB%E5%B9%B3%E5%8F%B0"

    @property
    def video_id(self):
        return self._video_id

    @property
    def video_id(self):
        return self._video_id

    @video_id.setter
    def video_id(self, video_id):
        self._video_id = video_id
    
    @property
    def video_published_at(self):
        return self._video_published_at

    @video_published_at.setter
    def video_published_at(self, video_published_at):
        self._video_published_at = video_published_at

    @property
    def video_title(self):
        return self._video_title

    @video_title.setter
    def video_title(self, video_title):
        self._video_title = video_title

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = duration


def save_to_csv(video_list: List[VideoInfo]) -> None:
    df = pd.DataFrame({
        "id": [video.video_id for video in video_list],
        "published_at": [video.video_published_at for video in video_list],
        "title": [video.video_title for video in video_list],
        "duration": [video.duration for video in video_list],
        "url": [video.video_url for video in video_list]
    })
    df.sort_values(by="published_at", inplace=True)
    df.to_csv(f"video_{datetime.now().strftime('%Y_%m_%d')}.csv", index=False)


def parse_channelListResponse(res: str):
    # parse upload playlist in channelListResponse
    try:
        result = res['items']
        contentDetails = result[0]['contentDetails']
        user_upload_playlist = contentDetails['relatedPlaylists']['uploads']
        return user_upload_playlist
    except Exception as e:
        print(e)
    
    return None


def request2playlist_item(youtube, playlist_id: str):
    def parse_publish_time2datetime(
        videoPublishedAt: str
    ) -> datetime:
        return datetime.strptime(
            videoPublishedAt, "%Y-%m-%dT%H:%M:%SZ"
        )

    video_list = list()

    # since each request only including at most 50 result,
    # parsing if nextPageToken exist
    try:
        flag = True
        nextPageToken = None
        while(flag or nextPageToken is not None):
            # request to get each video id  
            request = youtube.playlistItems().list(
                part="contentDetails",
                pageToken=nextPageToken,
                playlistId=playlist_id,
                maxResults=50
            )
            response = request.execute()

            videos = response['items']
            cur_page_video = [
                VideoInfo(
                    video['contentDetails']['videoId'], 
                    parse_publish_time2datetime(video['contentDetails']['videoPublishedAt'])
                )
                for video in videos
            ]
            video_list.extend(cur_page_video)

            # update to nextPage
            nextPageToken = response['nextPageToken'] \
                if 'nextPageToken' in response else None   

            flag = False

    except Exception as e:
        print(e)

    return video_list


def request2video_title(youtube, video_id: List[str]) -> dict:
    
    cnt = 0
    id2title = dict()
    while(cnt<len(video_id)):
        # request to get each video id  
        request = youtube.videos().list(
            part="snippet, contentDetails",
            id=video_id[cnt: cnt+50],
            maxResults=50
        )
        response = request.execute()

        videos = response['items']
        cur_page_video = {
            video['id']: (
                video['snippet']['title'], 
                video['contentDetails']['duration']
            ) for video in videos
        }
        id2title.update(cur_page_video)

        cnt += 50
        
    return id2title


def main():

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = SECRET_PATH

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, 
        scopes
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, 
        api_version, 
        credentials=credentials
    )

    request = youtube.channels().list(
        part="contentDetails",
        id=CHANNEL_ID,
        maxResults=50
    )
    response = request.execute()

    user_upload_playlist = parse_channelListResponse(response)
    if user_upload_playlist is None:
        exit(-1)

    print(f"Get playlist id: {user_upload_playlist}")

    video_list = request2playlist_item(youtube, user_upload_playlist)
    if len(video_list)==0:
        print("Empty videos of the user.")
        exit(0)
    else:
        print(f"Parsing {len(video_list)} playlist item")
    
    video_id = [video.video_id for video in video_list]
    video_id2title = request2video_title(youtube, video_id)

    for video in video_list:
        video.video_title = video_id2title[video.video_id][0]
        video.duration = pd.Timedelta(video_id2title[video.video_id][1])
    
    print(f"Parsing {len(video_list)} videos.")

    save_to_csv(video_list)


if __name__ == "__main__":
    main()