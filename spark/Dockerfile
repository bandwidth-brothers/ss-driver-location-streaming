FROM docker.io/bitnami/spark:3.1.2

USER root

ENV SPARK_MODE=master
ENV SPARK_RPC_AUTHENTICATION_ENABLED=no
ENV SPARK_RPC_ENCRYPTION_ENABLED=no
ENV SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
ENV SPARK_SSL_ENABLED=no

ENV VIRTUAL_ENV=/opt/bitnami/spark/python/.venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./ ./work
RUN pip install -r ./work/requirements.txt

# Spark UI
EXPOSE 8080
# Jupyter Notebook
EXPOSE 8888
# Spark
EXPOSE 7077
