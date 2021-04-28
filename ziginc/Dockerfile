FROM ubuntu:latest
RUN apt update && apt upgrade -y \
	&& apt install -y python3 python3-pip \
	&& export DEBIAN_FRONTEND=noninteractive && \
	export TZ=Europe/Oslo && \
	apt install -y firefox wget && \
	wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz && \
    	tar -xzf geckodriver-v0.23.0-linux64.tar.gz -O > /usr/bin/geckodriver && \
    	chmod +x /usr/bin/geckodriver && \
    	rm geckodriver-v0.23.0-linux64.tar.gz

