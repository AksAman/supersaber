#!/bin/bash


python -m sabersocket.app.single_publisher --broker emqx --role publisher --topic "saber/tone" --message $1
