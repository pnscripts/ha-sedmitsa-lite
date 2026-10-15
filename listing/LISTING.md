# Sedmitsa Lite: HACS default repository and Home Assistant brands

Rules: https://hacs.xyz/docs/publish/include/ (checked 2026-10-12 and 2026-10-15).

**Status 2026-10-15:** repo public with description, Issues and topics (`bulgaria hacs hacs-integration holidays home-assistant homeassistant-integration integration working-days`); manifest/README links fixed to `pnscripts/ha-sedmitsa-lite` (commit 6be62f2); Validate (HACS + Hassfest, no ignores) green: https://github.com/pnscripts/ha-sedmitsa-lite/actions/runs/38740515025 ; release after it: https://github.com/pnscripts/ha-sedmitsa-lite/releases/tag/v1.0.0 (asset `sedmitsa_lite.zip` from the Release workflow). Brands: not needed (HA 2026.3+ reads the integration's own `brand/` folder; home-assistant/brands keeps `custom_integrations` only as a legacy folder; the HACS brands check passes).

**HACS default PR: held.** HACS refuses PRs from organization accounts, and the only GitHub account signed in here is the owner's personal account, whose public profile carries his full name; his pnscripts org membership is private. Opening the PR (and the fork it needs) would publicly link that name to PN Scripts, against the rule "never the owner's personal name in anything public". Options: (a) owner opens it himself from his account, accepting the link; (b) a separate personal GitHub account for PN Scripts work (not an org), added to the pnscripts org with write access, opens it. Exact PR when decided:
- fork `hacs/default`, branch from `master`, in file `integration` insert `"pnscripts/ha-sedmitsa-lite",` in case-insensitive alphabetical order (the lint sorted check), JSON must stay valid;
- title: `Add pnscripts/ha-sedmitsa-lite`; body = the template with every box ticked and the links: current release https://github.com/pnscripts/ha-sedmitsa-lite/releases/tag/v1.0.0 , HACS action and hassfest action https://github.com/pnscripts/ha-sedmitsa-lite/actions/runs/38740515025 (re-run Validate first if older than a few weeks and use the new run link). Do not request reviews.


1. Done 2026-10-15: public repo `github.com/pnscripts/ha-sedmitsa-lite`, push `main`. Repo settings: description "Bulgarian working days and holidays for Home Assistant", **Issues on**, topics `home-assistant hacs integration bulgaria holidays`. Social preview: `listing/social-preview-1280x640.png`.
2. The Validate workflow (HACS action + Hassfest) must pass with no ignores. Public repos do not use the org's $0 Actions budget.
3. Create a full GitHub **release** `v1.0.0` (not just a tag). The Release workflow attaches `sedmitsa_lite.zip` (hacs.json `zip_release`). `make dist` builds the same zip locally.
4. Brand: the integration ships `custom_components/sedmitsa_lite/brand/icon.png` (+ @2x and dark), which HACS accepts in place of a home-assistant/brands PR.
5. HACS default PR: from a **personal** GitHub account (HACS asks for a personal account, not an organization), fork `hacs/default`, add `pnscripts/ha-sedmitsa-lite` alphabetically to the `integration` file, fill in the PR template completely. Only the owner or a major contributor may submit.
6. `hacs.json` sets `country: ["BG"]` because the integration is Bulgaria-specific.
