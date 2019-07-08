FROM python:slim

# Make container root
USER root
RUN mkdir /app && \
    apt update && \
    apt install -y ffmpeg \
        libavresample4 \
        libtag1v5 \
        libchromaprint1 \
        pkg-config && \
    apt clean;  

# Install Python dependencies
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

# Setup user to run the server as
RUN useradd -m python

# Install dumb-init
RUN apt-get update && apt-get install \
    dumb-init

USER python
ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "/app/main.py"]
