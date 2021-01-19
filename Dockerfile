FROM alpine:3.13 as base

RUN apk add \
    python3 \
    py3-pip
WORKDIR /gandi-ddns
ADD requirements.txt gandi_ddns.py ./
RUN pip install -r requirements.txt

FROM base as test

RUN apk add py3-pytest
ADD test_gandi_ddns.py ./
RUN pytest

FROM base as target

CMD [ "./gandi_ddns.py" ]
