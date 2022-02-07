FROM python:3.8.0

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY . /app

WORKDIR /app


ENTRYPOINT ["python3", "-u", "main.py"] 