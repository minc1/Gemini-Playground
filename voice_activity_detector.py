import os
import sys
from dotenv import load_dotenv
import signal
from config_gui import ConfigGUI

def signal_handler(signum, frame):
    print("\nSignal received, cleaning up...")
    sys.exit(0)

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify API key is set
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and run GUI
        gui = ConfigGUI()
        gui.run()
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
    finally:
        print("Application shutdown complete")

if __name__ == "__main__":
    main()
