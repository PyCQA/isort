#!/bin/bash
set -ux

result=0

for ver in {3.6,3.7,3.8}; do
	# latest tag will override after each build, leaving only the newest python version tagged
	docker build ./ --build-arg VERSION=$ver -t "isort:$ver" -t "isort:latest" && docker run "isort:$ver"
	result=$(( $? + $result ))
done

exit $result
