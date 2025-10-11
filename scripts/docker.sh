#!/usr/bin/env bash
set -ux

result=0

for ver in {3.10,3.11,3.12,3.13,3.14}; do
	# latest tag will override after each build, leaving only the newest python version tagged
	docker build ./ --build-arg VERSION=$ver -t "isort:$ver" -t "isort:latest" && docker run "isort:$ver"
	result=$(( $? + $result ))
done

exit $result
