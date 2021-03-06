# Android Phone Codenames

The objective of this project is to vet the best officially supported LineageOS phones by using the most popular phones currently used according to the [LineageOS Stats](https://stats.lineageos.org).

[Google Sheets Demo](https://docs.google.com/spreadsheets/d/1jPNMhV0SpWhsCrsvQY5CXokgTlbqypKyHTUcnr9Y2lw/edit?usp=sharing)

## Methodology

I had a lot of trouble finding a relation between code names and phone brand and model. After trawling the web for a bit, I found Google has a [`supported_devices.csv`](http://storage.googleapis.com/play_public/supported_devices.csv) file for their Google Play support which contains the data I want. This data doesn't completely fit the LineageOS data so I had to correct some of it by researching and adding my own corrections.

After collecting that data, I then hit the fonoapi to expand each phone's fields which gave me an additional 60 records. Some data is incomplete but still very useful. Going forward, I need to also collect cost for each phone to find budget phones. I'd also like to do a 3D bubble graph of a phone's price (z) vs specs score (y) vs release date (x).

Data Used

* Google Play supported devices
* LineageOS Stats
* Fono API
* Manual research

## Supported Devices

Update google api supported devices, convert to utf8, and remove BOM

    curl -s http://storage.googleapis.com/play_public/supported_devices.csv | iconv -f UTF-16LE -t UTF-8 | sed '1s/^\xEF\xBB\xBF//' > data/google_devices.csv

The file `missing_devices.csv` was built manually and the rest are automatic.

## Build manually

1. Follow the steps in this [tutorial](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) and you should have your own sheet with permission set to the email in your `client_secret.json`

2. Get fono api key and place it in a `.envrc` file to load the env variable using [`direnv`](https://github.com/direnv/direnv) or export `FONO_API` manually

        $ cat .envrc
        export FONO_API=abcdefghijklmnopqrstuvwxyz0123456789...

2. Create pip environment and install dependencies

        pipenv shell
        pipenv install

3. Remove old data (optional)

        rm data/fono_fields.csv
        rm data/lineageos*

4. Run

        python run.py

You should now see data in your Google Spreadsheet

## TODO

Important

* DONE - scrape lineageos stats
* DONE - find and scrape trove of code names from google data
* DONE - find and scape trove of code names from lineage data
* DONE - insert all device info into devices table
* DONE - hit fono api
* DONE - combine lineageos stats with google data
* DONE - combine new data with fono data
* DONE - upsert a google spreadsheet
* DONE - move cached data to data/ directory
* DONE - get devices that don't have any data
* Add a new `missing_devices_fono.csv` for devices like the Xiaomi Pocophone F1 that do not exist in the fono API but info does exist publicly
    * This is where we can add manual data from gsmarena or another source
* Scrape lineageos download page to get versions
    * `[...document.querySelectorAll('table.striped.bordered tr td:nth-child(2)')].map((val) => val.innerText)`
    * also get if this version is officially supported or not. might be able to tell if it's missing from `search.json`.
    * include links to supported devices
    * include links for unsupported devices
* Scrape ifixit for fixit scores
* Create separate Python SDK similar to [jaredrummler/AndroidDeviceNames](https://github.com/jaredrummler/AndroidDeviceNames)
* Get average or min/max cost metrics per phone. If new is unavailable, find used.
    * Amazon, Craigslist, FB Marketplace, Ebay

Medium

* DONE - get the top 100 lineageos phones instead of only 10
    * FIXED - getting 429 quota exceeded for quota group 'WriteGroup'. Now writes to google sheets in a single batched command.
* redownload files if last scrape is more than 7 days ago
    * save all files with a timestamp
* find a way to improve match rates. Roughly 50 to 70% right now.
    * once improved, go from top 100 to top 200 and keep iterating
* audit matches to see if they are correct

Minor

* strip out `android_x86` as it may be an android virtual machine
* save data to database file instead of memory
    * why? what does a db even buy us?
    * create better db schema
        * devices table
        * stats table
        * fono api table
        * create_at timestamp from when data was retrieved
* prefix comma delimited sources of data
