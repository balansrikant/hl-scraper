# HL Scraper
This solution and repository contains python objects for processing my Hargreaves Lansdown SIPP and ISA funds and some analysis on them.

## Pre-requisite steps
1. Log into Hargreaves Lansdown account
2. Download transaction details as csv (for all calendar years initially and then for latest year)
    - Folder path: /MyDevelopment/Logs/Data/
    - File name format: portfolio-summary-<isa/sipp>-<yyyy>.csv
3. Delete all extra header rows, footer rows, totals row
4. Remove special characters like '£'
4. Open investment-factsheets.csv
    - For each stock/fund that is not present in the csv file
    - Use the Hargreaves Lansdown fund finder search etc. to get URL containing factsheet
    - Add a row in the csv file
