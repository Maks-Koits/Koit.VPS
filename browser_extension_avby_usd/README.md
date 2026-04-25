# AV.BY BYN -> USD Extension

Browser extension (Manifest V3) that adds USD price near BYN price on AV.BY pages using official NBRB exchange rate.

## Files

- `manifest.json` - extension manifest.
- `background.js` - fetches and caches NBRB USD rate for 1 hour.
- `content.js` - finds BYN price on page and appends USD value.
- `styles.css` - style for inserted USD element.

## Load in Chrome / Edge

1. Open `chrome://extensions` (or `edge://extensions`).
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select this folder: `browser_extension_avby_usd`.

## Test

1. Open any AV.BY ad page, for example:
   `https://moto.av.by/bike/suzuki/sv/131070213`
2. Check price block: you should see `(... ≈ $XXXX)` near BYN price.

## Notes

- If NBRB API is unavailable, extension uses stale cached rate if present.
- If no rate is available at all, conversion is skipped safely.
