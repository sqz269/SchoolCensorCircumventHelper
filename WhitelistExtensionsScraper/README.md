# Whitelisted Extension Scraper

## Description
This is a script for retriving detailed information about all the whitelisted extensions

## Usage
- Prerequisite: Intelligence, Patience, Some Knowledge in python/general programming, and Python3.6+ (MUST BE 3.6+) installiation
- Clone this repository
- install the required packages using `pip install -r requirements.txt`
- Go to `chrome://policy` and find policy with name `ExtensionInstallAllowlist` or `ExtensionInstallWhitelist`
- Click on show more and the values
- paste the copied values to ext.txt
- run the script with python
- profit

## More Info
- Extensions with `item_category: PLATFORM_APP` can bypass monitoring from gogurdian
- Try find an extension that is PLATFORM_APP and allows you to access google
