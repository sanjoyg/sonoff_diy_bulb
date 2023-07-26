# SonOff Bulb BL05 Family Home Assistant Integration
This custom components help integrating Sonoff SMART Bulbs BL05 series into home assistant. 

## Pre-requisite
HomeAssistant custom component for sonoff BL05 bulb in DIY Mode. Read the intstructions with the manual to put the bulb in DIY mode. As of writing this README switching on/off the bulb 5 times in 1 second interval would allow to put in DIY mode.

## Installing
- Like all add-on installation goto the "HACS" option in the left menu bar in home assistant
- Select Integration and add custom repository and enter this repositoy

## Usage
Once installed, follow the sonoff diy instructions to put the bulb in DIY mode before proceeding futher. Once put in DIY mode, note the device id.

Having obtained the "device_id", got to Developer Tools/Integration in Home Assistant and add new integration. Select SonOff DIY BULB and follow instructions.

It add the name you provided as entity light thus giving you function available for any light entity
