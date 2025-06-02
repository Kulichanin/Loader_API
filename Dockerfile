FROM python:3.13.3-alpine

# Set environment variables
ENV TZ="Europe/Moscow" \
    USER=app \
    GROUPNAME=app \
    UID=1000 \
    GID=1000 \
    PATH_APP=loader  \
    PATH_UDLOAD=uploads \
    # Prevents Python from writing pyc files.
    PYTHONDONTWRITEBYTECODE=1 \
    # Keeps Python from buffering stdout and stderr to avoid situations where
    # the application crashes without emitting any logs due to buffering.
    PYTHONUNBUFFERED=1 \
    PORT_SERVICE=8000 \
    IP_SERVICE='0.0.0.0'

# Create a group and user without a shell
RUN addgroup -g "$GID" -S "$GROUPNAME" && \
    adduser -u "$UID" -D -G "$GROUPNAME" -S "$USER" && \
    mkdir -p /${PATH_APP}/${PATH_UDLOAD} && \
    chown -R ${USER}:${GROUPNAME} /${PATH_APP}/${PATH_UDLOAD} && \
    chmod -R 777 /${PATH_APP}/${PATH_UDLOAD}  

WORKDIR /${PATH_APP}

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE ${PORT_SERVICE}

# Switch to the new user
USER $USER

CMD ["sh", "-c", "uvicorn main:app --host $IP_SERVICE --port $PORT_SERVICE"]

# CMD ["sh", "-c", "ls -la"]