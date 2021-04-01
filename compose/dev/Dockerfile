FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

WORKDIR /usr/src/app

COPY requirements/dev/requirements.txt ./

RUN python3 -m ensurepip
RUN pip install -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app/iscram"

CMD ["uvicorn", "iscram.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
