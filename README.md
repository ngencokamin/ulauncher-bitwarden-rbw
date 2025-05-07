# Ulauncher Bitwarden RBW

A [Ulauncher](https://ulauncher.io/) extension to search your [Bitwarden](https://bitwarden.com/) vault and copy passwords to the clipboard using [RBW](https://github.com/doy/rbw). I created this because the only V2.0 Bitwarden extension was too slow for my taste, and the only other Bitwarden extension I found is based on V3.0 API. 

<a href="https://www.buymeacoffee.com/ngencokamin">
		<img alt="Buy Me A Coffee" src="https://gist.githubusercontent.com/juliomaqueda/1d4399f36b7350d6a73db6a470826076/raw/3c5d5e222f1805c2698227e4eb9c5458a8742b75/buy_me_a_coffee_badge.svg" />
	</a> 

## Features

### Blazing fast search

This extension runs incredibly quickly due to using the `rbw` binary to interface with Bitwarden. Searching through Bitwarden entries is near-instant.

### Full TOTP Support

Has supported for TOTP codes when Quick Copy is turned off. Does not require Bitwarden premium.

### Quick Copy

Optionally, you can choose to turn off the details page an immediately copy your password upon clicking enter. Note that this removes TOTP compatibility.

### Icons

Unofficial icon support separate from rbw. Changing the enable icons section in preferences to True will enable icon support. This will sync icons with Bitwarden's collection upon enabling the settings or running `bw sync`. Note that this takes a second. It basically just goes through the list of accounts from rbw and requests each icon from Bitwarden's servers.

## Requirements

- Install [rbw](https://github.com/doy/rbw).
- Follow the steps in the RBW readme to register your device and log in.

## Installation

In Ulauncher Preferences, go to the extensions tab and click "Add extension." Paste `https://github.com/ngencokamin/ulauncher-bitwarden-rbw` in the field that pops up. 

## Usage

After setting up RBW, open Ulauncher and type in "bw" to start the extension. If your vault is locked, you will be prompted to unlock it. Pressing enter on this entry will show a popup asking for your master password.

![bw-locked](https://github.com/user-attachments/assets/ea7f31ed-e064-443e-8c6b-45dd306a56ef)


If your vault is unlocked, it will instead show the first results in RBW with a number of entries equal to the maximum in settings (default 6).

![bw-results](https://github.com/user-attachments/assets/d6b1f404-f2d0-4ff2-8064-ee4c56025c61)


Start typing to narrow down your search results, clicking enter to copy the password on a given account.


https://github.com/user-attachments/assets/04f464cf-3d7a-43f7-aaf1-c8d48b72511d



## Credits

Massive thanks to @kbialek for all his work on the original [Bitwarden Search](https://github.com/kbialek/ulauncher-bitwarden) extension. While these extensions behave very differently under the hood, I could not have done this without his work for ulauncher API reference.
<a target="_blank" href="https://icons8.com/icon/18734/copy-to-clipboard">Copy to Clipboard</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>
Many other icons from [SVGRepo](https://www.svgrepo.com/)

## Todo

- [x] Detect when RBW is locked/uninitialized and prompt for password
- [x] Search Bitwarden database
  - [x] Filter and limit results dynamically
  - [x] Copy to clipboard on select
- [x] Write README
- [x] Add sync and lock
  - [x] Remove extra keywords from preferences
  - [x] Add each as arguments after the initial keyword
  - [x] Trigger rbw commands
- [X] Upload to Ulauncher community
- [X] Add optional setting to open details page instead of quick copy
- [X] TOTP support
- [X] Add optional icon support

- [ ] Update README
  - [ ] Redo usage section with new screenshots and info to account for the billion new features
