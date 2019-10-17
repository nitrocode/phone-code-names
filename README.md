# Phone Data

## Supported Devices

Get google api supported devices, convert to utf8, and remove BOM

    curl -s http://storage.googleapis.com/play_public/supported_devices.csv | iconv -f UTF-16LE -t UTF-8 | sed '1s/^\xEF\xBB\xBF//' > data/google_devices.csv

# TODO

* DONE - scrape lineageos stats
* DONE - find and scrape trove of code names from google data
* DONE - find and scape trove of code names from lineage data
* DONE - insert all device info into devices table
* hit fono api
* combine lineageos stats with google data
* combine new data with fono data
* upsert a google spreadsheet
* save data to database file instead of memory
* move cached data to data/ directory
* download supported_devices.csv using python
* create better db schema
  * devices table
  * stats table
  * fono api table
  * create timestamp from when data was retrieved
