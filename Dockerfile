# start with a base image
FROM ubuntu:18.04

# install os dependencies
COPY ./sources.list /etc/apt/
# RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 3B4FE6ACC0B21F32
RUN apt-get update
# RUN apt-get install -y autoconf automake libtool
# RUN apt-get install -y g++
# RUN apt-get install -y libcurl3-dev
# RUN apt-get install -y tk8.5 tcl8.5 tk8.5-dev tcl8.5-dev
# RUN apt-get install -y wget
# RUN apt-get install -y  libc6 libtool
# RUN python --version
# RUN apt-get python3-pip
# RUN pip --version
# RUN apt-get install tessract-ocr


# build tesseract
# RUN wget https://github.com/tesseract-ocr/tesseract/archive/4.1.1.tar.gz
# RUN tar -zxvf 4.1.1.tar.gz
# RUN ls -la
# WORKDIR tesseract-4.1.1/
# RUN ./autogen.sh
# RUN ./configure
# RUN make
# RUN make install
# RUN ldconfig
# RUN cd ..

# Install app dependencies
# ADD requirements.txt /
# RUN pip3 install -r requirements.txt


# update working directories
# ADD . /test
# WORKDIR /test

EXPOSE 8000
# CMD ["python", "main.py -i sample/"]
