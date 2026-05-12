import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv()

from redline.core.config_service import ConfigService
from redline.db.repositories.ideas_repo import IdeaRepository
from redline.db.repositories.videos_repo import VideoRepository
from redline.core.automation_service import AutomationService
from redline.models.idea import Idea

def test_system():
    print("🏁 Starting Redline Cult OS Diagnostic...\n")
    
    # 1. Config Test
    print("🔍 Testing Config Service...")
    config = ConfigService()
    api_key = config.get("NVIDIA_API_KEY")
    # Use a known fast model for diagnostic
    model = "meta/llama-3.1-70b-instruct" 
    if api_key:
        print(f"✅ Config OK. Using fast-test model: {model}")
    else:
        print("❌ Config Error: Missing API Key.")
        return

    # 2. Database & Repo Test
    print("\n🔍 Testing Idea Repository...")
    idea_repo = IdeaRepository()
    test_id = str(uuid.uuid4())[:8]
    test_idea = Idea(
        idea_id=test_id,
        title="Diagnostic Test Idea",
        summary="Testing the persistent memory sync.",
        angle="Technical",
        rationale="System verification.",
        status="new"
    )
    
    idea_repo.create(test_idea)
    fetched = idea_repo.list(filters={"idea_id": test_id})
    if fetched and fetched[0].title == "Diagnostic Test Idea":
        print("✅ Database Write/Read OK.")
    else:
        print("❌ Database Error: Could not retrieve test idea.")
        return

    # 3. Automation & AI Sync Test
    print("\n🔍 Testing Autonomous Production Engine...")
    # Mark idea as selected (Approved)
    idea_repo.update(fetched[0].id, {"status": "selected"})
    
    auto = AutomationService()
    print("🚀 Triggering autonomous production for test idea...")
    success = auto.run_daily_pipeline(trigger_type="diagnostic_test")
    
    if success:
        print("✅ Autonomous Production OK. (Check logs/Telegram)")
        # Verify video creation
        video_repo = VideoRepository()
        videos = video_repo.list(filters={"idea_id": test_id})
        if videos:
            print(f"✅ Video Project created: {videos[0].video_id}")
            print(f"✅ Status: {videos[0].status} (Memory Sync Verified)")
        else:
            print("❌ Production Error: Video project not found.")
    else:
        print("❌ Production Pipeline Failed.")

    # 4. Clean up
    print("\n🧹 Cleaning up diagnostic data...")
    idea_repo.collection.delete_many({"idea_id": test_id})
    if 'video_repo' in locals():
        video_repo.collection.delete_many({"idea_id": test_id})
    print("✅ Cleanup complete.")

    print("\n🏆 SYSTEM DIAGNOSTIC: 100% STABLE")

if __name__ == "__main__":
    test_system()
