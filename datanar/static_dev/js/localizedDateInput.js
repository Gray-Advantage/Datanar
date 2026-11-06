(() => {
  const lang = document.documentElement.lang || "en";

  const formatter = new Intl.DateTimeFormat(lang, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });

  const HINTS = {
    bg: { day: "дд", month: "мм", year: "гггг" },
    de: { day: "TT", month: "MM", year: "JJJJ" },
    es: { day: "dd", month: "mm", year: "aaaa" },
    fr: { day: "jj", month: "mm", year: "aaaa" },
    ja: { day: "日", month: "月", year: "年" },
    ru: { day: "дд", month: "мм", year: "гггг" },
    uk: { day: "дд", month: "мм", year: "рррр" },
  };

  const hints = HINTS[lang.split("-")[0]] ?? {
    day: "dd",
    month: "mm",
    year: "yyyy",
  };

  const SIZES = { day: 2, month: 2, year: 4 };

  const layout = () => {
    const all = formatter.formatToParts(new Date(2000, 11, 31));
    let end = all.length;
    while (end > 0 && all[end - 1].type === "literal") {
      end -= 1;
    }
    return all.slice(0, end);
  };

  const PARTS = layout();
  const FIELDS = PARTS.filter((part) => part.type !== "literal");
  const TOTAL = FIELDS.reduce((sum, part) => sum + SIZES[part.type], 0);
  const PLACEHOLDER = PARTS.map(
    (part) => hints[part.type] ?? part.value,
  ).join("");

  const render = (digits) => {
    let out = "";
    let used = 0;
    for (const part of PARTS) {
      if (part.type === "literal") {
        if (used === 0 || used > digits.length) {
          break;
        }
        out += part.value;
        continue;
      }

      const size = SIZES[part.type];
      const chunk = digits.slice(used, used + size);
      out += chunk;
      used += size;
      if (chunk.length < size) {
        break;
      }
    }
    return out;
  };

  const toIso = (digits) => {
    if (digits.length < TOTAL) {
      return "";
    }

    const values = {};
    let used = 0;
    for (const part of FIELDS) {
      const size = SIZES[part.type];
      values[part.type] = digits.slice(used, used + size);
      used += size;
    }

    const year = Number(values.year);
    const month = Number(values.month);
    const day = Number(values.day);
    const date = new Date(year, month - 1, day);
    if (
      date.getFullYear() !== year ||
      date.getMonth() !== month - 1 ||
      date.getDate() !== day
    ) {
      return "";
    }

    return `${values.year}-${values.month}-${values.day}`;
  };

  const fromIso = (value) => {
    if (!value) {
      return "";
    }

    const [year, month, day] = value.split("-");
    const values = { year, month, day };
    return FIELDS.map((part) => values[part.type]).join("");
  };

  const SPACING = /^m[btexy]?-/;

  const enhance = (input) => {
    if (input.dataset.localized) {
      return;
    }
    input.dataset.localized = "1";

    const spacing = [...input.classList].filter((name) =>
      SPACING.test(name),
    );
    input.classList.remove(...spacing);

    const wrapper = document.createElement("div");
    wrapper.classList.add("localized-date", ...spacing);
    input.parentNode.insertBefore(wrapper, input);

    const display = document.createElement("input");
    display.type = "text";
    display.className = input.className;
    display.id = input.id;
    display.placeholder = PLACEHOLDER;
    display.inputMode = "numeric";
    display.autocomplete = "off";
    if (input.hasAttribute("aria-describedby")) {
      display.setAttribute(
        "aria-describedby",
        input.getAttribute("aria-describedby"),
      );
    }

    input.id = `${input.id}_value`;
    input.tabIndex = -1;
    input.setAttribute("aria-hidden", "true");

    const button = document.createElement("button");
    button.type = "button";
    button.className = "localized-date__picker";
    button.tabIndex = -1;
    button.setAttribute("aria-hidden", "true");
    button.innerHTML = '<i class="bi bi-calendar"></i>';

    wrapper.append(display, input, button);

    let digits = fromIso(input.value);
    let serverInvalid = display.classList.contains("is-invalid");
    let syncing = false;

    const apply = (next, { caretToEnd = true } = {}) => {
      digits = next;
      display.value = render(digits);
      if (caretToEnd) {
        const end = display.value.length;
        display.setSelectionRange(end, end);
      }

      const value = toIso(digits);
      if (input.value !== value) {
        syncing = true;
        input.value = value;
        input.dispatchEvent(new Event("change", { bubbles: true }));
        syncing = false;
      }

      const typedInvalid = digits.length === TOTAL && !value;
      display.classList.toggle(
        "is-invalid",
        serverInvalid || typedInvalid,
      );
    };

    display.addEventListener("input", () => {
      serverInvalid = false;
      apply(display.value.replace(/\D/g, "").slice(0, TOTAL));
    });

    display.addEventListener("keydown", (event) => {
      const atEnd =
        display.selectionStart === display.value.length &&
        display.selectionStart === display.selectionEnd;
      if (event.key === "Backspace" && atEnd && digits) {
        event.preventDefault();
        serverInvalid = false;
        apply(digits.slice(0, -1));
      }
    });

    display.addEventListener("blur", () => {
      if (digits && !toIso(digits)) {
        display.classList.add("is-invalid");
      }
    });

    input.addEventListener("change", () => {
      if (!syncing) {
        apply(fromIso(input.value), { caretToEnd: false });
      }
    });

    if (typeof input.showPicker === "function") {
      button.addEventListener("mousedown", (event) => {
        event.preventDefault();
      });
      button.addEventListener("click", () => {
        display.focus();
        input.showPicker();
      });
    } else {
      button.remove();
    }

    apply(digits, { caretToEnd: false });
  };

  const enhanceAll = () => {
    document.querySelectorAll('input[type="date"]').forEach(enhance);
  };

  const observer = new MutationObserver(enhanceAll);
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  document.addEventListener("DOMContentLoaded", () => {
    observer.disconnect();
    enhanceAll();
  });
})();
