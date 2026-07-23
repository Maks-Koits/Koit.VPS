const USD_NODE_CLASS = "kufar-usd-converted";

function isPerUnitPrice(element, text) {
  if (/за\s*м/i.test(text || "")) {
    return true;
  }

  if (!(element instanceof HTMLElement)) {
    return false;
  }

  const className = element.className || "";
  if (/per_square|square_meter|price--secondary|price_secondary/i.test(className)) {
    return true;
  }

  // "за м2" may live in a sibling/parent label, not in the number node itself
  const parent = element.parentElement;
  if (parent instanceof HTMLElement) {
    const parentClass = parent.className || "";
    if (/per_square|square_meter|price--secondary|price_secondary/i.test(parentClass)) {
      return true;
    }
    if (/за\s*м/i.test(parent.innerText || "")) {
      const own = (text || "").replace(/\s+/g, " ").trim();
      const parentText = (parent.innerText || "").replace(/\s+/g, " ").trim();
      if (parentText.length <= own.length + 20) {
        return true;
      }
    }
  }

  return false;
}

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
    "[class*='price--main']",
    "[class*='styles_main__']",
    "[class*='price']",
    "[class*='Price']",
    "[data-testid*='price']",
    "[data-test*='price']",
    "[itemprop='price']",
    "strong"
  ];

  const nodes = new Set();
  for (const selector of selectors) {
    document.querySelectorAll(selector).forEach((element) => {
      nodes.add(element);
    });
  }

  // Fallback: scan short text nodes that look like "37 582 р."
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  let current = walker.nextNode();
  while (current) {
    if (
      current instanceof HTMLElement &&
      current.children.length === 0 &&
      current.innerText &&
      current.innerText.length < 40 &&
      /(р|руб|byn)/i.test(current.innerText)
    ) {
      nodes.add(current);
    }
    current = walker.nextNode();
  }

  return Array.from(nodes);
}

function pickLeafPriceNodes(candidates) {
  return candidates.filter((node) => {
    if (!(node instanceof HTMLElement)) {
      return false;
    }

    return !candidates.some(
      (other) => other !== node && node.contains(other)
    );
  });
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

function upsertUsdNearPrice(priceNode, usdText) {
  const next = priceNode.nextElementSibling;
  let node =
    next instanceof HTMLElement && next.classList.contains(USD_NODE_CLASS)
      ? next
      : null;

  if (!node) {
    node = document.createElement("span");
    node.className = USD_NODE_CLASS;
    priceNode.insertAdjacentElement("afterend", node);
  }

  node.textContent = ` (${usdText})`;
}

async function convertPagePrices() {
  let rate;
  try {
    rate = await requestUsdRate();
  } catch (error) {
    console.warn("[kufar-usd] Could not get NBRB rate:", error);
    return;
  }

  const priced = [];
  for (const node of findCandidatePriceNodes()) {
    if (!(node instanceof HTMLElement)) {
      continue;
    }

    if (node.classList.contains(USD_NODE_CLASS)) {
      continue;
    }

    const text = node.innerText;
    if (isPerUnitPrice(node, text)) {
      continue;
    }

    const bynPrice = parseBynPrice(text);
    if (!bynPrice) {
      continue;
    }

    priced.push({ node, bynPrice });
  }

  const leafNodes = new Set(pickLeafPriceNodes(priced.map((item) => item.node)));

  for (const { node, bynPrice } of priced) {
    if (!leafNodes.has(node)) {
      continue;
    }

    const usd = bynPrice / rate;
    if (!Number.isFinite(usd) || usd <= 0) {
      continue;
    }
    upsertUsdNearPrice(node, `$${formatUsd(usd)}`);
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
    console.warn("[kufar-usd] Conversion failed:", error);
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
