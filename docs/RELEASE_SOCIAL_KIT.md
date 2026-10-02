# AngysGuard local-first dashboard prerelease — social kit

Use this kit after the GitHub prerelease and npm `1.0.1` packages are publicly
visible. Replace the bracketed release URL before publishing. Do not claim that
Windows is supported or that the dashboard has completed full hardware/provider
qualification.

## Shared facts

- Linux-first, owner-controlled device protection tooling.
- `@angysguard/linux-agent@1.0.1` provides `angysguard` in the terminal.
- When the optional Linux dashboard `.deb` is installed, `angysguard` lets the
  owner choose dashboard or terminal.
- Bot credentials remain local; fixed bot actions are not a remote shell.
- The Linux dashboard is a prerelease; Windows remains experimental.

## English launch post

AngysGuard’s local-first dashboard prerelease is ready for Linux testing.

Install the terminal agent with `npm install -g @angysguard/linux-agent`, then
run `angysguard`. If you install the optional `.deb` dashboard too, choose the
dashboard or terminal from one command.

Your bot token stays on your device. Remote controls remain fixed, owner-only
actions—never a remote shell. Linux dashboard: prerelease. Windows: still
experimental.

Release: [URL]

#AngysGuard #Linux #OpenSource #CyberSecurity #Privacy #TelegramBot #Bale

## Persian launch post

پیش‌انتشار داشبورد محلی AngysGuard برای تست روی Linux آماده است.

با `npm install -g @angysguard/linux-agent` دستور `angysguard` را نصب کنید.
اگر داشبورد اختیاری `.deb` را هم نصب کنید، با همان دستور بین dashboard و
terminal انتخاب می‌کنید.

توکن بات فقط روی دستگاه شما می‌ماند. کنترل‌های بات فقط actionهای مشخص و
مجازِ مالک هستند؛ remote shell نداریم. داشبورد Linux در مرحلهٔ prerelease و
Windows همچنان experimental است.

انتشار: [URL]

#انجیس_گارد #لینوکس #امنیت #حریم_خصوصی #متن_باز #تلگرام #بله

## Channel adaptations

| Channel | Use | Asset |
| --- | --- | --- |
| X / Threads | Use the first two paragraphs plus release URL | `docs/assets/brand/angysguard-readme-hero.svg` |
| LinkedIn | Use the full English post and a short feature list | same hero, rendered to PNG if required |
| Telegram / Bale channel | Use the Persian post, then add the install command in a code block | app icon + hero |
| Instagram | Use Persian or English as caption; place the release URL in profile/story | rendered social-preview PNG |

Before posting, render the existing social preview with `python
scripts/generate_brand_assets.py` if `angysguard-social-preview.png` is absent.
Never include bot tokens, owner IDs, device names, screenshots of secrets, or
unqualified Windows-support wording.
