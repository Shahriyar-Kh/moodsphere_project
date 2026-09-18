# Security Policy

Do not report suspected vulnerabilities or exposed credentials in a public issue.

Use the contact information at https://shahriyarkhan.com to report security concerns privately.

## Credential hygiene

- Runtime secrets belong in environment variables.
- Real `.env` files must never be committed.
- Credentials previously committed to Git history should be considered compromised and rotated.
- Example configuration must use placeholders only.

This repository is an educational/portfolio project and is not a medical system.
