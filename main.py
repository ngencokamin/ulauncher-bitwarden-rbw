# Import ulauncher api tools
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

# Import subprocess for interacting with rbw
import subprocess

# Extension class


class BitwardenExtension(Extension):

    # Init
    # Subscribe to keyword query and item enter events
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    # Check if RBW is unlocked and initialized

    def get_lock_status(self):
        try:
            # Get output from running rbw unlocked command
            output = subprocess.check_output(
                ['rbw', 'unlocked'], stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e:
            # Return True if RBW is not initialized or unlocked
            return True
        else:
            return bool(output)

    # Get all bitwarden entries using subprocess and split into arrays containing ID, item name, and username
    def get_bitwarden_entries(self):
        entries_str = subprocess.check_output(
                ["rbw", "list", "--fields", "id,name,user"]  # noqa: S607
            ).decode("utf-8")
        entries_raw = entries_str.splitlines()
        return [entry.split("\t") for entry in entries_raw]

    # Check maximum number of results allowed by the user
    def get_max_returns(self):
        return int(self.preferences["max-results"])

    # Get password for a given item ID
    def get_pass(self, data):
        return subprocess.check_output(["rbw", "get", data["id"]]).decode("utf-8").strip()

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
                icon='images/bitwarden_search_locked.svg',
                name='Unlock Bitwarden',
                description='Enter passphrase to login/unlock bitwarden vault',
                on_enter=ExtensionCustomAction({"action": "read_passphrase"})))
        # Add entries based on search
        else:
            # All entries, number of results allowed, and matching logic
            entries = extension.get_bitwarden_entries()
            result_num = extension.get_max_returns()
            matching = [s for s in entries if query in s[1] + s[2]]
            # Add matching entries up to number of results allowed
            for entry in matching[:result_num]:
                # Set data with entry ID
                data = {"id": entry[0]}
                # Add entry with name, icon, and service
                # Copy to clipboard on enter
                items.append(ExtensionResultItem(
                    icon="images/bitwarden_search.svg",
                    name=entry[1],
                    description=entry[2],
                    on_enter=CopyToClipboardAction(
                        extension.get_pass(data))
                ))
                if query == 'lock':
                    items.insert(0, ExtensionResultItem(
                        icon="images/bitwarden_search_locked.svg",
                        name="Lock",
                        description="Lock Bitwarden vault",
                        on_enter=ExtensionCustomAction({"action": "lock"})))
                elif query == 'sync':
                    items.append(ExtensionResultItem(
                        icon="images/bitwarden_sync.svg",
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
    # TODO: Add sync and lock actions, error handling
    def on_event(self, event, extension):
        data = event.get_data()
        action = data.get("action", None)
        # Unlock if read_passphrase action is passed in
        if action == "read_passphrase":
            return self.unlock_vault(extension)
        elif action == "lock":
            return self.lock_vault()
        elif action == "sync":
            return self.sync_vault()

    # Run rbw unlock command
    # This creates a pop-up, so it can be left as is
    def unlock_vault(self, extension):
        subprocess.run(['rbw', 'unlock'])

    # Lock vault using rbw lock command
    def lock_vault(self):
        subprocess.run(['rbw', 'lock'])
        
    # Sync vault using rbw sync command
    def sync_vault(self):
        subprocess.run(['rbw', 'sync'])

if __name__ == '__main__':
    BitwardenExtension().run()
