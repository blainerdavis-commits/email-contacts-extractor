#!/usr/bin/env python3
"""
Email Contacts Extractor
========================

Extract your email contacts locally — your data stays on your machine.

This script connects to your email via IMAP, scans message headers (not content),
and exports a clean CSV of everyone you've communicated with.

Privacy-first: No cloud services. No data leaves your computer.

Usage:
    python extract_contacts.py --email you@gmail.com --output contacts.csv

Author: Blaine Davis
License: MIT
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
import csv
import argparse
import getpass
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Set
import sys


class ContactExtractor:
    """Extract contacts from email headers via IMAP."""
    
    # Common email providers and their IMAP servers
    IMAP_SERVERS = {
        'gmail.com': 'imap.gmail.com',
        'googlemail.com': 'imap.gmail.com',
        'outlook.com': 'imap-mail.outlook.com',
        'hotmail.com': 'imap-mail.outlook.com',
        'yahoo.com': 'imap.mail.yahoo.com',
        'icloud.com': 'imap.mail.me.com',
    }
    
    def __init__(self, email_address: str, password: str, imap_server: str = None):
        """
        Initialize the extractor.
        
        Args:
            email_address: Your email address
            password: Your email password (or app-specific password)
            imap_server: IMAP server (auto-detected if not provided)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server or self._detect_imap_server(email_address)
        self.contacts: Dict[str, dict] = defaultdict(lambda: {
            'name': '',
            'email': '',
            'sent_count': 0,
            'received_count': 0,
            'first_seen': None,
            'last_seen': None,
            'domains': set(),
        })
        
    def _detect_imap_server(self, email_address: str) -> str:
        """Auto-detect IMAP server from email domain."""
        domain = email_address.split('@')[-1].lower()
        if domain in self.IMAP_SERVERS:
            return self.IMAP_SERVERS[domain]
        # Default guess
        return f'imap.{domain}'
    
    def connect(self) -> None:
        """Connect to the IMAP server."""
        print(f"🔐 Connecting to {self.imap_server}...")
        self.mail = imaplib.IMAP4_SSL(self.imap_server)
        self.mail.login(self.email_address, self.password)
        print("✅ Connected successfully")
        
    def disconnect(self) -> None:
        """Disconnect from the IMAP server."""
        try:
            self.mail.logout()
        except:
            pass
            
    def _decode_header_value(self, value: str) -> str:
        """Decode an email header value."""
        if not value:
            return ''
        decoded_parts = decode_header(value)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or 'utf-8', errors='replace'))
                except:
                    result.append(part.decode('utf-8', errors='replace'))
            else:
                result.append(part)
        return ' '.join(result)
    
    def _parse_email_addresses(self, header_value: str) -> List[Tuple[str, str]]:
        """Parse email addresses from a header, returning (name, email) tuples."""
        if not header_value:
            return []
        
        # Handle multiple addresses
        addresses = []
        decoded = self._decode_header_value(header_value)
        
        # Split by comma, handling quoted names
        parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', decoded)
        
        for part in parts:
            name, addr = parseaddr(part.strip())
            if addr and '@' in addr:
                addr = addr.lower().strip()
                name = name.strip().strip('"').strip("'")
                addresses.append((name, addr))
                
        return addresses
    
    def _update_contact(self, name: str, email_addr: str, date: datetime, is_sent: bool) -> None:
        """Update contact information."""
        email_lower = email_addr.lower()
        
        # Skip your own email
        if email_lower == self.email_address.lower():
            return
            
        contact = self.contacts[email_lower]
        contact['email'] = email_lower
        
        # Keep the best name (longest, non-empty)
        if name and (not contact['name'] or len(name) > len(contact['name'])):
            contact['name'] = name
            
        # Update counts
        if is_sent:
            contact['sent_count'] += 1
        else:
            contact['received_count'] += 1
            
        # Update dates
        if date:
            if not contact['first_seen'] or date < contact['first_seen']:
                contact['first_seen'] = date
            if not contact['last_seen'] or date > contact['last_seen']:
                contact['last_seen'] = date
                
        # Track domain
        domain = email_lower.split('@')[-1]
        contact['domains'].add(domain)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date header."""
        if not date_str:
            return None
        try:
            # Remove timezone name in parentheses
            date_str = re.sub(r'\s*\([^)]+\)\s*$', '', date_str)
            # Try common formats
            for fmt in [
                '%a, %d %b %Y %H:%M:%S %z',
                '%d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S',
                '%d %b %Y %H:%M:%S',
            ]:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
        except:
            pass
        return None
    
    def scan_folder(self, folder: str = 'INBOX', limit: int = None) -> int:
        """
        Scan a folder for contacts.
        
        Args:
            folder: Folder name (INBOX, [Gmail]/Sent Mail, etc.)
            limit: Maximum messages to scan (None for all)
            
        Returns:
            Number of messages scanned
        """
        print(f"📂 Scanning {folder}...")
        
        try:
            status, _ = self.mail.select(folder, readonly=True)
            if status != 'OK':
                print(f"   ⚠️  Could not select folder: {folder}")
                return 0
        except Exception as e:
            print(f"   ⚠️  Error selecting folder: {e}")
            return 0
            
        # Search for all messages
        status, messages = self.mail.search(None, 'ALL')
        if status != 'OK':
            return 0
            
        message_ids = messages[0].split()
        total = len(message_ids)
        
        if limit:
            message_ids = message_ids[-limit:]  # Most recent
            
        print(f"   Found {total} messages, scanning {len(message_ids)}...")
        
        is_sent = 'sent' in folder.lower()
        scanned = 0
        
        for i, msg_id in enumerate(message_ids):
            if (i + 1) % 500 == 0:
                print(f"   Progress: {i + 1}/{len(message_ids)}")
                
            try:
                # Fetch headers only (not body)
                status, msg_data = self.mail.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (FROM TO CC DATE)])')
                if status != 'OK':
                    continue
                    
                raw_headers = msg_data[0][1]
                msg = email.message_from_bytes(raw_headers)
                
                date = self._parse_date(msg.get('Date', ''))
                
                # Process From
                for name, addr in self._parse_email_addresses(msg.get('From', '')):
                    self._update_contact(name, addr, date, is_sent=False)
                    
                # Process To and CC (these are people you've sent to)
                for header in ['To', 'Cc']:
                    for name, addr in self._parse_email_addresses(msg.get(header, '')):
                        self._update_contact(name, addr, date, is_sent=True)
                        
                scanned += 1
                
            except Exception as e:
                continue  # Skip problematic messages
                
        print(f"   ✅ Scanned {scanned} messages")
        return scanned
    
    def scan_all(self, limit_per_folder: int = None) -> None:
        """Scan common email folders."""
        # List all folders
        status, folders = self.mail.list()
        
        # Common folders to scan
        priority_folders = [
            'INBOX',
            '[Gmail]/Sent Mail',
            '[Gmail]/All Mail',
            'Sent',
            'Sent Items',
            'Sent Messages',
        ]
        
        scanned_folders = set()
        
        for folder in priority_folders:
            if folder.lower() not in scanned_folders:
                self.scan_folder(folder, limit=limit_per_folder)
                scanned_folders.add(folder.lower())
    
    def get_contacts(self, min_interactions: int = 1) -> List[dict]:
        """
        Get extracted contacts.
        
        Args:
            min_interactions: Minimum total interactions to include
            
        Returns:
            List of contact dictionaries
        """
        results = []
        for email_addr, data in self.contacts.items():
            total = data['sent_count'] + data['received_count']
            if total >= min_interactions:
                results.append({
                    'name': data['name'] or '',
                    'email': email_addr,
                    'sent_count': data['sent_count'],
                    'received_count': data['received_count'],
                    'total_interactions': total,
                    'first_seen': data['first_seen'].isoformat() if data['first_seen'] else '',
                    'last_seen': data['last_seen'].isoformat() if data['last_seen'] else '',
                    'domain': list(data['domains'])[0] if data['domains'] else '',
                })
                
        # Sort by total interactions
        results.sort(key=lambda x: x['total_interactions'], reverse=True)
        return results
    
    def export_csv(self, filepath: str, min_interactions: int = 1) -> int:
        """
        Export contacts to CSV.
        
        Args:
            filepath: Output file path
            min_interactions: Minimum interactions to include
            
        Returns:
            Number of contacts exported
        """
        contacts = self.get_contacts(min_interactions)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'email', 'domain', 'total_interactions',
                'sent_count', 'received_count', 'first_seen', 'last_seen'
            ])
            writer.writeheader()
            writer.writerows(contacts)
            
        return len(contacts)


def main():
    parser = argparse.ArgumentParser(
        description='Extract email contacts locally — your data stays on your machine.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --email you@gmail.com --output contacts.csv
  %(prog)s --email you@company.com --server imap.company.com --output contacts.csv
  %(prog)s --email you@gmail.com --limit 5000 --min-interactions 2

For Gmail, use an App Password:
  1. Enable 2FA on your Google account
  2. Go to myaccount.google.com/apppasswords
  3. Generate a new app password
  4. Use that password with this script

Privacy: This script only reads email headers (From, To, CC, Date).
         Message content is never accessed or stored.
        """
    )
    
    parser.add_argument('--email', '-e', required=True,
                        help='Your email address')
    parser.add_argument('--server', '-s',
                        help='IMAP server (auto-detected for common providers)')
    parser.add_argument('--output', '-o', default='contacts.csv',
                        help='Output CSV file (default: contacts.csv)')
    parser.add_argument('--limit', '-l', type=int,
                        help='Max messages to scan per folder')
    parser.add_argument('--min-interactions', '-m', type=int, default=1,
                        help='Minimum interactions to include (default: 1)')
    
    args = parser.parse_args()
    
    # Get password securely
    print("\n📧 Email Contacts Extractor")
    print("=" * 40)
    print(f"Email: {args.email}")
    print("\n🔑 Enter your email password (or app password for Gmail):")
    password = getpass.getpass("Password: ")
    
    if not password:
        print("❌ Password required")
        sys.exit(1)
    
    # Extract contacts
    extractor = ContactExtractor(args.email, password, args.server)
    
    try:
        extractor.connect()
        extractor.scan_all(limit_per_folder=args.limit)
        
        count = extractor.export_csv(args.output, min_interactions=args.min_interactions)
        
        print(f"\n🎉 Done! Exported {count} contacts to {args.output}")
        print("\n📊 Top 10 contacts by interaction:")
        for contact in extractor.get_contacts()[:10]:
            print(f"   {contact['total_interactions']:4d}  {contact['name'] or contact['email']}")
            
    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP Error: {e}")
        print("\nFor Gmail, make sure you're using an App Password:")
        print("  1. Enable 2FA: myaccount.google.com/security")
        print("  2. Create App Password: myaccount.google.com/apppasswords")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        extractor.disconnect()


if __name__ == '__main__':
    main()
