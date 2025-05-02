# Ulauncher Bitwarden RBW

A [Ulauncher](https://ulauncher.io/) extension to search your [Bitwarden](https://bitwarden.com/) vault and copy passwords to the clipboard using [RBW](https://github.com/doy/rbw). I created this because the only V2.0 Bitwarden extension was too slow for my taste, and the only other Bitwarden extension I found is based on V3.0 API. 

## Features

- Search through Bitwarden entries by name and copy to clipboard.
- Support for self-hosted Bitwarden Vaults.
- Incredibly fast searching and filtering.

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



## Todo

- [x] Detect when RBW is locked/uninitialized and prompt for password
- [x] Search Bitwarden database
  - [x] Filter and limit results dynamically
  - [x] Copy to clipboard on select
- [x] Write README
- [ ] Add sync and lock
  - [ ] Remove extra keywords from preferences
  - [ ] Add each as arguments after the initial keyword
  - [ ] Trigger rbw commands
- [ ] Upload to Ulauncher community
