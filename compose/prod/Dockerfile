FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8 as BASE

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN git clone https://github.com/tulip-control/dd.git; \
    cd dd; \
    python3 -m ensurepip; \
    pip install cython; \
    python setup.py install --fetch --cudd

COPY ./iscram ./iscram
COPY ./setup.py setup.py
RUN pip install .

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as RELEASE

COPY --from=BASE /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 80

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "80"]
