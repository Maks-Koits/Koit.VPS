const USD_NODE_CLASS = "avby-usd-converted";

function parseBynPrice(text) {
  if (!text) {
    return null;
  }

  if (!/(р|руб|byn)/i.test(text)) {
    return null;
  }

  const normalized = text
    .replace(/\u00A0/g, " ")
    .replace(/,/g, ".")
    .trim();

  const numberMatches = normalized.match(/\d[\d\s]*([.]\d+)?/g);
  if (!numberMatches || numberMatches.length === 0) {
    return null;
  }

  let bestValue = null;
  for (const candidate of numberMatches) {
    const raw = candidate.replace(/\s+/g, "");
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      continue;
    }

    if (bestValue === null || parsed > bestValue) {
      bestValue = parsed;
    }
  }

  return bestValue;
}

function findCandidatePriceNodes() {
  const selectors = [
    "[class*='price']",
    "[class*='Price']",
    "[data-testid*='price']",
    "[data-test*='price']",
    "strong"
  ];

  const nodes = new Set();
  for (const selector of selectors) {
    document.querySelectorAll(selector).forEach((element) => {
      nodes.add(element);
    });
  }

  return Array.from(nodes);
}

function findTitleNodeInScope(scope) {
  const selectors = [
    "h1",
    "h2",
    "h3",
    "[class*='title']",
    "[class*='Title']",
    "[data-testid*='title']",
    "[data-test*='title']",
    "a[href*='/bike/']"
  ];

  for (const selector of selectors) {
    const candidates = scope.querySelectorAll(selector);
    for (const element of candidates) {
      if (!(element instanceof HTMLElement)) {
        continue;
      }
      const text = element.innerText.trim();
      if (text.length < 3) {
        continue;
      }
      if (element.classList.contains(USD_NODE_CLASS)) {
        continue;
      }
      return element;
    }
  }

  return null;
}

function findRelatedTitleNode(priceNode) {
  let scope = priceNode.closest("article, li, [class*='card'], [class*='Card'], [class*='item'], [class*='Item']");
  if (!(scope instanceof HTMLElement)) {
    scope = priceNode.parentElement;
  }

  let depth = 0;
  while (scope && depth < 6) {
    const titleNode = findTitleNodeInScope(scope);
    if (titleNode) {
      return titleNode;
    }
    scope = scope.parentElement;
    depth += 1;
  }

  return findTitleNodeInScope(document);
}

function formatUsd(usdValue) {
  const rounded = Math.round(usdValue);
  return new Intl.NumberFormat("ru-RU", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(rounded);
}

function requestUsdRate() {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type: "GET_USD_RATE" }, (response) => {
      const runtimeError = chrome.runtime.lastError;
      if (runtimeError) {
        reject(new Error(runtimeError.message));
        return;
      }

      if (!response?.ok || !Number.isFinite(response.rate)) {
        reject(new Error(response?.error || "USD rate unavailable"));
        return;
      }

      resolve(response.rate);
    });
  });
}

function upsertUsdNode(titleElement, usdText) {
  let node = titleElement.querySelector(`.${USD_NODE_CLASS}`);
  if (!node) {
    node = document.createElement("span");
    node.className = USD_NODE_CLASS;
    titleElement.appendChild(node);
  }
  node.textContent = ` (${usdText})`;
}

async function convertPagePrices() {
  let rate;
  try {
    rate = await requestUsdRate();
  } catch (error) {
    console.warn("[avby-usd] Could not get NBRB rate:", error);
    return;
  }

  const nodes = findCandidatePriceNodes();
  const titleToPrice = new Map();

  for (const node of nodes) {
    if (!(node instanceof HTMLElement)) {
      continue;
    }

    const bynPrice = parseBynPrice(node.innerText);
    if (!bynPrice) {
      continue;
    }

    const titleNode = findRelatedTitleNode(node);
    if (!titleNode) {
      continue;
    }

    const currentPrice = titleToPrice.get(titleNode) || 0;
    if (bynPrice > currentPrice) {
      titleToPrice.set(titleNode, bynPrice);
    }
  }

  for (const [titleNode, bynPrice] of titleToPrice.entries()) {
    const usd = bynPrice / rate;
    if (!Number.isFinite(usd) || usd <= 0) {
      continue;
    }
    upsertUsdNode(titleNode, `≈ $${formatUsd(usd)}`);
  }
}

function debounce(fn, delayMs) {
  let timeoutId = null;
  return () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(fn, delayMs);
  };
}

const runConversion = debounce(() => {
  convertPagePrices().catch((error) => {
    console.warn("[avby-usd] Conversion failed:", error);
  });
}, 150);

runConversion();

const observer = new MutationObserver(() => {
  runConversion();
});

observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
  characterData: true
});
