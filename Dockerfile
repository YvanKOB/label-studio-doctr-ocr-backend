FROM ghcr.io/mindee/doctr:torch-py3.10.13-gpu-2024-02
# Install label-studio-ml backend from the repository and requirements
RUN pip3 install boto3 gunicorn "label-studio-ml@git+https://github.com/heartexlabs/label-studio-ml-backend.git"

WORKDIR /app
COPY * /app/

EXPOSE 9090

CMD gunicorn --bind :${PORT:-9090} --workers ${WORKERS:-1} --threads ${THREADS:-4} --timeout 0 _wsgi:app
