#!/usr/bin/env python3
"""
DefectDojo Finding Threshold Checker

This script checks findings from DefectDojo API and fails if thresholds are exceeded:
- More than 10 medium severity findings
- More than 2 high severity findings
- Any critical severity findings
- False positives are excluded from the count

Usage:
  python defectdojo_threshold_check.py --url <defectdojo_url> --api-key <api_key> [--product <product_id>]
"""

import requests
import argparse
import sys
import logging
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Check DefectDojo findings against thresholds')
    parser.add_argument('--url', required=True, help='DefectDojo API URL (e.g., https://defectdojo.example.com)')
    parser.add_argument('--api-key', required=True, help='DefectDojo API key')
    parser.add_argument('--product', type=int, help='Product ID to filter findings')
    return parser.parse_args()

def get_findings(base_url, api_key, product_id=None):
    """Retrieve findings from DefectDojo API"""
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Define API endpoint
    api_endpoint = urljoin(base_url, '/api/v2/findings/')
    
    # Set up query parameters
    params = {
        'limit': 1000,  # Adjust as needed
        'false_p': False,  # Exclude false positives
    }
    
    # Add product filter if specified
    if product_id:
        params['test__engagement__product'] = product_id
    
    # Make the API request
    try:
        response = requests.get(api_endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching findings: {e}")
        sys.exit(1)

def check_thresholds(findings_data):
    """Check findings against defined thresholds"""
    # Initialize counters
    critical_count = 0
    high_count = 0
    medium_count = 0
    
    # Process findings and count by severity
    for finding in findings_data.get('results', []):
        severity = finding.get('severity', '').lower()
        
        # Skip false positives
        if finding.get('false_p', False):
            continue
            
        # Count by severity
        if severity == 'critical':
            critical_count += 1
        elif severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
    
    # Report counts
    logger.info(f"Found {critical_count} critical findings")
    logger.info(f"Found {high_count} high findings")
    logger.info(f"Found {medium_count} medium findings")
    
    # Check against thresholds
    failed = False
    failure_reasons = []
    
    if critical_count > 0:
        failure_reasons.append(f"Found {critical_count} critical findings (threshold: 0)")
        failed = True
        
    if high_count > 2:
        failure_reasons.append(f"Found {high_count} high findings (threshold: 2)")
        failed = True
        
    if medium_count > 10:
        failure_reasons.append(f"Found {medium_count} medium findings (threshold: 10)")
        failed = True
    
    return failed, failure_reasons

def main():
    args = parse_arguments()
    
    # Get findings from DefectDojo
    logger.info(f"Fetching findings from DefectDojo API at {args.url}")
    findings_data = get_findings(args.url, args.api_key, args.product)
    
    # Check thresholds
    failed, reasons = check_thresholds(findings_data)
    
    # Output results
    if failed:
        logger.error("Pipeline check FAILED due to the following reasons:")
        for reason in reasons:
            logger.error(f"- {reason}")
        sys.exit(1)
    else:
        logger.info("Pipeline check PASSED - all thresholds are satisfied")
        sys.exit(0)

if __name__ == "__main__":
    main()