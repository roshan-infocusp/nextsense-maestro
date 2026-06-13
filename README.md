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
7. [Test Coverage](#7-test-coverage)
8. [Reliability Notes](#8-reliability-notes)
9. [What I Would Improve Given More Time](#9-what-i-would-improve-given-more-time)
10. [Recommendations for Improvement](#10-recommendations-for-improvement)
11. [Maestro Limitations — Color & Visual Testing](#11-maestro-limitations--color--visual-testing)


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
│       ├── screen_14.png        # Last step: Connect to Smartbuds Audio
│       ├── screen_17.png        # Your Smartbuds are connected!
│       └── homescreen.png       # Final Home Screen confirmation
│
├── run_tests.sh                 # ← Always use this to run tests
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

### Step 7 — Clone the Repository

```bash
git clone <repository-url>
cd Maestro
```

---

### Step 8 — Verify Everything is Ready

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

## 5. Running the Tests Locally


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
3. Generates a detailed HTML report via Maestro's native `--format html-detailed` flag
4. Opens `reports/report.html` in your browser automatically

### Manual run (without cleanup):

```bash
maestro test --config config/env.yaml \
  --device emulator-5558 \
  --format html-detailed \
  --output reports/report.html \
  --env APP_ID=io.nextsense.android.budz \
  --env TEST_NAME=Dev_User \
  --env TEST_EMAIL=your-email@example.com \
  --env TEST_PASSWORD=your-password \
  flows/onboarding_smoke.yaml
```

> ⚠️ Close Studio before using the CLI — they cannot share the device connection.

---

## 6. Understanding the Report

After every run, `reports/report.html` opens automatically. It is generated natively by Maestro using the `--format html-detailed` flag, which includes a step-by-step breakdown of every command executed.

The top of the report shows a **Flow Execution Summary** with three cards:

| Card | Meaning |
|---|---|
| **Total number of Flows** | How many flow files were executed |
| **Failed Flows** | Flows that ended in ERROR (red) |
| **Successful Flows** | Flows that passed completely (green) |

Expanding a flow reveals its per-step detail:

| Field | Meaning |
|---|---|
| **Test Steps (N)** | Total number of steps executed in that flow |
| **✅ step name** | Step completed successfully |
| **❌ step name** | Step failed — error message shown above the step list |
| **Duration badge** | Time taken for that step (e.g. `1ms`, `447ms`, `1.6s`) |

Use `--format html` instead of `--format html-detailed` if you only need a simple summary without per-step details.

**Debug screenshots** and other artifacts (video, AI reports) are saved to the `reports/` directory as configured by `testOutputDir` in `config/env.yaml`.

---


## 7. Test Coverage

| Screen | Description | Status |
|---|---|---|
| 1 | Sign-in — auto-skipped via `automation_sign_in: true` launch argument | ✅ |
| 2 | Enter Name — "Before we continue, what should we call you?" | ✅ |
| 3 | Welcome & Agree — "Welcome ${TEST_NAME}!" | ✅ |
| 4 | Brain Waves | ✅ |
| 5 | Detecting Sleep | ✅ |
| 6 | Restorative Sleep | ✅ |
| 7 | Sound Waves | ✅ |
| 8 | Your Sounds | ✅ |
| 9 | Notifications — Allow notifications | ✅ |
| 10 | Connect Smartbuds | ✅ |
| 11 | Remove Protective Tape | ✅ |
| 12 | Pairing | ✅ |
| 13 | Smartbuds Found (transitional, conditional) | ✅ |
| 14 | Last Step: Connect to Smartbuds Audio — tapping "Go to settings" auto-advances (fake BT permission, no real Settings page opens) | ✅ |
| 17 | Smartbuds Connected — "Your Smartbuds are connected!" | ✅ |
| 18 | Good Sensor Contact | ✅ |
| 19 | Insert Smartbuds | ✅ |
| 20 | Push Behind Ear Ridges | ✅ |
| 21 | Twist Towards Back of Head | ✅ |
| 22 | Sensor Connection | ✅ |
| 23 | Find Your Perfect Fit | ✅ |
| 24 | Smartbuds Disconnected (emulator only, conditional) | ✅ |
| 25 | Home Screen — sleep, Fall asleep, Deep Sleep, Nap, toggles, battery | ✅ |

---

## 8. Reliability Notes

### Areas That May Be Flaky

1. **Smartbuds Found Screen** — This screen appears only briefly. Sometimes it may disappear before Maestro detects it, causing the step to be skipped.
2. **Emulator / ADB Connection Issues** — Occasionally the emulator may lose connection with ADB. This is an environment issue rather than a test script issue.
3. **Name Input Field** — The test taps a specific position inside the name field before entering text. This behavior may vary across devices and screen sizes.
4. **Timeouts** — Most waits are limited. On slower machines or CI runners, some screens may take longer to load and cause failures.

### Waits, Permissions & BLE Handling

#### Wait Strategy

The framework uses smart waits instead of fixed delays:
- `extendedWaitUntil` — waits for UI elements to appear.
- `waitForAnimationToEnd` — waits for screen transitions and animations to finish.

This helps make the tests faster and more stable.

#### Permission Handling

- Bluetooth permissions are granted automatically before execution.
- Notification permission is handled within the test flow.

#### BLE Connection Handling

- The app uses a fake Bluetooth permission implementation — tapping "Go to settings" on the Last Step screen auto-advances to the next screen without opening real Android Bluetooth Settings.
- Pairing success is verified through the application's success message.
- Additional handling is included for emulator-specific Bluetooth disconnection cases (Screen 24).


---

## 9. What I Would Improve Given More Time

### 1. Add Retry Mechanism for Environment Failures

Implement automatic retries for temporary emulator or ADB connection issues to reduce false failures.

### 2. Increase Cross-Platform Support

Refactor the framework to support both Android and iOS by separating platform-specific steps while reusing common onboarding flows.

The current `onboarding_smoke.yaml` flow is designed and validated for Android and contains Android-specific actions such as Bluetooth Settings navigation and permission handling. Given more time, I would create dedicated iOS-specific flows for platform-dependent steps while keeping shared onboarding validations reusable. This would improve maintainability and enable reliable execution across both Android and iOS devices.

### 3. Improve Logging and Reporting

Add more detailed logs and reporting on UI elements that are visible, not visible, or not interactable to simplify debugging failures.

### 4. Optimize Timeout Strategy

Review and fine-tune timeout values based on real execution data to balance execution speed and stability.

---

## 10. Recommendations for Improvement

- Replace coordinate-based taps with UI element selectors wherever possible.
- Grant location permission in CI for better Android compatibility.
- Add automatic retry for temporary ADB connection failures.
- Improve handling of the temporary "Smartbuds Found" screen for better visibility and debugging.

---

## 11. Maestro Limitations — Color & Visual Testing

Maestro interacts with UI through the **accessibility tree** (element IDs, text, labels) — not visual or pixel properties. Color is a visual attribute, not an accessibility attribute, so it cannot be tested directly.

### Advantages of Maestro's Approach

| Advantage | Detail |
|---|---|
| **Fast & stable** | No flaky pixel comparisons; works even if design changes slightly |
| **Cross-platform** | Same YAML runs on iOS and Android |
| **Simple syntax** | Easy to write and maintain |
| **Resilient to minor UI tweaks** | Resizing, padding changes won't break tests |

### Disadvantages (for color testing)

| Limitation | Detail |
|---|---|
| **Cannot assert colors** | Can't check if a button is red or text is blue |
| **No visual regression testing** | Won't catch accidental color changes |
| **No pixel-level inspection** | Can't verify brand colors, accessibility contrast ratios, or dark mode colors |

### Alternatives for Color & Visual Testing

| Tool | Purpose |
|---|---|
| **Appium** | Can read some color properties via platform APIs |
| **Percy / Chromatic** | Visual snapshot testing — catches color regressions |
| **Screenshot diffing** | Compare before/after screenshots pixel by pixel |
| **Accessibility scanners** | Check color contrast ratios (e.g., WCAG compliance) |

> **Recommendation:** Use Maestro for functional flow testing and pair it with a visual testing tool (e.g.Percy) if color or design validation is required.
