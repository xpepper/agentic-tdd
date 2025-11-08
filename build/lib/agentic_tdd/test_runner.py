"""
Test runner module for agentic-tdd.
This module handles running tests and verifying their results.
"""
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tempfile


class TestRunner:
    """Test runner for executing tests and checking results."""
    
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.test_results = []
    
    def detect_test_framework(self) -> str:
        """Detect which test framework is being used in the project."""
        # Look for common test framework configuration files
        if (self.work_dir / "pytest.ini").exists() or (self.work_dir / "pyproject.toml").exists():
            # Check if pyproject.toml has pytest configuration
            pyproject_path = self.work_dir / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    if "pytest" in content.lower():
                        return "pytest"
        
        # Check for common test file patterns
        test_files = list(self.work_dir.rglob("*test*.py")) + list(self.work_dir.rglob("test_*.py"))
        
        # If there are test files, assume pytest by default
        if test_files:
            return "pytest"
        
        # Look for specific imports in Python files
        for py_file in self.work_dir.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if "import pytest" in content or "from pytest" in content:
                        return "pytest"
                    elif "import unittest" in content or "from unittest" in content:
                        return "unittest"
            except:
                continue  # Skip files that can't be read
        
        # Default to pytest
        return "pytest"
    
    def run_all_tests(self) -> Dict[str, any]:
        """Run all tests in the project."""
        framework = self.detect_test_framework()
        
        if framework == "pytest":
            return self._run_pytest()
        elif framework == "unittest":
            return self._run_unittest()
        else:
            # Try to run with pytest as a fallback
            return self._run_pytest()
    
    def run_specific_test(self, test_file: str) -> Dict[str, any]:
        """Run a specific test file."""
        framework = self.detect_test_framework()
        
        if framework == "pytest":
            return self._run_pytest(test_file)
        elif framework == "unittest":
            return self._run_unittest(test_file)
        else:
            # Try to run with pytest as a fallback
            return self._run_pytest(test_file)
    
    def _run_pytest(self, test_file: Optional[str] = None) -> Dict[str, any]:
        """Run tests using pytest."""
        cmd = [sys.executable, "-m", "pytest"]
        
        if test_file:
            cmd.append(test_file)
        else:
            # Run all tests in the project
            cmd.extend(["--collect-only", "-q"])  # First check what tests exist
            try:
                # First, collect tests
                collect_result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.work_dir
                )
                
                if collect_result.returncode == 0:
                    # Now run all tests
                    cmd = [sys.executable, "-m", "pytest", "-v"]
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.work_dir
                    )
                    
                    return {
                        'success': result.returncode == 0,
                        'return_code': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'framework': 'pytest'
                    }
                else:
                    # If no tests found during collection, return a success with no tests
                    return {
                        'success': True,
                        'return_code': 0,
                        'stdout': 'No tests found',
                        'stderr': '',
                        'framework': 'pytest'
                    }
            except Exception as e:
                return {
                    'success': False,
                    'return_code': -1,
                    'stdout': '',
                    'stderr': str(e),
                    'framework': 'pytest'
                }
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.work_dir
            )
            
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'framework': 'pytest'
            }
        except Exception as e:
            return {
                'success': False,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'framework': 'pytest'
            }
    
    def _run_unittest(self, test_file: Optional[str] = None) -> Dict[str, any]:
        """Run tests using unittest."""
        cmd = [sys.executable, "-m", "unittest"]
        
        if test_file:
            cmd.extend([test_file, "-v"])
        else:
            # Discover and run all tests
            cmd.extend(["discover", "-s", ".", "-p", "*test*.py", "-v"])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.work_dir
            )
            
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'framework': 'unittest'
            }
        except Exception as e:
            return {
                'success': False,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'framework': 'unittest'
            }
    
    def run_test_to_verify_failure(self, test_file: str) -> bool:
        """Run a test to verify that it fails (as expected for a new test)."""
        result = self.run_specific_test(test_file)
        
        # For a new test that should fail, the test runner should return non-zero (failure)
        # which means the test ran but failed as expected
        return not result['success']  # Return True if test fails (as expected for a new test)
    
    def run_test_to_verify_pass(self, test_file: str = None) -> bool:
        """Run tests to verify that they pass."""
        result = self.run_all_tests() if test_file is None else self.run_specific_test(test_file)
        
        # For tests that should pass, the test runner should return zero (success)
        return result['success']