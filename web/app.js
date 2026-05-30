var DATA_URL = "./widgets.json";
var DEFAULT_REFRESH_SECONDS = 300;

var fallbackData = {
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

var lastData = fallbackData;
var refreshTimer = null;

var elements = {
  date: document.getElementById("current-date"),
  time: document.getElementById("current-time"),
  freshness: document.getElementById("freshness"),
  refresh: document.getElementById("refresh-label"),
  status: document.getElementById("status-label"),
  focus: document.getElementById("widget-focus"),
  weather: document.getElementById("widget-weather"),
  calendar: document.getElementById("widget-calendar"),
  todo: document.getElementById("widget-todo")
};

function applyViewportScale() {
  var card = document.getElementsByTagName("main")[0];
  var viewportWidth = window.innerWidth || document.documentElement.clientWidth || 758;
  var viewportHeight = window.innerHeight || document.documentElement.clientHeight || 1024;
  var scaleX = viewportWidth / 758;
  var scaleY = viewportHeight / 1024;
  var scale = Math.min(scaleX, scaleY);
  var left;

  if (scale > 1) {
    scale = 1;
  }
  if (scale <= 0) {
    scale = 1;
  }

  left = Math.max(0, Math.floor((viewportWidth - 758 * scale) / 2));
  card.style.left = left + "px";
  card.style.webkitTransform = "scale(" + scale + ")";
  card.style.transform = "scale(" + scale + ")";
}

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function pad2(value) {
  return value < 10 ? "0" + value : String(value);
}

function formatDateTime() {
  var now = new Date();
  var weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  elements.date.innerHTML = (now.getMonth() + 1) + "月" + now.getDate() + "日" + weekdays[now.getDay()];
  elements.time.innerHTML = pad2(now.getHours()) + ":" + pad2(now.getMinutes());
}

function widgetByType(data, type) {
  var widgets = data && data.widgets ? data.widgets : [];
  var i;
  for (i = 0; i < widgets.length; i += 1) {
    if (widgets[i].type === type) {
      return widgets[i];
    }
  }
  return { type: type, data: {} };
}

function minutesSince(timestamp) {
  var updatedAt = new Date(timestamp).getTime();
  if (!isFinite(updatedAt)) {
    return Infinity;
  }
  return Math.max(0, Math.floor((new Date().getTime() - updatedAt) / 60000));
}

function freshnessState(data, offline) {
  var age;
  if (offline) {
    return { state: "offline", label: "offline" };
  }

  age = minutesSince(data.updated_at);
  if (age <= 15) {
    return { state: "normal", label: "updated " + age + "m ago" };
  }
  if (age <= 60) {
    return { state: "stale", label: "stale " + age + "m" };
  }
  return { state: "old", label: "old " + age + "m" };
}

function renderHeader(data, offline) {
  var fresh = freshnessState(data, offline);
  document.body.className = "state-" + fresh.state;
  elements.freshness.innerHTML = escapeHtml(fresh.label);
  elements.status.innerHTML = "status: " + escapeHtml(fresh.state);
  elements.refresh.innerHTML = "refresh: " + escapeHtml(data.refresh_seconds || DEFAULT_REFRESH_SECONDS) + "s";
}

function renderFocus(widget) {
  var data = widget.data || {};
  elements.focus.innerHTML = [
    '<div class="widget-header">',
    '<h2 class="widget-title">Focus</h2>',
    '<p class="meta">', escapeHtml(data.subtitle || "current focus"), "</p>",
    "</div>",
    '<p class="focus-task">', escapeHtml(data.task || "No focus task"), "</p>",
    '<p class="big-text">', escapeHtml(data.big_text || "--"), "</p>"
  ].join("");
}

function renderWeather(widget) {
  var data = widget.data || {};
  var current = data.current || {};
  var forecast = data.forecast || [];
  var temperature = current.temp_c;
  var condition = current.condition || data.condition || "--";
  var parts = [
    '<div class="widget-header">',
    '<h2 class="widget-title">Weather</h2>',
    '<p class="meta">', escapeHtml(data.location || "Local"), "</p>",
    "</div>",
    '<div class="weather-main">',
    '<p class="temperature">', escapeHtml(formatTemperature(temperature)), "</p>",
    '<p class="condition">', escapeHtml(condition), "</p>",
    "</div>",
    '<div class="item-list forecast-list">'
  ];
  var i;
  for (i = 0; i < forecast.length && i < 2; i += 1) {
    parts.push(
      '<div class="item-row forecast-row">',
      '<span class="row-left">', escapeHtml(forecast[i].day), "</span>",
      '<strong class="row-main">', escapeHtml(forecast[i].condition || ""), "</strong>",
      '<span class="row-tag">', escapeHtml(formatHighLow(forecast[i])), "</span>",
      "</div>"
    );
  }
  parts.push("</div>");
  elements.weather.innerHTML = parts.join("");
}

function renderCalendar(widget) {
  var data = widget.data || {};
  var events = data.events || [];
  var parts = [
    '<div class="widget-header">',
    '<h2 class="widget-title">Calendar</h2>',
    '<p class="meta">', escapeHtml(Math.min(events.length, 4)), " visible</p>",
    "</div>",
    '<div class="item-list">'
  ];
  var i;
  for (i = 0; i < events.length && i < 4; i += 1) {
    parts.push(
      '<div class="item-row">',
      '<span class="row-left">', escapeHtml(events[i].start || "--"), "</span>",
      '<strong class="row-main">', escapeHtml(events[i].title || "Untitled event"), "</strong>",
      '<span class="row-tag">', escapeHtml(events[i].end || ""), "</span>",
      "</div>"
    );
  }
  parts.push("</div>");
  elements.calendar.innerHTML = parts.join("");
}

function renderTodo(widget) {
  var data = widget.data || {};
  var items = data.items || [];
  var parts = [
    '<div class="widget-header">',
    '<h2 class="widget-title">', escapeHtml(data.title || "Todo"), "</h2>",
    '<p class="meta">', escapeHtml(Math.min(items.length, 4)), " items</p>",
    "</div>",
    '<div class="item-list">'
  ];
  var i;
  for (i = 0; i < items.length && i < 4; i += 1) {
    parts.push(
      '<div class="item-row todo-row">',
      '<span class="row-left"><span class="check" aria-hidden="true"></span></span>',
      '<strong class="row-main">', escapeHtml(items[i].text || "Untitled task"), "</strong>",
      '<span class="row-tag">', escapeHtml(items[i].tag || items[i].due || ""), "</span>",
      "</div>"
    );
  }
  parts.push("</div>");
  elements.todo.innerHTML = parts.join("");
}

function formatTemperature(value) {
  if (value === undefined || value === null || value === "") {
    return "--";
  }
  return typeof value === "number" ? Math.round(value) + "°C" : value;
}

function formatHighLow(item) {
  if (item.high === undefined || item.low === undefined) {
    return "";
  }
  return Math.round(item.high) + " / " + Math.round(item.low);
}

function render(data, offline) {
  formatDateTime();
  renderHeader(data, !!offline);
  renderFocus(widgetByType(data, "focus"));
  renderWeather(widgetByType(data, "weather"));
  renderCalendar(widgetByType(data, "calendar"));
  renderTodo(widgetByType(data, "todo"));
}

function loadWidgets() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", DATA_URL + "?t=" + new Date().getTime(), true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState !== 4) {
      return;
    }
    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        lastData = JSON.parse(xhr.responseText);
        render(lastData, false);
      } catch (error) {
        render(lastData, true);
      }
    } else {
      render(lastData, true);
    }
  };
  try {
    xhr.send(null);
  } catch (error) {
    render(lastData, true);
  }
}

function scheduleRefresh(data) {
  var seconds = Number(data.refresh_seconds || DEFAULT_REFRESH_SECONDS);
  window.clearInterval(refreshTimer);
  refreshTimer = window.setInterval(loadWidgets, Math.max(30, seconds) * 1000);
}

formatDateTime();
applyViewportScale();
render(fallbackData, false);
loadWidgets();
scheduleRefresh(lastData);
window.setInterval(formatDateTime, 30000);
window.onresize = applyViewportScale;
