FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8 as BASE

WORKDIR /app

COPY ./requirements.txt ./
RUN pip wheel --wheel-dir=/root/wheels -r ./requirements.txt

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8 as RELEASE

EXPOSE 80

WORKDIR /app

COPY --from=BASE /root/wheels /root/wheels
COPY ./dist/ ./dist/

RUN pip install --no-index --find-links=/root/wheels /root/wheels/* && \
    pip install dist/*

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "80"]
