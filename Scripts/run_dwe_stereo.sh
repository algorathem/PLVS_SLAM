#!/usr/bin/env bash

# ---------------------------------------------------------
# DWE Stereo Run Script for Custom Dataset
# ---------------------------------------------------------

SUFFIX="_old"               # Example binaries suffix
DWE_YAML="dwe.yaml" # Make sure this exists and is configured for your cameras
SEQUENCE="Kevin_Dataset"    # Label for your dataset/output

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
PATH_TO_SEQUENCE_FOLDER="$HOME/Downloads/Kevin_dataset"
OUTPUT_BASE_NAME="dataset_${SEQUENCE}_stereo"

echo "PATH_TO_SEQUENCE_FOLDER: $PATH_TO_SEQUENCE_FOLDER"
echo "OUTPUT_BASE_NAME: $OUTPUT_BASE_NAME"

# ---------------------------------------------------------
# Fix CSVs for DWE (only keep first column, no commas)
# ---------------------------------------------------------
for CAM in cam0 cam1; do
    CSV="$PATH_TO_SEQUENCE_FOLDER/mav0/$CAM/data.csv"
    echo "Fixing CSV for $CAM: $CSV"
    cut -d',' -f1 "$CSV" > "$CSV.tmp" && mv "$CSV.tmp" "$CSV"
done

# ---------------------------------------------------------
# Run DWE stereo
# ---------------------------------------------------------
$DEBUG_PREFIX ../Examples$SUFFIX/Stereo/stereo_euroc$SUFFIX \
    ../Vocabulary/ORBvoc.txt \
    ../Examples$SUFFIX/Stereo/$DWE_YAML \
    $PATH_TO_SEQUENCE_FOLDER \
    $PATH_TO_SEQUENCE_FOLDER/mav0/cam0/data.csv \
    $OUTPUT_BASE_NAME

# ---------------------------------------------------------
# Evaluation (optional, if you have ground truth)
# ---------------------------------------------------------
# python3 evaluate_ate_scale.py ... # Uncomment if GT exists

# ---------------------------------------------------------
# Move output to results folder
# ---------------------------------------------------------
./move_output_to_results.sh $OUTPUT_BASE_NAME
