# 🌌 ED-API

The backend API for [EDCompanion](https://github.com/corenting/edcompanion).

Handle tasks like autocomplete endpoints, proxying calls to external APIs etc.

## Setup

What is needed:
- An [Inara API key](https://inara.cz/elite/inara-api/) for the community goals endpoint
- An FCM server key if you want tosend community goals update as FCM push messages

See `config.py` for all the setting setup. The app use `environs` to load env variables.

## How to use

The project is divided in 2 parts :
- An API with FastAPI
- A community goal command to ping the community goals endpoint periodically and send FCM notifications when the state change

## Credits

- [EDCD](https://github.com/EDCD) for the FDevIDs repository used for commodities information
- [EDSM](https://www.edsm.net/): provides the [ships pictures](https://github.com/EDSM-NET/ED-Ships-ScreenShots) and the API used to fetch the data for some endpoints
- [FuelRats](https://fuelrats.com): provides the endpoint used for the systems typeahead function
- [Inara](https://inara.cz/): used to fetch the data for some endpoints
- [Spansh](https://spansh.co.uk): used to fetch the data for some endpoints

## Donations

If you wish to support the app, donations are possible [here](https://corenting.fr/donate).

## Contact

You can contact me on the [EDCD](https://edcd.github.io/) Discord server (`corenting#6836`).
