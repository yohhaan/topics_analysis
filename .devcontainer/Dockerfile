FROM debian:bullseye
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 \
    python3-pip \
    protobuf-compiler \
    wget \
    libusb-1.0-0-dev \
    parallel \
    locales \
    curl && \
    apt-get clean autoclean && \
    apt-get autoremove
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
RUN pip3 install --upgrade pip && \
    pip3 install tflite-support-nightly pandas matplotlib numpy seaborn nltk jinja2 black requests gensim beautifulsoup4 scipy
RUN addgroup --gid 1000 vscode
RUN adduser --disabled-password --gecos "" --uid 1000 --gid 1000 vscode
ENV HOME /home/vscode
USER vscode

