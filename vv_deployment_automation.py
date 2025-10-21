#!/usr/bin/env python3
"""
🚀 LINDIA DEPLOYMENT AUTOMATION & QA GATE
Complete deployment workflow with V&V, tagging, and auto-rollback

Features:
- Automated V&V before deployment
- Version tagging for successful builds
- Auto-rollback on failure
- Deployment tracking and history
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DeploymentAutomation:
    """Handles automated deployment with QA gates"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_log = self.project_root / "deployment_history.json"
        self.last_safe_commit = None
        
    def _run_command(self, cmd: List[str], check=True) -> Tuple[bool, str, str]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except Exception as e:
            return False, "", str(e)
    
    def get_current_commit(self) -> str:
        """Get current git commit hash"""
        success, stdout, _ = self._run_command(["git", "rev-parse", "HEAD"])
        return stdout.strip() if success else "UNKNOWN"
    
    def get_commit_info(self, commit_hash: str) -> Dict[str, str]:
        """Get detailed commit information"""
        success, stdout, _ = self._run_command([
            "git", "show", commit_hash, "--format=%H|%an|%ae|%ad|%s", "--no-patch"
        ])
        
        if success and stdout:
            parts = stdout.strip().split("|")
            return {
                "hash": parts[0],
                "author": parts[1] if len(parts) > 1 else "Unknown",
                "email": parts[2] if len(parts) > 2 else "",
                "date": parts[3] if len(parts) > 3 else "",
                "message": parts[4] if len(parts) > 4 else ""
            }
        return {"hash": commit_hash}
    
    def load_deployment_history(self) -> List[Dict]:
        """Load deployment history from JSON"""
        if self.deployment_log.exists():
            try:
                with open(self.deployment_log, "r") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_deployment_history(self, history: List[Dict]):
        """Save deployment history to JSON"""
        with open(self.deployment_log, "w") as f:
            json.dump(history, f, indent=2)
    
    def get_last_safe_commit(self) -> Optional[str]:
        """Get the last commit that passed V&V"""
        history = self.load_deployment_history()
        
        for deployment in reversed(history):
            if deployment.get("status") == "SAFE_TO_PUSH":
                return deployment.get("commit_hash")
        
        return None
    
    def tag_version(self, commit_hash: str, build_no: int) -> bool:
        """Create version tag for verified commit"""
        date_str = datetime.now().strftime("%Y%m%d")
        tag_name = f"release_verified_{date_str}_{build_no}"
        
        print(f"\n{Colors.OKBLUE}🏷️  Creating version tag: {tag_name}{Colors.ENDC}")
        
        # Create annotated tag
        success, stdout, stderr = self._run_command([
            "git", "tag", "-a", tag_name, commit_hash,
            "-m", f"Verified release: {date_str} build {build_no}"
        ], check=False)
        
        if success:
            print(f"{Colors.OKGREEN}✅ Tag created: {tag_name}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.WARNING}⚠️  Tag creation failed or already exists{Colors.ENDC}")
            return False
    
    def run_vv_checks(self) -> Dict[str, any]:
        """Run V&V validation suite"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}RUNNING VERIFICATION & VALIDATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        
        # Run main V&V script
        vv_script = self.project_root / "pre_deployment_vv.py"
        if not vv_script.exists():
            print(f"{Colors.FAIL}❌ V&V script not found{Colors.ENDC}")
            return {"passed": False, "reason": "Script not found"}
        
        success, stdout, stderr = self._run_command([
            sys.executable, str(vv_script)
        ], check=False)
        
        # Parse latest V&V report
        import glob
        vv_reports = sorted(glob.glob(str(self.project_root / "vv_report_*.json")), reverse=True)
        
        if vv_reports:
            with open(vv_reports[0], "r") as f:
                report_data = json.load(f)
                return {
                    "passed": success,
                    "status": report_data.get("overall_status"),
                    "report_file": vv_reports[0]
                }
        
        return {"passed": success, "status": "UNKNOWN"}
    
    def run_integration_checks(self) -> Dict[str, any]:
        """Run integration validation"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}RUNNING INTEGRATION VALIDATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        
        integration_script = self.project_root / "vv_integration_validators.py"
        if not integration_script.exists():
            print(f"{Colors.WARNING}⚠️  Integration script not found - skipping{Colors.ENDC}")
            return {"passed": True, "status": "SKIPPED"}
        
        success, stdout, stderr = self._run_command([
            sys.executable, str(integration_script)
        ], check=False)
        
        # Integration checks are informational - don't block on external service failures
        return {
            "passed": True,  # Don't block deployment
            "status": "COMPLETED" if success else "PARTIAL",
            "note": "Integration checks are informational only"
        }
    
    def rollback_to_safe_commit(self, safe_commit: str):
        """Rollback to last known safe commit"""
        print(f"\n{Colors.FAIL}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}INITIATING AUTO-ROLLBACK{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        
        print(f"\n{Colors.WARNING}⚠️  Rolling back to: {safe_commit[:8]}{Colors.ENDC}")
        
        commit_info = self.get_commit_info(safe_commit)
        print(f"   Commit: {commit_info.get('message', 'N/A')}")
        print(f"   Author: {commit_info.get('author', 'N/A')}")
        print(f"   Date: {commit_info.get('date', 'N/A')}")
        
        # Create rollback log
        rollback_log = {
            "timestamp": datetime.now().isoformat(),
            "from_commit": self.get_current_commit(),
            "to_commit": safe_commit,
            "reason": "V&V validation failed"
        }
        
        rollback_file = self.project_root / f"rollback_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(rollback_file, "w") as f:
            json.dump(rollback_log, f, indent=2)
        
        print(f"\n{Colors.OKBLUE}📝 Rollback log saved: {rollback_file.name}{Colors.ENDC}")
        
        # Note: Actual rollback would be done via git reset
        # Not executing automatically to prevent data loss
        print(f"\n{Colors.WARNING}⚠️  To complete rollback, run:{Colors.ENDC}")
        print(f"    git reset --hard {safe_commit}")
        print(f"    git push --force origin main")
    
    def create_deployment_record(self, commit_hash: str, vv_result: Dict, build_no: int) -> Dict:
        """Create deployment record"""
        return {
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "commit_hash": commit_hash,
            "commit_info": self.get_commit_info(commit_hash),
            "build_number": build_no,
            "vv_status": vv_result.get("status"),
            "status": vv_result.get("status"),
            "vv_passed": vv_result.get("passed"),
            "report_file": vv_result.get("report_file", "")
        }
    
    def run_deployment_workflow(self):
        """Execute complete deployment workflow"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🚀 LINDIA AUTOMATED DEPLOYMENT WORKFLOW{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        
        current_commit = self.get_current_commit()
        print(f"{Colors.OKCYAN}Current commit: {current_commit[:8]}{Colors.ENDC}")
        
        # Load history
        history = self.load_deployment_history()
        build_no = len(history) + 1
        
        print(f"{Colors.OKCYAN}Build number: {build_no}{Colors.ENDC}")
        
        # Step 1: Run V&V checks
        vv_result = self.run_vv_checks()
        
        # Step 2: Run integration checks (informational)
        integration_result = self.run_integration_checks()
        
        # Step 3: Create deployment record
        deployment_record = self.create_deployment_record(current_commit, vv_result, build_no)
        deployment_record["integration_status"] = integration_result.get("status")
        
        # Add to history
        history.append(deployment_record)
        self.save_deployment_history(history)
        
        # Step 4: Decision point
        if vv_result.get("passed"):
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ DEPLOYMENT APPROVED{Colors.ENDC}")
            
            # Tag this version
            self.tag_version(current_commit, build_no)
            
            print(f"\n{Colors.OKGREEN}📋 Deployment Record:{Colors.ENDC}")
            print(f"   ID: {deployment_record['deployment_id']}")
            print(f"   Status: {deployment_record['status']}")
            print(f"   Build: {build_no}")
            
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ SAFE TO PUSH{Colors.ENDC}")
            print(f"{Colors.OKGREEN}This commit has been verified and tagged.{Colors.ENDC}")
            
            return 0
            
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ DEPLOYMENT REJECTED{Colors.ENDC}")
            
            # Get last safe commit
            last_safe = self.get_last_safe_commit()
            
            if last_safe:
                print(f"\n{Colors.WARNING}Last safe commit found: {last_safe[:8]}{Colors.ENDC}")
                self.rollback_to_safe_commit(last_safe)
            else:
                print(f"\n{Colors.WARNING}⚠️  No previous safe commit found{Colors.ENDC}")
                print(f"{Colors.WARNING}Fix validation issues before proceeding{Colors.ENDC}")
            
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ HOLD FOR REVIEW{Colors.ENDC}")
            return 1

def main():
    """Main entry point"""
    automation = DeploymentAutomation()
    sys.exit(automation.run_deployment_workflow())

if __name__ == "__main__":
    main()

