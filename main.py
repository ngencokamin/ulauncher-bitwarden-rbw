from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

import subprocess


class BitwardenExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        

    def get_lock_status(self):
        try:
            output = subprocess.check_output(['rbw', 'unlocked'], stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e:
            return True
        else:
            return bool(output)  # Return False if no output, else True
        
    def get_bitwarden_entries(self):
        entries_str = subprocess.check_output(
                ["rbw", "list", "--fields", "id,name,user"]  # noqa: S607
            ).decode("utf-8")
        entries_raw = entries_str.splitlines()
        return  [entry.split("\t") for entry in entries_raw]

    def get_max_returns(self):
        return int(self.preferences["max-results"])
    
    def get_pass(self, data):
        return subprocess.check_output(["rbw", "get",data["id"]]).decode("utf-8").strip()

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() or ""
        items = []
        if extension.get_lock_status():
            # action = ExtensionCustomAction
            items.append(ExtensionResultItem(
                icon='images/bitwarden_search_locked.svg',
                name='Unlock Bitwarden',
                description='Enter passphrase to login/unlock bitwarden vault',
                on_enter=ExtensionCustomAction({"action": "read_passphrase"})))
        else:
            entries = extension.get_bitwarden_entries()
            result_num = extension.get_max_returns()
            query = event.get_argument() or ""
            print(query)
            print(result_num)
            matching = [s for s in entries if query in s[1] + s[2]]
            for entry in matching[:result_num]:
                
                data = {"id": entry[0]}
                items.append(ExtensionResultItem(
                    icon="images/bitwarden_search.svg",
                    name=entry[1],
                    description=entry[2],
                    action=CopyToClipboardAction(
                        data=extension.get_pass(data))
                ))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    # Manage user input
    
    def __init__(self):
        super().__init__()
    
    def on_event(self, event, extension):
        try:
            data = event.get_data()
            action = data.get("action", None)
            if action == "read_passphrase":
                return self.unlock_vault(extension)
        except 'test':
            print('test')
            
    def unlock_vault(self, extension):
        subprocess.run(['rbw', 'unlock'])

if __name__ == '__main__':
    BitwardenExtension().run()
