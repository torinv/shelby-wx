FROM python:3.10.0-bullseye
COPY ./app /app
RUN apt-get update && apt-get install -y python3-opencv
RUN pip3 install -r /app/requirements.txt

ENV CAM_USER=user
ENV CAM_PASSWORD=password

WORKDIR /app
ENTRYPOINT ["python3", "/app/ShelbyWx.py"]
