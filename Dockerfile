FROM python:3.13.3-alpine

# Set environment variables
ENV TZ="Europe/Moscow" \
    USER=app \
    GROUPNAME=app \
    UID=1000 \
    GID=1000 \
    PATH_APP=loader  \
    PATH_UDLOAD=uploads \
    # Configure Python to not buffer "stdout" or create .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT_SERVICE=8000 \
    IP_SERVICE='0.0.0.0'

# Create a group and user
RUN addgroup -g ${GID} -S ${GROUPNAME} && \
    adduser -u ${UID} -D -G ${GROUPNAME} -S ${USER}

WORKDIR /${PATH_APP}

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN mkdir -p /${PATH_APP}/${PATH_UDLOAD} && \
    chown -R ${USER}:${GROUPNAME} /${PATH_APP} && \
    chmod -R 777 /${PATH_APP}/${PATH_UDLOAD}

EXPOSE ${PORT_SERVICE}

# Switch to the new user
USER $USER

CMD ["sh", "-c", "uvicorn main:app --host $IP_SERVICE --port $PORT_SERVICE"]