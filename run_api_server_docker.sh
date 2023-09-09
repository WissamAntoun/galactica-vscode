MODEL_NAME_OR_PATH=$1

# docker build -t vllm:0.1.6 -f Dockerfile .

docker run \
--gpus all \
--rm \
--shm-size=8g \
-p 8000:8000 \
-v $(pwd):/app \
-v $MODEL_NAME_OR_PATH:/model_repo \
vllm:0.1.6 bash -c "cd /app && ./run_api_server.sh /model_repo"