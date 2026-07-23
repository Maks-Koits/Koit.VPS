const NBRB_USD_RATE_URLS = [
  "https://api.nbrb.by/exrates/rates/USD?parammode=2",
  "https://www.nbrb.by/api/exrates/rates/431?parammode=2"
];
const FALLBACK_RATE_URL = "https://open.er-api.com/v6/latest/USD";
const RATE_CACHE_KEY = "usdRateCache";
const RATE_TTL_MS = 24 * 60 * 60 * 1000;
const REQUEST_TIMEOUT_MS = 7000;

async function fetchJsonWithTimeout(url, timeoutMs) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { cache: "no-store", signal: controller.signal });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

function parseNbrbRate(payload) {
  const officialRate = Number(payload?.Cur_OfficialRate);
  if (!Number.isFinite(officialRate) || officialRate <= 0) {
    throw new Error("Invalid NBRB rate value");
  }
  return officialRate;
}

async function getRateFromNBRB() {
  let lastError = null;

  for (const url of NBRB_USD_RATE_URLS) {
    try {
      const payload = await fetchJsonWithTimeout(url, REQUEST_TIMEOUT_MS);
      const rate = parseNbrbRate(payload);
      return { rate, updatedAt: Date.now(), source: "nbrb" };
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("All NBRB endpoints failed");
}

async function getRateFromFallback() {
  const payload = await fetchJsonWithTimeout(FALLBACK_RATE_URL, REQUEST_TIMEOUT_MS);
  const bynPerUsd = Number(payload?.rates?.BYN);

  if (!Number.isFinite(bynPerUsd) || bynPerUsd <= 0) {
    throw new Error("Invalid fallback rate value");
  }

  return { rate: bynPerUsd, updatedAt: Date.now(), source: "fallback" };
}

async function loadFreshRate() {
  try {
    return await getRateFromNBRB();
  } catch (nbrbError) {
    const fallbackRate = await getRateFromFallback();
    return { ...fallbackRate, warning: `NBRB unavailable: ${String(nbrbError)}` };
  }
}

async function getUsdRate() {
  const storageResult = await chrome.storage.local.get(RATE_CACHE_KEY);
  const cached = storageResult[RATE_CACHE_KEY];

  if (
    cached &&
    Number.isFinite(cached.rate) &&
    Number.isFinite(cached.updatedAt) &&
    Date.now() - cached.updatedAt < RATE_TTL_MS
  ) {
    return { ...cached, source: "cache" };
  }

  try {
    const fresh = await loadFreshRate();
    await chrome.storage.local.set({ [RATE_CACHE_KEY]: fresh });
    return fresh;
  } catch (error) {
    if (cached && Number.isFinite(cached.rate) && Number.isFinite(cached.updatedAt)) {
      return { ...cached, source: "stale-cache", warning: String(error) };
    }
    throw error;
  }
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "GET_USD_RATE") {
    return false;
  }

  getUsdRate()
    .then((data) => {
      sendResponse({ ok: true, ...data });
    })
    .catch((error) => {
      sendResponse({ ok: false, error: String(error) });
    });

  return true;
});
