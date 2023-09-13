# GALACTICA for code completion with Hugging Face VSCode Endpoint Server

This is a quick and dirty project to make writing papers with code completion easier. Born out of procrastination and the need to quickly write a paper during my PhD.

Use this extension mainly to write latex documents with code completion using the [Hugging Face Custom VSCode Endpoint Server](https://github.com/huggingface/huggingface-vscode) with [Galactica](https://github.com/paperswithcode/galai) and [VLLM](https://github.com/vllm-project/vllm).

Compatible with all Galactica models from [here](https://huggingface.co/models?search=galactica).


Note: This repo will probably move to using the HuggingFace Text Generation Inference codebase once they fix support for Galactica models [LINK_TO_ISSUE](https://github.com/huggingface/text-generation-inference/issues/1004). With that you'll be able to use GPTQ quantized models.

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

# Contacts
**Wissam Antoun**: [Linkedin](https://www.linkedin.com/in/wissam-antoun-622142b4/) | [Twitter](https://twitter.com/wissam_antoun) | [Github](https://github.com/WissamAntoun) | wfa07 (AT) mail (DOT) aub (DOT) edu | wissam.antoun (AT) gmail (DOT) com