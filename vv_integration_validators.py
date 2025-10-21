#!/usr/bin/env python3
"""
🔗 LINDIA INTEGRATION VALIDATORS
Enhanced V&V system for Frontend, AI Engine, and Database Integration

This module provides specialized validators for cross-component integration testing.
"""

import os
import sys
import json
import httpx
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class FrontendValidator:
    """Validates frontend integration and health"""
    
    def __init__(self, frontend_path: Path):
        self.frontend_path = frontend_path
        self.results = {
            "component_count": 0,
            "api_integrations": [],
            "build_status": "UNKNOWN",
            "type_errors": 0,
            "overall": False
        }
    
    def validate_structure(self) -> Dict[str, Any]:
        """Validate frontend structure and dependencies"""
        print(f"\n{Colors.OKBLUE}🔍 Frontend Structure Validation{Colors.ENDC}")
        
        # Check for key files
        required_files = ["package.json", "tsconfig.json"]
        missing_files = []
        
        for file in required_files:
            if not (self.frontend_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"{Colors.FAIL}❌ Missing files: {', '.join(missing_files)}{Colors.ENDC}")
            return {"valid": False, "missing": missing_files}
        
        print(f"{Colors.OKGREEN}✅ Frontend structure valid{Colors.ENDC}")
        
        # Count components
        src_path = self.frontend_path / "src"
        if src_path.exists():
            components = list(src_path.rglob("*.tsx"))
            self.results["component_count"] = len(components)
            print(f"{Colors.OKCYAN}   Found {len(components)} React components{Colors.ENDC}")
        
        return {"valid": True, "components": self.results["component_count"]}
    
    def validate_api_integration(self) -> Dict[str, Any]:
        """Check for proper API integration patterns"""
        print(f"\n{Colors.OKBLUE}🔍 Frontend API Integration Check{Colors.ENDC}")
        
        src_path = self.frontend_path / "src"
        if not src_path.exists():
            return {"valid": False, "reason": "No src directory"}
        
        # Search for API calls in components
        api_patterns = ["fetch(", "axios.", "httpx", "/api/v1/"]
        found_integrations = []
        
        for tsx_file in src_path.rglob("*.tsx"):
            try:
                content = tsx_file.read_text()
                for pattern in api_patterns:
                    if pattern in content:
                        found_integrations.append({
                            "file": str(tsx_file.relative_to(src_path)),
                            "pattern": pattern
                        })
                        break
            except:
                pass
        
        self.results["api_integrations"] = found_integrations
        print(f"{Colors.OKGREEN}✅ Found {len(found_integrations)} API integration points{Colors.ENDC}")
        
        return {"valid": True, "integrations": len(found_integrations)}
    
    def validate_env_config(self) -> Dict[str, Any]:
        """Check environment configuration"""
        print(f"\n{Colors.OKBLUE}🔍 Frontend Environment Config{Colors.ENDC}")
        
        # Check for .env files
        env_files = [".env", ".env.local", ".env.production"]
        found_env = [f for f in env_files if (self.frontend_path / f).exists()]
        
        if found_env:
            print(f"{Colors.OKGREEN}✅ Environment config found: {', '.join(found_env)}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️  No environment files found{Colors.ENDC}")
        
        return {"valid": len(found_env) > 0 or True, "files": found_env}
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all frontend validations"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}FRONTEND INTEGRATION VALIDATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        
        if not self.frontend_path.exists():
            print(f"{Colors.WARNING}⚠️  Frontend directory not found: {self.frontend_path}{Colors.ENDC}")
            return {"overall": "N/A", "reason": "Frontend not present"}
        
        structure = self.validate_structure()
        api_integration = self.validate_api_integration()
        env_config = self.validate_env_config()
        
        self.results["overall"] = structure["valid"] and api_integration["valid"]
        
        return {
            "overall": self.results["overall"],
            "structure": structure,
            "api_integration": api_integration,
            "env_config": env_config,
            "summary": f"{self.results['component_count']} components, {len(self.results['api_integrations'])} API integrations"
        }


class AIEngineValidator:
    """Validates AI Engine integration and health"""
    
    def __init__(self, ai_endpoint: Optional[str] = None):
        self.ai_endpoint = ai_endpoint or os.getenv("AI_ENGINE_URL", "https://lindia-ai-production.up.railway.app")
        self.results = {
            "endpoint_reachable": False,
            "models_available": [],
            "response_time_ms": 0,
            "overall": False
        }
    
    async def validate_endpoint_health(self) -> Dict[str, Any]:
        """Check if AI endpoint is reachable"""
        print(f"\n{Colors.OKBLUE}🔍 AI Engine Endpoint Health{Colors.ENDC}")
        print(f"   Testing: {self.ai_endpoint}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                start_time = datetime.now()
                
                # Try health endpoint
                health_url = f"{self.ai_endpoint}/health"
                response = await client.get(health_url)
                
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                self.results["response_time_ms"] = elapsed
                
                if response.status_code == 200:
                    print(f"{Colors.OKGREEN}✅ AI Engine healthy (response: {elapsed:.0f}ms){Colors.ENDC}")
                    self.results["endpoint_reachable"] = True
                    return {"valid": True, "response_time": elapsed}
                else:
                    print(f"{Colors.FAIL}❌ AI Engine returned {response.status_code}{Colors.ENDC}")
                    return {"valid": False, "status": response.status_code}
                    
        except httpx.TimeoutException:
            print(f"{Colors.FAIL}❌ AI Engine timeout after 10s{Colors.ENDC}")
            return {"valid": False, "error": "Timeout"}
        except Exception as e:
            print(f"{Colors.FAIL}❌ AI Engine unreachable: {str(e)}{Colors.ENDC}")
            return {"valid": False, "error": str(e)}
    
    async def validate_inference_capability(self) -> Dict[str, Any]:
        """Test AI inference endpoint"""
        print(f"\n{Colors.OKBLUE}🔍 AI Inference Capability{Colors.ENDC}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test inference with simple query
                inference_url = f"{self.ai_endpoint}/inference"
                test_payload = {
                    "query": "What is Indian Penal Code?",
                    "context": "Test validation",
                    "tenant_id": "vv_test"
                }
                
                response = await client.post(inference_url, json=test_payload)
                
                if response.status_code == 200:
                    data = response.json()
                    model = data.get("model", "unknown")
                    self.results["models_available"].append(model)
                    print(f"{Colors.OKGREEN}✅ AI inference working (model: {model}){Colors.ENDC}")
                    return {"valid": True, "model": model}
                else:
                    print(f"{Colors.FAIL}❌ Inference failed: {response.status_code}{Colors.ENDC}")
                    return {"valid": False, "status": response.status_code}
                    
        except Exception as e:
            print(f"{Colors.FAIL}❌ Inference test failed: {str(e)}{Colors.ENDC}")
            return {"valid": False, "error": str(e)}
    
    async def validate_integration_with_backend(self) -> Dict[str, Any]:
        """Check backend->AI integration"""
        print(f"\n{Colors.OKBLUE}🔍 Backend-AI Integration{Colors.ENDC}")
        
        # Check if main.py has AI endpoint configured
        try:
            main_py = Path(__file__).parent / "main.py"
            if main_py.exists():
                content = main_py.read_text()
                
                # Look for AI endpoint usage
                ai_patterns = ["lindia-ai", "/inference", "AI Legal"]
                found_patterns = [p for p in ai_patterns if p in content]
                
                if found_patterns:
                    print(f"{Colors.OKGREEN}✅ Backend has AI integration configured{Colors.ENDC}")
                    return {"valid": True, "patterns": found_patterns}
                else:
                    print(f"{Colors.WARNING}⚠️  No AI integration patterns found in backend{Colors.ENDC}")
                    return {"valid": False, "patterns": []}
        except Exception as e:
            print(f"{Colors.FAIL}❌ Integration check failed: {str(e)}{Colors.ENDC}")
            return {"valid": False, "error": str(e)}
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all AI engine validations"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}AI ENGINE INTEGRATION VALIDATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        
        # Run async validations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            health = loop.run_until_complete(self.validate_endpoint_health())
            inference = loop.run_until_complete(self.validate_inference_capability())
            integration = loop.run_until_complete(self.validate_integration_with_backend())
        finally:
            loop.close()
        
        self.results["overall"] = health.get("valid", False) and inference.get("valid", False)
        
        return {
            "overall": self.results["overall"],
            "health": health,
            "inference": inference,
            "integration": integration,
            "summary": f"Endpoint: {self.results['endpoint_reachable']}, Models: {len(self.results['models_available'])}"
        }


class DatabaseValidator:
    """Validates database integration and health"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path(__file__).parent / "legalindia.db")
        self.results = {
            "db_exists": False,
            "tables_count": 0,
            "connection_test": False,
            "overall": False
        }
    
    def validate_db_existence(self) -> Dict[str, Any]:
        """Check if database file exists"""
        print(f"\n{Colors.OKBLUE}🔍 Database File Check{Colors.ENDC}")
        
        if self.db_path.exists():
            size_kb = self.db_path.stat().st_size / 1024
            print(f"{Colors.OKGREEN}✅ Database found: {self.db_path.name} ({size_kb:.1f} KB){Colors.ENDC}")
            self.results["db_exists"] = True
            return {"valid": True, "size_kb": size_kb}
        else:
            print(f"{Colors.WARNING}⚠️  Database not found: {self.db_path}{Colors.ENDC}")
            return {"valid": False}
    
    def validate_db_structure(self) -> Dict[str, Any]:
        """Validate database schema"""
        print(f"\n{Colors.OKBLUE}🔍 Database Structure{Colors.ENDC}")
        
        if not self.db_path.exists():
            return {"valid": False, "reason": "Database not found"}
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.results["tables_count"] = len(tables)
            print(f"{Colors.OKGREEN}✅ Found {len(tables)} tables: {', '.join(tables)}{Colors.ENDC}")
            
            conn.close()
            self.results["connection_test"] = True
            
            return {"valid": True, "tables": tables}
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Database validation failed: {str(e)}{Colors.ENDC}")
            return {"valid": False, "error": str(e)}
    
    def validate_migrations(self) -> Dict[str, Any]:
        """Check migration files"""
        print(f"\n{Colors.OKBLUE}🔍 Database Migrations{Colors.ENDC}")
        
        migrations_path = Path(__file__).parent / "migrations"
        if migrations_path.exists():
            versions = migrations_path / "versions"
            if versions.exists():
                migration_files = list(versions.glob("*.py"))
                print(f"{Colors.OKGREEN}✅ Found {len(migration_files)} migration(s){Colors.ENDC}")
                return {"valid": True, "count": len(migration_files)}
        
        print(f"{Colors.WARNING}⚠️  No migrations directory found{Colors.ENDC}")
        return {"valid": True, "count": 0}  # Not critical
    
    def validate_models(self) -> Dict[str, Any]:
        """Check for ORM models"""
        print(f"\n{Colors.OKBLUE}🔍 Database Models{Colors.ENDC}")
        
        models_paths = [
            Path(__file__).parent / "models",
            Path(__file__).parent / "app" / "models"
        ]
        
        model_files = []
        for models_path in models_paths:
            if models_path.exists():
                model_files.extend(list(models_path.glob("*.py")))
        
        if model_files:
            print(f"{Colors.OKGREEN}✅ Found {len(model_files)} model file(s){Colors.ENDC}")
            return {"valid": True, "count": len(model_files)}
        
        print(f"{Colors.WARNING}⚠️  No model files found{Colors.ENDC}")
        return {"valid": True, "count": 0}  # Not critical for simple setups
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all database validations"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}DATABASE INTEGRATION VALIDATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        
        existence = self.validate_db_existence()
        structure = self.validate_db_structure()
        migrations = self.validate_migrations()
        models = self.validate_models()
        
        self.results["overall"] = existence.get("valid", False) and structure.get("valid", False)
        
        return {
            "overall": self.results["overall"],
            "existence": existence,
            "structure": structure,
            "migrations": migrations,
            "models": models,
            "summary": f"Tables: {self.results['tables_count']}, Connection: {self.results['connection_test']}"
        }


def main():
    """Main entry point for integration validation"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}LINDIA INTEGRATION VALIDATION SUITE{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    project_root = Path(__file__).parent
    
    # Initialize validators
    frontend_validator = FrontendValidator(project_root / "frontend")
    ai_validator = AIEngineValidator()
    db_validator = DatabaseValidator()
    
    # Run validations
    results = {
        "timestamp": datetime.now().isoformat(),
        "frontend": frontend_validator.run_validation(),
        "ai_engine": ai_validator.run_validation(),
        "database": db_validator.run_validation()
    }
    
    # Summary
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}INTEGRATION VALIDATION SUMMARY{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    all_passed = True
    for component, result in [
        ("Frontend", results["frontend"]),
        ("AI Engine", results["ai_engine"]),
        ("Database", results["database"])
    ]:
        status = result.get("overall")
        if status == "N/A":
            print(f"{Colors.OKCYAN}⊘  {component}: Not applicable{Colors.ENDC}")
        elif status:
            print(f"{Colors.OKGREEN}✅ {component}: PASSED{Colors.ENDC}")
            print(f"   {result.get('summary', '')}")
        else:
            print(f"{Colors.FAIL}❌ {component}: FAILED{Colors.ENDC}")
            print(f"   {result.get('summary', '')}")
            if status != "N/A":
                all_passed = False
    
    # Save report
    report_file = project_root / f"integration_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{Colors.OKGREEN}📊 Report saved to: {report_file}{Colors.ENDC}")
    
    if all_passed:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ALL INTEGRATIONS VALIDATED{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ INTEGRATION VALIDATION FAILED{Colors.ENDC}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

