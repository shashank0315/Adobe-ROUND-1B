#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import os
from pathlib import Path

class ComprehensiveDocumentAnalysisTest:
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

    def test_full_pdf_analysis(self):
        """Test the complete PDF analysis workflow"""
        try:
            # Prepare the PDF file
            pdf_path = "/app/challenge_data/Collection 1/PDFs/South of France - Cities.pdf"
            
            if not os.path.exists(pdf_path):
                self.log_test("PDF Analysis - File Check", False, f"PDF file not found: {pdf_path}")
                return False
            
            # Prepare analysis request
            analysis_request = {
                "challenge_info": {
                    "challenge_id": "round_1b_001",
                    "test_case_name": "travel_planning_test",
                    "description": "Travel Planning Analysis Test"
                },
                "documents": [
                    {
                        "filename": "South of France - Cities.pdf",
                        "title": "South of France Cities Guide"
                    }
                ],
                "persona": {
                    "role": "Travel Planner"
                },
                "job_to_be_done": {
                    "task": "Plan a trip of 4 days for a group of 10 college friends"
                }
            }
            
            # Prepare multipart form data
            files = {
                'files': ('South of France - Cities.pdf', open(pdf_path, 'rb'), 'application/pdf')
            }
            
            data = {
                'analysis_request': json.dumps(analysis_request)
            }
            
            print("📤 Sending PDF analysis request...")
            response = requests.post(
                f"{self.base_url}/analyze",
                files=files,
                data=data,
                timeout=60  # Allow up to 60 seconds for analysis
            )
            
            # Close the file
            files['files'][1].close()
            
            success = response.status_code == 200
            
            if success:
                result = response.json()
                
                # Validate response structure
                required_keys = ['id', 'result', 'created_at']
                has_required_keys = all(key in result for key in required_keys)
                
                if not has_required_keys:
                    self.log_test("PDF Analysis - Response Structure", False, f"Missing keys in response: {list(result.keys())}")
                    return False
                
                # Validate result structure
                result_data = result['result']
                required_result_keys = ['metadata', 'extracted_sections', 'subsection_analysis']
                has_result_keys = all(key in result_data for key in required_result_keys)
                
                if not has_result_keys:
                    self.log_test("PDF Analysis - Result Structure", False, f"Missing keys in result: {list(result_data.keys())}")
                    return False
                
                # Validate metadata
                metadata = result_data['metadata']
                required_metadata_keys = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
                has_metadata_keys = all(key in metadata for key in required_metadata_keys)
                
                if not has_metadata_keys:
                    self.log_test("PDF Analysis - Metadata Structure", False, f"Missing metadata keys: {list(metadata.keys())}")
                    return False
                
                # Check content quality
                extracted_sections = result_data['extracted_sections']
                subsection_analysis = result_data['subsection_analysis']
                
                has_sections = len(extracted_sections) > 0
                has_subsections = len(subsection_analysis) > 0
                
                if not has_sections:
                    self.log_test("PDF Analysis - Content Quality", False, "No extracted sections found")
                    return False
                
                if not has_subsections:
                    self.log_test("PDF Analysis - Content Quality", False, "No subsection analysis found")
                    return False
                
                # Validate section structure
                first_section = extracted_sections[0]
                required_section_keys = ['document', 'section_title', 'importance_rank', 'page_number']
                has_section_keys = all(key in first_section for key in required_section_keys)
                
                if not has_section_keys:
                    self.log_test("PDF Analysis - Section Structure", False, f"Missing section keys: {list(first_section.keys())}")
                    return False
                
                # Validate subsection structure
                first_subsection = subsection_analysis[0]
                required_subsection_keys = ['document', 'refined_text', 'page_number']
                has_subsection_keys = all(key in first_subsection for key in required_subsection_keys)
                
                if not has_subsection_keys:
                    self.log_test("PDF Analysis - Subsection Structure", False, f"Missing subsection keys: {list(first_subsection.keys())}")
                    return False
                
                self.log_test("PDF Analysis - Complete Workflow", True, 
                             f"Successfully analyzed PDF with {len(extracted_sections)} sections and {len(subsection_analysis)} subsections")
                return True
                
            else:
                self.log_test("PDF Analysis - API Response", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PDF Analysis - Exception", False, f"Error: {str(e)}")
            return False

    def test_analysis_retrieval(self, analysis_id):
        """Test retrieving a specific analysis result"""
        try:
            response = requests.get(f"{self.base_url}/analysis/{analysis_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                retrieved_id = data.get('id')
                self.log_test("Analysis Retrieval", True, f"Retrieved analysis: {retrieved_id}")
            else:
                self.log_test("Analysis Retrieval", False, f"Status code: {response.status_code}")
                
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test("Analysis Retrieval", False, f"Connection error: {e}")
            return False

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Document Analysis Tests")
        print("=" * 60)
        
        # Test PDF analysis workflow
        pdf_success = self.test_full_pdf_analysis()
        
        # If PDF analysis succeeded, test retrieval
        if pdf_success:
            # This would require storing the analysis ID from the previous test
            # For now, we'll skip this test
            pass
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All comprehensive tests passed!")
            return True
        else:
            print("⚠️  Some comprehensive tests failed")
            return False

def main():
    """Main function to run comprehensive tests"""
    test_suite = ComprehensiveDocumentAnalysisTest()
    success = test_suite.run_comprehensive_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()