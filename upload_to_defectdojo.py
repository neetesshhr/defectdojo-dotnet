#!/usr/bin/env python3
"""
DefectDojo Import Scan

A simple script for importing scan reports to DefectDojo.
"""

import argparse
import logging
import os
import sys
import requests


def setup_logger(debug=False):
    """Set up the logger."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("defect_dojo_import")


def import_scan(api_key, host, scan_file, scan_type, verify_ssl=True, debug=False, **kwargs):
    """
    Import a scan report to DefectDojo.
    
    Args:
        api_key (str): DefectDojo API key
        host (str): DefectDojo host URL (e.g., https://defectdojo.example.com)
        scan_file (str): Path to the scan report file
        scan_type (str): Type of scan report (e.g., "ZAP Scan")
        verify_ssl (bool): Whether to verify SSL certificates
        debug (bool): Enable debug logging
        **kwargs: Additional parameters for the import-scan API
        
    Returns:
        dict: Response from the API
    """
    logger = setup_logger(debug)
    
    host = host.rstrip('/')
    
    if not os.path.isfile(scan_file):
        logger.error(f"Scan file not found: {scan_file}")
        return None
    
    # Prepare data
    data = {
        'scan_type': scan_type,
        'active': kwargs.get('active', True),
        'verified': kwargs.get('verified', False),
        'close_old_findings': kwargs.get('close_old_findings', False),
        'push_to_jira': kwargs.get('push_to_jira', False),
    }
    
    # Add optional parameters based on ID approach or Name approach
    if kwargs.get('engagement'):
        data['engagement'] = kwargs.get('engagement')
    else:
        # Using the Name approach
        if kwargs.get('product_name'):
            data['product_name'] = kwargs.get('product_name')
        if kwargs.get('engagement_name'):
            data['engagement_name'] = kwargs.get('engagement_name')
        if kwargs.get('product_type_name'):
            data['product_type_name'] = kwargs.get('product_type_name')
        if kwargs.get('auto_create_context'):
            data['auto_create_context'] = kwargs.get('auto_create_context')
        if kwargs.get('deduplication_on_engagement'):
            data['deduplication_on_engagement'] = kwargs.get('deduplication_on_engagement')
    
    # Add other optional parameters
    if kwargs.get('scan_date'):
        data['scan_date'] = kwargs.get('scan_date')
    if kwargs.get('minimum_severity'):
        data['minimum_severity'] = kwargs.get('minimum_severity')
    if kwargs.get('endpoint_to_add'):
        data['endpoint_to_add'] = kwargs.get('endpoint_to_add')
    if kwargs.get('test_title'):
        data['test_title'] = kwargs.get('test_title')
    if kwargs.get('build_id'):
        data['build_id'] = kwargs.get('build_id')
    if kwargs.get('branch_tag'):
        data['branch_tag'] = kwargs.get('branch_tag')
    if kwargs.get('commit_hash'):
        data['commit_hash'] = kwargs.get('commit_hash')
    if kwargs.get('tags'):
        data['tags'] = kwargs.get('tags')
    if kwargs.get('environment'):
        data['environment'] = kwargs.get('environment')
    if kwargs.get('version'):
        data['version'] = kwargs.get('version')
    if kwargs.get('service'):
        data['service'] = kwargs.get('service')
    if kwargs.get('source_code_management_uri'):
        data['source_code_management_uri'] = kwargs.get('source_code_management_uri')
    
    # When using engagement name approach, we might need these
    if kwargs.get('engagement_end_date'):
        data['engagement_end_date'] = kwargs.get('engagement_end_date')
    if kwargs.get('lead'):
        data['lead'] = kwargs.get('lead')
    
    logger.info(f"Importing scan from {scan_file} with scan type: {scan_type}")
    if debug:
        logger.debug(f"Import parameters: {data}")
    
    # Upload the scan
    with open(scan_file, 'rb') as f:
        files = {'file': f}
        
        headers = {'Authorization': f'Token {api_key}'}
        
        endpoint = f"{host}/api/v2/import-scan/"
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=data,
                files=files,
                verify=verify_ssl
            )
            
            if debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response content: {response.text}")
            
            if response.status_code in [200, 201]:
                logger.info("Successfully imported the scan")
                return response.json()
            else:
                logger.error(f"Failed to import scan: {response.status_code} {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during API request: {str(e)}")
            return None


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Import a scan report to DefectDojo')
    
    # Required arguments
    parser.add_argument('--api-key', required=True, help='DefectDojo API key')
    parser.add_argument('--host', required=True, help='DefectDojo host URL')
    parser.add_argument('--file', required=True, help='Path to the scan report file')
    parser.add_argument('--scan-type', required=True, help='Type of scan report (e.g., "ZAP Scan")')
    
    # Identification approach - either by ID or by name
    id_group = parser.add_argument_group('ID Approach', 'Identify where to import using IDs')
    id_group.add_argument('--engagement', type=int, help='ID of the engagement')
    
    name_group = parser.add_argument_group('Name Approach', 'Identify where to import using names')
    name_group.add_argument('--product-name', help='Name of the product')
    name_group.add_argument('--engagement-name', help='Name of the engagement')
    name_group.add_argument('--product-type-name', help='Name of the product type')
    name_group.add_argument('--auto-create-context', action='store_true', help='Auto create engagements/products/product types')
    name_group.add_argument('--deduplication-on-engagement', action='store_true', help='Restrict deduplication to the engagement')
    
    # Optional parameters
    opt_group = parser.add_argument_group('Optional Parameters', 'Additional options for the import')
    opt_group.add_argument('--scan-date', help='Scan completion date (YYYY-MM-DD)')
    opt_group.add_argument('--minimum-severity', choices=['Info', 'Low', 'Medium', 'High', 'Critical'], help='Minimum severity level to be imported')
    opt_group.add_argument('--active', action='store_true', default=True, help='Force findings to be active')
    opt_group.add_argument('--verified', action='store_true', help='Force findings to be verified')
    opt_group.add_argument('--endpoint-to-add', type=int, help='ID of an endpoint to associate with findings')
    opt_group.add_argument('--test-title', help='Title for the test')
    opt_group.add_argument('--build-id', help='ID of the build that was scanned')
    opt_group.add_argument('--branch-tag', help='Branch or tag that was scanned')
    opt_group.add_argument('--commit-hash', help='Commit that was scanned')
    opt_group.add_argument('--environment', help='Environment (e.g., Development, Production)')
    opt_group.add_argument('--version', help='Version that was scanned')
    opt_group.add_argument('--service', help='Service within the product')
    opt_group.add_argument('--source-code-management-uri', help='Link to source code')
    opt_group.add_argument('--tags', nargs='+', help='Tags to apply to the findings')
    opt_group.add_argument('--close-old-findings', action='store_true', help='Close old findings not in the report')
    opt_group.add_argument('--lead', type=int, help='ID of the user who is the lead for this test')
    opt_group.add_argument('--engagement-end-date', help='End Date for auto-created Engagement (YYYY-MM-DD)')
    
    # Connection options
    conn_group = parser.add_argument_group('Connection Options', 'Options for the API connection')
    conn_group.add_argument('--no-verify-ssl', action='store_false', dest='verify_ssl', default=True, help='Do not verify SSL certificates')
    conn_group.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Check for required fields based on the approach
    if not args.engagement and not args.product_name:
        print("Error: Either --engagement or --product-name must be provided", file=sys.stderr)
        sys.exit(1)
    
    if args.product_name and not args.engagement_name and not args.auto_create_context:
        print("Warning: When using --product-name, you should also provide --engagement-name or --auto-create-context", file=sys.stderr)
    
    # Convert args to a dictionary for kwargs
    kwargs = vars(args)
    
    # Remove the arguments we'll pass directly
    file_path = kwargs.pop('file')
    api_key = kwargs.pop('api_key')
    host = kwargs.pop('host')
    scan_type = kwargs.pop('scan_type')
    verify_ssl = kwargs.pop('verify_ssl')
    debug = kwargs.pop('debug')
    
    result = import_scan(
        api_key=api_key,
        host=host,
        scan_file=file_path,
        scan_type=scan_type,
        verify_ssl=verify_ssl,
        debug=debug,
        **kwargs
    )
    
    if result:
        print("Scan import successful!")
        print(f"Test ID: {result.get('test', 'Unknown')}")
        print(f"Finding count: {result.get('finding_count', 0)}")
        sys.exit(0)
    else:
        print("Scan import failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()