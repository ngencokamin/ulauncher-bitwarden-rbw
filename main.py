import gi
gi.require_version("Notify", "0.7")

# Import ulauncher api tools
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from gi.repository import Notify

# Import subprocess for interacting with rbw
import subprocess

# Import icon methods
from icons import IconSync


# Extension class
class BitwardenExtension(Extension):
    # Init
    # Subscribe to keyword query and item enter events
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(
            PreferencesUpdateEvent, PreferencesUpdateEventListener()
        )
        self.icon_sync = IconSync()

    # Check if RBW is unlocked and initialized

    def get_lock_status(self):
        try:
            # Get output from running rbw unlocked command
            output = subprocess.check_output(
                ["rbw", "unlocked"], stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            # Return True if RBW is not initialized or unlocked
            return True
        else:
            return bool(output)

    # Get all bitwarden entries using subprocess and split into arrays containing ID, item name, and username
    def get_bitwarden_entries(self):
        entries_str = subprocess.check_output(
                ["rbw", "list", "--fields", "id,name,user,folder"]
            ).decode("utf-8")
        entries_raw = entries_str.splitlines()
        return [entry.split("\t") for entry in entries_raw]

    # Check maximum number of results allowed by the user
    def get_max_returns(self):
        return int(self.preferences["max-results"])

    # Get password for a given item ID
    def get_pass(self, data):
        return subprocess.check_output(["rbw", "get", data["id"]]).decode("utf-8").strip()

    # Process username
    def username(self, user):
        return user if user else "No username"

    # Process folder name
    def folder_name(self, folder):
        return folder if folder else "No folder"
        
    def sync_vault(self):
        subprocess.run(["rbw", "sync"])
        # Check if icons are enabled
        if self.preferences["icons-enabled"] != "false":
            # Start sync if enabled
            if self.icon_sync.check_lock():
                Notify.Notification.new("Sync partially complete", "Vault sync complete, but icon sync is still running. New entry icons have not be updated.").show()
            else:
                Notify.Notification.new("Vault sync complete", "Beginning icon sync.").show()
                self.icon_sync.sync()
        else:
            Notify.Notification.new("Sync complete", "Vault is now up to date.").show()
            
    # Get icons on settings change
    def get_icons(self):
        if self.icon_sync.check_lock():
                Notify.Notification.new("Icons already syncing", "Sync is currently in progress.").show()
        else:
            Notify.Notification.new("Syncing icons", "Beginning icon sync.").show()
            self.icon_sync.sync()
        
            

# Listen for keyword events and queries
class KeywordQueryEventListener(EventListener):

    # Handle keyword trigger
    def on_event(self, event, extension):
        # Get query after keyword
        query = event.get_argument() or ""
        # Initialize array of items to return as results
        items = []
        # Add only entry with prompt to unlock if bitwarden is locked
        if extension.get_lock_status():
            items.append(ExtensionResultItem(
                icon="images/bitwarden_search_locked.svg",
                name="Unlock Bitwarden",
                description="Enter passphrase to login/unlock bitwarden vault",
                on_enter=ExtensionCustomAction({"action": "read_passphrase"})))
        # Add entries based on search
        else:
            # All entries, number of results allowed, and matching logic
            entries = extension.get_bitwarden_entries()
            result_num = extension.get_max_returns()
            matching = [s for s in entries if query in s[1]] 
            # Add matching entries up to number of results allowed
            for entry in matching[:result_num]:
                # Set data with entry ID
                data = {"id": entry[0]}
                user = extension.username(entry[2])
                folder = extension.folder_name(entry[3])
                # Add entry with name, icon, and service
                # Copy to clipboard on enter
                items.append(ExtensionResultItem(
                    icon="images/bitwarden_search.svg",
                    name=entry[1],
                    description=f"{user} • {folder}",
                    on_enter=CopyToClipboardAction(
                        extension.get_pass(data))
                ))
            if query == "lock":
                items.insert(0, ExtensionResultItem(
                    icon="images/bitwarden_search_locked.svg",
                    name="Lock",
                    description="Lock Bitwarden vault",
                    on_enter=ExtensionCustomAction({"action": "lock"})))
            elif query == "sync":
                items.insert(0, ExtensionResultItem(
                    icon="images/sync.svg",
                    name="Sync",
                    description="Sync Bitwarden Vault with server",
                    on_enter=ExtensionCustomAction({"action": "sync"})))

        # Return list of items
        return RenderResultListAction(items)


# Listener for when enter is pressed
# Handles custom actions
class ItemEnterEventListener(EventListener):

    def __init__(self):
        super().__init__()

    # On clicking enter, check action from data
    def on_event(self, event, extension):
        data = event.get_data()
        action = data.get("action", None)
        # Unlock if read_passphrase action is passed in
        if action == "read_passphrase":
            return self.unlock_vault(extension)
        elif action == "lock":
            return self.lock_vault()
        elif action == "sync":
            return extension.sync_vault()
        
    # Run rbw unlock command
    # This creates a pop-up, so it can be left as is
    def unlock_vault(self, extension):
        subprocess.run(["rbw", "unlock"])
        extension.get_icons()

    # Lock vault using rbw lock command
    def lock_vault(self):
        subprocess.run(["rbw", "lock"])

# Preferences update, handle icons
class PreferencesUpdateEventListener(EventListener):
    
    def __init__(self):
        super().__init__()
    
    def on_event(self, event, extension):
        if event.id == "icons-enabled" and event.new_value == "true":
            if extension.get_lock_status():
                subprocess.run(["rbw", "unlock"])
            extension.get_icons()

if __name__ == "__main__":
    Notify.init("Bitwarden - RBW")
    BitwardenExtension().run()
    Notify.uninit()
