FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as BASE

WORKDIR /app

COPY ./requirements/prod/requirements.txt ./
RUN python -m ensurepip
RUN pip wheel --wheel-dir=/root/wheels -r ./requirements.txt

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as RELEASE

WORKDIR /app

COPY --from=BASE /root/wheels /root/wheels
COPY ./iscram ./iscram

RUN python -m ensurepip
RUN pip install --no-index --find-links=/root/wheels /root/wheels/*

ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 80

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "80"]
