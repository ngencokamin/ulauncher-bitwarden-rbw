# Import Icons class from second file
from icons import Icons
# Import subprocess for interacting with rbw
import subprocess
# Notify and Ulauncher libraries
from gi.repository import Notify
from ulauncher.api.shared.action.ActionList import ActionList
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesUpdateEvent
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
import gi
gi.require_version("Notify", "0.7")

# Notify and copy to clipboard
def copy_notify_action(name, value):
    # ActionList
    # Notify custom action with name of attribute, then copy value to clipboard
    return [
        ExtensionCustomAction(
            {
                "action": "show_notification",
                "summary": "{} copied to clipboard.".format(
                    name
                ),
            }
        ),
        CopyToClipboardAction(value),
    ]

# Extension class


class BitwardenExtension(Extension):
    # Init
    # Subscribe to keyword query, item enter, and preference updated events
    # Initialize instance of icons class
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(
            PreferencesUpdateEvent, PreferencesUpdateEventListener()
        )
        self.icon = Icons()

    # Check if RBW is unlocked and initialized
    # Return True is locked or uninitialized, else false (unlocked sends no output)
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
    def get_pass(self, id):
        return subprocess.check_output(["rbw", "get", id]).decode("utf-8").strip()

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
            # Notify if icon sync is already running
            # Else notify and start sync
            if self.icon.check_lock():
                Notify.Notification.new(
                    "Sync partially complete", "Vault sync complete, but icon sync is still running. New entry icons have not be updated.").show()
            else:
                Notify.Notification.new(
                    "Vault sync complete", "Beginning icon sync.").show()
                self.icon.sync()
        # Send sync complete notification if icons are disabled
        else:
            Notify.Notification.new(
                "Sync complete", "Vault is now up to date.").show()

    # Get icons on settings change
    def get_icons(self):
        # Don't run sync and send notification if sync is already running
        # Else send sync notification and begin sync
        if self.icon.check_lock():
            Notify.Notification.new(
                "Icons already syncing", "Sync is currently in progress.").show()
        else:
            Notify.Notification.new(
                "Syncing icons", "Beginning icon sync.").show()
            self.icon.sync()

    # Set icon to correct value
    def set_icon(self, name):
        # Use generic SVG if icons are disabled, else retrieve icon
        if self.preferences["icons-enabled"] == "false":
            return "images/bitwarden_search.svg"
        else:
            return self.icon.retrieve_icon(name)

    # Check if quick copy is enabled
    def get_quick_copy_status(self):
        return bool(self.preferences["quick-copy"] == "true")

    # Check if entry has totp
    def check_totp(self, entry):
        try:
            # Try to get code from entry name and user
            code = subprocess.check_output(
                ["rbw", "code", entry[1], entry[2]], stderr=subprocess.STDOUT).decode("utf-8")
            # Return totp code on success
            return code
        except subprocess.CalledProcessError as e:
            # Return None if no code is found
            return None

    # Format entry to be printed prettily
    def entry_attrs(self, entry):
        # Add universal attributes to attr dict
        attrs = {"Password": self.get_pass(entry[0]), "Username": self.username(
            entry[2]), "URL": entry[1]}

        # Check if entry has totp code
        # Add to attrs dict if code is returned
        totp = self.check_totp(entry)
        if totp:
            attrs["TOTP Code"] = totp
        
        # Return attributes
        return attrs

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
            matching = [s for s in entries if query.lower() in s[1].lower()]
            # Add matching entries up to number of results allowed
            for entry in matching[:result_num]:
                # Set data with entry ID
                id = entry[0]
                user = extension.username(entry[2])
                folder = extension.folder_name(entry[3])

                # Check if quick copy is enabled
                if extension.get_quick_copy_status():
                    # Set action to copy pass and send notification if quick copy is enabled
                    action = ActionList(copy_notify_action(
                        f"Password", extension.get_pass(id)))
                else:
                    # Go to details screen if quick copy is disabled
                    action = ExtensionCustomAction(
                        {"action": "activate_entry", "entry": entry}, keep_app_open=True)

                # Add entry with name, icon, and service
                # Pass appropriate action on enter
                items.append(ExtensionResultItem(
                    icon=extension.set_icon(entry[1]),
                    name=entry[1],
                    description=f"{user} • {folder}",
                    on_enter=action
                ))
            # If user enters `lock` after keyword, add entry to lock
            # rbw at beginning of list
            if query == "lock":
                items.insert(0, ExtensionResultItem(
                    icon="images/bitwarden_search_locked.svg",
                    name="Lock",
                    description="Lock Bitwarden vault",
                    on_enter=ExtensionCustomAction({"action": "lock"}))) 
            # If user enters `sync` after keyword, add entry to sync
            # rbw at beginning of list
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
        # Match action to result
        match action:
            case "read_passphrase":
                return self.unlock_vault(extension)
            case "lock":
                return self.lock_vault()
            case "sync":
                return extension.sync_vault()
            case "activate_entry":
                entry = data.get("entry")
                return self.active_entry(extension, entry)
            case "show_notification":
                Notify.Notification.new(data.get("summary")).show()

    # Run rbw unlock command
    # This creates a pop-up, so it can be left as is
    def unlock_vault(self, extension):
        subprocess.run(["rbw", "unlock"])

    # Lock vault using rbw lock command
    def lock_vault(self):
        subprocess.run(["rbw", "lock"])

    # Show entry details
    def active_entry(self, extension, entry):
        # Initialize items to show
        items = []
        # Get attributes dict
        attrs = extension.entry_attrs(entry)
        # Loop through keys, values and format each attribute
        for name, value in attrs.items():
            # Pass in True for optional "hide" argument if Password
            if name == "Password":
                items.append(self.format_attr(name, value, True))
            else:
                items.append(self.format_attr(name, value))

        return RenderResultListAction(items)

    # Format attributes
    def format_attr(self, name, value, hide=False):
        # Entry description
        desc = "Copy {} to clipboard".format(name)
        # Hide text if hide argument is true (for Password), else show value
        item_name = "{}: ********".format(
            name) if hide else "{}: {}".format(name, value)
        # Return result
        return ExtensionResultItem(
            icon="images/copy.png",
            name=item_name,
            description=desc,
            on_enter=ActionList(copy_notify_action(name, value))
        )

# Preferences update, handle icons


class PreferencesUpdateEventListener(EventListener):

    def __init__(self):
        super().__init__()
    
    # When preferences are updated
    def on_event(self, event, extension):
        # If icons-enabled is changed to "True"
        if (event.id == "icons-enabled" and
            event.new_value != event.old_value and
            event.new_value == "true"):
            
            # Unlock vault if vault is locked
            if extension.get_lock_status():
                subprocess.run(["rbw", "unlock"])
            # Fetch icons
            extension.get_icons()


# On run
if __name__ == "__main__":
    # Initialize notification service
    Notify.init("Bitwarden - RBW")
    # Run extension class
    BitwardenExtension().run()
    # Uninit notification service when extension is done running
    Notify.uninit()
