import os
import requests
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from gi.repository import Notify

# Set Icons Dir
ICON_DIR = f"{os.path.dirname(os.path.realpath(__file__))}/images/icons"
ICON_DEFAULT = f"{os.path.dirname(os.path.realpath(__file__))}/images/icon_blank.png"

# Sync icons
class Icons:
    
    def __init__(self):
        self.concurrency = 15
        self.retry_delay = 3
        self.max_retries = 2
        self.timeout = 2
        
        self.lock_file = "/tmp/bitwarden_icon_sync.lock"
        os.makedirs(ICON_DIR, exist_ok=True)
        
    # Check if lock is active
    def check_lock(self):
        return True if os.path.exists(self.lock_file) else False
    
    # Fetch icons and save to files
    def fetch_and_save_icon(self, entry):
        # Variables
        icon_path = f"{ICON_DIR}/{entry}.png"
        
        # Skip if icon already exists
        if os.path.isfile(icon_path):
            return "Exists"
        
        # Set icon URL, set attempts to 0
        url = f"https://icons.bitwarden.net/{entry}/icon.png"
        retries = 0
        
        # Run until max retries are hit
        while retries < self.max_retries:
            try:
                # Make get request + fetch status code with timeout
                response = requests.get(url, timeout=self.timeout)
                status = response.status_code
                content_type = response.headers.get("Content-Type", "")
                
                # On rate limit
                if status == 429:
                    # Set time before retry to value from headers if present, else defined delay
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                    # Wait before retrying
                    time.sleep(retry_after) 
                    # Increase retries by one and try again
                    retries += 1
                    continue
                
                # For errors like 404, 500, no need to retry
                if status != 200:  
                    # Return status code and name of icon
                    return f"Error fetching icon for {entry}: status {status}"
                
                # Fail immediately if response is not image
                if "image" not in content_type:
                    return f"Invalid content for {entry}: content-type {content_type}"

                # Save the icon on valid response
                with open(icon_path, "wb") as f:
                    f.write(response.content)
                    return f"Icon saved for entry {entry}"

            # Retry on timeout
            except requests.exceptions.Timeout as e:
                # Try again
                retries += 1
                err = e
                continue
            
            # Don't retry on other exceptions
            except requests.exceptions.RequestException as e:
                return f"Request failed for {entry}: {e}"
            
        
        # Return error if failed after max retries
        return f"Failed to fetch icon for {entry} after {self.max_retries} retries, error {err}"
    
    # Get icons if enabled in preferences
    def sync(self):
        
        # Write to lock file
        with open(self.lock_file, "w") as f:
            f.write("sync_in_progress") 
        
        try:
            # Get list of URIs
            entries_str = subprocess.check_output(["rbw", "list"]).decode("utf-8")
            entries = entries_str.splitlines()
            
            with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                futures = {}

                for entry in entries:
                    futures[executor.submit(self.fetch_and_save_icon, entry)] = entry

                for future in as_completed(futures):
                    result = future.result()
                    if "Failed" in result:
                        print(result)
            
            # Send notification when sync is complete
            Notify.Notification.new("Sync complete", "Icons have been synced with Bitwarden.").show()
        finally:
            # Remove lock file
            if os.path.isfile(self.lock_file):
                os.remove(self.lock_file)


    def retrieve_icon(self, entry):
        icon_path = f"{ICON_DIR}/{entry}.png"
        if os.path.isfile(icon_path):
            return icon_path
        else:
            return ICON_DEFAULT
        
        
