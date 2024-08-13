#!/bin/bash

i=1

for mp4 in ./videos/*.mp4; do
    echo "Processing $mp4"
    basename=$(basename $mp4)
    basename="${basename%.*}"
    
    ffmpeg -i $mp4 -vf "thumbnail" -frames:v 5 -q:v 2 ./videos/$basename.jpg
done