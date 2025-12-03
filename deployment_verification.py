import configurations as config
from daily_api import DailyAPI as daily

def verify_deployment():
    """Verify configuration is ready for deployment"""
    
    print("🔍 VoiceSnap Deployment Verification\n")
    
    issues = []
    warnings = []
    
    # Check Daily.co API key
    if not config.DAILY_API_KEY:
        issues.append("❌ DAILY_API_KEY not configured")
    else:
        print(f"✅ DAILY_API_KEY configured: {config.DAILY_API_KEY[:10]}...")
        
        # Test API key
        is_valid, message = daily.test_api_key()
        if is_valid:
            print(f"✅ Daily.co API key is valid")
        else:
            issues.append(f"❌ Daily.co API key test failed: {message}")
    
    # Check Google OAuth redirect URI
    if not config.GOOGLE_REDIRECT_URI:
        issues.append("❌ GOOGLE_REDIRECT_URI not configured")
    else:
        print(f"✅ GOOGLE_REDIRECT_URI: {config.GOOGLE_REDIRECT_URI}")
        
        if config.GOOGLE_REDIRECT_URI == "http://localhost:8501/":
            warnings.append("⚠️ Using localhost redirect URI - update for production")
    
    # Check google_credentials.json
    import os
    if not os.path.exists('google_credentials.json'):
        issues.append("❌ google_credentials.json not found")
    else:
        print("✅ google_credentials.json found")
        
        # Verify JSON is valid
        try:
            import json
            with open('google_credentials.json', 'r') as f:
                creds = json.load(f)
                if 'web' in creds and 'client_id' in creds['web']:
                    print(f"✅ Google OAuth credentials valid")
                else:
                    issues.append("❌ google_credentials.json has invalid format")
        except Exception as e:
            issues.append(f"❌ google_credentials.json error: {e}")
    
    # Check .gitignore
    if not os.path.exists('.gitignore'):
        warnings.append("⚠️ .gitignore not found - create one to avoid committing secrets")
    else:
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
            if 'google_credentials.json' not in gitignore:
                warnings.append("⚠️ google_credentials.json not in .gitignore")
            if '.env' not in gitignore:
                warnings.append("⚠️ .env not in .gitignore")
    
    # Check database
    if os.path.exists(config.DATABASE_PATH):
        print(f"✅ Database exists: {config.DATABASE_PATH}")
    else:
        print(f"ℹ️ Database will be created on first run")
    
    # Print summary
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    
    if issues:
        print("\n❌ CRITICAL ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\n⚠️ WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues and not warnings:
        print("\n✅ All checks passed! Ready to deploy.")
    elif not issues:
        print("\n✅ No critical issues. Review warnings before deploying.")
    else:
        print("\n❌ Fix critical issues before deploying!")
    
    print("="*50 + "\n")
    
    return len(issues) == 0

if __name__ == "__main__":
    verify_deployment()