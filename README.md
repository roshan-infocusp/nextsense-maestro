# NextSense Budz — Maestro Test Automation Framework

Mobile UI test automation for the **NextSense Budz** Android app using [Maestro](https://maestro.mobile.dev) 2.6.0.

> **Goal:** Any engineer with a Mac, Windows, or Linux machine and Android Studio should be able to clone this repo, follow these steps, and run the full onboarding smoke test — with no prior knowledge of the project.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [System Requirements](#2-system-requirements)
3. [Step-by-Step First-Time Setup](#3-step-by-step-first-time-setup)
4. [Configure Test Credentials](#4-configure-test-credentials)
5. [Running the Tests](#5-running-the-tests)
6. [Understanding the Report](#6-understanding-the-report)
7. [What to Expect](#7-what-to-expect)
8. [Test Coverage](#8-test-coverage)
9. [Known Blockers](#9-known-blockers)
10. [Assumptions Made](#10-assumptions-made)
11. [Reliability Observations](#11-reliability-observations)
12. [Automation Readiness Recommendations](#12-automation-readiness-recommendations)
13. [Adding a New Test](#13-adding-a-new-test)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Project Structure

```
Maestro/
│
├── flows/
│   └── onboarding_smoke.yaml    # Full onboarding smoke test (Screens 1–25)
│
├── config/
│   └── env.yaml                 # Maestro suite config + environment variables
│
├── test-data/
│   └── users.json               # Test account credentials
│
├── reports/
│   ├── report.html              # Auto-generated HTML report (opens after every run)
│   ├── <timestamp>/             # Debug artifacts from the latest run
│   └── screenshots/             # Screenshots captured mid-test
│       ├── screen_17.png        # Your Smartbuds are connected!
│       └── homescreen.png       # Final Home Screen confirmation
│
├── run_tests.sh                 # ← Always use this to run tests
├── generate_report.py           # Converts Maestro JSON output → HTML report
└── README.md
```

---

## 2. System Requirements

| Requirement | Version | Notes |
|---|---|---|
| macOS / Windows / Linux | — | Any modern OS |
| Java (JDK) | 11+ | Required by Maestro CLI |
| Android Studio | Latest | For emulator management |
| Android SDK / ADB | Any recent | Must be on `PATH` |
| Maestro CLI | 2.6.0 | Test runner |
| Python | 3.8+ | For HTML report generation |

---

## 3. Step-by-Step First-Time Setup

Follow every step in order. Do not skip.

---

### Step 1 — Install Java (JDK 11+)

Check if Java is already installed:
```bash
java -version
```
If not installed:
```bash
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
java -version   # should print 17.x
```

---

### Step 2 — Install Maestro CLI

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
```

Restart your terminal, then verify:
```bash
maestro --version
# Expected: 2.6.0
```

---

### Step 3 — Install Android Studio & ADB

1. Download [Android Studio](https://developer.android.com/studio) and install it.
2. Open Android Studio → **More Actions → SDK Manager**.
3. Under **SDK Tools**, make sure **Android SDK Platform-Tools** is checked → Apply.
4. Add ADB to your PATH:
   ```bash
   echo 'export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   adb version   # should print Android Debug Bridge version x.x.x
   ```

---

### Step 4 — Create the Android Emulator

1. Open Android Studio → **More Actions → Virtual Device Manager**.
2. Click **Create Device**.
3. Select **Pixel 4 XL** → Next.
4. Select system image: **API 35 (Android 15)** → Download if needed → Next.
5. Name it `Pixel_4_XL_API_35` → Finish.
6. Click ▶ to start the emulator. Wait until it fully boots (home screen visible).
7. Verify ADB sees it:
   ```bash
   adb devices
   # Expected: emulator-5558   device
   ```

---

### Step 5 — Install the NextSense Budz APK

Get the APK from Milan (or the shared drive), then install it:
```bash
adb -s emulator-5558 install -r /path/to/NextSenseBudz.apk
```

Verify installation:
```bash
adb -s emulator-5558 shell pm list packages | grep nextsense
# Expected: package:io.nextsense.android.budz
```

---

### Step 6 — Add the Google Test Account to the Emulator

The test logs in with Google. The test account must be added to the emulator before running.

1. On the emulator, open **Settings → Accounts → Add Account → Google**.
2. Sign in with:
   - **Email:** `infocuspqapune@gmail.com`
   - **Password:** `Test@123`
3. Complete the sign-in flow (allow all permissions).
4. Go back to the home screen.

> ⚠️ If you skip this step, the Google login in the test will fail.

---

### Step 7 — Enable Bluetooth on the Emulator

```bash
adb -s emulator-5558 shell settings put global bluetooth_on 1
```

Or manually: On the emulator → **Settings → Connected devices → Bluetooth → ON**.

---

### Step 8 — Grant Bluetooth Permissions to the App

```bash
adb -s emulator-5558 shell pm grant io.nextsense.android.budz android.permission.BLUETOOTH_SCAN
adb -s emulator-5558 shell pm grant io.nextsense.android.budz android.permission.BLUETOOTH_CONNECT
```

---

### Step 9 — Clone the Repository

```bash
git clone <repository-url>
cd Maestro
```

---

### Step 10 — Verify Everything is Ready

Run this checklist before executing the test:

```bash
# 1. Java
java -version                          # 11+ required

# 2. Maestro
maestro --version                      # 2.6.0

# 3. ADB + emulator
adb devices                            # emulator-5558 listed as 'device'

# 4. App installed
adb -s emulator-5558 shell pm list packages | grep nextsense

# 5. Google account on emulator
adb -s emulator-5558 shell dumpsys account | grep google

# 6. Maestro Studio is CLOSED
# (Studio and CLI cannot run simultaneously on the same device)
```

All checks must pass before running the test.

---

## 4. Configure Test Credentials

`config/env.yaml` holds per-environment values for `APP_ID` and `TEST_NAME` (used as a reference):

```yaml
env:
  dev:
    APP_ID: io.nextsense.android.budz
    TEST_NAME: Dev_User
  staging:
    APP_ID: io.nextsense.android.budz
    TEST_NAME: Stage_User
  prod:
    APP_ID: io.nextsense.android.budz
    TEST_NAME: Prod_User
```

All credentials (`APP_ID`, `TEST_NAME`, `TEST_EMAIL`, `TEST_PASSWORD`) are set per environment inside `run_tests.sh`. Update the values in the relevant `case` block:

```bash
dev)
  APP_ID="io.nextsense.android.budz"
  TEST_NAME="Dev_User"
  TEST_EMAIL="your-dev-email@example.com"
  TEST_PASSWORD="your-dev-password"
  ;;
staging)
  APP_ID="io.nextsense.android.budz"
  TEST_NAME="Stage_User"
  TEST_EMAIL="your-staging-email@example.com"
  TEST_PASSWORD="your-staging-password"
  ;;
prod)
  APP_ID="io.nextsense.android.budz"
  TEST_NAME="Prod_User"
  TEST_EMAIL="your-prod-email@example.com"
  TEST_PASSWORD="your-prod-password"
  ;;
```

Also update `test-data/users.json` to reflect the credentials in use:
```json
{
  "app_id": "io.nextsense.android.budz",
  "email": "your-email@example.com",
  "password": "your-password",
  "name": "Your Name"
}
```

> ⚠️ Never commit real credentials to Git. Use a `.env` file or CI/CD secrets for production.

---

## 5. Running the Tests

### Always use the run script:

`run_tests.sh` accepts an optional environment argument — `dev`, `staging`, or `prod`. Defaults to `dev` if omitted.

```bash
# Dev (default)
bash run_tests.sh
bash run_tests.sh dev

# Staging
bash run_tests.sh staging

# Prod
bash run_tests.sh prod
```

Or with the full path:

```bash
bash /Users/roshan.giri/Documents/Maestro/run_tests.sh dev
bash /Users/roshan.giri/Documents/Maestro/run_tests.sh staging
bash /Users/roshan.giri/Documents/Maestro/run_tests.sh prod
```

This single command does everything:
1. Clears all previous reports
2. Runs the full onboarding smoke test on `emulator-5558` with the chosen environment's credentials
3. Generates the HTML report
4. Opens the report in your browser automatically

### Manual run (without cleanup):

```bash
maestro test --config config/env.yaml \
  --device emulator-5558 \
  --env APP_ID=io.nextsense.android.budz \
  --env TEST_NAME=Dev_User \
  --env TEST_EMAIL=your-email@example.com \
  --env TEST_PASSWORD=your-password \
  flows/onboarding_smoke.yaml
```

### Visual debugging in Maestro Studio:

```bash
maestro studio --config config/env.yaml flows/onboarding_smoke.yaml
```

> ⚠️ Close Studio before using the CLI — they cannot share the device connection.

---

## 6. Understanding the Report

After every run, `reports/report.html` opens automatically. It shows:

| Metric | Meaning |
|---|---|
| **Total Steps** | All actions and assertions executed |
| **Passed** | Steps that completed successfully (green) |
| **Failed** | Steps that failed — error shown inline (red) |
| **Skipped** | Conditional steps not applicable this run (grey) |
| **Pass Rate** | Overall health of the run |
| **Duration** | Time taken per step (seconds) |

**Debug screenshots** on failure are saved to:
```
reports/<timestamp>/screenshot-❌-<id>-(onboarding_smoke.yaml).png
```

---

## 7. What to Expect

| Item | Value |
|---|---|
| **Typical run duration** | 3–5 minutes |
| **Total screens covered** | 25 screens |
| **Total steps** | ~128 (122 passed, 6 skipped) |
| **Expected pass rate** | 95%+ (6 conditional skips are normal) |
| **Expected result** | All steps COMPLETED or SKIPPED — no FAILED |
| **Report location** | `reports/report.html` (auto-opens) |
| **Screenshots** | `reports/screenshots/screen_17.png`, `reports/screenshots/homescreen.png` |

**Normal SKIPPED steps** (these are expected, not failures):

| Step | Why it skips |
|---|---|
| `Run flow when "Bluetooth is off"` | Bluetooth is already ON |
| `Run flow when "Smartbuds found"` | Emulator already paired from a previous run |
| `Run flow when "Connected devices"` | BT Settings opened to "Pair new device" directly |
| `Run flow when "Rename this device"` | No stale rename dialog from prior run |
| `Run flow when "Available devices"` | Page not shown on this run |
| `Run flow when "Last step: Connect to Smartbuds Audio"` | App already moved past that screen |

---

## 8. Test Coverage

| Screen | Description | Status |
|---|---|---|
| 1 | Sign-in — Continue with Google / Apple ID | ✅ |
| 2 | Enter Name — "Before we continue, what should we call you?" | ✅ |
| 3 | Welcome & Agree — "Welcome ${TEST_NAME}!" | ✅ |
| 4 | Brain Waves | ✅ |
| 5 | Detecting Sleep | ✅ |
| 6 | Restorative Sleep | ✅ |
| 7 | Sound Waves | ✅ |
| 8 | Your Sounds | ✅ |
| 9 | Notifications — Allow notifications | ✅ |
| — | Bluetooth Setup (conditional, BT OFF only) | ✅ |
| 10 | Connect Smartbuds | ✅ |
| 11 | Remove Protective Tape | ✅ |
| 12 | Pairing | ✅ |
| 13 | Smartbuds Found (transitional, conditional) | ✅ |
| 14 | Last Step: Connect to Smartbuds Audio | ✅ |
| 15 | Android BT Settings | ✅ |
| 16 | Navigate Back to App | ✅ |
| 17 | Smartbuds Connected — "Your Smartbuds are connected!" | ✅ |
| 18 | Good Sensor Contact | ✅ |
| 19 | Insert Smartbuds | ✅ |
| 20 | Push Behind Ear Ridges | ✅ |
| 21 | Twist Towards Back of Head | ✅ |
| 22 | Sensor Connection | ✅ |
| 23 | Find Your Perfect Fit | ✅ |
| 24 | Smartbuds Disconnected (emulator only, conditional) | ✅ |
| **25** | **Home Screen — sleep, Fall asleep, Deep Sleep, Nap, toggles, battery** | ✅ |

**Home Screen assertions:**

| Element | Type |
|---|---|
| `sleep` | Sleep mode circle text |
| `Fall asleep` | Section label |
| `Deep Sleep` | Current sleep mode value |
| `Change` | Change mode button |
| `Nap` | Section label |
| `20 min` | Default nap duration |
| `Set timer` | Nap timer button |
| `Disable Touch Controls` | Settings toggle |
| `Disable Voice Prompts` | Settings toggle |
| `Left` | Left bud battery indicator |
| `Right` | Right bud battery indicator |
| `Case` | Case battery indicator |

---

## 9. Known Blockers

| # | Blocker | Impact | Owner |
|---|---|---|---|
| B1 | **No real Smartbuds available for emulator testing** — The emulator cannot simulate an actual BLE device discovery. On emulator, the "Smartbuds disconnected" screen appears and the test uses the `Skip` button to reach Home Screen. On a real device with real Smartbuds, this screen is bypassed automatically. | Full BLE pairing assertion requires real hardware | Dev team |
| B2 | **Google account must be pre-configured on emulator** — Maestro cannot interact with Google's system sign-in dialog (WebView). The account must already exist on the device. | Setup step cannot be automated | Engineering setup |
| B3 | **Maestro Studio and CLI cannot run simultaneously** — Sharing the same gRPC port causes the CLI to fail with `UNAVAILABLE` when Studio is open. | Engineers must remember to close Studio before running CLI tests | Maestro limitation |

---

## 10. Assumptions Made

| # | Assumption |
|---|---|
| A1 | Bluetooth is enabled on the emulator before running (the flow handles the BT-OFF case but BT-ON is the primary path) |
| A2 | The NextSense Budz APK is already installed on the emulator |
| A3 | The Google account pre-fills the name field with the account's display name — the test clears this field and types `${TEST_NAME}` |
| A4 | `clearState: true` resets only the NextSense app state; Android system app state (BT Settings) persists between runs |
| A5 | The emulator is API 35 (Android 15) — behaviour may differ on other API levels |
| A6 | On emulator, after the wear-guide screens, the app shows "Smartbuds disconnected" with a `Skip` button — this is handled conditionally and does not affect real-device runs |

---

## 11. Reliability Observations

### Flaky Areas

| Area | Observation | Mitigation |
|---|---|---|
| **Name field pre-fill** | Google sign-in pre-fills the name field with the account's display name. A plain `tapOn` lands the cursor in the middle of the text. | Fixed: tap at `91%,44%` (right edge of the field, confirmed via `uiautomator dump`) to place cursor at end, then `eraseText: 20` clears the field before typing. |
| **Screen 13 — Smartbuds Found** | Appears on first run; skipped on subsequent runs (emulator retains BT pairing state) | Wrapped in `runFlow: when: visible` conditional — handles both cases |
| **Screen 15 — BT Settings page** | Opens to "Connected devices" or "Pair new device" depending on emulator state | Both pages detected dynamically with separate `runFlow` blocks |
| **Rename device dialog** | Appears if a previous run left BT settings in a broken state | Dismissed automatically with a `runFlow: when: visible: "Rename this device"` guard |
| **Maestro driver startup** | After emulator reboot, the first `maestro test` call may fail (gRPC not ready) | Run twice — driver installs on first attempt, succeeds on second |
| **Screen 24 — Smartbuds Disconnected** | Appears on emulator after wear-guide screens (no real BT hardware) | Handled with `runFlow: when: visible` — conditionally taps `Skip` on emulator, skipped on real device |

### Wait Strategy

| Strategy | Where Used | Reason |
|---|---|---|
| `extendedWaitUntil: visible` | Screen transitions | Waits until the target element appears (up to timeout) before asserting — prevents race conditions |
| `waitForAnimationToEnd` | After every tap | Gives the app time to finish transition animations before the next step |
| `scrollUntilVisible` | Welcome screen (Agree button), Screen 10 (Connect Smartbuds) | Handles long pages where content loads below the visible fold |
| Avoid `sleep` | Everywhere | Hard sleeps are brittle — all waits are condition-based |

---

## 12. Automation Readiness Recommendations

| # | Recommendation | Priority |
|---|---|---|
| R1 | **Expose a test/debug bypass for BLE pairing** — Add a developer flag (e.g. `intent extra` or `deep link`) that skips the BLE pairing step entirely. Standard practice for automating hardware-dependent flows. | 🔴 High |
| R2 | **Use resource IDs as selectors** — Some screens use text-based selectors that will break if copy changes. Adding `testID` / `accessibilityLabel` to key UI elements makes tests resilient to text changes. | 🟡 Medium |
| R3 | **Set up CI/CD pipeline** — Integrate `./run_tests.sh` into GitHub Actions or Bitrise to run automatically on every PR and build. See the example workflow below. | 🟡 Medium |
| R4 | **Separate Google login into a reusable flow** — The login steps can be extracted into `flows/helpers/google_login.yaml` and reused across multiple test files. | 🟡 Medium |
| R5 | **Add Slack/email notification on failure** — Pipe the exit code from `run_tests.sh` to a Slack webhook so the team is alerted immediately when the smoke test fails. | 🟢 Low |
| R6 | **Test on a physical device** — The emulator cannot fully replicate BLE behaviour. Running on a real device with real Smartbuds will give a more accurate reliability picture. | 🟢 Low |

### CI/CD Example — GitHub Actions

Create `.github/workflows/maestro.yml`:

```yaml
name: Maestro Smoke Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  smoke-test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Java
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Install Maestro
        run: curl -Ls "https://get.maestro.mobile.dev" | bash

      - name: Start Android Emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 35
          arch: x86_64
          script: |
            adb install apps/NextSenseBudz.apk
            bash run_tests.sh

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: maestro-report
          path: reports/
```

---

## 13. Adding a New Test

1. Create a new file in `flows/`, e.g. `flows/settings_change_name.yaml`.
2. Use `onboarding_smoke.yaml` as a reference.
3. Add `- wip` to tags while writing; remove it when ready.

```yaml
appId: ${APP_ID}

# Test: <short description>
# Precondition: User must be logged in

tags:
  - smoke
  - wip

---

- launchApp:
    clearState: false    # false = keep login state
- waitForAnimationToEnd:
    timeout: 2000

# Add your steps here
```

---

## 14. Troubleshooting

**Maestro Studio open → CLI fails with `UNAVAILABLE` / gRPC error**
Studio holds the ADB connection. Quit Studio, then run `bash run_tests.sh`.

---

**`${APP_ID}` shows as `undefined` in test output**
Always pass env vars via `--env` flags explicitly (the `run_tests.sh` does this automatically).

---

**`assertVisible` fails — text not found**
Check the failure screenshot:
```
reports/<timestamp>/screenshot-❌-<id>-(onboarding_smoke.yaml).png
```
Common causes: text changed in a new build, loading overlay still visible, system dialog appeared on top.

---

**`assertVisible` fails but the text is clearly on screen**
The app may use Unicode curly apostrophes `'` (U+2019) instead of straight apostrophes `'` (U+0027) in its UI strings. Maestro's `textRegex` matches literally, so a mismatch causes failure even when the element is visible. To diagnose, inspect the `hierarchyRoot` in the debug JSON and check the apostrophe's Unicode code point. Update the YAML assertion to use the curly apostrophe character directly.

---

**Google login fails / name screen not reached**
The Google account is not set up on the emulator. Follow [Step 6](#step-6--add-the-google-test-account-to-the-emulator) again.

---

**Emulator not detected by Maestro**
```bash
adb kill-server && adb start-server && adb devices
```
Then re-run the test.

---

**Maestro driver startup fails after emulator reboot**
Run `bash run_tests.sh` twice. The first run installs the Maestro driver APK; the second run finds it ready.

---

**BT Settings opens to wrong page**
This is expected — the emulator BT state varies between runs. The flow handles both "Connected devices" and "Pair new device" pages automatically.

---

**BT permissions lost after app reinstall**
```bash
adb -s emulator-5558 shell pm grant io.nextsense.android.budz android.permission.BLUETOOTH_SCAN
adb -s emulator-5558 shell pm grant io.nextsense.android.budz android.permission.BLUETOOTH_CONNECT
```

---

*Last updated: June 2026 | Maintained by: Roshan Giri (roshan.giri@infocusp.com)*

---

## Changelog

| Date | Change |
|---|---|
| June 2026 | Added multi-environment support to `run_tests.sh` (`dev` / `staging` / `prod`) |
| June 2026 | Fixed Screen 10 — added `scrollUntilVisible` and increased `extendedWaitUntil` timeout to 15 s after notification permission handling |
| June 2026 | Fixed Unicode apostrophe mismatch (U+2019) in Screen 10 and Screen 11 assertions |
