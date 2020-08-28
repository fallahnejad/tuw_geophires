FROM debian:bullseye

RUN apt update && \
    apt install --no-install-recommends -y \
    python3 python3-pip python3-dev \
    build-essential \
    gdal-bin libgdal-dev proj-bin \
    python3-fiona python3-pyproj \
    python3-six python3-shapely \
    python3-numpy python3-pandas python3-geopandas && \
    rm -rf /var/lib/apt/lists/*

ADD docker_requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ADD . /app
RUN ln -s /app/uploads /uploads
