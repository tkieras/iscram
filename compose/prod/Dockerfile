FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as BASE

WORKDIR /usr/src/app

COPY ./requirements/prod/requirements.txt ./
RUN python -m ensurepip
RUN pip wheel --wheel-dir=/root/wheels -r ./requirements.txt

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as RELEASE

WORKDIR /usr/src/app

COPY --from=BASE /root/wheels /root/wheels

RUN python -m ensurepip
RUN pip install --no-index --find-links=/root/wheels /root/wheels/*
RUN python ./setup.py sdist
RUN pip install ./dist/*

EXPOSE 80

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "80"]
