#!/usr/bin/env python3
"""
LinkedIn Connections Parser

Parses LinkedIn's data export (Connections.csv) and outputs a clean,
enriched CSV with your professional network.

LinkedIn data export: Settings > Data Privacy > Get a copy of your data
"""

import csv
import argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path


def parse_linkedin_export(input_file: str) -> list[dict]:
    """Parse LinkedIn's Connections.csv export."""
    contacts = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        # LinkedIn CSVs sometimes have extra header rows
        content = f.read()
        lines = content.strip().split('\n')
        
        # Find the actual header row (contains 'First Name' or 'Email')
        header_idx = 0
        for i, line in enumerate(lines):
            if 'First Name' in line or 'Email' in line:
                header_idx = i
                break
        
        # Parse from header onwards
        reader = csv.DictReader(lines[header_idx:])
        
        for row in reader:
            # Handle different LinkedIn export formats
            first_name = row.get('First Name', row.get('first_name', '')).strip()
            last_name = row.get('Last Name', row.get('last_name', '')).strip()
            email = row.get('Email Address', row.get('Email', row.get('email', ''))).strip()
            company = row.get('Company', row.get('company', '')).strip()
            position = row.get('Position', row.get('position', '')).strip()
            connected_on = row.get('Connected On', row.get('connected_on', '')).strip()
            url = row.get('URL', row.get('Profile URL', row.get('url', ''))).strip()
            
            if not first_name and not last_name:
                continue
                
            name = f"{first_name} {last_name}".strip()
            
            # Parse connection date
            conn_date = None
            if connected_on:
                for fmt in ['%d %b %Y', '%b %d, %Y', '%Y-%m-%d', '%m/%d/%Y']:
                    try:
                        conn_date = datetime.strptime(connected_on, fmt)
                        break
                    except ValueError:
                        continue
            
            # Extract domain from company for grouping
            domain = ''
            if company:
                # Simple domain guess from company name
                domain = company.lower().replace(' ', '').replace(',', '')[:20]
            
            contacts.append({
                'name': name,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'company': company,
                'position': position,
                'domain': domain,
                'connected_on': conn_date.isoformat() if conn_date else connected_on,
                'linkedin_url': url,
                'source': 'linkedin'
            })
    
    return contacts


def analyze_network(contacts: list[dict]) -> dict:
    """Analyze network composition."""
    companies = defaultdict(int)
    years = defaultdict(int)
    
    for c in contacts:
        if c['company']:
            companies[c['company']] += 1
        if c['connected_on']:
            try:
                year = c['connected_on'][:4]
                years[year] += 1
            except:
                pass
    
    return {
        'total_connections': len(contacts),
        'with_email': sum(1 for c in contacts if c['email']),
        'top_companies': sorted(companies.items(), key=lambda x: -x[1])[:10],
        'by_year': dict(sorted(years.items()))
    }


def export_csv(contacts: list[dict], output_file: str, min_fields: bool = False):
    """Export contacts to CSV."""
    if min_fields:
        fieldnames = ['name', 'email', 'company', 'position', 'connected_on']
    else:
        fieldnames = ['name', 'first_name', 'last_name', 'email', 'company', 
                      'position', 'domain', 'connected_on', 'linkedin_url', 'source']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(contacts)
    
    print(f"✓ Exported {len(contacts)} contacts to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse LinkedIn connections export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
How to get your LinkedIn data:
  1. Go to LinkedIn Settings > Data Privacy
  2. Click "Get a copy of your data"
  3. Select "Connections" and request archive
  4. Download and unzip when ready
  5. Run this script on Connections.csv
        """
    )
    parser.add_argument('input', help='Path to LinkedIn Connections.csv')
    parser.add_argument('-o', '--output', default='linkedin_contacts.csv',
                        help='Output CSV file (default: linkedin_contacts.csv)')
    parser.add_argument('--minimal', action='store_true',
                        help='Export minimal fields only')
    parser.add_argument('--stats', action='store_true',
                        help='Show network statistics')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        return 1
    
    print(f"Parsing {args.input}...")
    contacts = parse_linkedin_export(args.input)
    
    if args.stats:
        stats = analyze_network(contacts)
        print(f"\n📊 Network Stats:")
        print(f"   Total connections: {stats['total_connections']}")
        print(f"   With email: {stats['with_email']}")
        print(f"\n   Top companies:")
        for company, count in stats['top_companies']:
            print(f"     {company}: {count}")
        print(f"\n   By year:")
        for year, count in stats['by_year'].items():
            print(f"     {year}: {count}")
        print()
    
    export_csv(contacts, args.output, min_fields=args.minimal)
    return 0


if __name__ == '__main__':
    exit(main())
