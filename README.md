# Contacts Extractor

Extract your professional network from email + LinkedIn. Everything runs locally.

## Email Contacts

Pull everyone you've ever emailed:

```bash
python extract_contacts.py --email you@gmail.com
```

Gmail users need an [App Password](https://myaccount.google.com/apppasswords).

**Output:** CSV with name, email, interaction count, first/last contact dates.

## LinkedIn Connections

Parse your LinkedIn data export:

```bash
python linkedin_contacts.py ~/Downloads/Connections.csv --stats
```

**How to get your LinkedIn data:**
1. LinkedIn Settings → Data Privacy → Get a copy of your data
2. Select "Connections" → Request archive
3. Download zip when ready, extract `Connections.csv`

**Output:** CSV with name, email (if shared), company, position, connection date.

## Options

### Email
```
--email, -e       Your email address
--output, -o      Output file (default: contacts.csv)
--limit, -l       Max messages to scan per folder
--min-interactions  Only contacts with N+ emails
```

### LinkedIn
```
input             Path to Connections.csv
--output, -o      Output file (default: linkedin_contacts.csv)
--stats           Show network analysis
--minimal         Export fewer fields
```

## Why?

Your real network is in your email and LinkedIn — people you've actually talked to. This gets that data out so you can use it.

No cloud. No tracking. Just Python scripts and CSVs.

---

Made by [Blaine Davis](https://twitter.com/blainerdavis)
