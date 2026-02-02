# Security & Deployment Guidance (Low‑Infrastructure Medical Sites)

This application stores clinical data in a local SQLite database. In low‑resource
environments, the most reliable protection is **filesystem‑level encryption** plus
strict **share permissions**, rather than app‑level encryption that requires key
distribution.

## Recommended deployment pattern

**1) Central Windows PC or server hosts the database**
- Store the SQLite file in a shared folder on a single machine.
- Grant access only to authorized clinical users.

**2) Use filesystem encryption**
- Enable **BitLocker** (preferred) or **EFS** on the host machine.
- This protects data at rest without changing the application.

**3) Lock down file shares**
- Share permissions: allow only required user groups.
- NTFS permissions: match or be stricter than share permissions.
- Deny “Everyone” and guest access.

**4) Backup strategy**
- Use the app’s **Backup Database…** button regularly.
- Store backups on encrypted media (BitLocker USB or encrypted drive).

**5) Operational practices**
- Use unique Windows accounts for each staff member.
- Use strong passwords; rotate if staff change.
- Limit admin rights to IT support only.

## Why not app‑level encryption (SQLCipher)?
SQLCipher requires distributing a decryption key to all users. In low‑resource
settings, key sharing often becomes insecure or unmanageable. Filesystem
encryption provides a simpler, more reliable control with fewer operational
failure points.

## Minimum checklist for deployment
- [ ] SQLite database stored on a single managed Windows machine.
- [ ] BitLocker/EFS enabled on that machine.
- [ ] Share permissions restricted to clinical users only.
- [ ] Backups enabled and stored on encrypted media.
- [ ] Unique Windows accounts per user.

If your site requires encryption at the application layer for regulatory reasons,
contact the maintainer to discuss SQLCipher integration and key management.
