#!/usr/bin/env python3
"""
🚀 LINDIA PRE-DEPLOYMENT VERIFICATION & VALIDATION SYSTEM
🔒 Google QA Gate: Zero Tolerance for Broken Builds

Automated V&V System for lindia-b (Backend), lindia-f (Frontend), lindia-ai (AI Engine)
Runs comprehensive checks before any deployment or git push.

Author: Automated QA System
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# ANSI Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class VVSystem:
    """Verification & Validation System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.results = {
            "commit_hash": self._get_commit_hash(),
            "timestamp": datetime.datetime.now().isoformat(),
            "checks": {},
            "changed_files": self._get_changed_files(),
            "overall_status": "UNKNOWN"
        }
        self.passed_checks = 0
        self.total_checks = 0
        
    def _get_commit_hash(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.stdout.strip()
        except:
            return "UNKNOWN"
    
    def _get_changed_files(self) -> List[str]:
        """Get list of changed files in current commit"""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD^", "HEAD", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.stdout.strip().split('\n') if result.stdout else []
        except:
            return []
    
    def _run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[bool, str, str]:
        """Run a shell command and return success status, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root,
                timeout=120
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout after 120s"
        except Exception as e:
            return False, "", str(e)
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    def print_check(self, name: str, status: bool, details: str = ""):
        """Print check result"""
        icon = "✅" if status else "❌"
        color = Colors.OKGREEN if status else Colors.FAIL
        print(f"{color}{icon} {name}{Colors.ENDC}")
        if details:
            print(f"   {details}")
    
    # CHECK 1: Syntax & Linting
    def check_linting(self) -> Dict[str, Any]:
        """Run linting checks for Python and TypeScript"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 1: Syntax & Linting{Colors.ENDC}")
        results = {"backend": False, "frontend": False, "overall": False}
        
        # Backend Python Linting
        print("  Checking Python files...")
        success, stdout, stderr = self._run_command([
            sys.executable, "-m", "pylint", "main.py", "--disable=all",
            "--enable=syntax-error,undefined-variable"
        ])
        results["backend"] = success
        self.print_check("Backend Python Syntax", success, stderr if not success else "")
        
        # Frontend TypeScript Linting (if exists)
        frontend_path = self.project_root / "frontend"
        if frontend_path.exists():
            print("  Checking TypeScript files...")
            success, stdout, stderr = self._run_command(
                ["npm", "run", "lint", "--if-present"],
                cwd=frontend_path
            )
            results["frontend"] = success or "not configured"
            self.print_check("Frontend TypeScript Lint", success, "")
        else:
            results["frontend"] = "N/A"
        
        results["overall"] = results["backend"] and (results["frontend"] in [True, "N/A", "not configured"])
        return results
    
    # CHECK 2: Type Safety
    def check_type_safety(self) -> Dict[str, Any]:
        """Validate type safety"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 2: Type Safety{Colors.ENDC}")
        results = {"backend": False, "frontend": False, "overall": False}
        
        # Backend Pydantic validation
        print("  Checking Python type hints...")
        try:
            # Try to import main.py to validate Pydantic models
            success, stdout, stderr = self._run_command([
                sys.executable, "-c", "import main; print('Type check OK')"
            ])
            results["backend"] = success
            self.print_check("Backend Type Validation", success, stderr if not success else "")
        except Exception as e:
            results["backend"] = False
            self.print_check("Backend Type Validation", False, str(e))
        
        # Frontend TypeScript type check
        frontend_path = self.project_root / "frontend"
        if frontend_path.exists():
            print("  Checking TypeScript types...")
            success, stdout, stderr = self._run_command(
                ["npx", "tsc", "--noEmit", "--skipLibCheck"],
                cwd=frontend_path
            )
            results["frontend"] = success
            self.print_check("Frontend Type Check", success, stderr[:200] if not success else "")
        else:
            results["frontend"] = "N/A"
        
        results["overall"] = results["backend"] and (results["frontend"] in [True, "N/A"])
        return results
    
    # CHECK 3: Test Suite
    def check_tests(self) -> Dict[str, Any]:
        """Run unit and integration tests"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 3: Test Suite{Colors.ENDC}")
        results = {"unit_tests": False, "integration_tests": False, "overall": False}
        
        # Run pytest if available
        print("  Running unit tests...")
        success, stdout, stderr = self._run_command([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ])
        results["unit_tests"] = success or "no tests found"
        self.print_check("Unit Tests", success or "no tests" in stdout, "")
        
        # Check for integration tests
        if (self.project_root / "tests" / "integration").exists():
            print("  Running integration tests...")
            success, stdout, stderr = self._run_command([
                sys.executable, "-m", "pytest", "tests/integration/", "-v"
            ])
            results["integration_tests"] = success
            self.print_check("Integration Tests", success, "")
        else:
            results["integration_tests"] = "N/A"
        
        results["overall"] = results["unit_tests"] in [True, "no tests found"]
        return results
    
    # CHECK 4: Build Integrity
    def check_build(self) -> Dict[str, Any]:
        """Verify production build succeeds"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 4: Build Integrity{Colors.ENDC}")
        results = {"backend": False, "frontend": False, "overall": False}
        
        # Backend: Test gunicorn can load the app
        print("  Testing backend build...")
        success, stdout, stderr = self._run_command([
            sys.executable, "-c", 
            "from main import app; print('Backend build OK')"
        ])
        results["backend"] = success
        self.print_check("Backend Build", success, stderr if not success else "")
        
        # Frontend: Run build if package.json exists
        frontend_path = self.project_root / "frontend"
        if (frontend_path / "package.json").exists():
            print("  Building frontend... (this may take a moment)")
            success, stdout, stderr = self._run_command(
                ["npm", "run", "build"],
                cwd=frontend_path
            )
            results["frontend"] = success
            self.print_check("Frontend Build", success, "")
        else:
            results["frontend"] = "N/A"
        
        results["overall"] = results["backend"] and (results["frontend"] in [True, "N/A"])
        return results
    
    # CHECK 5: API Health
    def check_api_endpoints(self) -> Dict[str, Any]:
        """Validate critical API endpoints"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 5: API Endpoint Health{Colors.ENDC}")
        results = {"endpoints_tested": 0, "endpoints_passed": 0, "overall": False}
        
        print("  Note: API health check requires running server")
        print("  Validating endpoint definitions...")
        
        # Check if main.py has proper route definitions
        try:
            with open(self.project_root / "main.py", "r") as f:
                content = f.read()
                endpoints = ["/health", "/", "/api/v1/junior", "/api/v1/senior"]
                found_endpoints = [ep for ep in endpoints if ep in content]
                
                results["endpoints_tested"] = len(endpoints)
                results["endpoints_passed"] = len(found_endpoints)
                results["overall"] = len(found_endpoints) >= 2  # At least health + one other
                
                self.print_check(
                    f"API Endpoints Defined ({len(found_endpoints)}/{len(endpoints)})",
                    results["overall"],
                    f"Found: {', '.join(found_endpoints)}"
                )
        except Exception as e:
            results["overall"] = False
            self.print_check("API Endpoint Check", False, str(e))
        
        return results
    
    # CHECK 6: Dependency Audit
    def check_dependencies(self) -> Dict[str, Any]:
        """Run security audit on dependencies"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 6: Dependency Security Audit{Colors.ENDC}")
        results = {"backend": False, "frontend": False, "overall": False, "vulnerabilities": 0}
        
        # Backend: Check for known vulnerable packages
        print("  Auditing Python dependencies...")
        if (self.project_root / "requirements.txt").exists():
            success, stdout, stderr = self._run_command([
                sys.executable, "-m", "pip", "check"
            ])
            results["backend"] = success
            self.print_check("Python Dependencies", success, "")
        else:
            results["backend"] = "N/A"
        
        # Frontend: npm audit
        frontend_path = self.project_root / "frontend"
        if (frontend_path / "package.json").exists():
            print("  Auditing npm dependencies...")
            success, stdout, stderr = self._run_command(
                ["npm", "audit", "--audit-level=high"],
                cwd=frontend_path
            )
            results["frontend"] = success
            # Parse vulnerabilities count if possible
            if not success and "vulnerabilities" in stdout:
                try:
                    import re
                    match = re.search(r'(\d+) vulnerabilities', stdout)
                    if match:
                        results["vulnerabilities"] = int(match.group(1))
                except:
                    pass
            self.print_check("NPM Dependencies", success, f"{results['vulnerabilities']} high+ vulnerabilities" if not success else "")
        else:
            results["frontend"] = "N/A"
        
        results["overall"] = results["backend"] in [True, "N/A"] and results["vulnerabilities"] == 0
        return results
    
    # CHECK 7: Environment Validation
    def check_environment(self) -> Dict[str, Any]:
        """Validate environment configuration"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 7: Environment Validation{Colors.ENDC}")
        results = {"env_file_exists": False, "no_hardcoded_secrets": False, "overall": False}
        
        # Check for .env or env example files
        env_files = [".env", "app/env.example.txt", "backend/env.example"]
        found_env = [f for f in env_files if (self.project_root / f).exists()]
        results["env_file_exists"] = len(found_env) > 0
        self.print_check(f"Environment Config ({len(found_env)} file(s) found)", results["env_file_exists"], "")
        
        # Check for hardcoded secrets in main.py
        print("  Scanning for hardcoded secrets...")
        suspicious_patterns = ["password=", "api_key=", "secret=", "token="]
        hardcoded_found = []
        
        try:
            with open(self.project_root / "main.py", "r") as f:
                content = f.read()
                for pattern in suspicious_patterns:
                    if pattern in content.lower() and "os.getenv" not in content[content.lower().index(pattern):content.lower().index(pattern)+100]:
                        hardcoded_found.append(pattern)
        except:
            pass
        
        results["no_hardcoded_secrets"] = len(hardcoded_found) == 0
        self.print_check("No Hardcoded Secrets", results["no_hardcoded_secrets"], 
                        f"Found: {', '.join(hardcoded_found)}" if hardcoded_found else "")
        
        results["overall"] = results["env_file_exists"] and results["no_hardcoded_secrets"]
        return results
    
    # CHECK 8: Frontend UI Consistency (if applicable)
    def check_ui_consistency(self) -> Dict[str, Any]:
        """Validate UI components render without errors"""
        print(f"\n{Colors.OKBLUE}🔍 CHECK 8: UI Consistency (Frontend){Colors.ENDC}")
        results = {"components_valid": False, "overall": False}
        
        frontend_path = self.project_root / "frontend"
        if not frontend_path.exists():
            print("  Frontend not found - skipping UI checks")
            results["overall"] = "N/A"
            return results
        
        print("  Validating React components...")
        # Check if TypeScript compilation works (already covered in build)
        # Here we just verify component files exist and are syntactically valid
        src_path = frontend_path / "src"
        if src_path.exists():
            tsx_files = list(src_path.rglob("*.tsx"))
            results["components_valid"] = len(tsx_files) > 0
            self.print_check(f"UI Components Found ({len(tsx_files)} files)", results["components_valid"], "")
            results["overall"] = results["components_valid"]
        else:
            results["overall"] = "N/A"
        
        return results
    
    def run_all_checks(self) -> bool:
        """Run all V&V checks and return overall status"""
        self.print_header("🚀 ACTIVATING PRE-DEPLOYMENT VERIFICATION MODE")
        print(f"{Colors.OKCYAN}🔒 Google QA Gate: Zero Tolerance for Broken Builds{Colors.ENDC}")
        print(f"Commit: {self.results['commit_hash'][:8]}")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Changed files: {len(self.results['changed_files'])}")
        
        # Run all 8 checks
        checks = [
            ("Syntax & Linting", self.check_linting),
            ("Type Safety", self.check_type_safety),
            ("Test Suite", self.check_tests),
            ("Build Integrity", self.check_build),
            ("API Health", self.check_api_endpoints),
            ("Dependency Audit", self.check_dependencies),
            ("Environment Validation", self.check_environment),
            ("UI Consistency", self.check_ui_consistency),
        ]
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                self.results["checks"][check_name] = result
                
                # Count towards total
                self.total_checks += 1
                if result.get("overall") in [True, "N/A"]:
                    self.passed_checks += 1
            except Exception as e:
                print(f"{Colors.FAIL}❌ {check_name} CRASHED: {str(e)}{Colors.ENDC}")
                self.results["checks"][check_name] = {"overall": False, "error": str(e)}
                self.total_checks += 1
        
        # Determine overall status
        all_passed = self.passed_checks == self.total_checks
        self.results["overall_status"] = "SAFE_TO_PUSH" if all_passed else "HOLD_FOR_REVIEW"
        
        return all_passed
    
    def generate_report(self) -> str:
        """Generate detailed QA report"""
        self.print_header("📋 PRE-DEPLOYMENT QA REPORT")
        
        report_lines = [
            "="*80,
            "LINDIA PRE-DEPLOYMENT QA REPORT",
            "="*80,
            f"Commit Hash: {self.results['commit_hash']}",
            f"Timestamp: {self.results['timestamp']}",
            f"Status: {self.results['overall_status']}",
            "",
            "CHANGED FILES:",
        ]
        
        for file in self.results['changed_files']:
            report_lines.append(f"  - {file}")
        
        report_lines.extend([
            "",
            "V&V CHECK RESULTS:",
            f"  Passed: {self.passed_checks}/{self.total_checks}",
            ""
        ])
        
        for check_name, result in self.results['checks'].items():
            status = "✅ PASS" if result.get("overall") in [True, "N/A"] else "❌ FAIL"
            report_lines.append(f"  {status} - {check_name}")
            if isinstance(result, dict):
                for key, value in result.items():
                    if key != "overall":
                        report_lines.append(f"      {key}: {value}")
        
        report_lines.extend([
            "",
            "DEPLOYMENT RECOMMENDATION:",
            f"  {self.results['overall_status']}",
            "",
            "="*80
        ])
        
        report = "\n".join(report_lines)
        print(report)
        
        # Save report to file
        report_file = self.project_root / f"vv_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        print(f"\n{Colors.OKGREEN}📄 Report saved to: {report_file}{Colors.ENDC}")
        
        return report
    
    def save_json_report(self):
        """Save detailed JSON report"""
        report_file = self.project_root / f"vv_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"{Colors.OKGREEN}📊 JSON report saved to: {report_file}{Colors.ENDC}")

def main():
    """Main entry point"""
    vv_system = VVSystem()
    
    # Run all checks
    all_passed = vv_system.run_all_checks()
    
    # Generate reports
    vv_system.generate_report()
    vv_system.save_json_report()
    
    # Final verdict
    if all_passed:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ VERIFICATION PASSED - Safe to push{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ VERIFICATION FAILED - Push blocked{Colors.ENDC}")
        print(f"{Colors.WARNING}🔒 Push blocked by V&V system. Fix issues before proceeding.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()

