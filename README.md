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

### Step 6 — Grant Bluetooth Permissions to the App

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

---



