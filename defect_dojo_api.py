#!/usr/bin/env python3
"""
DefectDojo API Integration for CI/CD Pipelines

This module provides functionality to upload security scan reports to DefectDojo from CI/CD pipelines.
"""

import os
import sys
import json
import argparse
import logging
import datetime
import requests
from pathlib import Path


class DefectDojoAPI:
    """Class to interact with the DefectDojo API and manage test results in CI/CD pipelines."""

    def __init__(self, api_key=None, host=None, verify_ssl=True, debug=False):
        """
        Initialize the DefectDojo API client.

        Args:
            api_key (str): DefectDojo API key
            host (str): DefectDojo host URL (e.g., https://defectdojo.example.com)
            verify_ssl (bool): Whether to verify SSL certificates
            debug (bool): Enable debug logging
        """
        self.api_key = api_key
        self.host = host.rstrip('/') if host else None
        self.verify_ssl = verify_ssl
        
        # Set up logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("DefectDojoAPI")
        
        # Validate required parameters
        if not self.api_key or not self.host:
            self.logger.error("API key and host are required")
            raise ValueError("API key and host are required")
            
        # Setup request headers
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test connection
        self.test_connection()

    def test_connection(self):
        """Test the connection to the DefectDojo instance."""
        try:
            response = requests.get(
                f"{self.host}/api/v2/users/",
                headers=self.headers,
                verify=self.verify_ssl
            )
            if response.status_code == 200:
                self.logger.info(f"Successfully connected to DefectDojo at {self.host}")
            else:
                self.logger.error(f"Failed to connect to DefectDojo: {response.status_code} {response.text}")
                raise ConnectionError(f"Failed to connect to DefectDojo: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise ConnectionError(f"Connection error: {str(e)}")

    def get_environments(self):
        """
        Get a list of available test environments.
        
        Returns:
            list: Available environments
        """
        response = requests.get(
            f"{self.host}/api/v2/development_environments/",
            headers=self.headers,
            verify=self.verify_ssl
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'results' in data:
                    return data['results']
                return data
            except json.JSONDecodeError:
                self.logger.error("Failed to parse environments response as JSON")
                return []
        else:
            self.logger.error(f"Failed to retrieve environments: {response.status_code} {response.text}")
            return []

    def get_environment_id(self, environment_name_or_id):
        """
        Get environment ID from name or ID
        
        Args:
            environment_name_or_id (str): Environment name or ID
            
        Returns:
            int: Environment ID or None if not found
        """
        # If it's already an integer, return it
        if isinstance(environment_name_or_id, int) or (isinstance(environment_name_or_id, str) and environment_name_or_id.isdigit()):
            return int(environment_name_or_id)
            
        # Otherwise, look up by name
        environments = self.get_environments()
        for env in environments:
            if env.get('name', '').lower() == environment_name_or_id.lower():
                return env.get('id')
                
        # If not found, let's get the default environment ID if available
        if environments and len(environments) > 0:
            self.logger.warning(f"Environment '{environment_name_or_id}' not found. Using first available environment: {environments[0].get('name')} (ID: {environments[0].get('id')})")
            return environments[0].get('id')
            
        return None

    def get_engagement(self, engagement_id):
        """
        Retrieve engagement details by ID.
        
        Args:
            engagement_id (int): The ID of the engagement
            
        Returns:
            dict: Engagement details
        """
        self.logger.info(f"Retrieving engagement with ID: {engagement_id}")
        response = requests.get(
            f"{self.host}/api/v2/engagements/{engagement_id}/",
            headers=self.headers,
            verify=self.verify_ssl
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error(f"Failed to retrieve engagement: {response.status_code} {response.text}")
            return None

    def get_product_from_engagement(self, engagement_id):
        """
        Get product ID from engagement ID.
        
        Args:
            engagement_id (int): ID of the engagement
            
        Returns:
            int: ID of the product or None if not found
        """
        engagement = self.get_engagement(engagement_id)
        if engagement and 'product' in engagement:
            return engagement['product']
        return None

    def get_product(self, product_id):
        """
        Retrieve product details by ID.
        
        Args:
            product_id (int): The ID of the product
            
        Returns:
            dict: Product details
        """
        self.logger.info(f"Retrieving product with ID: {product_id}")
        response = requests.get(
            f"{self.host}/api/v2/products/{product_id}/",
            headers=self.headers,
            verify=self.verify_ssl
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error(f"Failed to retrieve product: {response.status_code} {response.text}")
            return None

    def get_test_types(self):
        """
        Get a list of available test types.
        
        Returns:
            list: Available test types
        """
        response = requests.get(
            f"{self.host}/api/v2/test_types/",
            headers=self.headers,
            verify=self.verify_ssl
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'results' in data:
                    return data['results']
                return data
            except json.JSONDecodeError:
                self.logger.error("Failed to parse test types response as JSON")
                return []
        else:
            self.logger.error(f"Failed to retrieve test types: {response.status_code} {response.text}")
            return []

    def _get_test_type_id(self, test_type_name):
        """
        Get test type ID from its name
        
        Args:
            test_type_name (str): Name of the test type
            
        Returns:
            int: ID of the test type or None if not found
        """
        test_types = self.get_test_types()
        for test_type in test_types:
            if test_type['name'].lower() == test_type_name.lower():
                return test_type['id']
        return None

    def get_scan_types(self):
        """
        Get a list of supported scan types.
        
        Returns:
            list: Supported scan types
        """
        # Try the v2 API endpoint
        endpoints = [
            "/api/v2/import-scan-info/",  # Standard endpoint
            "/api/v2/scan_type_info/",    # Alternative endpoint sometimes used
            "/api/v2/test-types/"         # Fallback endpoint
        ]
        
        for endpoint in endpoints:
            try:
                self.logger.info(f"Trying to get scan types from endpoint: {endpoint}")
                response = requests.get(
                    f"{self.host}{endpoint}",
                    headers=self.headers,
                    verify=self.verify_ssl
                )
                
                if response.status_code == 200:
                    scan_types = []
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, list):
                        for item in data:
                            if 'scan_type_name' in item:
                                scan_types.append(item['scan_type_name'])
                            elif 'name' in item:
                                scan_types.append(item['name'])
                    elif 'results' in data:
                        for item in data['results']:
                            if 'scan_type_name' in item:
                                scan_types.append(item['scan_type_name'])
                            elif 'name' in item:
                                scan_types.append(item['name'])
                    
                    if scan_types:
                        self.logger.info(f"Successfully retrieved {len(scan_types)} scan types from {endpoint}")
                        return scan_types
                else:
                    self.logger.warning(f"Failed to retrieve scan types from {endpoint}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Error accessing {endpoint}: {str(e)}")
        
        # If we get here, all endpoints failed
        self.logger.error("Failed to retrieve scan types from all endpoints")
        
        # Try to fetch directly from DefectDojo's swagger documentation to help the user
        try:
            self.logger.info("Attempting to extract information from Swagger UI...")
            response = requests.get(
                f"{self.host}/api/v2/oa3/swagger-ui/",
                verify=self.verify_ssl
            )
            if response.status_code == 200:
                self.logger.info("Successfully accessed Swagger UI. Please check the API documentation manually.")
        except:
            pass
            
        return []

    def create_test(self, engagement_id, test_type, environment, target_start, target_end=None, title=None, notes=None):
        """
        Create a new test in DefectDojo.
        
        Args:
            engagement_id (int): The ID of the engagement
            test_type (str or int): Type of the test (name or ID)
            environment (str or int): Test environment (name or ID)
            target_start (str): Start date in YYYY-MM-DD format
            target_end (str, optional): End date in YYYY-MM-DD format
            title (str, optional): Test title
            notes (str or list, optional): Additional notes
            
        Returns:
            dict: Created test details
        """
        if not target_end:
            target_end = target_start
            
        if not title:
            title = f"{test_type} test on {target_start}"
        
        # If test_type is a string (name), get its ID
        if isinstance(test_type, str) and not test_type.isdigit():
            test_type_id = self._get_test_type_id(test_type)
            if not test_type_id:
                self.logger.error(f"Test type '{test_type}' not found")
                return None
        else:
            test_type_id = test_type
        
        # Handle environment (could be name or ID)
        environment_id = self.get_environment_id(environment)
        if not environment_id:
            self.logger.error(f"Environment '{environment}' not found and no default available")
            return None
            
        # Create the test without notes for now
        data = {
            "engagement": engagement_id,
            "test_type": test_type_id,
            "environment": environment_id,
            "target_start": target_start,
            "target_end": target_end,
            "title": title
        }
            
        self.logger.info(f"Creating new test: {title}")
        self.logger.debug(f"Test creation data: {json.dumps(data)}")
        
        response = requests.post(
            f"{self.host}/api/v2/tests/",
            headers=self.headers,
            data=json.dumps(data),
            verify=self.verify_ssl
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            self.logger.error(f"Failed to create test: {response.status_code} {response.text}")
            return None

    def upload_findings(self, test_id, report_file, scan_type, close_old_findings=False, push_to_jira=False, 
                        engagement_id=None, product_id=None, product_name=None):
        """
        Upload a test report file with findings.
        
        Args:
            test_id (int): The ID of the test
            report_file (str): Path to the report file
            scan_type (str): Type of scan report
            close_old_findings (bool): Whether to close old findings
            push_to_jira (bool): Whether to push findings to JIRA
            engagement_id (int, optional): The ID of the engagement (for product lookup)
            product_id (int, optional): The ID of the product to associate with the findings
            product_name (str, optional): The name of the product to associate with the findings
            
        Returns:
            dict: Import details
        """
        self.logger.info(f"Uploading findings from file: {report_file} with scan type: {scan_type}")
        
        if not os.path.isfile(report_file):
            self.logger.error(f"Report file not found: {report_file}")
            return None
        
        # Skip scan type verification since the API endpoint might not be available
        # Just proceed with the upload and let the server decide if the scan type is valid
        
        # Get product info from engagement if available and not explicitly provided
        if engagement_id and not product_id and not product_name:
            product_id = self.get_product_from_engagement(engagement_id)
            if product_id:
                product = self.get_product(product_id)
                if product and 'name' in product:
                    product_name = product['name']
            
        with open(report_file, 'rb') as f:
            files = {'file': f}
            data = {
                'scan_type': scan_type,
                'test': test_id,
                'active': True,
                'verified': False,
                'close_old_findings': close_old_findings,
                'push_to_jira': push_to_jira
            }
            
            # Add product information if available
            if product_id:
                data['product_id'] = product_id
            
            if product_name:
                data['product_name'] = product_name
                
            # Try import-scan endpoint with additional debugging
            try:
                endpoint = f"{self.host}/api/v2/import-scan/"
                self.logger.info(f"Trying to upload to: {endpoint}")
                self.logger.debug(f"Upload data: {data}")
                
                response = requests.post(
                    endpoint,
                    headers={'Authorization': f'Token {self.api_key}'},  # Content-Type is set by requests for multipart
                    data=data,
                    files=files,
                    verify=self.verify_ssl
                )
                
                self.logger.debug(f"Response status: {response.status_code}")
                self.logger.debug(f"Response content: {response.text}")
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"Successfully uploaded findings to {endpoint}")
                    return response.json()
                else:
                    self.logger.warning(f"Failed to upload to {endpoint}: {response.status_code} {response.text}")
                    
                    # If product_name is missing, try one more time with scan_type as product_name
                    if "product_name parameter missing" in response.text and not product_name:
                        self.logger.info(f"Trying again with scan_type as product_name")
                        data['product_name'] = scan_type
                        
                        # Reopen the file
                        with open(report_file, 'rb') as f2:
                            files = {'file': f2}
                            
                            retry_response = requests.post(
                                endpoint,
                                headers={'Authorization': f'Token {self.api_key}'},
                                data=data,
                                files=files,
                                verify=self.verify_ssl
                            )
                            
                            self.logger.debug(f"Retry response status: {retry_response.status_code}")
                            self.logger.debug(f"Retry response content: {retry_response.text}")
                            
                            if retry_response.status_code in [200, 201]:
                                self.logger.info(f"Successfully uploaded findings on retry")
                                return retry_response.json()
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Error uploading to {endpoint}: {str(e)}")
            
            self.logger.error("Failed to upload findings")
            return None

    def scan_and_import(self, engagement_id, test_type, report_file, scan_type, environment="Development", 
                      close_old_findings=False, push_to_jira=False, build_id=None, branch_name=None,
                      product_id=None, product_name=None):
        """
        Scan a report file and import findings into DefectDojo.
        
        Args:
            engagement_id (int): The ID of the engagement
            test_type (str): Type of the test
            report_file (str): Path to the report file
            scan_type (str): Type of scan report
            environment (str or int): Test environment (name or ID)
            close_old_findings (bool): Whether to close old findings
            push_to_jira (bool): Whether to push findings to JIRA
            build_id (str): CI/CD build ID
            branch_name (str): Git branch name
            product_id (int, optional): The ID of the product to associate with the findings
            product_name (str, optional): The name of the product to associate with the findings
            
        Returns:
            dict: Result of the operation
        """
        # Create a new test
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Create title with CI/CD info if available
        title = f"{test_type} scan"
        if build_id:
            title += f" - Build #{build_id}"
        if branch_name:
            title += f" - Branch: {branch_name}"
        
        # First create the test without notes
        test = self.create_test(
            engagement_id=engagement_id,
            test_type=test_type,
            environment=environment,
            target_start=today,
            title=title
        )
        
        if not test:
            return {'success': False, 'message': "Failed to create test"}
        
        # Upload findings
        import_result = self.upload_findings(
            test_id=test['id'],
            report_file=report_file,
            scan_type=scan_type,
            close_old_findings=close_old_findings,
            push_to_jira=push_to_jira,
            engagement_id=engagement_id,  # Pass engagement_id for product lookup
            product_id=product_id,
            product_name=product_name
        )
        
        if import_result:
            return {
                'success': True,
                'test_id': test['id'],
                'import_id': import_result['id'],
                'message': f"Successfully created test and imported findings",
                'test_title': test['title']
            }
        else:
            return {
                'success': False,
                'test_id': test['id'],
                'message': "Created test but failed to import findings"
            }


def main():
    """Main entry point for the command line tool."""
    parser = argparse.ArgumentParser(description='DefectDojo API Integration for CI/CD Pipelines')
    
    # Connection arguments (always required)
    parser.add_argument('--api-key', required=True, help='DefectDojo API key')
    parser.add_argument('--host', required=True, help='DefectDojo host URL')
    
    # Utility flags
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--list-scan-types', action='store_true', 
                        help='List all available scan types and exit')
    parser.add_argument('--list-test-types', action='store_true', 
                        help='List all available test types and exit')
    parser.add_argument('--list-environments', action='store_true', 
                        help='List all available environments and exit')
    
    # SSL verification options
    parser.add_argument('--verify-ssl', action='store_true', default=True, 
                        help='Verify SSL certificates')
    parser.add_argument('--no-verify-ssl', action='store_false', dest='verify_ssl',
                        help='Do not verify SSL certificates')
    
    # Import-specific arguments
    import_group = parser.add_argument_group('Import Arguments', 'Arguments required for importing scan results')
    import_group.add_argument('--report-file', help='Path to the test report file')
    import_group.add_argument('--scan-type', help='Type of security scan (e.g., ZAP Scan, Nessus Scan)')
    import_group.add_argument('--engagement-id', type=int, help='ID of the engagement')
    import_group.add_argument('--test-type', help='Type of the test')
    import_group.add_argument('--product-id', type=int, help='ID of the product (required by some DefectDojo installations)')
    import_group.add_argument('--product-name', help='Name of the product (required by some DefectDojo installations)')
    
    # Optional import arguments
    import_group.add_argument('--environment', default='Development', 
                        help='Test environment (name or ID)')
    import_group.add_argument('--build-id', help='CI/CD build ID')
    import_group.add_argument('--branch-name', help='Git branch name')
    import_group.add_argument('--close-old-findings', action='store_true', 
                        help='Close old findings for this test')
    import_group.add_argument('--push-to-jira', action='store_true', 
                        help='Push findings to JIRA')
    
    args = parser.parse_args()
    
    try:
        # Initialize the API client
        client = DefectDojoAPI(
            api_key=args.api_key,
            host=args.host,
            verify_ssl=args.verify_ssl,
            debug=args.debug
        )
        
        # Handle information listing options
        if args.list_scan_types:
            print("Retrieving available scan types...")
            scan_types = client.get_scan_types()
            print("Available scan types:")
            if scan_types:
                for scan_type in sorted(scan_types):
                    print(f"  - {scan_type}")
            else:
                print("  No scan types found or API endpoint returned no data.")
                print("  You may need to check the API endpoints in the DefectDojo swagger docs.")
                print(f"  Try visiting: {args.host}/api/v2/oa3/swagger-ui/")
            sys.exit(0)
            
        if args.list_test_types:
            print("Retrieving available test types...")
            test_types = client.get_test_types()
            print("Available test types:")
            if test_types:
                for test_type in sorted(test_types, key=lambda x: x['name']):
                    print(f"  - {test_type['name']} (ID: {test_type['id']})")
            else:
                print("  No test types found or API endpoint returned no data.")
                print("  You may need to check the API endpoints in the DefectDojo swagger docs.")
                print(f"  Try visiting: {args.host}/api/v2/oa3/swagger-ui/")
            sys.exit(0)
            
        if args.list_environments:
            print("Retrieving available environments...")
            environments = client.get_environments()
            print("Available environments:")
            if environments:
                for env in sorted(environments, key=lambda x: x['id']):
                    print(f"  - {env.get('name', 'Unknown')} (ID: {env.get('id')})")
            else:
                print("  No environments found or API endpoint returned no data.")
                print("  You may need to check the API endpoints in the DefectDojo swagger docs.")
                print(f"  Try visiting: {args.host}/api/v2/oa3/swagger-ui/")
            sys.exit(0)
        
        # Check if all required import arguments are provided
        if not all([args.report_file, args.scan_type, args.engagement_id, args.test_type]):
            parser.error("For importing scan results, the following arguments are required: --report-file, --scan-type, --engagement-id, --test-type")
        
        # Display additional information about the engagement/product
        if args.debug:
            # Get product information from engagement
            product_id = client.get_product_from_engagement(args.engagement_id)
            if product_id:
                product = client.get_product(product_id)
                if product and 'name' in product:
                    print(f"Found product: {product['name']} (ID: {product_id})")
                else:
                    print(f"Found product ID {product_id}, but could not retrieve details")
            else:
                print("Warning: Could not determine product from engagement")
        
        # Verify scan_type is valid
        scan_types = client.get_scan_types()
        if not scan_types:
            print("Warning: Could not retrieve scan types from API. Proceeding anyway.", file=sys.stderr)
        elif args.scan_type not in scan_types:
            print(f"Error: Invalid scan type '{args.scan_type}'", file=sys.stderr)
            print("Available scan types:", file=sys.stderr)
            for scan_type in sorted(scan_types):
                print(f"  - {scan_type}", file=sys.stderr)
            sys.exit(1)
        
        # Import the scan
        result = client.scan_and_import(
            engagement_id=args.engagement_id,
            test_type=args.test_type,
            report_file=args.report_file,
            scan_type=args.scan_type,
            environment=args.environment,
            close_old_findings=args.close_old_findings,
            push_to_jira=args.push_to_jira,
            build_id=args.build_id,
            branch_name=args.branch_name,
            product_id=args.product_id,
            product_name=args.product_name
        )
        
        if result['success']:
            print(json.dumps(result, indent=2))
            sys.exit(0)
        else:
            print(f"Error: {result['message']}", file=sys.stderr)
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()