#!/usr/bin/env python

import re

import gspread

def load_google_sheet(url, sheet_index=0, credentials_file="./google_service_account_credentials.json"):
    # Service Account: updating-attack-surface-sa@updating-the-attack-surface.iam.gserviceaccount.com
    google_service_account = gspread.service_account(filename=credentials_file)

    workbook = google_service_account.open_by_url(url)
    worksheet = workbook.get_worksheet(sheet_index)
    return worksheet.get_all_records()

domain_verification_cname_pattern = re.compile('^_[0-9a-f]{32}\\.')

# Open by url sheet from a spreadsheet in one go
# 16a6lA5JWsqROZGgFElJZ8H7UP5zx8q8iFxnBT7XnFPE is an open copy of the data for dev purposes, in Ryan's drive.
# FIXME: we need to use the auto-updating one for production.
dns_records = load_google_sheet("https://docs.google.com/spreadsheets/d/16a6lA5JWsqROZGgFElJZ8H7UP5zx8q8iFxnBT7XnFPE")

# Massage the domain names so they're human-friendly
for record in dns_records:
    # DNS records from Route53 end with a dot, that's not helpful here.
    record['Name'] = record['Name'].rstrip('.').lower()

# Process the dns records
ignored_records = []
included_records = []
for record in dns_records:
    # Ignore if it's not a CNAME or A records
    if record['Type'] != 'CNAME' and record['Type'] != 'A':
        ignored_records.append(record)
    # Ignore if it includes domainkey
    elif 'domainkey' in record['Name']:
        ignored_records.append(record)
    # Ignore if it's a wildcard record, because we can't do anything with it:
    elif '*.' in record['Name']:
        ignored_records.append(record)
    # Ignore if it's a load of random characters
    elif domain_verification_cname_pattern.match(record['Name']):
        ignored_records.append(record)
    # Ignore records we _know_ we don't want to scan because they're email services
    elif record['Name'] == 'em6144.hackney.gov.uk' or record['Name'] == 'email.lb.hackney.gov.uk':
        ignored_records.append(record)
    else:
        included_records.append(record)

##
# Compare the actual DNS records with what we've got in the attack surface sheet
#

# Load the attack surface sheet and grab the list of domain names
# 175xUWcJKDsrobrSY9bslR6sEH06HqMo5Qb8yQXzegig is an open copy of the data for dev purposes, in Ryan's drive.
# FIXME: we need to use the real one for production.
attack_surface_dns_records = load_google_sheet("https://docs.google.com/spreadsheets/d/175xUWcJKDsrobrSY9bslR6sEH06HqMo5Qb8yQXzegig", sheet_index=2)

# Compare that with the DNS list
dns_record_host_names = [record['Name'] for record in included_records]

attack_surface_host_names = []
non_hackney_domains = []
for record in attack_surface_dns_records:
    domain_name = record['Hostname/URL/IP Address'].replace('https://', "").replace('http://', "").lower()

    # Only add to our list if it's a Hackney domain
    if 'hackney.gov.uk' in domain_name:
        attack_surface_host_names.append(domain_name)
    else:
        non_hackney_domains.append(domain_name)

print('\n\nThings we want to ADD')
for record in list(set(dns_record_host_names).difference(set(attack_surface_host_names))):
    print(record)


print("\n\nThings we might want to REMOVE (check these aren't nameservers)")
for record in set(attack_surface_host_names).difference(set(dns_record_host_names)):
    print(record)

print('\n\nNon-Hackney domain names. Check these:')
for record in non_hackney_domains:
    print(record)
    