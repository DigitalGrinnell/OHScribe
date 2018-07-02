FROM python:3.6-alpine

RUN adduser -D ohscribe

WORKDIR /home/ohscribe

RUN apk add --update --no-cache g++ gcc libxslt-dev

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

ENV UPLOAD_FOLDER /home/ohscribe/data
COPY data /home/ohscribe/data

COPY app app
COPY ohscribe.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP ohscribe.py
ENV FLASK_DEBUG 1

RUN chown -R ohscribe:ohscribe ./
USER ohscribe

EXPOSE 5001
ENTRYPOINT ["./boot.sh"]
