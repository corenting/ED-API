# ED-API

An API for Elite:Dangerous, used mainly by [EDCompanion](https://github.com/corenting/edcompanion).

## Setup

You need an Inara API ley for the community goals endpoint, and a FCM server key if you want to send community goals update as FCM push messages.

See `config.py` for all the setting setup. The app can use `python-dotenv` to load env variables.

## Credits

- [EDDB](https://eddb.io/) : data dumps used to update the database
- [EDDN](https://eddn.edcd.io/) : live data used by the commodities endpoints
- [EDEngineer](https://github.com/msarilar/EDEngineer) : JSON of the engineering blueprints
- [EDM](https://gitlab.com/flat-galaxy/edm/issues) : modified code from the project is used for fetching the commodities from EDDN
- [EDSM](https://www.edsm.net/) : API used to get additional data (systems, factions...)
- [Inara](https://inara.cz/) : API used to get community goals data

## Contact

You can contact me on the [EDCD](https://edcd.github.io/) Discord server (`corenting#6836`).