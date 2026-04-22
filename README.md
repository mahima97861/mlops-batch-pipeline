# MLOps Batch Job

## Description
This project implements a reproducible batch pipeline:
- Loads YAML config
- Processes OHLCV data
- Computes rolling mean & trading signal
- Outputs metrics JSON and logs

## Local Run
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

## Docker
docker build -t mlops-task .
docker run --rm mlops-task

## Output
metrics.json contains:
- rows_processed
- signal_rate
- latency
