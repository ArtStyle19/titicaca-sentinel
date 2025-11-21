#!/usr/bin/env python3
"""
Test script to verify Titicaca Sentinel setup
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    
    packages = {
        'ee': 'earthengine-api',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'streamlit': 'streamlit',
        'folium': 'folium',
        'plotly': 'plotly',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'dotenv': 'python-dotenv'
    }
    
    failed = []
    
    for package, install_name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - install with: pip install {install_name}")
            failed.append(install_name)
    
    return len(failed) == 0, failed

def test_earth_engine():
    """Test Earth Engine initialization"""
    print("\nTesting Earth Engine...")
    
    try:
        import ee
        ee.Initialize()
        print("  ✓ Earth Engine initialized")
        return True
    except Exception as e:
        print(f"  ✗ Earth Engine error: {e}")
        print("  Run: earthengine authenticate")
        return False

def test_directory_structure():
    """Test if directory structure exists"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        'backend',
        'frontend',
        'gee',
        'notebooks',
        'data',
        'config'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ missing")
            all_exist = False
    
    return all_exist

def test_files():
    """Test if required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'backend/main.py',
        'frontend/app.py',
        'gee/gee_processor.py'
    ]
    
    all_exist = True
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} missing")
            all_exist = False
    
    return all_exist

def test_env_file():
    """Test if .env file exists"""
    print("\nTesting configuration...")
    
    if os.path.exists('.env'):
        print("  ✓ .env file exists")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if project_id:
            print(f"  ✓ GOOGLE_CLOUD_PROJECT: {project_id}")
            return True
        else:
            print("  ⚠ GOOGLE_CLOUD_PROJECT not set in .env")
            return False
    else:
        print("  ⚠ .env file not found")
        print("  Create it from .env.example")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TITICACA SENTINEL - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    success, failed = test_imports()
    results.append(("Package imports", success))
    
    if failed:
        print(f"\nInstall missing packages with:")
        print(f"  pip install {' '.join(failed)}")
    
    # Test directory structure
    results.append(("Directory structure", test_directory_structure()))
    
    # Test files
    results.append(("Required files", test_files()))
    
    # Test .env
    results.append(("Configuration", test_env_file()))
    
    # Test Earth Engine
    results.append(("Earth Engine", test_earth_engine()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All tests passed! You're ready to go!")
        print()
        print("Next steps:")
        print("  1. Start backend:  ./start_backend.sh")
        print("  2. Start frontend: ./start_frontend.sh")
        print("  3. Open browser:   http://localhost:8501")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
