#!/usr/bin/env python

import re

import gspread

random_character_pattern = re.compile('^_[0-9a-f]{32}\\.')

# Service Account: updating-attack-surface-sa@updating-the-attack-surface.iam.gserviceaccount.com
google_service_account = gspread.service_account(filename="./google_service_account_credentials.json")

# Open by url sheet from a spreadsheet in one go
# FIXME: 16a6lA5JWsqROZGgFElJZ8H7UP5zx8q8iFxnBT7XnFPE is an open copy of the data for dev purposes, in Ryan's drive.
# FIXME: we need to use the auto-updating one for production.
worksheet = google_service_account.open_by_url("https://docs.google.com/spreadsheets/d/16a6lA5JWsqROZGgFElJZ8H7UP5zx8q8iFxnBT7XnFPE").sheet1

dns_records = worksheet.get_all_records()

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
    elif random_character_pattern.match(record['Name']):
        ignored_records.append(record)
    # Ignore records we _know_ we don't want to scan because they're email services
    elif record['Name'] == 'em6144.hackney.gov.uk' or record['Name'] == 'email.lb.hackney.gov.uk':
        ignored_records.append(record)
    else:
        included_records.append(record)

# print out what we care about
# print("Included things we care about!")

# for record in included_records:
#     print(record['Name'])
# print("\n\n")

##
# Compare the actual DNS records with what we've got in the attack surface sheet
#

# Load the attack surface sheet and grab the list of domain names
# Service Account: updating-attack-surface-sa@updating-the-attack-surface.iam.gserviceaccount.com
google_service_account = gspread.service_account(filename="./google_service_account_credentials.json")

# Open by url sheet from a spreadsheet in one go
# FIXME: 175xUWcJKDsrobrSY9bslR6sEH06HqMo5Qb8yQXzegig is an open copy of the data for dev purposes, in Ryan's drive.
# FIXME: we need to use the real one for production.
workbook = google_service_account.open_by_url("https://docs.google.com/spreadsheets/d/175xUWcJKDsrobrSY9bslR6sEH06HqMo5Qb8yQXzegig")
worksheet = workbook.get_worksheet(2)

attack_surface_dns_records = worksheet.get_all_records()
# Compare that with the DNS list

dns_record_host_names = []
for record in included_records:
    dns_record_host_names.append(record['Name'])

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


# # print out what we're ignoring
# print("Things we're ignoring")
# for record in ignored_records:
#     print(record['Type'] + ": " + record['Name'])
# print("\n\n")
