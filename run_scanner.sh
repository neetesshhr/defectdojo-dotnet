#!/bin/bash

# Run the patched DefectDojo scanner script
python patch_defectdojo.py
python scanner.py "$@"