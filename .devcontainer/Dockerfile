# Use python base image
FROM python:3.10-slim-buster

# Update packages, install uuidgen, and clean up
RUN apt-get update \
    && apt-get install -y uuid-runtime git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Set the timezone to Africa/Nairobi
RUN ln -sf /usr/share/zoneinfo/Africa/Nairobi /etc/localtime

#RUN pip install -r requirements.txt


