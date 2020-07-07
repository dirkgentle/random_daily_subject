#!/bin/bash

docker run \
	-d \
	--rm \
	--env-file .env \
	-v "$(pwd)/db:/random_daily_subject/db" \
	-v "$(pwd)/logs:/random_daily_subject/logs" \
	random_daily_subject:latest
