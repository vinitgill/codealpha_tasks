// ===== Configuration =====
// Points to the live backend on Render. If running the backend locally,
// change this back to "http://127.0.0.1:8000".
const API_BASE = "https://ai-translator-t8g4.onrender.com";

// ===== Grab all the elements we need =====
const inputText = document.getElementById("input-text");
const outputText = document.getElementById("output-text");
const charCount = document.getElementById("char-count");
const detectedLang = document.getElementById("detected-lang");
const targetLanguage = document.getElementById("target-language");
const customLanguage = document.getElementById("custom-language");
const translateBtn = document.getElementById("translate-btn");
const translateBtnText = document.getElementById("translate-btn-text");
const toneButtons = document.querySelectorAll(".tone-btn");
const grammarBtn = document.getElementById("grammar-btn");
const copyBtn = document.getElementById("copy-btn");
const downloadBtn = document.getElementById("download-btn");
const speakBtn = document.getElementById("speak-btn");
const themeToggle = document.getElementById("theme-toggle");
const wordInput = document.getElementById("word-input");
const explainBtn = document.getElementById("explain-btn");
const explainResult = document.getElementById("explain-result");
const historyList = document.getElementById("history-list");
const clearHistoryBtn = document.getElementById("clear-history-btn");
const toast = document.getElementById("toast");

// ===== State =====
let selectedTone = "neutral";
let currentTranslation = "";
let currentLangCode = "en-US";

// ===== Helper: show a toast message =====
function showToast(message) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 2500);
}

// ===== Character counter =====
inputText.addEventListener("input", () => {
  charCount.textContent = `${inputText.value.length} / 2000`;
});

// ===== Target language helpers (handles the "Other" custom option) =====
function getTargetLanguage() {
  return targetLanguage.value === "custom" ? customLanguage.value.trim() : targetLanguage.value;
}

function getTargetLangCode() {
  const selectedOption = targetLanguage.options[targetLanguage.selectedIndex];
  return selectedOption.dataset.langCode || "en-US"; // fallback to English if unknown
}

targetLanguage.addEventListener("change", () => {
  customLanguage.classList.toggle("hidden", targetLanguage.value !== "custom");
});

// ===== Tone selector =====
toneButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    toneButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    selectedTone = btn.dataset.tone;
  });
});

// ===== Dark / Light mode =====
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
}
// Default to system preference, no localStorage needed for theme itself
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(prefersDark ? "dark" : "light");

themeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
});

// ===== Translate =====
async function translate() {
  const text = inputText.value.trim();
  const lang = getTargetLanguage();

  if (!text) {
    showToast("Type something to translate first");
    return;
  }
  if (!lang) {
    showToast("Type a target language first");
    return;
  }

  translateBtn.disabled = true;
  translateBtnText.textContent = "Translating...";
  outputText.textContent = "";

  try {
    const response = await fetch(`${API_BASE}/api/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        target_language: lang,
        tone: selectedTone,
      }),
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || "Translation failed");
    }

    const data = await response.json();
    currentTranslation = data.translation;
    currentLangCode = getTargetLangCode();
    outputText.textContent = data.translation;
    detectedLang.textContent = `(detected: ${data.source_language})`;

    saveToHistory(text, data.translation, lang);
  } catch (err) {
    showToast(err.message);
  } finally {
    translateBtn.disabled = false;
    translateBtnText.textContent = "Translate";
  }
}

translateBtn.addEventListener("click", translate);

// ===== Grammar correction =====
grammarBtn.addEventListener("click", async () => {
  const text = inputText.value.trim();
  if (!text) {
    showToast("Type something first");
    return;
  }
  grammarBtn.textContent = "Checking...";
  try {
    const response = await fetch(`${API_BASE}/api/grammar-check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    if (data.had_errors) {
      inputText.value = data.corrected_text;
      charCount.textContent = `${inputText.value.length} / 2000`;
      showToast("Grammar fixed ✓");
    } else {
      showToast("No grammar issues found ✓");
    }
  } catch (err) {
    showToast("Grammar check failed");
  } finally {
    grammarBtn.textContent = "✓ Fix grammar";
  }
});

// ===== Copy =====
copyBtn.addEventListener("click", () => {
  if (!currentTranslation) return showToast("Nothing to copy yet");
  navigator.clipboard.writeText(currentTranslation);
  showToast("Copied to clipboard");
});

// ===== Download =====
downloadBtn.addEventListener("click", () => {
  if (!currentTranslation) return showToast("Nothing to download yet");
  const blob = new Blob([currentTranslation], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "translation.txt";
  a.click();
  URL.revokeObjectURL(url);
});

// ===== Text-to-speech (AI-generated audio, with browser voice as fallback) =====
let cachedVoices = [];
function loadVoices() {
  cachedVoices = speechSynthesis.getVoices();
}
loadVoices();
speechSynthesis.onvoiceschanged = loadVoices;

function guessLangCodeFromScript(text) {
  const scriptRanges = [
    { range: /[\u0900-\u097F]/, code: "hi-IN" },
    { range: /[\u0A00-\u0A7F]/, code: "pa-IN" },
    { range: /[\u0980-\u09FF]/, code: "bn-IN" },
    { range: /[\u0B80-\u0BFF]/, code: "ta-IN" },
    { range: /[\u0C00-\u0C7F]/, code: "te-IN" },
    { range: /[\u0600-\u06FF]/, code: "ar-SA" },
    { range: /[\u0400-\u04FF]/, code: "ru-RU" },
    { range: /[\u0370-\u03FF]/, code: "el-GR" },
    { range: /[\u0590-\u05FF]/, code: "he-IL" },
    { range: /[\u0E00-\u0E7F]/, code: "th-TH" },
    { range: /[\u3040-\u30FF]/, code: "ja-JP" },
    { range: /[\uAC00-\uD7AF]/, code: "ko-KR" },
    { range: /[\u4E00-\u9FFF]/, code: "zh-CN" },
  ];
  for (const { range, code } of scriptRanges) {
    if (range.test(text)) return code;
  }
  return null;
}

function speakWithBrowserVoice() {
  const isKnownLangCode = targetLanguage.value !== "custom";
  let effectiveLangCode = currentLangCode;

  if (!isKnownLangCode) {
    const guessed = guessLangCodeFromScript(currentTranslation);
    if (guessed) {
      effectiveLangCode = guessed;
    } else if (/[^\u0000-\u024F\s.,!?;:'"()-]/.test(currentTranslation)) {
      showToast("Can't find a matching voice for this language yet");
      return;
    }
  }

  const baseLangCode = effectiveLangCode.split("-")[0];
  const matchingVoice =
    cachedVoices.find((v) => v.lang === effectiveLangCode) ||
    cachedVoices.find((v) => v.lang.toLowerCase().startsWith(baseLangCode));

  if (!matchingVoice) {
    showToast(`No voice available for this language right now`);
    return;
  }
  const utterance = new SpeechSynthesisUtterance(currentTranslation);
  utterance.voice = matchingVoice;
  utterance.lang = matchingVoice.lang;
  speechSynthesis.speak(utterance);
}

speakBtn.addEventListener("click", async () => {
  if (!currentTranslation) return showToast("Nothing to play yet");

  speakBtn.disabled = true;
  const originalIcon = speakBtn.textContent;
  speakBtn.textContent = "⏳";

  try {
    const response = await fetch(`${API_BASE}/api/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: currentTranslation }),
    });

    if (!response.ok) throw new Error("AI voice unavailable");

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
    audio.onended = () => URL.revokeObjectURL(audioUrl);
  } catch (err) {
    // AI voice failed (likely rate-limited on the free tier) — quietly fall
    // back to the browser's own voice instead of showing an error.
    speakWithBrowserVoice();
  } finally {
    speakBtn.disabled = false;
    speakBtn.textContent = originalIcon;
    speakBtn.textContent = originalIcon;
  }
});

// ===== Word / idiom explanation =====
explainBtn.addEventListener("click", async () => {
  const word = wordInput.value.trim();
  if (!word) return showToast("Type a word or phrase first");

  explainBtn.textContent = "...";
  try {
    const response = await fetch(`${API_BASE}/api/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ word, context: inputText.value.trim() }),
    });
    const data = await response.json();

    explainResult.innerHTML = `
      <p><strong>Meaning:</strong> ${data.meaning}</p>
      <p><strong>Synonyms:</strong> ${data.synonyms.join(", ")}</p>
      <p><strong>Example:</strong> ${data.example_sentence}</p>
      ${data.idiom_or_cultural_note ? `<p><strong>Note:</strong> ${data.idiom_or_cultural_note}</p>` : ""}
    `;
    explainResult.classList.remove("hidden");
  } catch (err) {
    showToast("Explanation failed");
  } finally {
    explainBtn.textContent = "Explain";
  }
});

// ===== History (stored in browser localStorage) =====
function getHistory() {
  return JSON.parse(localStorage.getItem("translation_history") || "[]");
}

function saveToHistory(original, translated, language) {
  let history = getHistory();

  // If this exact original text already exists in history, remove the old
  // entry first — so trying different tones on the same sentence just
  // updates the one entry instead of piling up duplicates.
  history = history.filter((item) => item.original.trim().toLowerCase() !== original.trim().toLowerCase());

  history.unshift({ original, translated, language, langCode: currentLangCode, tone: selectedTone, time: Date.now() });
  localStorage.setItem("translation_history", JSON.stringify(history.slice(0, 20)));
  renderHistory();
}

function renderHistory() {
  const history = getHistory();
  if (history.length === 0) {
    historyList.innerHTML = `<p class="empty-state">No translations yet</p>`;
    return;
  }
  historyList.innerHTML = history
    .map(
      (item) => `
      <div class="history-item" data-original="${encodeURIComponent(item.original)}" data-translated="${encodeURIComponent(item.translated)}" data-langcode="${item.langCode || "en-US"}" data-tone="${item.tone || "neutral"}">
        <div class="h-original">${item.original.slice(0, 40)}${item.original.length > 40 ? "..." : ""}</div>
        <div class="h-translated">${item.translated.slice(0, 40)}${item.translated.length > 40 ? "..." : ""} <span style="opacity:0.6">(${item.language} · ${item.tone || "neutral"})</span></div>
      </div>`
    )
    .join("");

  // Clicking a history item loads it back into the panels
  document.querySelectorAll(".history-item").forEach((el) => {
    el.addEventListener("click", () => {
      inputText.value = decodeURIComponent(el.dataset.original);
      outputText.textContent = decodeURIComponent(el.dataset.translated);
      currentTranslation = decodeURIComponent(el.dataset.translated);
      currentLangCode = el.dataset.langcode;
      selectedTone = el.dataset.tone;
      toneButtons.forEach((b) => b.classList.toggle("active", b.dataset.tone === selectedTone));
      charCount.textContent = `${inputText.value.length} / 2000`;
    });
  });
}

clearHistoryBtn.addEventListener("click", () => {
  localStorage.removeItem("translation_history");
  renderHistory();
  showToast("History cleared");
});

// ===== Keyboard shortcut: Ctrl/Cmd + Enter to translate =====
inputText.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    translate();
  }
});

// ===== Initial render =====
renderHistory();
