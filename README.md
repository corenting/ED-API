# ED-API

An API for Elite:Dangerous, used mainly by [EDCompanion](https://github.com/corenting/edcompanion).

## Setup

You need an Inara API key for the community goals endpoint, and a FCM server key if you want to send community goals update as FCM push messages.

See `config.py` for all the setting setup. The app use `environs` to load env variables.

## How to use

The project is divided in 2 parts :
- An API with FastAPI
- A community goal command to ping the community goals endpoint periodically and send FCM notifications when the state change

## Credits

- [EDDB API](https://elitebgs.app/eddb/): API used for stations informations
- [EDSM](https://www.edsm.net/): provides the [ships pictures](https://github.com/EDSM-NET/ED-Ships-ScreenShots) and the API used for systems informations
- [FuelRats](https://fuelrats.com): provides the endpoint used for the systems typeahead function
- [Inara](https://inara.cz/): API used to get community goals data

## Contact

You can contact me on the [EDCD](https://edcd.github.io/) Discord server (`corenting#6836`).
