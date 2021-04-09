FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /build

RUN apt-get update && apt-get install git;

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN git clone https://github.com/tulip-control/dd.git; \
    cd dd; \
    python3 -m ensurepip; \
    pip install cython; \
    python setup.py install --fetch --cudd

WORKDIR /app

COPY requirements/dev/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./iscram ./iscram

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
