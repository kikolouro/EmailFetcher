FROM python:3.8.0

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-u", "main.py"] 