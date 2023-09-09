# you can go up to nvcr.io/nvidia/pytorch:22.12-py3 since VLLM only supports cuda 11.X not 12
FROM nvcr.io/nvidia/pytorch:22.10-py3

# https://vllm.readthedocs.io/en/latest/getting_started/installation.html
RUN pip uninstall torch -y

COPY requirements.txt .
RUN pip install -r requirements.txt