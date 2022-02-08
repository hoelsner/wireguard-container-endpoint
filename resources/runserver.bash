#!/bin/bash -e
# startup script for the container
mkdir -p ${DATA_DIR}/ssl

# apply DB migrations and start the webapp
#aerich upgrade > /opt/aerich.log

if [ -z "$UVICORN_SSL_KEYFILE" ]
then
    uvicorn app:create \
        --factory \
        --host=${APP_HOST} \
        --port=${APP_PORT} \
        --timeout-keep-alive=60

else
    # generate certificates if not already available
    if [ -f "$UVICORN_SSL_KEYFILE" ]; then
        echo "keyfile found, skip generating a self singed certificate"
    else
        openssl req -nodes -x509 -newkey rsa:4096 -keyout $UVICORN_SSL_KEYFILE -out $UVICORN_SSL_CERTFILE -sha256 -days 365 \
            -subj "/C=/ST=/L=/O=/CN=${SELF_SIGNED_CERT_CN}"
    fi

    uvicorn app:create \
        --factory \
        --host=${APP_HOST} \
        --port=${APP_PORT} \
        --timeout-keep-alive=60 \
        --ssl-keyfile=${UVICORN_SSL_KEYFILE} \
        --ssl-certfile=${UVICORN_SSL_CERTFILE}
fi
