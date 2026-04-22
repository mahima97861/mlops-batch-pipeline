import argparse
import pandas as pd
import numpy as np
import yaml
import logging
import json
import time
import sys
import os


# ---------------- LOGGER SETUP ----------------
def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


# ---------------- LOAD CONFIG ----------------
def load_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("Config file not found")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    required_keys = ["seed", "window", "version"]

    for key in required_keys:
        if key not in config:
            raise Exception(f"Missing config key: {key}")

    return config


# ---------------- LOAD DATA ----------------
def load_data(input_path):
    if not os.path.exists(input_path):
        raise Exception("Input file not found")

    try:
        df = pd.read_csv(input_path)
    except Exception:
        raise Exception("Invalid CSV format")

    if df.empty:
        raise Exception("CSV file is empty")

    if "close" not in df.columns:
        raise Exception("Missing 'close' column")

    return df


# ---------------- MAIN FUNCTION ----------------
def main():
    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    # Setup logger
    setup_logger(args.log_file)

    start_time = time.time()

    try:
        logging.info("Job started")

        # ---- Load Config ----
        config = load_config(args.config)

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        np.random.seed(seed)

        logging.info(f"Config loaded: seed={seed}, window={window}, version={version}")

        # ---- Load Data ----
        df = load_data(args.input)

        logging.info(f"Rows loaded: {len(df)}")

        # ---- Rolling Mean ----
        logging.info("Computing rolling mean")
        df["rolling_mean"] = df["close"].rolling(window=window).mean()

        # ---- Signal Generation ----
        logging.info("Generating signal")
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)

        # ---- Handle NaN ----
        df = df.dropna()

        # ---- Metrics ----
        rows_processed = len(df)
        signal_rate = df["signal"].mean()
        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }

        logging.info(f"Metrics summary: {metrics}")
        logging.info("Job completed successfully")

        # Write output
        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=4)

        # Print to stdout (important for Docker)
        print(json.dumps(metrics, indent=4))

        sys.exit(0)

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        # Write error output
        with open(args.output, "w") as f:
            json.dump(error_metrics, f, indent=4)

        print(json.dumps(error_metrics, indent=4))

        sys.exit(1)


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()