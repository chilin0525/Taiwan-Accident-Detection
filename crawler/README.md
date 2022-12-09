# Crawler to collect YT videos

In this section, you will know:
* How to parse video file from youtube channel using source code by reading this section.
    * Read every section and prepare environment
* If you don't want to parse video by yourself, you can using the `.csv` file we prepared to install all video, please jump to [Download chapter](https://github.com/chilin0525/Taiwan-Accident-Detection/tree/crawler/crawler#download-video)
* In our research, we using from [WoWtchout - 地圖型行車影像分享平台 ](https://www.youtube.com/@WoWtchout). There are lot of Taiwan dashcam and we also appreciate they authorize we can use the video to do our research project. If you want to parse other channel, you need to rewrite source code of some setting, like channel id.

## Prerequisite

Before parse video on youtube, you must have some resource and permission on Google API:
1. You must have a Google acount
2. Create API key and OAuth 2.0 client ID
3. Enable **Youtube Data API**.
    * You have **free** quota per day, so don't afraid you need to pay money for using API.
    * You can check limit quota in GCP.
4. Download Oauth json file and rename as **client_secret.json**
    * If you do not want name as our setting, you need to update source code in `main.py`
        ```python
        SECRET_PATH = "client_secret.json"
        ```
    * If you want to download from other channel, you also need to update source code.
5. Execute and the terminal will prompt the URL and you need to login and copy secret and paste to terminal:
    ```
    $ python3 main.py
    ```

### Python dependency package

```bash
$ pip install -r requirements.txt 
```

### Docker

* cd to `crawler` folder
* build
    ```bash
    $ docker build -t <IMAGE NAME>:<TAG> .
    ```
* execute with source folder:
    ```bash
    $ cd ..
    ```
    ```bash
    $ docker run -it \
     -w /src \
     -v $PWD/crawler:/src \
     <IMAGE NAME>:<TAG> /bin/bash 
    ```

## Split video into normal and defect

* We using the video title including some keywords about car crash to filter which video is normal video without car crash
* Since some video is very long, we also support to filter video duration
* Command to execute python script:
    * `Video csv file` is the path of csv including video information in last step
    ```python
    $ python3 split_normal_defect_video.py \
        <Video csv file> \
        <Normal video path you want to save> \
        <Defect video path you want to save> \
        <Video duration limit>
    ```

## Download video

* We using `yt-dlp` tool to install youtube video, because it is faster than original `youtube-dl` and also support multiprocess
* We write a bash script to install video
* WARNING: the csv format must have like this, or you need to update source code by yourself:
    ```
                    id         published_at                                 title         duration                                                url
    0     6gj6A79W0bo  2018-01-02 04:19:45           過路口應減速慢行,避免意外發生 | wowtchout  0 days 00:00:33  https://www.youtube.com/watch?v=6gj6A79W0bo&ab...
    1     VCt_gUZx2xs  2018-01-02 07:46:26                    開車請專心！ | wowtchout  0 days 00:00:24  https://www.youtube.com/watch?v=VCt_gUZx2xs&ab...
    ```
* Execute:
    ```bash
    $ ./install.sh <the csv file you want to install> <your destination folder> 
    ```