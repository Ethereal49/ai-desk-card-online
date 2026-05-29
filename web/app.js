const DATA_URL = "./widgets.json";
const DEFAULT_REFRESH_SECONDS = 300;

const fallbackData = {
  updated_at: new Date().toISOString(),
  layout: "dashboard",
  refresh_seconds: DEFAULT_REFRESH_SECONDS,
  widgets: [
    {
      slot: "focus",
      type: "focus",
      data: {
        task: "Initialize AI desk card web MVP",
        big_text: "25:00",
        subtitle: "current focus"
      }
    },
    {
      slot: "weather",
      type: "weather",
      data: {
        location: "Local",
        current: {
          temp_c: 24,
          condition: "Clear"
        },
        forecast: [
          { day: "Today", high: 27, low: 19, condition: "Light wind" },
          { day: "Tomorrow", high: 26, low: 20, condition: "Cloudy" }
        ]
      }
    },
    {
      slot: "calendar",
      type: "calendar",
      data: {
        now_iso: new Date().toISOString(),
        events: [
          { start: "09:30", title: "Review dashboard layout" },
          { start: "14:00", title: "Update widgets.json" },
          { start: "18:30", title: "Daily shutdown" }
        ]
      }
    },
    {
      slot: "todo",
      type: "todo",
      data: {
        title: "Todo",
        items: [
          { text: "Create static web shell", tag: "today" },
          { text: "Verify 758x1024 layout", tag: "today" },
          { text: "Try on e-ink browser", tag: "this-week" }
        ]
      }
    }
  ]
};

let lastData = fallbackData;
let refreshTimer = null;

const elements = {
  date: document.querySelector("#current-date"),
  time: document.querySelector("#current-time"),
  freshness: document.querySelector("#freshness"),
  source: document.querySelector("#source-label"),
  refresh: document.querySelector("#refresh-label"),
  status: document.querySelector("#status-label"),
  focus: document.querySelector("#widget-focus"),
  weather: document.querySelector("#widget-weather"),
  calendar: document.querySelector("#widget-calendar"),
  todo: document.querySelector("#widget-todo")
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDateTime() {
  const now = new Date();
  elements.date.textContent = new Intl.DateTimeFormat("zh-CN", {
    weekday: "short",
    month: "short",
    day: "numeric"
  }).format(now);
  elements.time.textContent = new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(now);
}

function widgetByType(data, type) {
  return (data.widgets || []).find((widget) => widget.type === type) || { type, data: {} };
}

function minutesSince(timestamp) {
  const updatedAt = new Date(timestamp).getTime();
  if (!Number.isFinite(updatedAt)) {
    return Infinity;
  }
  return Math.max(0, Math.floor((Date.now() - updatedAt) / 60000));
}

function freshnessState(data, offline) {
  if (offline) {
    return { state: "offline", label: "offline" };
  }

  const age = minutesSince(data.updated_at);
  if (age <= 15) {
    return { state: "normal", label: `updated ${age}m ago` };
  }
  if (age <= 60) {
    return { state: "stale", label: `stale ${age}m` };
  }
  return { state: "old", label: `old ${age}m` };
}

function renderHeader(data, offline = false) {
  const fresh = freshnessState(data, offline);
  document.body.className = `state-${fresh.state}`;
  elements.freshness.textContent = fresh.label;
  elements.status.textContent = `status: ${fresh.state}`;
  elements.refresh.textContent = `refresh: ${data.refresh_seconds || DEFAULT_REFRESH_SECONDS}s`;
}

function renderFocus(widget) {
  const data = widget.data || {};
  elements.focus.innerHTML = `
    <div class="widget-header">
      <h2 class="widget-title">Focus</h2>
      <p class="meta">${escapeHtml(data.subtitle || "current focus")}</p>
    </div>
    <p class="focus-task">${escapeHtml(data.task || "No focus task")}</p>
    <p class="big-text">${escapeHtml(data.big_text || "--")}</p>
  `;
}

function renderWeather(widget) {
  const data = widget.data || {};
  const forecast = (data.forecast || []).slice(0, 2);
  const temperature = data.current?.temp_c ?? data.temperature;
  const condition = data.current?.condition || data.condition || "--";
  elements.weather.innerHTML = `
    <div class="widget-header">
      <h2 class="widget-title">Weather</h2>
      <p class="meta">${escapeHtml(data.location || "Local")}</p>
    </div>
    <div class="weather-main">
      <p class="temperature">${escapeHtml(formatTemperature(temperature))}</p>
      <p class="condition">${escapeHtml(condition)}</p>
    </div>
    <div class="forecast">
      ${forecast.map((item) => `
        <div class="forecast-row">
          <strong>${escapeHtml(item.day)}</strong>
          <span>${escapeHtml(item.condition || item.summary || "")}</span>
          <span>${escapeHtml(formatHighLow(item))}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderCalendar(widget) {
  const data = widget.data || {};
  const events = (data.events || []).slice(0, 4);
  elements.calendar.innerHTML = `
    <div class="widget-header">
      <h2 class="widget-title">Calendar</h2>
      <p class="meta">${events.length} visible</p>
    </div>
    <div class="item-list">
      ${events.map((item) => `
        <div class="item-row">
          <strong>${escapeHtml(item.start || item.time || "--")}</strong>
          <span>${escapeHtml(item.title || "Untitled event")}</span>
          <span class="tag">${escapeHtml(item.end || item.note || "")}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function renderTodo(widget) {
  const data = widget.data || {};
  const items = (data.items || []).slice(0, 4);
  elements.todo.innerHTML = `
    <div class="widget-header">
      <h2 class="widget-title">${escapeHtml(data.title || "Todo")}</h2>
      <p class="meta">${items.length} items</p>
    </div>
    <div class="item-list">
      ${items.map((item) => `
        <div class="item-row todo-row">
          <span class="check" aria-hidden="true"></span>
          <strong>${escapeHtml(item.text || item.title || "Untitled task")}</strong>
          <span class="tag">${escapeHtml(item.tag || item.due || "")}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function formatTemperature(value) {
  if (value === undefined || value === null || value === "") {
    return "--";
  }
  return typeof value === "number" ? `${Math.round(value)}°C` : value;
}

function formatHighLow(item) {
  if (item.high_low) {
    return item.high_low;
  }
  if (item.high === undefined || item.low === undefined) {
    return "";
  }
  return `${Math.round(item.high)} / ${Math.round(item.low)}`;
}

function render(data, offline = false) {
  formatDateTime();
  renderHeader(data, offline);
  renderFocus(widgetByType(data, "focus"));
  renderWeather(widgetByType(data, "weather"));
  renderCalendar(widgetByType(data, "calendar"));
  renderTodo(widgetByType(data, "todo"));
}

async function loadWidgets() {
  try {
    const response = await fetch(`${DATA_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    lastData = await response.json();
    render(lastData, false);
  } catch (error) {
    render(lastData, true);
  }
}

function scheduleRefresh(data) {
  const seconds = Number(data.refresh_seconds || DEFAULT_REFRESH_SECONDS);
  window.clearInterval(refreshTimer);
  refreshTimer = window.setInterval(loadWidgets, Math.max(30, seconds) * 1000);
}

formatDateTime();
render(fallbackData, false);
loadWidgets().then(() => scheduleRefresh(lastData));
window.setInterval(formatDateTime, 30000);
