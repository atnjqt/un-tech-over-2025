FROM ubuntu:24.04
RUN export DEBIAN_FRONTEND=noninteractive
RUN export TZ=UTC
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.10 python3.10-venv python3.10-dev git && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    apt install -y python3-pip && \
    apt install -y gdal-bin libgdal-dev

WORKDIR /app

RUN python3.10 -m pip install gdal

# Clone specific branch
RUN git clone -b un-tech-over-2025-day2 https://github.com/atnjqt/giga-spatial.git /tmp/giga-spatial

# Install from local directory
RUN cd /tmp/giga-spatial && python3.10 -m pip install -e .

COPY . .

EXPOSE 8000
CMD ["python", "./application.py"]