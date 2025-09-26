# Have to use python 3.11, otherwise can not get most recent version of tflite-support
FROM python:3.11-trixie

# Other dependencies
RUN apt-get update && apt-get install -y protobuf-compiler \
    unzip \
    libusb-1.0-0-dev \
    parallel \
    locales \
    curl \
    wget && \
    apt-get clean autoclean && \
    apt-get autoremove

# Locales for parallel
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

# Configurations for virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Create group and user to avoid permissions issues with local user/group
# when editing files in and out of docker container.
# Note: GNU/Linux systems assign the default 1000 User Identifier (UID) and
# Group Identifier (GID) to the first account created during installation. It is
# possible that your local UID and GID on your machine may be different, in that
# case you should edit the values in the commands below.
# You can see your UID and GID(s) by executing: `id`
RUN addgroup --gid 1000 groupname
RUN adduser --disabled-password --gecos "" --uid 1000 --gid 1000 username
ENV HOME=/home/username
USER username

