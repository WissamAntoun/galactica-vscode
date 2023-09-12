# GALACTICA for code completion with Hugging Face VSCode Endpoint Server

Use this extension mainly to write latex documents with code completion using the [Hugging Face Custom VSCode Endpoint Server](https://github.com/huggingface/huggingface-vscode) with [Galactica](https://github.com/paperswithcode/galai) and [VLLM](https://github.com/vllm-project/vllm).

## Installation

Follow the instructions on the [VLLM Docs](https://vllm.readthedocs.io/en/latest/getting_started/installation.html) to install the VLLM server.

Then install the VSCode extension that only supports `latex` files then get it from [here](https://github.com/WissamAntoun/huggingface-vscode) go there and download the latest `.vsix` file and install it.

Or if you're planning to use the Hugging Face Code for everything then get it from the [VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=HuggingFace.huggingface-vscode)

## Model Download

Download the model from [here](https://huggingface.co/models?search=galactica) using:

```python
from huggingface_hub import snapshot_download

snapshot_download("facebook/galactica-6.7b", local_dir="facebook-galactica-6.7b", local_dir_use_symlinks=False); print("done")
```

## Usage

Run the VLLM server with:

```bash
./run_api_server.sh <MODEL_PATH>
```

or with docker:

```bash
# Build the docker image (first time only)
docker build -t vllm:0.1.6 -f Dockerfile .
./run_api_server_docker.sh <MODEL_PATH>
```

Then go to the extension setting and set the `Hugging Face Code: Config template` to `Custom` and the `Hugging Face: Model Id Or Endpoint` to `http://localhost:8000`.
