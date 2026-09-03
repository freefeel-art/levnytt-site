# LevNytt Pinterest Standard Access — Demo Video Script

This is the exact, step-by-step script for the Owner to record the demo video
required for the **Pinterest Standard Access** application. It demonstrates the
two things the previous application was rejected for:

1. the **full OAuth flow** (not just a pre-existing token), and
2. a **real Pinterest API integration from LevNytt**.

Everything shown on screen is either public Pinterest UI, read-only API output,
or the LevNytt code itself. **No secret is ever shown.**

---

## Recording rules (read before starting)

- Record the terminal AND the browser in the same frame (picture-in-picture or
  side-by-side is fine).
- Do **not** type `PINTEREST_*` secrets into view. Do not `cat` the `.env` file.
- If a command would print a token or secret, stop and use the exact commands
  below — they are all sanitised and print only non-secret fields.
- Speak over the video explaining each step; the text below is the narration.

---

## Step 0 — One-time prerequisites (do OFF camera)

1. The LevNytt Pinterest app exists with these credentials already in the
   Hermes control repo's ignored `.env` (do not show this file):
   - `PINTEREST_APP_ID`
   - `PINTEREST_CLIENT_SECRET`
   - `PINTEREST_OAUTH_REDIRECT_URI=http://localhost:8085/callback`
2. In the Pinterest app's settings, confirm the redirect URI
   `http://localhost:8085/callback` is registered exactly.
3. Confirm `levnytt.se` is claimed (the site is live and the Pinterest
   verification meta tag is present).

Do not record this step. The video starts at Step 1.

---

## Step 1 — Start the real LevNytt Pinterest OAuth flow

**What the Owner types:**

```bash
cd /home/yampa/projects/active/hermes
.venv/bin/python -c "from app.providers.pinterest import run_callback_server, load_oauth_config; run_callback_server(load_oauth_config())"
```

**What appears on screen:**

1. Terminal prints:

   ```
   Opening Pinterest OAuth in the default browser.
   Waiting for one OAuth callback. Press Ctrl-C to stop.
   ```

2. The default browser opens a `pinterest.com` URL (the OAuth authorization
   endpoint).

**Narration:** "This starts LevNytt's OAuth authorization-code flow. It opens a
local callback server on `localhost:8085` and hands the browser a URL that asks
Pinterest for exactly four scopes."

**What must NOT be shown:** the `client_id` query value, and any `.env` content.

---

## Step 2 — Pinterest authorization / consent

**What the Owner does:**

1. Log in to the LevNytt Pinterest business account (if not already logged in).
2. On the Pinterest consent screen, read the scopes aloud and point at them:

   - `boards:read`
   - `boards:write`
   - `pins:read`
   - `pins:write`

3. Click **Allow / Give access**.

**What appears on screen:** the Pinterest consent screen showing the LevNytt app
name and the four requested scopes listed above.

**Narration:** "Pinterest is asking for consent. The app requests only these
four scopes — read and write boards, read and write pins. It requests no ads,
no catalog, no analytics, and no user-account scope."

**What must NOT be shown:** anything with a token, secret, or the app's client
secret.

---

## Step 3 — Callback completion and token exchange

**What happens (no Owner input required):**

1. Pinterest redirects the browser to
   `http://localhost:8085/callback?code=...&state=...`.
2. The local server validates the one-time `state`, then exchanges the
   authorization code for tokens via `POST https://api.pinterest.com/v5/oauth/token`
   (Basic auth uses app id + secret on the server side, never shown).
3. The tokens are written atomically to the ignored `.env` with file mode
   `0600`.
4. The browser shows the JSON the local server returned:

   ```json
   {"status":"PINTEREST_OAUTH_COMPLETED"}
   ```

5. The terminal process exits (callback finished).

**Narration:** "The browser lands back on the local callback. The authorization
code is exchanged for access and refresh tokens server-side. The tokens are
written to a `0600` file — never printed, never shown, and the browser only
sees a completion status."

**What must NOT be shown:** the `code` or `state` query parameters, the access
token, the refresh token, or the `.env` file.

---

## Step 4 — Read the real Pinterest boards (boards:read)

**What the Owner types:**

```bash
cd /home/yampa/projects/active/hermes
.venv/bin/python -c "import json; from app.providers.pinterest import PinterestProvider; print(json.dumps(PinterestProvider().boards(), ensure_ascii=False, indent=2))"
```

**What appears on screen:** a JSON list of the six real, PUBLIC LevNytt boards:

```
[
  {"id": "1151232792187766810", "name": "Hälsosam Livsstil", "privacy": "PUBLIC"},
  {"id": "1151232792187766803", "name": "Hållbar Städning",   "privacy": "PUBLIC"},
  {"id": "1151232792188035184", "name": "LevNytt – Hälsa",    "privacy": "PUBLIC"},
  {"id": "1151232792187766813", "name": "NeoLife Historia",   "privacy": "PUBLIC"},
  {"id": "1151232792187766770", "name": "NeoLife Kosttillskott", "privacy": "PUBLIC"},
  {"id": "1151232792187766808", "name": "Vetenskap & Näring", "privacy": "PUBLIC"}
]
```

**Narration:** "This is a live `GET /v5/boards` call with the LevNytt access
token. It returns the six boards LevNytt already manages — this proves the
`boards:read` scope works end to end."

**What must NOT be shown:** the access token (it is not part of this command's
output).

---

## Step 5 — Perform a second Trial-safe API action: read pins (pins:read)

**What the Owner types:**

```bash
cd /home/yampa/projects/active/hermes
.venv/bin/python -c "import json; from app.providers.pinterest import PinterestProvider; print(json.dumps(PinterestProvider()._get('/boards/1151232792187766770/pins', {'page_size': 25}), ensure_ascii=False, indent=2))"
```

**What appears on screen:** the real pins on the "NeoLife Kosttillskott" board
(e.g. the existing "NeoLife Pro Vitality+" pin) with its Pin ID and title.

**Narration:** "Under Trial access, reads are permitted — so this demonstrates
the second read scope, `pins:read`, by listing the pins on a real board through
the same authenticated provider."

**What must NOT be shown:** the access token.

---

## Step 6 — Show the LevNytt integration code (what will actually publish)

**What the Owner types:**

```bash
cd /home/yampa/projects/active/hermes
.venv/bin/python -c "import sys, json; sys.path.insert(0, '/home/yampa/projects/active/levnytt-site'); from pathlib import Path; from commander import pinterest_channel as pc; root=Path('/home/yampa/projects/active/levnytt-site'); print(json.dumps({'product_pins': len(pc.product_pin_opportunities(root)), 'informational_pins': len(pc.informational_pin_opportunities(root))}, indent=2))"
```

Then open the file in the editor and show the mapping:

```bash
cd /home/yampa/projects/active/levnytt-site
sed -n '27,50p' commander/pinterest_channel.py
```

**What appears on screen:**

1. Terminal prints `{"product_pins": 9, "informational_pins": 20}` — the current
   LevNytt opportunity pool.
2. The editor shows the `BOARDS` mapping and board-selection code: each NeoLife
   product (supplements / home care) and each informational topic maps to a
   specific board, every Pin points at a `https://levnytt.se/...` destination,
   and every destination is UTM-attributed.

**Narration:** "This is the LevNytt integration itself. It builds Pin
opportunities from the live NeoLife product catalogue and the published article
set, picks the right board and destination, attaches UTM attribution, and
deduplicates against a durable publication ledger. A Pin is never created with
one product's image linked to another's page — there is deterministic
image/product/destination validation before any call."

**What must NOT be shown:** nothing sensitive in this step.

---

## Step 7 — Show the honest Standard Access boundary

**What the Owner types:**

```bash
cd /home/yampa/projects/active/hermes
.venv/bin/python -c "import sys; sys.path.insert(0, '/home/yampa/projects/active/levnytt-site'); from pathlib import Path; from types import SimpleNamespace; from commander.procedure import LevNyttProcedure; ctx=SimpleNamespace(working_repository=Path('/home/yampa/projects/active/levnytt-site'), runtime_directory=Path('/home/yampa/projects/active/levnytt-site/runtime')); print(LevNyttProcedure()._execute_pinterest(ctx, {'capability':'pinterest'}))"
```

**What appears on screen:**

```
{'status': 'BLOCKED_BY_PINTEREST_STANDARD_ACCESS', 'detail': 'Pinterest publication is blocked until PINTEREST_ACCESS_TIER=standard', ...}
```

**Narration:** "This is the only remaining boundary. The full pipeline — OAuth,
opportunity generation, board and destination selection, image validation, UTM
attribution, package building — is complete and exercised. The single remaining
gate is that Pinterest's Trial tier does not permit creating a Pin in
production, so the integration fails closed with an honest status instead of
fabricating success. Granting Standard Access is what unlocks that final
`POST /pins`."

**What must NOT be shown:** the access token.

---

## What this demo proves to the reviewer

| Requirement | Where demonstrated |
|---|---|
| Full OAuth flow | Steps 1–3 |
| Pinterest authorization/consent | Step 2 |
| Callback completion | Step 3 |
| Authorization-code → token exchange without exposing secrets | Step 3 |
| Granted scopes | Step 2 (consent screen lists all four) |
| Real Pinterest API integration from LevNytt | Steps 4, 5, 6 |
| Reading the real Pinterest boards | Step 4 |
| A Trial-safe Pinterest API action | Steps 4 and 5 (boards:read + pins:read) |
| LevNytt context | Step 6 |
| Honest boundary (no fabricated success) | Step 7 |

## Current state

- `LEVNYTT_PINTEREST_INTERNAL_CAPABILITY = READY`
- `PINTEREST_STANDARD_ACCESS = EXTERNAL_PENDING`
