# راهنمای شروع و استفاده از AngysGuard / Laptop Guard

> **English:** Persian-first, bilingual guide for the current Linux release. Canonical security and platform claims remain in the root README, `PLATFORM_SUPPORT.md`, and `CONTROL_MODES.md`.

## کاربرد درست / When to use it

AngysGuard برای **دستگاهی است که مالک آن هستید یا مجوز صریح مدیریت آن را دارید**. نسخهٔ فعلی Linux-first است و برای محافظت از لپ‌تاپ شخصی، هشدار محدود از طریق Telegram/Bale، بررسی رخدادها و پاسخ امن محلی مناسب است.

برای نظارت پنهانی، کنترل دستگاه دیگران، keylogging، دریافت رمز سیستم‌عامل، اجرای shell از راه دور یا مرور فایل‌های دلخواه طراحی نشده است.

## پلتفرم فعلی / Current platform

| مورد | وضعیت |
| --- | --- |
| Linux / Ubuntu-oriented desktop | مسیر فعلی محصول؛ برای قابلیت‌های فعال Doctor را اجرا کنید |
| Telegram و Bale | providerهای قابل پیکربندی؛ روی دستگاه خودتان تست live لازم است |
| Windows و Android | هنوز پشتیبانی عمومی تأییدشده نیستند |

## نصب و شروع / Install and start

از ریشهٔ repository اجرا کنید:

```bash
./install.sh
./run.sh
```

`./install.sh` محیط Python را آماده می‌کند. `./run.sh` داشبورد terminal فارسی/English را باز می‌کند؛ Setup را از همان‌جا انتخاب کنید.

دستورهای مستقیم:

```bash
./run.sh setup      # پیکربندی اولیه یا ادامهٔ setup
./run.sh doctor     # بررسی سلامت و راهنمای رفع مشکل
./run.sh run        # اجرای runtime Guard
./run.sh status     # وضعیت فعلی
```

## پیکربندی اولیه / First-time setup

1. نام دستگاه و profile اولیه را انتخاب کنید.
2. provider را انتخاب کنید: `telegram`، `bale` یا `local`.
3. token را فقط در prompt محلی وارد کنید؛ هرگز در chat، screenshot، issue یا repository قرار ندهید.
4. برای Telegram پشت Hidify، در prompt proxy فقط این مقدار را وارد کنید (بدون `Proxy URL:`):

   ```text
   http://127.0.0.1:12334
   ```

5. شناسهٔ owner را فقط برای private chat خودتان ثبت کنید.
6. `./run.sh doctor` و سپس `./run.sh test bot` را اجرا کنید.

## چند دستگاه و bot / Multiple devices and bots

در self-hosted mode فعلی، هر laptop باید bot/token جداگانه داشته باشد. چند runtime محلی با یک token مشترک updateهای provider را بین خودشان رقابتی دریافت می‌کنند؛ command ممکن است به دستگاه نادرست برسد یا از دست برود. Multi-device با یک bot رسمی، به managed service نیاز دارد و هنوز current support نیست.

## داشبورد terminal / Terminal dashboard

`./run.sh` گزینه‌های Setup، Start Guard، Arm/Disarm، Live status، hardware tests، Doctor، Autostart و events را نشان می‌دهد. Disarm و عملیات پرخطر confirmation دارند.

## کنترل bot / Telegram and Bale control

پس از setup، `/menu` این بخش‌ها را ارائه می‌دهد:

```text
🏠 Dashboard     🛡 Protection     🚨 Incidents
📷 Evidence      💻 Device Health  ⚙️ Settings
```

- Dashboard: profile، protection، battery، camera/input، provider و queue.
- Incidents: filter severity، acknowledgement و evidence محدود/ثبت‌شده.
- Settings: quiet hours و notification rules؛ high/critical در quiet hours هم ارسال می‌شوند.
- Recovery: گزارش redacted می‌دهد. Re-pair/revoke فقط محلی است: `./run.sh reconfigure owner`.

کنترل حساس فقط از private owner chat پذیرفته می‌شود. Unlock و power actionها نیازمند opt-in محلی و confirmation هستند.

## نگهداری و حریم خصوصی / Maintenance and privacy

```bash
./run.sh doctor
./run.sh events --limit 20
./run.sh service status
./run.sh reconfigure provider
./run.sh reconfigure owner
```

Retention به‌طور محلی evidence منقضی را پاک می‌کند. Outbox فقط متن را به‌شکل محدود retry می‌کند؛ media خودکار تکرار نمی‌شود. رمز سیستم‌عامل هرگز نباید به Telegram، Bale، backend یا environment variable معمولی ارسال شود.

برای جزئیات بیشتر: [Configuration](CONFIGURATION.md)، [Security](SECURITY.md)، [Testing](TESTING.md)، [Control modes](CONTROL_MODES.md).
