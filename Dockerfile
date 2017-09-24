# Build / run:
# docker build --tag="${PWD##*/}" .
# docker run --tty --interactive --volume "${PWD}":/opt/project --publish=8000:8000 "${PWD##*/}"
# docker run --tty --interactive --volume "${PWD}":/opt/project --entrypoint="bash" "${PWD##*/}"
# Cleanup:
# docker rm $(docker ps --all --quiet)
# docker rmi $(docker images --quiet --filter "dangling=true")
# docker volume rm $(docker volume ls --quiet)


FROM ubuntu:16.04

ENV last_update 20170911


# Install required packages

RUN apt-get update --quiet --yes && apt-get install --quiet --yes --force-yes ca-certificates \
    python3-dev \
    python3-pip \
    python3-setuptools \
    curl \
    unzip \
    git

# Install required packages
ADD requirements.txt /root/requirements.txt
RUN pip3 install --upgrade pip 
RUN pip3 install --upgrade setuptools urllib3[secure]
RUN pip3 install -r /root/requirements.txt

# These are stored in https://chromedriver.storage.googleapis.com/index.html
# from time to time they will need to be updated
ENV CHROMEDRIVER_VERSION 2.32
ENV CHROMEDRIVER_SHA256 1e053ebec954790bab426f1547faa6328abff607b246e4493a9d927b1e13d7e4

RUN curl -SLO "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" \
  && echo "$CHROMEDRIVER_SHA256  chromedriver_linux64.zip" | sha256sum -c - \
  && unzip "chromedriver_linux64.zip" -d /usr/local/bin \
  && rm "chromedriver_linux64.zip"

# Configure environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONWARNINGS d

# Entrypoint
# Also need
EXPOSE 8000
WORKDIR /opt/project/binarycrate
ENTRYPOINT ["python3", "/opt/project/binarycrate/manage.py"]
CMD ["check"]
