# 📧 Email Contacts Extractor

**Extract your email contacts locally — your data stays on your machine.**

A privacy-first Python script that scans your email headers and exports everyone you've ever communicated with. No cloud services. No data leaves your computer.

## Why?

Your email contains your real network — the people you've actually talked to, not just the contacts you remembered to save. This script helps you:

- 🔍 **Discover your network** — Find all the people you've emailed over the years
- 📊 **See who matters** — Ranked by how often you interact
- 🔒 **Keep it private** — Runs locally, reads only headers, exports a simple CSV
- 🧠 **Build your CRM** — Export to any system you want

## Quick Start

```bash
# Clone the repo
git clone https://github.com/blainerdavis/email-contacts-extractor.git
cd email-contacts-extractor

# Run it
python extract_contacts.py --email you@gmail.com --output my_contacts.csv
```

You'll be prompted for your password. For Gmail, use an [App Password](#gmail-setup).

## What It Does

1. Connects to your email via IMAP (secure, encrypted connection)
2. Scans email **headers only** — From, To, CC, Date
3. **Never reads message content** — your emails stay private
4. Extracts unique contacts with:
   - Name and email
   - How many emails sent/received
   - First and last interaction date
5. Exports a clean CSV

## Output

```csv
name,email,domain,total_interactions,sent_count,received_count,first_seen,last_seen
John Smith,john@acme.com,acme.com,47,23,24,2022-03-15T10:30:00,2024-02-20T14:15:00
Jane Doe,jane@startup.io,startup.io,31,15,16,2023-01-10T09:00:00,2024-02-18T11:30:00
```

## Options

```
--email, -e        Your email address (required)
--server, -s       IMAP server (auto-detected for Gmail, Outlook, Yahoo, iCloud)
--output, -o       Output CSV file (default: contacts.csv)
--limit, -l        Max messages to scan per folder (default: all)
--min-interactions Minimum interactions to include (default: 1)
```

### Examples

```bash
# Basic usage
python extract_contacts.py --email you@gmail.com

# Custom output file
python extract_contacts.py --email you@gmail.com --output my_network.csv

# Only contacts you've emailed 2+ times
python extract_contacts.py --email you@gmail.com --min-interactions 2

# Limit to most recent 5000 emails per folder
python extract_contacts.py --email you@gmail.com --limit 5000

# Custom IMAP server
python extract_contacts.py --email you@company.com --server imap.company.com
```

## Gmail Setup

Gmail requires an **App Password** (not your regular password):

1. Enable 2-Factor Authentication at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use that 16-character password with this script

## Privacy & Security

- ✅ **Runs 100% locally** — nothing sent to any server
- ✅ **Headers only** — never reads email content
- ✅ **No dependencies on external APIs** — just Python standard library
- ✅ **Open source** — inspect the code yourself
- ✅ **You control the output** — review the CSV before sharing anywhere

Your password is entered securely (hidden input) and never stored.

## Use Cases

- **Build a personal CRM** — Import the CSV into Notion, Airtable, or any CRM
- **Audit your network** — See who you've lost touch with
- **Backup your contacts** — Email contacts you actually use, not stale address books
- **Data portability** — Your relationships, your data, your choice

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Philosophy

Your email is one of the most complete records of your professional relationships. But that data is locked inside your inbox. This tool gives it back to you — privately, locally, on your terms.

**Your data. Your network. Your choice.**

---

Made with ☕ by [Blaine Davis](https://twitter.com/blainerdavis)

## License

MIT — Do whatever you want with it.
