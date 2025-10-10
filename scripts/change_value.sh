#!/bin/bash



python -m sabersocket.app.single_publisher --broker emqx --role publisher --topic "audio-values" --message $1
