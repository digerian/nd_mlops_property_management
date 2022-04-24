#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
Add docstrings and the proper type to all parameters, both in the script and in the MLproject file.
import argparse
import logging
import wandb
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    """
    executing the basic cleaning
    """
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    df = pd.read_csv(artifact_path, low_memory=False)

    # Drop the duplicates
    logger.info("Dropping duplicates")
    df = df.drop_duplicates().reset_index(drop=True)

    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    filename = "clean_sample.csv"
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type of output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="minimum price for apartment",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="maximum price for apartment",
        required=True
    )

    args = parser.parse_args()

    go(args)
