#!/bin/bash


tones=("warm", "cold", "cool", "hot", "red", "green", "blue", "yellow", "purple", "cyan", "magenta", "orange", "change", "chase", "moving")
echo "Available tones: ${tones[@]}"

if [[ ! " ${tones[@]} " =~ " $1 " ]]; then
    echo "Invalid tone: $1"
    exit 1
fi

python -m sabersocket.app.single_publisher --broker emqx --role publisher --topic "saber/tone" --message $1
