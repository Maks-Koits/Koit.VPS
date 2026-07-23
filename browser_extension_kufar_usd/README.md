# Kufar.by BYN -> USD Extension

Browser extension (Manifest V3) that adds USD price near BYN price on Kufar.by pages using official NBRB exchange rate.

## Files

- `manifest.json` - extension manifest.
- `background.js` - fetches and caches NBRB USD rate for 24 hours.
- `content.js` - finds BYN price on page and appends USD value.
- `styles.css` - style for inserted USD element.

## Load in Chrome / Edge

1. Open `chrome://extensions` (or `edge://extensions`).
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select this folder: `browser_extension_kufar_usd`.

## Test

1. Open any Kufar ad page, for example:
   `https://re.kufar.by/vi/minskij-rajon/kupit/dom/dacha/1058572702`
2. Check the price block: you should see `($XXXX)` right after the BYN price.

## Notes

- Works on `kufar.by` and subdomains (`re.kufar.by`, etc.).
- Skips price-per-m² (`per_square_meter` / «р. за м²») so only the main price is converted.
- If NBRB API is unavailable, extension uses stale cached rate if present.
- If no rate is available at all, conversion is skipped safely.
