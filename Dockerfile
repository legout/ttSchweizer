
# build stage
FROM python:3.11-slim AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md /project/
COPY app/ /project/app

# install dependencies and project into the local packages directory
WORKDIR /project
RUN pdm export -o requirements.txt
RUN pip install -r requirements.txt


# run stage
FROM python:3.11-slim

COPY app /app
# retrieve packages from build stage
#ENV PYTHONPATH=/project/pkgs
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

WORKDIR /app/data
# set command/entrypoint, adapt to fit your needs
CMD ["python", "../ttSchweizerHttp.py"]
#ENTRYPOINT [ "/bin/bash" ]