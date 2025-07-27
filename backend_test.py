#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import os
from pathlib import Path

class BackendTestSuite:
    def __init__(self):
        # Use local development server
        self.base_url = "http://localhost:8000/api"
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details and success:
            print(f"   Details: {details}")

    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", False, f"Connection error: {e}")
            return False

    def test_collections_endpoint(self):
        """Test the collections endpoint"""
        try:
            response = requests.get(f"{self.base_url}/collections", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                collections_count = len(data.get('collections', []))
                self.log_test("Collections Endpoint", True, f"Found {collections_count} collections")
            else:
                self.log_test("Collections Endpoint", False, f"Status code: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test("Collections Endpoint", False, f"Connection error: {e}")
            return False

    def test_analysis_list_endpoint(self):
        """Test the analysis list endpoint"""
        try:
            response = requests.get(f"{self.base_url}/analysis", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                analyses_count = len(data.get('analyses', []))
                self.log_test("Analysis List Endpoint", True, f"Found {analyses_count} analyses")
            else:
                self.log_test("Analysis List Endpoint", False, f"Status code: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test("Analysis List Endpoint", False, f"Connection error: {e}")
            return False

    def test_single_analysis_endpoint(self):
        """Test retrieving a single analysis"""
        try:
            # First get the list of analyses
            list_response = requests.get(f"{self.base_url}/analysis", timeout=10)
            if list_response.status_code != 200:
                self.log_test("Single Analysis Endpoint", False, "Could not get analysis list")
                return False
            
            analyses = list_response.json().get('analyses', [])
            if not analyses:
                self.log_test("Single Analysis Endpoint", True, "No analyses to test")
                return True
            
            # Test with the first analysis ID
            first_analysis_id = analyses[0].get('id')
            if not first_analysis_id:
                self.log_test("Single Analysis Endpoint", False, "No valid analysis ID found")
                return False
            
            response = requests.get(f"{self.base_url}/analysis/{first_analysis_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                analysis_id = data.get('id')
                self.log_test("Single Analysis Endpoint", True, f"Retrieved analysis: {analysis_id}")
            else:
                self.log_test("Single Analysis Endpoint", False, f"Status code: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test("Single Analysis Endpoint", False, f"Connection error: {e}")
            return False

    def run_backend_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend Test Suite")
        print("=" * 50)
        
        # Test basic endpoints
        self.test_health_check()
        self.test_collections_endpoint()
        self.test_analysis_list_endpoint()
        self.test_single_analysis_endpoint()
        
        # Print summary
        print("=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print("⚠️  Some backend tests failed")
            return False

def main():
    """Main function to run backend tests"""
    test_suite = BackendTestSuite()
    success = test_suite.run_backend_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()