#!/usr/bin/env python3
"""
Test Script for Antigravity Logic
Tests the complete flow: upload → matching → applications → profile
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_TOKEN = "your_test_token_here"  # À remplacer par un token valide
TEST_CV_PATH = "path/to/test/cv.pdf"  # À remplacer par un CV de test

class AntigravityTester:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def test_upload_cv(self, cv_path: str) -> Dict[str, Any]:
        """Test CV upload and extraction"""
        print("🧪 Testing CV Upload...")

        if not os.path.exists(cv_path):
            print(f"❌ Test CV not found: {cv_path}")
            return {}

        with open(cv_path, 'rb') as f:
            files = {'file': ('test_cv.pdf', f, 'application/pdf')}
            headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}

            response = requests.post(
                f"{self.base_url}/upload-cv",
                files=files,
                headers=headers
            )

        if response.status_code == 200:
            data = response.json()
            print("✅ CV Upload successful")
            print(f"   📁 Local path: {data.get('chemin_acces_local')}")
            print(f"   🧠 Skills extracted: {data.get('competences_extraites')[:100]}...")
            return data
        else:
            print(f"❌ CV Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return {}

    def test_matching(self, location: str = "Paris") -> Dict[str, Any]:
        """Test job matching"""
        print("🧪 Testing Job Matching...")

        payload = {
            "location": location,
            "preferred_contract": "Stage"
        }

        response = requests.post(
            f"{self.base_url}/match",
            json=payload,
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Matching successful")
            print(f"   📊 Found {len(data.get('jobs', []))} jobs")

            # Analyser les scores
            scores = [job.get('score_matching', 0) for job in data.get('jobs', [])]
            if scores:
                print(f"   📈 Score range: {min(scores)} - {max(scores)}")
                print(f"   🎯 Average score: {sum(scores)/len(scores):.1f}")

            return data
        else:
            print(f"❌ Matching failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return {}

    def test_save_job(self, job_id: int) -> bool:
        """Test saving a job to catalog"""
        print(f"🧪 Testing Save Job {job_id}...")

        response = requests.post(
            f"{self.base_url}/applications/save/{job_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            print("✅ Job saved to catalog")
            return True
        else:
            print(f"❌ Save job failed: {response.status_code}")
            return False

    def test_apply_job(self, job_id: int) -> bool:
        """Test applying to a job"""
        print(f"🧪 Testing Apply to Job {job_id}...")

        response = requests.put(
            f"{self.base_url}/applications/apply/{job_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            print("✅ Job application confirmed")
            return True
        else:
            print(f"❌ Apply job failed: {response.status_code}")
            return False

    def test_get_saved_jobs(self) -> Dict[str, Any]:
        """Test retrieving saved jobs"""
        print("🧪 Testing Get Saved Jobs...")

        response = requests.get(
            f"{self.base_url}/applications/saved",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data)} saved jobs")
            return data
        else:
            print(f"❌ Get saved jobs failed: {response.status_code}")
            return {}

    def test_get_applied_jobs(self) -> Dict[str, Any]:
        """Test retrieving applied jobs"""
        print("🧪 Testing Get Applied Jobs...")

        response = requests.get(
            f"{self.base_url}/applications/applied",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data)} applied jobs")
            return data
        else:
            print(f"❌ Get applied jobs failed: {response.status_code}")
            return {}

    def test_get_profile(self) -> Dict[str, Any]:
        """Test retrieving user profile"""
        print("🧪 Testing Get Profile...")

        response = requests.get(
            f"{self.base_url}/profile/me",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Profile retrieved")
            print(f"   📁 Local CV path: {data.get('chemin_acces_local')}")
            print(f"   🧠 Skills: {data.get('competences_extraites')[:100]}...")
            return data
        else:
            print(f"❌ Get profile failed: {response.status_code}")
            return {}

    def test_download_cv(self) -> bool:
        """Test downloading CV file"""
        print("🧪 Testing CV Download...")

        response = requests.get(
            f"{self.base_url}/profile/cv",
            headers=self.headers
        )

        if response.status_code == 200:
            print("✅ CV download successful")
            print(f"   📄 Content type: {response.headers.get('content-type')}")
            print(f"   📏 File size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ CV download failed: {response.status_code}")
            return False

    def run_full_test(self, cv_path: str):
        """Run complete Antigravity test suite"""
        print("🚀 Starting Antigravity Test Suite")
        print("=" * 50)

        # 1. Upload CV
        upload_result = self.test_upload_cv(cv_path)
        if not upload_result:
            print("❌ Cannot continue without successful upload")
            return

        print()

        # 2. Test matching
        matching_result = self.test_matching()
        if not matching_result.get('jobs'):
            print("❌ No jobs found for matching test")
            return

        job_id = matching_result['jobs'][0]['id']
        print()

        # 3. Test save job
        self.test_save_job(job_id)
        print()

        # 4. Test apply job
        self.test_apply_job(job_id)
        print()

        # 5. Test get saved jobs
        self.test_get_saved_jobs()
        print()

        # 6. Test get applied jobs
        self.test_get_applied_jobs()
        print()

        # 7. Test get profile
        self.test_get_profile()
        print()

        # 8. Test download CV
        self.test_download_cv()
        print()

        print("🎉 Antigravity Test Suite Complete!")
        print("=" * 50)


def main():
    # Configuration des tests
    tester = AntigravityTester(BASE_URL, TEST_USER_TOKEN)

    # Vérifier si un CV de test est fourni
    if len(sys.argv) > 1:
        test_cv = sys.argv[1]
    else:
        test_cv = TEST_CV_PATH

    # Lancer les tests
    tester.run_full_test(test_cv)


if __name__ == "__main__":
    main()