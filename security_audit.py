#!/usr/bin/env python3
"""
Security Audit Script for MusicSeeker
Verifica vulnerabilidades e configurações de segurança
"""

import os
import sys
import re
import requests
import subprocess
from pathlib import Path

def check_env_security():
    """Verifica segurança das variáveis de ambiente"""
    print("🔍 Checking environment security...")
    
    issues = []
    
    # Check if .env is in .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if ".env" not in gitignore_content:
            issues.append("❌ .env not in .gitignore")
        else:
            print("✅ .env properly ignored by git")
    
    # Check for exposed API keys in code
    python_files = list(Path(".").rglob("*.py"))
    for file_path in python_files:
        content = file_path.read_text()
        if re.search(r'sk-[a-zA-Z0-9-_]{20,}', content):
            issues.append(f"❌ Potential API key exposed in {file_path}")
    
    # Check .env file security
    env_path = Path(".env")
    if env_path.exists():
        env_content = env_path.read_text()
        if "REPLACE_WITH_YOUR" not in env_content and "sk-" in env_content:
            issues.append("❌ .env contains what appears to be a real API key")
        else:
            print("✅ .env appears to be using placeholder values")
    
    return issues


def check_dependencies():
    """Verifica dependências por vulnerabilidades conhecidas"""
    print("🔍 Checking dependencies for vulnerabilities...")
    
    try:
        # Run safety check if available
        result = subprocess.run(
            ["pip", "list"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Check for known vulnerable packages
        vulnerable_patterns = [
            r"pillow==.*[2-7]\..*",  # Old Pillow versions
            r"urllib3==.*1\.2[0-5].*",  # Old urllib3
            r"requests==.*2\.1[0-9].*"  # Very old requests
        ]
        
        issues = []
        for pattern in vulnerable_patterns:
            if re.search(pattern, result.stdout, re.IGNORECASE):
                issues.append(f"❌ Potentially vulnerable package found: {pattern}")
        
        if not issues:
            print("✅ No obvious vulnerable dependencies found")
        
        return issues
        
    except subprocess.CalledProcessError:
        return ["⚠️ Could not check dependencies"]


def check_api_security():
    """Testa configurações de segurança da API"""
    print("🔍 Testing API security...")
    
    issues = []
    
    try:
        # Test rate limiting
        base_url = "http://localhost:8000"
        
        # Test if API is running
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print("✅ API is accessible")
        except requests.exceptions.RequestException:
            print("⚠️ API not running, skipping security tests")
            return []
        
        # Test security headers
        headers = response.headers
        
        security_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy"
        ]
        
        for header in security_headers:
            if header not in headers:
                issues.append(f"❌ Missing security header: {header}")
            else:
                print(f"✅ Security header present: {header}")
        
        # Test rate limiting
        print("Testing rate limiting...")
        search_data = {"query": "test", "limit": 5}
        
        rapid_requests = 0
        for i in range(15):  # Try to exceed 10/minute limit
            try:
                resp = requests.post(
                    f"{base_url}/api/v1/search", 
                    json=search_data, 
                    timeout=2
                )
                if resp.status_code == 429:  # Too Many Requests
                    print("✅ Rate limiting is working")
                    break
                rapid_requests += 1
            except:
                break
        
        if rapid_requests >= 12:
            issues.append("❌ Rate limiting may not be working properly")
        
        # Test SQL injection protection
        malicious_queries = [
            "'; DROP TABLE songs; --",
            "' UNION SELECT * FROM songs --",
            "test'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for query in malicious_queries:
            try:
                resp = requests.post(
                    f"{base_url}/api/v1/search",
                    json={"query": query, "limit": 5},
                    timeout=5
                )
                if resp.status_code == 422:  # Validation error
                    print("✅ SQL injection attempt blocked")
                elif resp.status_code == 500:
                    issues.append(f"❌ Potential SQL injection vulnerability: {query[:20]}...")
            except:
                pass
                
    except Exception as e:
        issues.append(f"⚠️ API security test failed: {e}")
    
    return issues


def check_file_permissions():
    """Verifica permissões de arquivos sensíveis"""
    print("🔍 Checking file permissions...")
    
    issues = []
    sensitive_files = [".env", "app/config.py"]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            mode = stat.st_mode & 0o777
            
            # Check if file is world-readable
            if mode & 0o004:
                issues.append(f"❌ {file_path} is world-readable")
            else:
                print(f"✅ {file_path} has safe permissions")
    
    return issues


def main():
    """Executa auditoria de segurança completa"""
    print("🛡️ MusicSeeker Security Audit")
    print("=" * 40)
    
    all_issues = []
    
    # Run all security checks
    all_issues.extend(check_env_security())
    all_issues.extend(check_dependencies())
    all_issues.extend(check_api_security())
    all_issues.extend(check_file_permissions())
    
    print("\n" + "=" * 40)
    print("📋 SECURITY AUDIT RESULTS")
    print("=" * 40)
    
    if all_issues:
        print("❌ SECURITY ISSUES FOUND:")
        for issue in all_issues:
            print(f"  {issue}")
        print(f"\nTotal issues: {len(all_issues)}")
        sys.exit(1)
    else:
        print("✅ NO CRITICAL SECURITY ISSUES FOUND!")
        print("🎉 Your MusicSeeker installation appears secure!")
        sys.exit(0)


if __name__ == "__main__":
    main()
