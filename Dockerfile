FROM python:3.8

WORKDIR /code

ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ADD code/ /code/

CMD [ "python3", "SensorConnector.py" ]

