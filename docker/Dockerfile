FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python3 python3-pip git curl net-tools
RUN git clone https://github.com/timwoj/tlmbot
RUN cd tlmbot && pip3 install -r requirements.txt

WORKDIR tlmbot
