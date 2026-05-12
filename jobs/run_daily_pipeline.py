import os
import sys
from dotenv import load_dotenv

# Ensure root is in path for imports
sys.path.append(os.getcwd())

from core.automation_service import AutomationService

def main():
    print("🚀 Starting Daily Content Pipeline...")
    service = AutomationService()
    success = service.run_daily_pipeline(trigger_type="scheduled")
    
    if success:
        print("✅ Pipeline completed successfully.")
        sys.exit(0)
    else:
        print("❌ Pipeline failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
