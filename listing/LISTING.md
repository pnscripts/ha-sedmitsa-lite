# Sedmitsa Lite: HACS default repository and Home Assistant brands

Nothing has been submitted. Rules: https://hacs.xyz/docs/publish/include/ (checked 2026-10-12).

1. Owner: create the public repo `github.com/pnscripts/ha-sedmitsa-lite`, push `main`. Repo settings: description "Bulgarian working days and holidays for Home Assistant", **Issues on**, topics `home-assistant hacs integration bulgaria holidays`. Social preview: `listing/social-preview-1280x640.png`.
2. The Validate workflow (HACS action + Hassfest) must pass with no ignores. Public repos do not use the org's $0 Actions budget.
3. Create a full GitHub **release** `v1.0.0` (not just a tag). The Release workflow attaches `sedmitsa_lite.zip` (hacs.json `zip_release`). `make dist` builds the same zip locally.
4. Brand: the integration ships `custom_components/sedmitsa_lite/brand/icon.png` (+ @2x and dark), which HACS accepts in place of a home-assistant/brands PR.
5. HACS default PR: from a **personal** GitHub account (HACS asks for a personal account, not an organization), fork `hacs/default`, add `pnscripts/ha-sedmitsa-lite` alphabetically to the `integration` file, fill in the PR template completely. Only the owner or a major contributor may submit.
6. `hacs.json` sets `country: ["BG"]` because the integration is Bulgaria-specific.
