FROM python:alpine

WORKDIR /loader

COPY ./requirements.txt /loader/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /loader/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]