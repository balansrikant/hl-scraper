# HL Scraper
This solution and repository contains python objects for processing my Hargreaves Lansdown SIPP and ISA funds and some analysis on them .

## Pre-requisite steps
1. Log into Hargreaves Lansdown account
2. Download Account summary as csv files into a folder
    a. Folder path: /root_path/Account-Summary/
    b. File name format: <yyyymmdd-<account_type>-accountsummary.csv
    c. account_type: isa/sipp
3. Delete all extra header rows, footer rows, totals row
4. For each investment (fund/stock), open fact sheet in new tab
5. Download page as webpage complete format
    a. Folder path: /root_path/Investments/<yyyy-mm-dd>/
    b. File name format: <name of investment>.html

## Script steps
1. Execute hl-scraper with root_path as argument

### Deployment
1. Create image with dockerfile
2. Use production_environment.yml for installing ependencies