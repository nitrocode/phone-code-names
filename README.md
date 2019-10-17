# Phone Codenames

The objective of this project is to vet the best officially supported LineageOS phones by using the most popular phones currently used.

[Google Sheets Demo](https://docs.google.com/spreadsheets/d/1jPNMhV0SpWhsCrsvQY5CXokgTlbqypKyHTUcnr9Y2lw/edit?usp=sharing)

## Methodology

I had a lot of trouble finding a relation between code names and phone brand and model. After trawling the web for a bit, I found Google has a [`supported_devices.csv`](http://storage.googleapis.com/play_public/supported_devices.csv) file for their Google Play support which contains the data I want. This data doesn't completely fit the LineageOS data so I had to correct some of it by researching and adding my own corrections.

After collecting that data, I then hit the fonoapi to expand each phone's fields which gave me an additional 60 records. Some data is incomplete but still very useful. Going forward, I need to also collect cost for each phone to find budget phones. I'd also like to do a 3D bubble graph of a phone's price (z) vs specs score (y) vs release date (x).

## Supported Devices

Update google api supported devices, convert to utf8, and remove BOM

    curl -s http://storage.googleapis.com/play_public/supported_devices.csv | iconv -f UTF-16LE -t UTF-8 | sed '1s/^\xEF\xBB\xBF//' > data/google_devices.csv

The other file called `missing_devices.csv`, I've built manually.

## Build manually

1. Follow the steps in this [tutorial](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) and you should have your own sheet with permission set to the email in your `client_secret.json`

2. Create pip environment

        pipenv shell

3. Install dependencies

        pipenv install

4. Run script

        python run.py

You should now see data in your Google Spreadsheet

## TODO

* DONE - scrape lineageos stats
* DONE - find and scrape trove of code names from google data
* DONE - find and scape trove of code names from lineage data
* DONE - insert all device info into devices table
* DONE - hit fono api
* DONE - combine lineageos stats with google data
* DONE - combine new data with fono data
* DONE - upsert a google spreadsheet
* DONE - move cached data to data/ directory
* download supported_devices.csv using python instead of curl
* redownload files if last scrape is more than 7 days ago
    * save all files with a timestamp
* get the top 100 lineageos phones instead of only 10
* find a way to improve match rates. Roughly 50 to 70% right now.
* audit matches to see if they are correct
* save data to database file instead of memory
    * why? what does a db even buy us?
    * create better db schema
        * devices table
        * stats table
        * fono api table
        * create_at timestamp from when data was retrieved
