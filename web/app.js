var DATA_URL = "./widgets.json";
var DEFAULT_REFRESH_SECONDS = 300;

var fallbackData = {
  updated_at: new Date().toISOString(),
  layout: "dashboard",
  refresh_seconds: DEFAULT_REFRESH_SECONDS,
  widgets: [
    {
      slot: "glance-left",
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
      slot: "glance-right",
      type: "ai-status",
      data: {
        session_name: "Local fallback",
        model: "Codex",
        task: "Render the dashboard",
        context: {
          used: 0,
          limit: 30000
        },
        elapsed_seconds: 0
      }
    },
    {
      slot: "headline",
      type: "focus",
      data: {
        task: "Initialize AI desk card web MVP",
        big_text: "25:00",
        subtitle: "current focus"
      }
    },
    {
      slot: "detail-left",
      type: "ai-tasks",
      data: {
        title: "AI Tasks",
        counts: {
          running: 1,
          waiting: 0,
          blocked: 0,
          completed_today: 2
        }
      }
    },
    {
      slot: "detail-middle",
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
      slot: "detail-right",
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
  aiStatus: document.getElementById("widget-ai-status"),
  aiTasks: document.getElementById("widget-ai-tasks"),
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
  var meta = data.location || "Local";
  if (data.stale) {
    meta += " · stale";
  } else if (data.source) {
    meta += " · " + data.source;
  }
  var parts = [
    '<div class="widget-header">',
    '<h2 class="widget-title">Weather</h2>',
    '<p class="meta">', escapeHtml(meta), "</p>",
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

function renderAiStatus(widget) {
  var data = widget.data || {};
  var sessionName = data.session_name || "No active AI session";
  var context = data.context || {};
  var parts = [
    '<div class="widget-header">',
    '<h2 class="widget-title">AI Status</h2>',
    '<p class="meta">', escapeHtml(data.model || "--"), "</p>",
    "</div>",
    '<p class="ai-session">', escapeHtml(sessionName), "</p>",
    '<p class="ai-task">', escapeHtml(data.task || "No task reported"), "</p>",
    '<div class="ai-metrics">',
    '<span>', escapeHtml(formatContext(context)), "</span>",
    '<span>', escapeHtml(formatElapsed(data.elapsed_seconds)), "</span>",
    "</div>"
  ];
  elements.aiStatus.innerHTML = parts.join("");
}

function renderAiTasks(widget) {
  var data = widget.data || {};
  var counts = data.counts || {};
  var metrics = [
    ["RUN", counts.running],
    ["WAIT", counts.waiting],
    ["BLOCK", counts.blocked],
    ["DONE", counts.completed_today]
  ];
  var parts = [
    '<div class="widget-header">',
    '<h2 class="widget-title">', escapeHtml(data.title || "AI Tasks"), "</h2>",
    "</div>",
    '<div class="task-count-grid">'
  ];
  var i;
  for (i = 0; i < metrics.length; i += 1) {
    parts.push(
      '<div class="task-count">',
      '<strong>', escapeHtml(formatCount(metrics[i][1])), "</strong>",
      '<span>', escapeHtml(metrics[i][0]), "</span>",
      "</div>"
    );
  }
  parts.push("</div>");
  elements.aiTasks.innerHTML = parts.join("");
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

function formatContext(context) {
  var used = Number(context.used);
  var limit = Number(context.limit);
  if (!isFinite(used) || !isFinite(limit) || limit <= 0) {
    return "context --";
  }
  return "context " + Math.round((used / limit) * 100) + "%";
}

function formatElapsed(seconds) {
  var value = Number(seconds);
  var minutes;
  if (!isFinite(value) || value <= 0) {
    return "elapsed --";
  }
  minutes = Math.floor(value / 60);
  if (minutes < 60) {
    return "elapsed " + minutes + "m";
  }
  return "elapsed " + Math.floor(minutes / 60) + "h " + (minutes % 60) + "m";
}

function formatCount(value) {
  var number = Number(value);
  if (!isFinite(number) || number < 0) {
    return "0";
  }
  return String(Math.floor(number));
}

function render(data, offline) {
  formatDateTime();
  renderHeader(data, !!offline);
  renderWeather(widgetByType(data, "weather"));
  renderAiStatus(widgetByType(data, "ai-status"));
  renderFocus(widgetByType(data, "focus"));
  renderAiTasks(widgetByType(data, "ai-tasks"));
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
