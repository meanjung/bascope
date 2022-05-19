FROM ubuntu:20.04

RUN apt-get update -y && apt-get upgrade -y python3 && apt-get install -y python3-pip

COPY . /web-server
WORKDIR /web-server

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "run.py"]
