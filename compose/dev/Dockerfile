FROM ubuntu:latest as COIN

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update
RUN apt-get -y install --no-install-recommends git subversion gcc g++ make wget gfortran patch pkg-config file
RUN apt-get -y install --no-install-recommends libgfortran-10-dev libblas-dev liblapack-dev libmetis-dev libnauty2-dev
RUN apt-get -y install --no-install-recommends ca-certificates

RUN git clone https://github.com/coin-or/coinbrew /var/coin-or
WORKDIR /var/coin-or
RUN ./coinbrew fetch Couenne@0.5.8 --skip="ThirdParty/Blas ThirdParty/Lapack ThirdParty/Metis" --no-prompt
RUN ./coinbrew build Couenne@0.5.8 --skip="ThirdParty/Blas ThirdParty/Lapack ThirdParty/Metis" --no-prompt --prefix=/usr --tests=none LT_LDFLAGS=-all-static LDFLAGS=-static --disable-shared

FROM ubuntu:latest as RELEASE

RUN apt-get update
RUN apt-get -y install --no-install-recommends libgfortran-10-dev libblas-dev liblapack-dev libmetis-dev libnauty2-dev
COPY --from=COIN /usr/bin/couenne /bin/couenne


RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN apt-get update && apt-get -y install git python3-venv

#RUN apt-get update && apt-get install git

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
