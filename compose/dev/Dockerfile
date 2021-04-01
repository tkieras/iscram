FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

WORKDIR /app

COPY requirements/dev/requirements.txt ./

RUN python3 -m ensurepip
RUN pip install -r requirements.txt

COPY ./iscram ./iscram

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
