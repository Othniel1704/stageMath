#!/usr/bin/env python3
"""
Test script to verify all imports and Phase 2 components work correctly.
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all Phase 2 components import correctly."""
    
    tests = [
        ("Cache Service", lambda: __import__('services.cache_service')),
        ("Retry Service", lambda: __import__('services.retry_service')),
        ("Rate Limiter", lambda: __import__('middleware.rate_limiter')),
        ("Embedding Service", lambda: __import__('services.embedding_service')),
        ("Job Fetcher", lambda: __import__('services.job_fetcher')),
        ("Match Router", lambda: __import__('routers.match')),
        ("Admin Router", lambda: __import__('routers.admin')),
    ]
    
    print("=" * 60)
    print("TESTING PHASE 2 COMPONENTS IMPORTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, import_func in tests:
        try:
            import_func()
            print(f"[OK] {name:30} - PASSED")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name:30} - {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_cache_service():
    """Test cache service functionality."""
    print("\nTesting Cache Service...")
    try:
        from services.cache_service import cache_get, cache_set, cache_delete, cache_clear
        
        # Test set and get
        cache_set("test_key", "test_value")
        result = cache_get("test_key")
        assert result == "test_value", f"Cache get failed: got {result}"
        
        # Test delete
        cache_delete("test_key")
        result = cache_get("test_key")
        assert result is None, "Cache delete failed"
        
        print("[OK] Cache service functional")
        return True
    except Exception as e:
        print(f"[FAIL] Cache service test failed: {e}")
        return False


def test_retry_decorator():
    """Test retry decorator."""
    print("\nTesting Retry Decorator...")
    try:
        from services.retry_service import retry_on_failure
        
        attempt_count = 0
        
        @retry_on_failure(max_retries=2, initial_delay=0.1)
        def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise IOError("Simulated failure")  # IOError is in default exceptions
            return "success"
        
        result = test_function()
        assert result == "success", f"Retry decorator failed: got {result}"
        assert attempt_count == 2, f"Expected 2 attempts, got {attempt_count}"
        
        print("[OK] Retry decorator functional")
        return True
    except Exception as e:
        print(f"[FAIL] Retry decorator test failed: {e}")
        return False


def test_rate_limiter():
    """Test rate limiter."""
    print("\nTesting Rate Limiter...")
    try:
        from middleware.rate_limiter import rate_limiter
        
        # Test setting limit
        rate_limiter.set_limit("/test", 2, 60)
        
        # First two requests should pass
        allowed1, info1 = rate_limiter.is_allowed("192.168.1.1", "/test")
        assert allowed1, "First request should be allowed"
        
        allowed2, info2 = rate_limiter.is_allowed("192.168.1.1", "/test")
        assert allowed2, "Second request should be allowed"
        
        # Third request should fail
        allowed3, info3 = rate_limiter.is_allowed("192.168.1.1", "/test")
        assert not allowed3, "Third request should be blocked"
        
        print("[OK] Rate limiter functional")
        return True
    except Exception as e:
        print(f"[FAIL] Rate limiter test failed: {e}")
        return False


if __name__ == "__main__":
    results = [
        test_imports(),
        test_cache_service(),
        test_retry_decorator(),
        test_rate_limiter(),
    ]
    
    if all(results):
        print("\n[SUCCESS] All Phase 2 component tests passed!")
        sys.exit(0)
    else:
        print("\n[WARNING] Some tests failed. Check errors above.")
        sys.exit(1)
