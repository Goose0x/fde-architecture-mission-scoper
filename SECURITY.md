# Security

This is a demonstration scoping tool, not a production or accredited system.

## Data policy

- Use **fictional, unclassified** intake only.
- Do not paste real personal data, real customer documents, real unit or organization identifiers, or anything that is or might be classified, CUI, or otherwise restricted.
- Example requests in this repository are invented. They are not based on a real program, company, or engagement.
- Generated statements of work are planning artifacts for a demo. They are not authority to operate, and they are not a real threat assessment of a live system.

## Secrets

- API keys and cloud credentials come from the environment or Application Default Credentials. They are never committed.
- Copy `.env.example` to `.env` locally. `.env` is gitignored.
- If a key is ever committed by mistake, revoke it immediately and rotate it at the provider.

## What this software does not do

- It does not connect to real production systems, identity providers, or production data stores.
- It does not claim to meet a government or industry authorization regime (FedRAMP or similar).
- Template mode does not call a model at all; cloud providers are optional and explicit.
