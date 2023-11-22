#!/usr/bin/env python

import re
import gspread

def load_google_sheet(url, sheet_title="Sheet1", credentials_file="./google_service_account_credentials.json"):
    """Loads a Google Sheet and returns the contents of the sheet as an array of dictionaries"""
    google_service_account = gspread.service_account(filename=credentials_file)
    workbook = google_service_account.open_by_url(url)
    worksheet = workbook.worksheet(sheet_title)
    return worksheet.get_all_records()


def pretty_print_list(list_to_print, title):
    """Format the list with an underlined title, so we get consistent formatting"""
    print(title)
    print(len(title) * '-')

    if not list_to_print:
        print('🎉🎉🎉 Nothing')
    else:
        for record in sorted(list_to_print):
            print(record)
    print("\n")

domain_verification_cname_pattern = re.compile('^_[0-9a-f]{32}\\.')

# Open by url sheet from a spreadsheet in one go
# 16a6lA5JWsqROZGgFElJZ8H7UP5zx8q8iFxnBT7XnFPE is an open copy of the data for dev purposes, in Ryan's drive.
# FIXME: we need to use the auto-updating one for production.
route53_export_url="https://docs.google.com/spreadsheets/d/197u2GPYJBZUViYF8vsXOEimHF2JL7Vi9owwBlroBYaA"
route53_copy_url="https://docs.google.com/spreadsheets/d/16a6lA5JWsqROZGgFElJZ8H7UP5zx8q8iFxnBT7XnFPE"
dns_records = load_google_sheet(route53_copy_url)

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
attack_surface_url = "https://docs.google.com/spreadsheets/d/1KbUY_k5D_xbz633XalWwKcIT9_vV4ysMT7mIN5EECj0"
attack_surface_records = load_google_sheet(attack_surface_url, sheet_title="Current Attack Surface")

# Compare that with the DNS list
route53_domains = [record['Name'] for record in included_records]

attack_surface_domains = []
non_hackney_domains = []
for record in attack_surface_records:
    domain_name = record['Hostname/URL/IP Address'].lower()
    
    # Strip HTTP/S protocol as we just want the domain name
    domain_name = re.sub("https?://","", domain_name)

    # Strip any trailing URL pieces - anything from the first / or ? in the URL
    domain_name = re.sub("[/?)].*","", domain_name)

    # Only add to our list if it's a Hackney domain
    if 'hackney.gov.uk' in domain_name:
        attack_surface_domains.append(domain_name)
    else:
        non_hackney_domains.append(domain_name)

pretty_print_list(set(route53_domains).difference(set(attack_surface_domains)), 
                  title='To be added to the attack surface')

pretty_print_list(set(attack_surface_domains).difference(set(route53_domains)), 
                  title="Things we might want to REMOVE (check these aren't nameservers)")

pretty_print_list(non_hackney_domains, title='Non-Hackney domain names. Check these:')
