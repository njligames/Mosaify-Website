# Use an official Ubuntu runtime as a parent image
FROM ubuntu:20.04

# Set the working directory in the container
WORKDIR /app

ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# RUN apt-get update
# RUN apt-get install -y unzip wget build-essential checkinstall libx11-dev libxext-dev zlib1g-dev libpng-dev libjpeg-dev libfreetype6-dev libxml2-dev
# # RUN apt-get build-dep imagemagick
# 
# RUN apt-get update
# RUN apt-get dist-upgrade
# RUN apt-get install --reinstall tar
# 
# RUN wget https://download.imagemagick.org/archive/ImageMagick-7.1.1-34.zip
# RUN unzip ImageMagick-7.1.1-34.zip
# WORKDIR ImageMagick-7.1.1-34
# RUN sh configure # (or configure or sudo configure)
# RUN make install
# RUN ldconfig /usr/local/lib # (or sudo ldconfig /usr/local/lib)
# WORKDIR ../

# Install dependencies, including Python 3.11 and C++ standard libraries
RUN apt-get update && \
    apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    python3.11-lib2to3 \
    python3.11-gdbm \
    python3.11-tk \
    python3-pip \
    build-essential \
    gcc \
    g++ \
    swig \
    libmagick++-6.q16-dev \
    libmagick++-6.q16-8 \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3.11 -m venv /opt/venv

# Activate the virtual environment and install dependencies
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0", "wsgi:app"]
