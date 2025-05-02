from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

import subprocess


class BitwardenExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def get_lock_status(self):
        return True if subprocess.check_output(['rbw', 'unlocked'], shell=True, stdout=subprocess.PIPE) else False


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
        for i in range(5):
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='Item %s' % i,
                                             description='Item description %s' % i,
                                             on_enter=HideWindowAction()))

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
