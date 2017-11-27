FROM python:3


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./src /app

ENTRYPOINT [ "python" ]

CMD [ "demo.py" ]