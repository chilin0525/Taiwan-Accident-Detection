#!/bin/bash

cat $1 | awk -F "," '{
    if(NR!=1){
        printf("%s \n", $5)
    }
}' | xargs yt-dlp -N 10 -P $2