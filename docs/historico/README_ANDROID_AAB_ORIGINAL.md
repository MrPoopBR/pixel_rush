# Pixel Rush — Android AAB via GitHub Actions

This repository builds a signed Android App Bundle (`.aab`) for the Pygame Community Edition (pygame-ce) Android/SDL2 recipe. The runner uses Ubuntu 24.04, Python 3.14 for Buildozer tooling, Python/hostpython 3.12.12 for the Android app, Android target API 36, minimum/NDK API 26, NDK 28c, and ARM64 only.

> **Public repository warning:** all committed source code, including `main.py`, is public and can be copied. Never commit the `.jks`, passwords, base64 keystore, or other credentials. `.gitignore` excludes common signing key formats, but always verify `git status` before pushing.

## Before publishing

1. Check `buildozer.spec`. Its package ID is currently `com.pixelrush.runner` (`package.domain = com.pixelrush`, `package.name = runner`). If your app already exists in Google Play Console, change these fields to the exact existing application ID **before** your first upload; an app's package ID cannot be changed for future updates.
2. The version code is `1`. Increase `android.numeric_version` by at least one for every subsequent upload.
3. Create a **public, empty GitHub repository** (do not initialize it with a README/license/.gitignore, because these files are already included here).
4. Unzip this project folder locally and push its contents to the empty repository, or use GitHub Desktop to add the folder to the repo.

## Set GitHub Actions secrets

Open **Settings → Secrets and variables → Actions → New repository secret** and add all four secrets:

- `PIXELRUSH_KEYSTORE_B64`: the original `pixelrush-upload-key.jks` encoded as one line of Base64. Do not upload the JKS itself to the repository.
- `PIXELRUSH_KEYSTORE_PASS`: the keystore password.
- `PIXELRUSH_KEY_PASS`: the private-key/alias password (may be the same as the keystore password).
- `PIXELRUSH_KEY_ALIAS`: the exact alias, previously `pixelrush-upload` if that is still the alias in your key.

### Encode the JKS on Windows PowerShell

Run locally, changing the path to where the original JKS file is saved:

```powershell
$bytes = [System.IO.File]::ReadAllBytes("$HOME\Downloads\pixelrush-upload-key.jks")
[Convert]::ToBase64String($bytes) | Set-Clipboard
```

Paste the clipboard contents into the `PIXELRUSH_KEYSTORE_B64` secret. Do not paste the Base64 value in an issue, commit, README, or chat. Keep an offline backup of the original `.jks`.

## Run the build

1. In the repository, open the **Actions** tab.
2. Select **Build Pixel Rush Android AAB**.
3. Click **Run workflow** and select the `main` branch.
4. Open the resulting workflow run and wait for the job to complete. The workflow prints heartbeat messages while native compilation is active, redacts signing passwords from the log, and has a 350-minute timeout.
5. Download the `pixel-rush-android-aab` artifact. The sanitized diagnostic log is uploaded separately as `pixel-rush-build-log` if needed.

The workflow is manual-only and refuses signed builds on branches other than `main`. Do not add automatic signed builds to `pull_request` events in a public repository.

## Notes and limitations

- The first Android build compiles CPython, SDL2, pygame-ce, and native dependencies, so it can still take a while. The workflow caches SDK/NDK and build directories for later builds; cache entries are subject to GitHub Actions cache storage/eviction limits.
- This uses a community pygame-ce Android recipe. A successful compilation does not replace testing the resulting app on a real Android device.
- ARM64 only means 32-bit-only devices are not supported by this build.
- GitHub-hosted standard runners for public repositories currently provide 4 vCPUs and 16 GB RAM and are free/unlimited for public repos, but ephemeral disk space is limited; the build workflow removes several unused preinstalled tools to free space.
- Do not commit the `.jks`, passwords, `build-release.log`, or `.aab` file.
