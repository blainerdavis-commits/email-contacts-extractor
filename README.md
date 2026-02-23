# Email Contacts Extractor

Extract everyone you've ever emailed. Runs locally, never touches a server.

## Quick Start

```bash
git clone https://github.com/blainerdavis-commits/email-contacts-extractor.git
cd email-contacts-extractor
python extract_contacts.py --email you@gmail.com
```

Gmail users: you'll need an [App Password](https://myaccount.google.com/apppasswords) (not your regular password).

## What You Get

A CSV with everyone you've communicated with:
- Name + email
- How often you talk
- First/last interaction dates

That's it. Headers only — never reads your actual emails.

## Options

```bash
--email, -e       Your email address
--output, -o      Output file (default: contacts.csv)  
--limit, -l       Max messages to scan per folder
--min-interactions  Only include contacts with N+ emails
```

## Why?

Your email has your real network — people you've *actually* talked to. This gets that data out so you can use it however you want.

No cloud. No tracking. Just a Python script and a CSV.

---

Made by [Blaine Davis](https://twitter.com/blainerdavis)
