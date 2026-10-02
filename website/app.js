const FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas", "06": "California",
    "08": "Colorado", "09": "Connecticut", "10": "Delaware", "11": "District of Columbia",
    "12": "Florida", "13": "Georgia", "15": "Hawaii", "16": "Idaho", "17": "Illinois",
    "18": "Indiana", "19": "Iowa", "20": "Kansas", "21": "Kentucky", "22": "Louisiana",
    "23": "Maine", "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
    "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York",
    "37": "North Carolina", "38": "North Dakota", "39": "Ohio", "40": "Oklahoma", "41": "Oregon",
    "42": "Pennsylvania", "44": "Rhode Island", "45": "South Carolina", "46": "South Dakota",
    "47": "Tennessee", "48": "Texas", "49": "Utah", "50": "Vermont", "51": "Virginia",
    "53": "Washington", "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming"
};

const INK = "#1c1915";
const ACCENT = "#8c2f2f";
const STONE = "#c4b8a5";
const charts = {};
const PEOPLE_PAGE = 8;
let people = [];
let peoplePage = 0;
let showPhotos = true;
let peopleReady = false;

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
    }[ch]));
}

function safeUrl(value) {
    const url = String(value || "").trim();
    return /^https:\/\//i.test(url) ? url : "";
}

function setStatus(text) {
    const node = document.getElementById("status");
    if (node) node.textContent = text;
}

function loadCsv(name) {
    return new Promise((resolve, reject) => {
        if (!window.Papa) {
            reject(new Error("The table reader did not load."));
            return;
        }
        Papa.parse(name, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: (result) => resolve(result.data || []),
            error: (error) => reject(error)
        });
    });
}

function num(value) {
    if (value === null || value === undefined || value === "") return null;
    const parsed = Number(String(value).replace(/,/g, ""));
    return Number.isFinite(parsed) ? parsed : null;
}

function money(value) {
    return "$" + Math.round(value).toLocaleString();
}

function comma(value) {
    return value === null ? "—" : Math.round(value).toLocaleString();
}

function pounds(value) {
    return value === null ? "—" : Number(value).toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function destroyChart(id) {
    if (charts[id]) {
        charts[id].destroy();
        delete charts[id];
    }
}

function monthLabel(value) {
    return String(value).slice(0, 7);
}

function monthShift(label, delta) {
    const [year, month] = label.split("-").map(Number);
    const date = new Date(Date.UTC(year, month - 1 + delta, 1));
    return date.getUTCFullYear() + "-" + String(date.getUTCMonth() + 1).padStart(2, "0");
}

function formatMonth(value, style) {
    const label = monthLabel(value);
    const match = label.match(/^(\d{4})-(\d{2})$/);
    if (!match) return String(value || "");
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const name = months[Number(match[2]) - 1];
    if (style === "short") return name.slice(0, 3) + " " + match[1];
    return name + " " + match[1];
}

function shortGroup(name) {
    return {
        "American Indian or Alaska Native": "American Indian",
        "Black or African American": "Black",
        "Native Hawaiian or Other Pacific Islander": "Pacific Islander",
        "More than one race": "Multiracial"
    }[name] || name;
}

const TABLE_PREVIEW = 18;
const seriesTables = {};

function paintSeriesTable(id) {
    const cached = seriesTables[id];
    if (!cached) return;
    const more = document.getElementById(id + "-more");
    const expanded = more && more.getAttribute("aria-expanded") === "true";
    const rows = !expanded && cached.rows.length > TABLE_PREVIEW ? cached.rows.slice(-TABLE_PREVIEW) : cached.rows;
    const caption = !expanded && cached.rows.length > TABLE_PREVIEW
        ? "Latest " + TABLE_PREVIEW + " months"
        : cached.caption;
    fillTable(id, cached.headers, rows, caption);
    if (!more) return;
    more.hidden = cached.rows.length <= TABLE_PREVIEW;
    more.textContent = expanded
        ? "Show the latest " + TABLE_PREVIEW + " months"
        : "Show all " + cached.rows.length.toLocaleString() + " months";
}

function setSeriesTable(id, headers, rows, caption) {
    seriesTables[id] = { headers, rows, caption };
    const more = document.getElementById(id + "-more");
    if (more && !more.dataset.bound) {
        more.dataset.bound = "true";
        more.setAttribute("aria-expanded", "false");
        more.addEventListener("click", () => {
            const open = more.getAttribute("aria-expanded") === "true";
            more.setAttribute("aria-expanded", open ? "false" : "true");
            paintSeriesTable(id);
        });
    }
    paintSeriesTable(id);
}

function monthAxis(labels) {
    const narrow = window.matchMedia("(max-width: 700px)").matches;
    const firstYear = labels.length ? Number(labels[0].slice(0, 4)) : 0;
    const lastYear = labels.length ? Number(labels[labels.length - 1].slice(0, 4)) : 0;
    const step = narrow ? (lastYear - firstYear > 16 ? 5 : 3) : (lastYear - firstYear > 16 ? 4 : 2);
    return {
        grid: { display: false },
        border: { display: false },
        ticks: {
            color: INK,
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0,
            font: { size: narrow ? 11 : 13 },
            callback(value, index) {
                const label = labels[index];
                if (!label || !label.endsWith("-01")) return "";
                const year = Number(label.slice(0, 4));
                if (year !== lastYear && year % step !== 0) return "";
                if (year !== lastYear && lastYear - year < step) return "";
                return String(year);
            }
        }
    };
}

function noteChartMissing(canvas) {
    if (!canvas || canvas.dataset.missing) return;
    canvas.dataset.missing = "true";
    const note = document.createElement("p");
    note.className = "note";
    note.textContent = "The chart did not load in this browser. The table below has the same numbers.";
    canvas.insertAdjacentElement("afterend", note);
}

function writeReadout(readoutId, lines) {
    const node = document.getElementById(readoutId);
    if (!node) return;
    const text = (lines || []).filter(Boolean).join(" · ");
    if (text) node.textContent = text;
}

function watchChart(chart, readoutId, linesForIndex) {
    if (!chart) return;
    const writeIndex = (index) => {
        if (index == null) return;
        writeReadout(readoutId, linesForIndex(index));
    };
    const fromNative = (event) => {
        const points = chart.getElementsAtEventForMode(event, "nearest", { intersect: false }, false);
        if (points && points.length) writeIndex(points[0].index);
    };
    chart.canvas.addEventListener("pointerdown", fromNative);
    chart.options.onClick = (event, elements) => {
        if (elements && elements.length) writeIndex(elements[0].index);
    };
    chart.options.onHover = (event, elements, activeChart) => {
        if (activeChart && activeChart.canvas) {
            activeChart.canvas.style.cursor = elements && elements.length ? "crosshair" : "default";
        }
        if (elements && elements.length) writeIndex(elements[0].index);
    };
}

function shortMethod(value) {
    const text = String(value || "");
    if (text.startsWith("Estimated")) return "Preliminary estimate";
    if (text.startsWith("Official")) return "Final certificate";
    return text;
}

function fitCharts() {
    Object.values(charts).forEach((chart) => {
        if (chart && chart.resize) chart.resize();
    });
}

function isEstimated(row) {
    return String(row["How this number was produced"] || "").startsWith("Estimated");
}

function isGap(row) {
    return String(row.Note || "").includes("below zero");
}

function usableMonths(rows) {
    return rows.filter((row) => num(row["Estimated deaths"]) !== null && !isGap(row));
}

function configureCharts() {
    if (!window.Chart) return;
    if (window["chartjs-plugin-annotation"]) {
        Chart.register(window["chartjs-plugin-annotation"]);
    }
    const sans = getComputedStyle(document.documentElement).getPropertyValue("--sans").trim() || "sans-serif";
    Chart.defaults.font.family = sans;
    Chart.defaults.font.size = 13;
    Chart.defaults.color = INK;
    Chart.defaults.borderColor = "#e2d9cc";
    Chart.defaults.interaction.mode = "index";
    Chart.defaults.interaction.intersect = false;
    Chart.defaults.plugins.tooltip.enabled = false;
    Chart.defaults.plugins.tooltip.external = externalTooltip;
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.onHover = (event, elements, chart) => {
        if (chart && chart.canvas) chart.canvas.style.cursor = elements && elements.length ? "crosshair" : "default";
    };
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    Chart.defaults.animation = reduce ? false : { duration: 280 };
    if (!Chart.defaults.transitions) Chart.defaults.transitions = {};
    if (!Chart.defaults.transitions.active) Chart.defaults.transitions.active = {};
    Chart.defaults.transitions.active.animation = { duration: 0 };
}

function barStyle(color) {
    return {
        backgroundColor: color,
        hoverBackgroundColor: color === ACCENT ? INK : ACCENT,
        borderWidth: 0,
        hoverBorderWidth: 0
    };
}

const ALONG_ROWS = { mode: "index", intersect: false, axis: "y" };

function valueAxis(title) {
    const narrow = window.matchMedia("(max-width: 700px)").matches;
    const scale = {
        beginAtZero: true,
        grid: { color: "#efe8dc" },
        border: { display: false },
        ticks: { color: INK, maxTicksLimit: narrow ? 5 : 6, font: { size: narrow ? 11 : 13 } }
    };
    if (title && !narrow) scale.title = { display: true, text: title, color: "#5c564c" };
    return scale;
}

function categoryAxis(extra) {
    return Object.assign({
        grid: { display: false },
        border: { display: false },
        ticks: { color: INK }
    }, extra || {});
}

function fillTable(id, headers, rows, caption) {
    const node = document.getElementById(id);
    if (!node) return;
    const cap = caption ? `<caption>${escapeHtml(caption)}</caption>` : "";
    const head = "<thead><tr>" + headers.map((header) => `<th scope="col">${escapeHtml(header)}</th>`).join("") + "</tr></thead>";
    const body = "<tbody>" + rows.map((row) => "<tr>" + row.map((cell, index) => {
        const tag = index === 0 ? "th" : "td";
        const scope = index === 0 ? " scope=\"row\"" : "";
        return `<${tag}${scope}>${escapeHtml(cell)}</${tag}>`;
    }).join("") + "</tr>").join("") + "</tbody>";
    node.innerHTML = `<table>${cap}${head}${body}</table>`;
}

function ensureVizTip() {
    let tip = document.getElementById("viz-tip");
    if (tip) return tip;
    tip = document.createElement("div");
    tip.id = "viz-tip";
    tip.className = "viz-tip";
    tip.setAttribute("role", "tooltip");
    tip.hidden = true;
    document.body.appendChild(tip);
    window.addEventListener("scroll", hideVizTip, true);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") hideVizTip();
    });
    return tip;
}

function showVizTip(lines, clientX, clientY) {
    const tip = ensureVizTip();
    const clean = (lines || []).map((line) => String(line || "").trim()).filter(Boolean);
    if (!clean.length || clientX == null || clientY == null) {
        hideVizTip();
        return;
    }
    tip.innerHTML = clean.map((line, index) =>
        `<p class="${index === 0 ? "viz-tip-title" : "viz-tip-line"}">${escapeHtml(line)}</p>`
    ).join("");
    tip.hidden = false;
    tip.style.left = "0px";
    tip.style.top = "0px";
    const box = tip.getBoundingClientRect();
    let left = clientX + 16;
    let top = clientY + 18;
    if (left + box.width > window.innerWidth - 8) left = clientX - box.width - 16;
    if (top + box.height > window.innerHeight - 8) top = clientY - box.height - 16;
    tip.style.left = Math.max(8, left) + "px";
    tip.style.top = Math.max(8, top) + "px";
}

function hideVizTip() {
    const tip = document.getElementById("viz-tip");
    if (tip) tip.hidden = true;
}

function pushTipLines(lines, value) {
    if (Array.isArray(value)) {
        value.forEach((item) => pushTipLines(lines, item));
        return;
    }
    if (value) lines.push(String(value));
}

function tooltipLines(tooltip) {
    const lines = [];
    pushTipLines(lines, tooltip.title);
    pushTipLines(lines, tooltip.beforeBody);
    (tooltip.body || []).forEach((part) => {
        pushTipLines(lines, part.before);
        pushTipLines(lines, part.lines);
        pushTipLines(lines, part.after);
    });
    pushTipLines(lines, tooltip.afterBody);
    pushTipLines(lines, tooltip.footer);
    return lines;
}

function pointFromChartEvent(event, chart) {
    const native = event && (event.native || event);
    if (native && native.clientX != null) return { x: native.clientX, y: native.clientY };
    if (chart && event && event.x != null) {
        const rect = chart.canvas.getBoundingClientRect();
        return { x: rect.left + event.x, y: rect.top + event.y };
    }
    return { x: null, y: null };
}

function externalTooltip(context) {
    const tooltip = context && context.tooltip;
    const chart = context && context.chart;
    if (!tooltip || tooltip.opacity === 0 || !chart) {
        hideVizTip();
        return;
    }
    const rect = chart.canvas.getBoundingClientRect();
    showVizTip(tooltipLines(tooltip), rect.left + tooltip.caretX, rect.top + tooltip.caretY);
}

function yearChangeLine(row) {
    const delta = num(row["Change from the same month a year earlier"]);
    if (delta === null) return "";
    if (delta < 0) return comma(Math.abs(delta)) + " fewer than the same month a year earlier";
    if (delta > 0) return comma(delta) + " more than the same month a year earlier";
    return "Same number as a year earlier";
}

function monthTipLines(row, actions) {
    if (!row) return [];
    const lines = [formatMonth(row.Month)];
    if (isGap(row)) lines.push("Not plotted. The estimate fell below zero.");
    else lines.push(comma(num(row["Estimated deaths"])) + " deaths");
    if (row["How this number was produced"]) lines.push(row["How this number was produced"]);
    const change = yearChangeLine(row);
    if (change) lines.push(change);
    const matched = (actions || []).filter((action) => monthLabel(action.action_date) === row.Month);
    matched.forEach((action) => {
        lines.push(action.action_date + " — " + action.title);
        const who = [action.theme, action.actor].filter(Boolean).join(" · ");
        if (who) lines.push(who);
    });
    if (matched.length) lines.push("A date is not proof an action changed the deaths.");
    return lines;
}

function policyAnnotations(actions, labels, rows) {
    const annotations = {};
    actions.forEach((action, index) => {
        const label = monthLabel(action.action_date);
        if (!labels.includes(label)) return;
        const show = (first, second) => {
            const event = second && (second.native || second.clientX != null || second.x != null) ? second : first;
            const chart = (first && first.chart) || (second && second.chart);
            const point = pointFromChartEvent(event, chart);
            const row = (rows || []).find((item) => item.Month === label);
            showVizTip(monthTipLines(row, actions), point.x, point.y);
        };
        annotations["line" + index] = {
            type: "line",
            xMin: label,
            xMax: label,
            borderColor: ACCENT,
            borderWidth: 1.5,
            label: { display: false },
            enter: show
        };
        annotations["hit" + index] = {
            type: "line",
            xMin: label,
            xMax: label,
            borderColor: "rgba(140, 47, 47, 0.02)",
            borderWidth: 14,
            enter: show
        };
    });
    return annotations;
}

function drawMonthly(canvasId, rows, actions, fromYear) {
    const canvas = document.getElementById(canvasId);
    const shown = rows.filter((row) => Number(String(row.Month).slice(0, 4)) >= fromYear);
    const labels = shown.map((row) => row.Month);
    const deaths = shown.map((row) => (isGap(row) ? null : num(row["Estimated deaths"])));
    const listed = actions || [];
    setSeriesTable(
        canvasId + "-data",
        ["Month", "Deaths", "What the number is"],
        shown.map((row) => [
            formatMonth(row.Month, "short"),
            isGap(row) ? "Not plotted. The estimate fell below zero." : comma(num(row["Estimated deaths"])),
            isGap(row) ? "Not plotted" : shortMethod(row["How this number was produced"])
        ]),
        "Deaths in each month"
    );
    if (!canvas || !window.Chart) {
        noteChartMissing(canvas);
        return;
    }
    destroyChart(canvasId);
    const narrow = window.matchMedia("(max-width: 700px)").matches;
    charts[canvasId] = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Deaths that month",
                data: deaths,
                borderColor: INK,
                backgroundColor: "rgba(28, 25, 21, 0.05)",
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointHitRadius: narrow ? 18 : 12,
                pointHoverBackgroundColor: ACCENT,
                pointHoverBorderColor: "#fffdf8",
                pointHoverBorderWidth: 2,
                borderWidth: 2,
                tension: 0.12,
                spanGaps: false,
                segment: {
                    borderDash(ctx) {
                        const row = shown[ctx.p1DataIndex];
                        return row && isEstimated(row) ? [5, 4] : undefined;
                    }
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            layout: { padding: { top: 8, right: 16, bottom: 2, left: 0 } },
            plugins: {
                legend: { display: false },
                annotation: {
                    interaction: { mode: "point", intersect: true },
                    annotations: policyAnnotations(listed, labels, shown)
                },
                tooltip: {
                    callbacks: {
                        title(items) {
                            const row = shown[items[0].dataIndex];
                            return row ? formatMonth(row.Month) : "";
                        },
                        label(item) {
                            const row = shown[item.dataIndex];
                            if (!row || isGap(row)) return "Not plotted. The estimate fell below zero.";
                            return comma(num(row["Estimated deaths"])) + " deaths";
                        },
                        afterBody(items) {
                            const row = shown[items[0].dataIndex];
                            if (!row) return [];
                            return monthTipLines(row, listed).slice(2);
                        }
                    }
                }
            },
            scales: {
                y: valueAxis(narrow ? "" : "Deaths"),
                x: monthAxis(labels)
            }
        }
    });
    watchChart(charts[canvasId], canvasId + "-readout", (index) => monthTipLines(shown[index], listed));
    const latestShown = shown.filter((row) => !isGap(row)).pop();
    if (latestShown) writeReadout(canvasId + "-readout", monthTipLines(latestShown, listed));
    requestAnimationFrame(() => fitCharts());
}

function bindRange(chartId, monthly, actions) {
    const recent = document.getElementById("range-recent");
    const all = document.getElementById("range-all");
    if (!recent || !all) return;
    recent.addEventListener("click", () => {
        recent.setAttribute("aria-pressed", "true");
        all.setAttribute("aria-pressed", "false");
        drawMonthly(chartId, monthly, actions, 2015);
    });
    all.addEventListener("click", () => {
        all.setAttribute("aria-pressed", "true");
        recent.setAttribute("aria-pressed", "false");
        drawMonthly(chartId, monthly, actions, 1999);
    });
}

function summarizeMonths(rows, summaryId, answerId) {
    const usable = usableMonths(rows);
    if (!usable.length) return;
    let peak = usable[0];
    usable.forEach((row) => {
        if (num(row["Estimated deaths"]) > num(peak["Estimated deaths"])) peak = row;
    });
    const latest = usable[usable.length - 1];
    const summary = document.getElementById(summaryId);
    if (summary) {
        summary.textContent = "The highest month in this file is " + formatMonth(peak.Month) + " (" + comma(num(peak["Estimated deaths"]))
            + " deaths). The latest month is " + formatMonth(latest.Month) + " (" + comma(num(latest["Estimated deaths"])) + ").";
    }
    const answer = document.getElementById(answerId);
    if (!answer) return;
    const latestDeaths = num(latest["Estimated deaths"]);
    const peakDeaths = num(peak["Estimated deaths"]);
    if (latest.Month === peak.Month) {
        answer.textContent = "The latest month in this file, " + formatMonth(latest.Month) + ", is the highest month.";
        return;
    }
    const relation = latestDeaths < peakDeaths ? "lower than" : "higher than";
    answer.textContent = "The latest month, " + formatMonth(latest.Month) + ", is " + relation + " the highest month in this file (" + formatMonth(peak.Month) + ").";
}

function renderStats(monthly, provisional) {
    const usable = usableMonths(monthly);
    const latest = usable[usable.length - 1];
    const nation = provisional
        .filter((row) => row.geo_type === "nation")
        .sort((a, b) => String(a.month).localeCompare(String(b.month)));
    const latestNation = nation[nation.length - 1];
    const prior = latest ? usable.find((row) => row.Month === monthShift(latest.Month, -12)) : null;
    const yearChange = latest && prior ? num(latest["Estimated deaths"]) - num(prior["Estimated deaths"]) : null;
    let changeText = "—";
    if (yearChange === 0) changeText = "No change";
    else if (yearChange !== null) changeText = comma(Math.abs(yearChange)) + (yearChange > 0 ? " more" : " fewer");
    const cards = [
        ["Deaths in the latest month", latest ? comma(num(latest["Estimated deaths"])) : "—", latest ? formatMonth(latest.Month) + " · " + (isEstimated(latest) ? "Preliminary estimate" : "Final death certificate") : ""],
        ["Compared with a year earlier", changeText, prior ? "Same month in " + prior.Month.slice(0, 4) : "Same month, previous year"],
        ["Deaths in the last 12 months", latestNation ? comma(num(latestNation.headline_deaths)) : "—", latestNation ? twelveMonthDetail(latestNation) : ""]
    ];
    const stats = document.getElementById("stats");
    if (stats) {
        stats.innerHTML = cards.map(([label, value, detail]) =>
            `<div class="stat"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b><span>${escapeHtml(detail)}</span></div>`
        ).join("");
    }
    const extracted = latestNation && latestNation.extracted_at;
    setStatus(extracted
        ? "Provisional CDC extract " + extracted + ". Final months use CDC WONDER."
        : "Latest month in the spreadsheet: " + (latest ? latest.Month : ""));
}

function twelveMonthDetail(row) {
    const ending = formatMonth(row.month);
    if (row.headline_basis === "predicted") {
        return "CDC predicted total for the 12 months ending " + ending + ". Not a sum of single months.";
    }
    return "CDC reported total for the 12 months ending " + ending + ". Not a sum of single months.";
}

function deathsInMonth(monthly, month) {
    const row = monthly.find((item) => item.Month === month);
    if (!row || isGap(row)) return null;
    const value = num(row["Estimated deaths"]);
    if (value === null) return null;
    const kind = isEstimated(row) ? "estimated" : "official";
    return comma(value) + " (" + kind + ")";
}

function crisisAnswer(monthly) {
    const usable = usableMonths(monthly);
    if (!usable.length) return "";
    const latest = usable[usable.length - 1];
    const prior = usable.find((row) => row.Month === monthShift(latest.Month, -12));
    const official = usable.filter((row) => !isEstimated(row));
    const lastOfficial = official[official.length - 1];
    const latestDeaths = num(latest["Estimated deaths"]);
    let change = "";
    if (prior) {
        const delta = latestDeaths - num(prior["Estimated deaths"]);
        if (delta < 0) {
            change = " Deaths are lower than " + formatMonth(prior.Month) + ", by " + comma(Math.abs(delta)) + ".";
        } else if (delta > 0) {
            change = " Deaths are higher than " + formatMonth(prior.Month) + ", by " + comma(delta) + ".";
        } else {
            change = " That is the same number as " + formatMonth(prior.Month) + ".";
        }
    }
    const layer = isEstimated(latest)
        ? " This month is a preliminary estimate. Final death certificates run through " + (lastOfficial ? lastOfficial.Month.slice(0, 4) : "the last final year") + "."
        : " This month is a final death certificate.";
    return "In " + formatMonth(latest.Month) + ", " + comma(latestDeaths) + " people died from synthetic opioids other than methadone, the CDC category that includes fentanyl." + change + layer;
}

function renderFreshness(rows, monthly) {
    const nodes = document.querySelectorAll("[data-freshness]");
    if (!nodes.length) return;
    const row = (rows || [])[0] || {};
    let text = "";
    if (row.latest_provisional_month && row.latest_final_year) {
        const checked = String(row.checked_at || "").slice(0, 10);
        text = "Final through " + row.latest_final_year
            + ". Newest CDC month: " + formatMonth(row.latest_provisional_month)
            + (checked ? ". Checked " + checked : "")
            + ". Updated every Monday.";
    } else {
        const usable = usableMonths(monthly || []);
        const latest = usable[usable.length - 1];
        const official = usable.filter((item) => !isEstimated(item));
        const lastOfficial = official[official.length - 1];
        if (lastOfficial && latest) {
            text = "Final death certificates run through " + lastOfficial.Month.slice(0, 4)
                + ". The latest month in this file is " + formatMonth(latest.Month)
                + (isEstimated(latest) ? ", a preliminary estimate." : ".");
        }
    }
    nodes.forEach((node) => { node.textContent = text; });
}

function loadOptionalCsv(name) {
    return loadCsv(name).catch(() => []);
}

function renderAge(rows, fullYearDeaths) {
    const summary = document.getElementById("age-summary");
    fillTable(
        "age-table",
        ["Age group", "Deaths"],
        rows.map((row) => [row.group, comma(num(row.deaths))]),
        "Deaths by age group"
    );
    if (summary && rows.length) {
        let peak = rows[0];
        rows.forEach((row) => {
            if ((num(row.deaths) || 0) > (num(peak.deaths) || 0)) peak = row;
        });
        const total = rows.reduce((sum, row) => sum + (num(row.deaths) || 0), 0);
        let text = "The largest group in " + rows[0].year + " was " + peak.group + " (" + comma(num(peak.deaths)) + " deaths). The youngest groups are shorter than ten years.";
        if (fullYearDeaths && total !== fullYearDeaths) {
            text += " These groups add up to " + comma(total) + ". The full year is " + comma(fullYearDeaths) + ". The chart does not fill in the difference.";
        }
        summary.textContent = text;
    }
    const canvas = document.getElementById("age-chart");
    if (!canvas || !window.Chart) return;
    destroyChart("age");
    charts.age = new Chart(canvas, {
        type: "bar",
        data: {
            labels: rows.map((row) => row.group),
            datasets: [{
                label: "Deaths",
                data: rows.map((row) => num(row.deaths)),
                ...barStyle(INK)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title(items) {
                            const row = rows[items[0].dataIndex];
                            return row ? row.group : "";
                        },
                        label(item) {
                            const row = rows[item.dataIndex];
                            return comma(num(row.deaths)) + " deaths";
                        },
                        afterBody(items) {
                            const row = rows[items[0].dataIndex];
                            return row ? [row.year + ", final death certificates"] : [];
                        }
                    }
                }
            },
            scales: {
                x: categoryAxis({
                    ticks: {
                        color: INK,
                        autoSkip: false,
                        maxRotation: 50,
                        minRotation: 50,
                        font: { size: 11 },
                        callback(value) {
                            const label = this.getLabelForValue(value);
                            return String(label).replace(" years", "").replace(" year", "");
                        }
                    }
                }),
                y: valueAxis("")
            }
        }
    });
    watchChart(charts.age, "age-readout", (index) => {
        const row = rows[index];
        return row ? [row.group, comma(num(row.deaths)) + " deaths", String(row.year)] : [];
    });
}

function renderRace(deaths, population) {
    const popByGroup = Object.fromEntries(population.map((row) => [row.wonder_group, row]));
    const deathTotal = deaths.reduce((sum, row) => sum + (num(row.deaths) || 0), 0);
    const popTotal = population.reduce((sum, row) => sum + (num(row.population) || 0), 0);
    const deathShare = deaths.map((row) => (deathTotal ? (num(row.deaths) / deathTotal) * 100 : null));
    const popShare = deaths.map((row) => {
        const pop = popByGroup[row.group];
        return pop && popTotal ? (num(pop.population) / popTotal) * 100 : null;
    });
    fillTable(
        "race-table",
        ["Group on the death certificate", "Share of deaths", "Share of population", "Deaths"],
        deaths.map((row, index) => [
            row.group,
            deathShare[index] === null ? "—" : deathShare[index].toFixed(1) + "%",
            popShare[index] === null ? "—" : popShare[index].toFixed(1) + "%",
            comma(num(row.deaths))
        ]),
        "Share of deaths and share of the population"
    );
    const canvas = document.getElementById("race-chart");
    if (!canvas || !window.Chart) return;
    destroyChart("race");
    charts.race = new Chart(canvas, {
        type: "bar",
        data: {
            labels: deaths.map((row) => shortGroup(row.group)),
            datasets: [
                { label: "Share of deaths", data: deathShare, ...barStyle(ACCENT) },
                { label: "Share of population", data: popShare, ...barStyle(STONE) }
            ]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            interaction: ALONG_ROWS,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        title(items) {
                            const row = deaths[items[0].dataIndex];
                            return row ? row.group : "";
                        },
                        label(item) {
                            const value = item.parsed.x;
                            const shown = value === null || value === undefined ? "Not published" : value.toFixed(1) + "%";
                            if (item.datasetIndex === 0) {
                                const row = deaths[item.dataIndex];
                                return "Share of deaths: " + shown + " (" + comma(num(row.deaths)) + " deaths)";
                            }
                            return "Share of population: " + shown;
                        }
                    }
                }
            },
            scales: {
                x: valueAxis("Percent"),
                y: categoryAxis({
                    ticks: {
                        color: INK,
                        autoSkip: false,
                        font: { size: window.matchMedia("(max-width: 700px)").matches ? 11 : 13 }
                    }
                })
            }
        }
    });
    watchChart(charts.race, "race-readout", (index) => {
        const row = deaths[index];
        if (!row) return [];
        const deathText = deathShare[index] === null ? "Share of deaths not published" : "Share of deaths " + deathShare[index].toFixed(1) + "%";
        const popText = popShare[index] === null ? "Population share not published" : "Population share " + popShare[index].toFixed(1) + "%";
        return [row.group, deathText, popText, comma(num(row.deaths)) + " deaths"];
    });
}

function renderShare(rows) {
    const row = rows[0];
    const node = document.getElementById("share-text");
    const fill = document.getElementById("share-fill");
    const meter = document.getElementById("share-meter");
    if (!row) {
        if (node) node.textContent = "The share is not in this extract yet.";
        return;
    }
    const share = num(row.share_of_drug_poisoning_deaths);
    const percent = share === null ? null : share * 100;
    if (node) {
        node.textContent = "In " + row.year + ", " + (percent === null ? "—" : percent.toFixed(1))
            + "% of U.S. drug-poisoning deaths also listed a synthetic opioid other than methadone ("
            + comma(num(row.t40_4_deaths)) + " of " + comma(num(row.drug_poisoning_deaths)) + "). " + row.note;
    }
    if (fill && percent !== null) fill.style.width = Math.max(0, Math.min(100, percent)) + "%";
    if (meter && percent !== null) meter.setAttribute("aria-valuenow", percent.toFixed(1));
    if (!meter) return;
    const lines = [
        String(row.year),
        (percent === null ? "Share not published" : percent.toFixed(1) + "% of drug-poisoning deaths"),
        comma(num(row.t40_4_deaths)) + " listed a synthetic opioid other than methadone",
        comma(num(row.drug_poisoning_deaths)) + " drug-poisoning deaths"
    ];
    const show = (event) => showVizTip(lines, event.clientX, event.clientY);
    meter.addEventListener("mousemove", show);
    meter.addEventListener("mouseleave", hideVizTip);
    meter.addEventListener("focus", () => {
        const box = meter.getBoundingClientRect();
        showVizTip(lines, box.left + 24, box.top + box.height);
    });
    meter.addEventListener("blur", hideVizTip);
}

function completeYears(rows) {
    return [...new Set(rows.map((row) => row.fiscal_year))].filter((year) => !String(year).includes("FYTD")).sort();
}

function renderSeizures(rows) {
    const years = [...new Set(rows.map((row) => row.fiscal_year))];
    const components = [...new Set(rows.map((row) => row.component))];
    const colors = [INK, STONE, ACCENT];
    const componentTotals = (year, component) => rows
        .filter((row) => row.fiscal_year === year && row.component === component)
        .reduce((sum, row) => sum + (num(row.pounds) || 0), 0);
    fillTable(
        "seizure-table",
        ["Fiscal year", "Component", "Pounds"],
        years.flatMap((year) => components.map((component) => [year, component, pounds(componentTotals(year, component))])),
        "Fentanyl pounds seized by CBP component"
    );
    const finished = completeYears(rows);
    const year = finished[finished.length - 1];
    const yearRows = rows.filter((row) => row.fiscal_year === year);
    const total = yearRows.reduce((sum, row) => sum + (num(row.pounds) || 0), 0);
    const byComponent = components.map((component) => {
        const amount = componentTotals(year, component);
        return [component, pounds(amount), total ? ((amount / total) * 100).toFixed(1) + "%" : "—"];
    });
    fillTable("component-table", ["CBP component", "Pounds", "Share of CBP pounds"], byComponent, "Share of CBP fentanyl pounds in " + year);
    const componentNote = document.getElementById("component-note");
    if (componentNote) {
        componentNote.textContent = "In " + year + ", the latest fiscal year in this file that is not marked year-to-date, these two CBP components account for the pounds below. This is not every federal agency, and it is not a measure of how much got through.";
    }
    const regions = [...new Set(yearRows.map((row) => row.region))];
    const regionTotals = regions.map((region) => yearRows
        .filter((row) => row.region === region)
        .reduce((sum, row) => sum + (num(row.pounds) || 0), 0));
    const southwest = regionTotals[regions.indexOf("Southwest Border")] || 0;
    const regionNote = document.getElementById("region-note");
    if (regionNote) {
        const share = total ? Math.round((southwest / total) * 100) : null;
        regionNote.textContent = "Fiscal year " + year + ". Field offices are added up to a region. "
            + (share === null ? "" : share + "% of these pounds were counted at the Southwest Border. ")
            + "Adding pounds is not a map of crossings, and it is not a measure of how much got through.";
    }
    fillTable(
        "region-table",
        ["Region", "Pounds in " + year],
        regions.map((region, index) => [region, pounds(regionTotals[index])]),
        "Where CBP counted fentanyl seizures in " + year
    );
    if (!window.Chart) return;
    const seizureCanvas = document.getElementById("seizure-chart");
    if (seizureCanvas) {
        destroyChart("seizure");
        charts.seizure = new Chart(seizureCanvas, {
            type: "bar",
            data: {
                labels: years,
                datasets: components.map((component, index) => ({
                    label: component,
                    data: years.map((item) => componentTotals(item, component)),
                    ...barStyle(colors[index % colors.length])
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
                    tooltip: {
                        callbacks: {
                            title(items) { return years[items[0].dataIndex]; },
                            label(item) {
                                return item.dataset.label + ": " + pounds(item.parsed.y) + " pounds";
                            },
                            afterBody() {
                                return ["Pounds CBP reports seizing. Not a measure of how much got through."];
                            }
                        }
                    }
                },
                scales: {
                    x: categoryAxis({ ticks: { color: INK, maxRotation: 0, minRotation: 0 } }),
                    y: valueAxis("Pounds")
                }
            }
        });
        watchChart(charts.seizure, "seizure-readout", (index) => {
            const year = years[index];
            return [year].concat(components.map((component) => component + ": " + pounds(componentTotals(year, component)) + " pounds"));
        });
    }
    const regionCanvas = document.getElementById("region-chart");
    if (regionCanvas) {
        destroyChart("region");
        charts.region = new Chart(regionCanvas, {
            type: "bar",
            data: {
                labels: regions,
                datasets: [{ label: "Pounds", data: regionTotals, ...barStyle(INK) }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                interaction: ALONG_ROWS,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title(items) { return regions[items[0].dataIndex]; },
                            label(item) { return pounds(item.parsed.x) + " pounds"; },
                            afterBody() {
                                return ["Fiscal year " + year + ". Pounds seized, not pounds that got through."];
                            }
                        }
                    }
                },
                scales: {
                    x: valueAxis("Pounds"),
                    y: categoryAxis()
                }
            }
        });
    }
}

function renderBudgets(rows) {
    fillTable(
        "budget-table",
        ["Agency", "Fiscal year", "Line", "Amount", "What kind of amount"],
        rows.map((row) => [row.agency, row.fiscal_year, row.line_name, money(num(row.amount_dollars)), row.amount_kind]),
        "Budget lines as printed"
    );
    const canvas = document.getElementById("budget-chart");
    if (!canvas || !window.Chart) return;
    destroyChart("budget");
    charts.budget = new Chart(canvas, {
        type: "bar",
        data: {
            labels: rows.map((row) => row.agency + ", FY" + row.fiscal_year),
            datasets: [{
                label: "Dollars",
                data: rows.map((row) => num(row.amount_dollars)),
                ...barStyle(INK)
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            interaction: ALONG_ROWS,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title(item) {
                            const row = rows[item[0].dataIndex];
                            return row.agency + ", FY" + row.fiscal_year;
                        },
                        label(item) {
                            const row = rows[item.dataIndex];
                            return [money(num(row.amount_dollars)), row.line_name, row.amount_kind];
                        }
                    }
                }
            },
            scales: {
                x: valueAxis("Dollars"),
                y: categoryAxis()
            }
        }
    });
}

function seriesValue(row, basis) {
    if (!row) return null;
    if (basis === "predicted") {
        const predicted = num(row.predicted_12_month_deaths);
        if (predicted !== null) return predicted;
    }
    if (basis === "reported") {
        const reported = num(row.rolling_12_month_deaths);
        if (reported !== null) return reported;
    }
    return num(row.headline_deaths);
}

function blankChange(name) {
    return { state: name, pct: null, now: null, then: null, basis: "" };
}

function stateChanges(provisional) {
    const states = provisional.filter((row) => row.geo_type === "state");
    const latest = states.reduce((max, row) => (row.month > max ? row.month : max), "");
    const latestLabel = monthLabel(latest);
    const priorLabel = monthShift(latestLabel, -12);
    const priorMonth = priorLabel + "-01";
    const changes = [];
    const bases = new Set();
    [...new Set(states.map((row) => row.state))].forEach((name) => {
        const current = states.find((row) => row.state === name && row.month === latest);
        const prior = states.find((row) => row.state === name && row.month === priorMonth);
        if (!current || current.reporting_status === "not_reportable" || String(current.is_suppressed) === "true") {
            changes.push(blankChange(name));
            return;
        }
        const basis = current.headline_basis || "reported";
        const now = seriesValue(current, basis);
        const then = seriesValue(prior, basis);
        if (now === null || then === null || then === 0) {
            changes.push(blankChange(name));
            return;
        }
        bases.add(basis);
        changes.push({ state: name, pct: ((now - then) / then) * 100, now, then, basis });
    });
    const comparison = bases.has("predicted")
        ? "Both months use CDC's predicted total, so a reporting adjustment is not counted as a change."
        : "Both months use CDC's reported total.";
    return { latest: latestLabel, prior: priorLabel, changes, comparison };
}

function mapTipLines(row, latest, prior) {
    if (!row) return ["Unknown", "Not published"];
    if (row.pct === null) {
        return [row.state, "Not published", "CDC did not publish a comparable 12-month total."];
    }
    const basis = row.basis === "predicted"
        ? "Both months use CDC's predicted total."
        : "Both months use CDC's reported total.";
    return [
        row.state,
        formatPercent(row.pct) + " from a year earlier",
        "12 months ending " + latest + ": " + comma(row.now),
        "12 months ending " + prior + ": " + comma(row.then),
        basis
    ];
}

function colorFor(pct) {
    if (pct === null) return "#d9d4cc";
    const clamped = Math.max(-40, Math.min(40, pct));
    if (clamped < 0) {
        const t = Math.abs(clamped) / 40;
        return `rgb(${Math.round(244 - t * 213)}, ${Math.round(241 - t * 134)}, ${Math.round(234 - t * 158)})`;
    }
    const t = clamped / 40;
    return `rgb(${Math.round(244 - t * 104)}, ${Math.round(241 - t * 194)}, ${Math.round(234 - t * 185)})`;
}

function formatPercent(pct) {
    if (pct === null || pct === undefined) return "Not published";
    return (pct > 0 ? "+" : "") + pct.toFixed(0) + "%";
}

function stateName(feature) {
    return FIPS[String(feature.id).padStart(2, "0")] || "Unknown";
}

async function renderMap(provisional) {
    const { latest, prior, changes, comparison } = stateChanges(provisional);
    const byName = Object.fromEntries(changes.map((row) => [row.state, row]));
    const ranked = changes.filter((row) => row.pct !== null).sort((a, b) => a.pct - b.pct);
    const down = ranked.filter((row) => row.pct < 0).slice(0, 5);
    const up = ranked.filter((row) => row.pct > 0).reverse().slice(0, 5);
    const list = document.getElementById("state-list");
    const item = (row) => `<li>${escapeHtml(row.state)}: ${escapeHtml(formatPercent(row.pct))}</li>`;
    if (list) {
        list.innerHTML = `<p class="note">Percent change in the 12-month total ending ${escapeHtml(formatMonth(latest))}, compared with a year earlier. ${escapeHtml(comparison)}</p>
            <p><strong>Largest decreases</strong></p><ul>${down.map(item).join("")}</ul>
            <p><strong>Largest increases</strong></p><ul>${up.map(item).join("")}</ul>`;
    }
    const published = (value) => (value === null ? "Not published" : comma(value));
    fillTable(
        "state-table",
        ["State", "Change in the 12-month total", "12-month total", "A year earlier"],
        changes.slice().sort((a, b) => a.state.localeCompare(b.state)).map((row) => [
            row.state,
            formatPercent(row.pct),
            published(row.now),
            published(row.then)
        ]),
        "Percent change by state, 12 months ending " + formatMonth(latest)
    );
    const comparable = changes.filter((row) => row.pct !== null);
    const downCount = comparable.filter((row) => row.pct < 0).length;
    const upCount = comparable.filter((row) => row.pct > 0).length;
    const flatCount = comparable.filter((row) => row.pct === 0).length;
    const missingCount = changes.length - comparable.length;
    const stateAnswer = document.getElementById("state-answer");
    if (stateAnswer) {
        const parts = [
            downCount + (downCount === 1 ? " state is" : " states are") + " lower than a year earlier",
            upCount + (upCount === 1 ? " is" : " are") + " higher"
        ];
        if (flatCount) parts.push(flatCount + (flatCount === 1 ? " is" : " are") + " unchanged");
        stateAnswer.textContent = "For the 12 months ending " + formatMonth(latest) + ", " + parts.join(", ") + ". "
            + missingCount + (missingCount === 1 ? " state was" : " states were") + " not published in this CDC series.";
    }
    const readout = document.getElementById("map-readout");
    if (readout) readout.textContent = "Tap a state to see both 12-month totals.";
    const svg = window.d3 ? d3.select("#state-map") : null;
    if (!svg || svg.empty()) return;
    svg.selectAll("*").remove();
    svg.attr("role", "group");
    svg.attr("aria-label", "Map of the percent change in the 12-month death total by state, ending " + formatMonth(latest) + ". Gray means not published. Tap or focus a state for both totals.");
    try {
        const atlas = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json");
        const states = topojson.feature(atlas, atlas.objects.states);
        const path = d3.geoPath(d3.geoAlbersUsa());
        const rowFor = (feature) => byName[stateName(feature)] || blankChange(stateName(feature));
        let selected = null;
        const pin = (row) => {
            if (selected === row.state) {
                selected = null;
                svg.selectAll("path").classed("is-selected", false);
                if (readout) readout.textContent = "Tap a state to see both 12-month totals.";
                return;
            }
            selected = row.state;
            svg.selectAll("path").classed("is-selected", (feature) => stateName(feature) === row.state);
            if (readout) readout.textContent = mapTipLines(row, latest, prior).join(" ");
        };
        svg.selectAll("path")
            .data(states.features)
            .join("path")
            .attr("d", path)
            .attr("fill", (feature) => colorFor(rowFor(feature).pct))
            .attr("stroke", "#fffdf8")
            .attr("tabindex", "0")
            .attr("role", "button")
            .attr("aria-label", (feature) => mapTipLines(rowFor(feature), latest, prior).join(". "))
            .on("mouseenter", function () { d3.select(this).classed("is-hot", true); })
            .on("mousemove", (event, feature) => {
                showVizTip(mapTipLines(rowFor(feature), latest, prior), event.clientX, event.clientY);
            })
            .on("mouseleave", function () {
                d3.select(this).classed("is-hot", false);
                hideVizTip();
            })
            .on("click", (event, feature) => {
                const row = rowFor(feature);
                pin(row);
                showVizTip(mapTipLines(row, latest, prior), event.clientX, event.clientY);
            })
            .on("focus", function (event, feature) {
                const box = this.getBoundingClientRect();
                showVizTip(mapTipLines(rowFor(feature), latest, prior), box.left + box.width / 2, box.top + 8);
            })
            .on("blur", hideVizTip)
            .on("keydown", (event, feature) => {
                if (event.key !== "Enter" && event.key !== " ") return;
                event.preventDefault();
                pin(rowFor(feature));
            })
            .append("title")
            .text((feature) => {
                const row = rowFor(feature);
                return row.state + ": " + formatPercent(row.pct);
            });
    } catch (error) {
        svg.append("text").attr("x", 20).attr("y", 40).text("The map could not be loaded. The list and the table are still complete.");
    }
}

function renderActions(actions, monthly) {
    const body = document.querySelector("#action-table tbody");
    if (!body) return;
    const sorted = actions.slice().sort((a, b) => String(a.action_date).localeCompare(String(b.action_date)));
    body.innerHTML = sorted.map((row) => {
        const month = monthLabel(row.action_date);
        const later = monthShift(month, 12);
        const href = safeUrl(row.source_url);
        const source = href
            ? `<a href="${escapeHtml(href)}">${escapeHtml(row.source_title || "Source")}</a>`
            : escapeHtml(row.source_title || "");
        return `<tr>
            <th scope="row" data-label="Date">${escapeHtml(formatDate(row.action_date))}</th>
            <td data-label="Theme">${escapeHtml(row.theme || "")}</td>
            <td data-label="Action">${escapeHtml(row.title)}<br><span class="note">${escapeHtml(row.summary)}</span></td>
            <td data-label="Who">${escapeHtml(row.actor)}</td>
            <td data-label="Deaths that month">${escapeHtml(deathsInMonth(monthly, month) || "Not in the file")}</td>
            <td data-label="Deaths 12 months later">${escapeHtml(deathsInMonth(monthly, later) || "Not in the file yet")}</td>
            <td data-label="Source">${source}</td>
        </tr>`;
    }).join("");
}

function bindPolicyControls(chartId, monthly, actions) {
    let fromYear = 2015;
    let theme = "All";
    const redraw = () => {
        const shown = theme === "All" ? actions : actions.filter((action) => action.theme === theme);
        drawMonthly(chartId, monthly, shown, fromYear);
        renderActions(shown, monthly);
    };
    const themeSelect = document.getElementById("theme-filter");
    if (themeSelect) {
        themeSelect.addEventListener("change", () => {
            theme = themeSelect.value || "All";
            redraw();
        });
    }
    const recent = document.getElementById("range-recent");
    const all = document.getElementById("range-all");
    if (recent && all) {
        recent.addEventListener("click", () => {
            fromYear = 2015;
            recent.setAttribute("aria-pressed", "true");
            all.setAttribute("aria-pressed", "false");
            redraw();
        });
        all.addEventListener("click", () => {
            fromYear = 1999;
            all.setAttribute("aria-pressed", "true");
            recent.setAttribute("aria-pressed", "false");
            redraw();
        });
    }
    redraw();
}

function formatDate(value) {
    const text = String(value || "");
    const match = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (!match) return text || "Date on the page";
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    return months[Number(match[2]) - 1] + " " + Number(match[3]) + ", " + match[1];
}

function renderNews(rows) {
    const node = document.getElementById("news-list");
    if (!node) return;
    const sorted = rows.slice().sort((a, b) => String(b.published).localeCompare(String(a.published)));
    node.innerHTML = "<ul class=\"news\">" + sorted.map((row) => {
        const href = safeUrl(row.url);
        const title = escapeHtml(row.title || "Untitled release");
        const link = href ? `<a href="${escapeHtml(href)}">${title}</a>` : title;
        const when = escapeHtml(formatDate(row.published));
        const iso = escapeHtml(String(row.published || "").slice(0, 10));
        return `<li><p class="note"><time datetime="${iso}">${when}</time> · ${escapeHtml(row.publisher || "")}</p>${link}</li>`;
    }).join("") + "</ul>";
}

function filteredPeople() {
    const search = document.getElementById("people-search");
    const state = document.getElementById("people-state");
    const query = search ? search.value.trim().toLowerCase() : "";
    const chosen = state ? state.value : "";
    return people.filter((person) => {
        if (chosen === "__missing__" && person.state) return false;
        if (chosen && chosen !== "__missing__" && person.state !== chosen) return false;
        if (query && !String(person.first_name || "").toLowerCase().includes(query)) return false;
        return true;
    });
}

function renderPeople() {
    const grid = document.getElementById("people");
    const count = document.getElementById("people-count");
    const prev = document.getElementById("people-prev");
    const next = document.getElementById("people-next");
    if (!grid || !count) return;
    const shown = filteredPeople();
    const pages = Math.max(1, Math.ceil(shown.length / PEOPLE_PAGE));
    if (peoplePage > pages - 1) peoplePage = pages - 1;
    if (peoplePage < 0) peoplePage = 0;
    const start = peoplePage * PEOPLE_PAGE;
    const slice = shown.slice(start, start + PEOPLE_PAGE);
    if (!people.length) {
        grid.innerHTML = "";
        count.textContent = "The exhibit listing is not in this copy of the site.";
    } else if (!shown.length) {
        grid.innerHTML = "";
        count.textContent = "No names match.";
    } else {
        grid.innerHTML = slice.map((person) => {
            const age = person.age_description || person.age || "";
            const ageText = age ? "Age " + String(age).replace(/\.0$/, "") : "";
            const detail = [ageText, person.state || ""].filter(Boolean).join(" · ") || "Age and state were not listed";
            const href = safeUrl(person.exhibit_url);
            const photoUrl = safeUrl(person.image_url);
            const name = escapeHtml(person.first_name);
            const photo = showPhotos && photoUrl
                ? `<img src="${escapeHtml(photoUrl)}" alt="Photo submitted for ${name}" width="400" height="500" loading="lazy" decoding="async" onerror="this.remove()">`
                : "";
            const link = href ? `<a href="${escapeHtml(href)}">View on the DEA exhibit</a>` : "";
            return `<article class="person">${photo}<h3>${name}</h3><p>${escapeHtml(detail)}</p>${link}</article>`;
        }).join("");
        count.textContent = "Showing " + (start + 1) + "–" + Math.min(start + PEOPLE_PAGE, shown.length) + " of " + shown.length.toLocaleString() + " names";
    }
    if (prev) prev.disabled = peoplePage === 0 || !shown.length;
    if (next) next.disabled = peoplePage >= pages - 1 || !shown.length;
}

function setupPeople() {
    if (peopleReady) return;
    peopleReady = true;
    const select = document.getElementById("people-state");
    if (select) {
        const states = [...new Set(people.map((person) => person.state).filter(Boolean))].sort((a, b) => a.localeCompare(b));
        select.innerHTML = "<option value=\"\">All states</option>"
            + states.map((state) => `<option value="${escapeHtml(state)}">${escapeHtml(state)}</option>`).join("")
            + "<option value=\"__missing__\">State not listed</option>";
    }
    const search = document.getElementById("people-search");
    if (search) search.addEventListener("input", () => { peoplePage = 0; renderPeople(); });
    if (select) select.addEventListener("change", () => { peoplePage = 0; renderPeople(); });
    const prev = document.getElementById("people-prev");
    const next = document.getElementById("people-next");
    const toggle = document.getElementById("photos-toggle");
    if (prev) prev.addEventListener("click", () => { peoplePage = Math.max(0, peoplePage - 1); renderPeople(); });
    if (next) {
        next.addEventListener("click", () => {
            const pages = Math.max(1, Math.ceil(filteredPeople().length / PEOPLE_PAGE));
            peoplePage = Math.min(pages - 1, peoplePage + 1);
            renderPeople();
        });
    }
    if (toggle) {
        toggle.addEventListener("click", () => {
            showPhotos = !showPhotos;
            toggle.setAttribute("aria-pressed", showPhotos ? "true" : "false");
            toggle.textContent = showPhotos ? "Hide photos" : "Show photos";
            renderPeople();
        });
    }
}

function bindMenu() {
    const button = document.querySelector(".menu-button");
    const links = document.getElementById("site-nav");
    if (!button || !links) return;
    button.addEventListener("click", () => {
        const open = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", open ? "false" : "true");
        links.classList.toggle("is-open", !open);
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            button.setAttribute("aria-expanded", "false");
            links.classList.remove("is-open");
        }
    });
    links.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            button.setAttribute("aria-expanded", "false");
            links.classList.remove("is-open");
        });
    });
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(fitCharts, 120);
    });
}

async function renderHome() {
    const [monthly, provisional, freshness] = await Promise.all([
        loadCsv("deaths_by_month.csv"),
        loadCsv("fact_fentanyl_deaths_over_time.csv"),
        loadOptionalCsv("data_freshness.csv")
    ]);
    const answer = document.getElementById("trend-answer");
    if (answer) answer.textContent = crisisAnswer(monthly);
    renderFreshness(freshness, monthly);
    renderStats(monthly, provisional);
    summarizeMonths(monthly, "monthly-summary", null);
    drawMonthly("monthly-chart", monthly, [], 2015);
    bindRange("monthly-chart", monthly, []);
}

async function renderTrend() {
    const [provisional, freshness] = await Promise.all([
        loadCsv("fact_fentanyl_deaths_over_time.csv"),
        loadOptionalCsv("data_freshness.csv")
    ]);
    renderFreshness(freshness, []);
    await renderMap(provisional);
}

async function renderWho() {
    const [age, raceDeaths, racePop, share, seizures, memorials] = await Promise.all([
        loadCsv("wonder_age.csv"),
        loadCsv("wonder_race.csv"),
        loadCsv("census_race_2024.csv"),
        loadCsv("wonder_drug_share.csv"),
        loadCsv("cbp_fentanyl_seizures.csv"),
        loadCsv("faces_of_fentanyl.csv")
    ]);
    people = memorials
        .filter((row) => row.first_name)
        .sort((a, b) => String(a.first_name).localeCompare(String(b.first_name)) || String(a.state).localeCompare(String(b.state)));
    setupPeople();
    renderPeople();
    const fullYear = share[0] ? num(share[0].t40_4_deaths) : null;
    renderAge(age, fullYear);
    renderRace(raceDeaths, racePop);
    renderShare(share);
    renderSeizures(seizures);
}

function deathCell(value) {
    const parsed = num(value);
    return parsed === null ? "Not published" : comma(parsed);
}

async function renderDownload() {
    const [rows, freshness] = await Promise.all([
        loadCsv("deaths_by_state_month.csv"),
        loadOptionalCsv("data_freshness.csv")
    ]);
    renderFreshness(freshness, []);
    const select = document.getElementById("data-state");
    const more = document.getElementById("data-more");
    const count = document.getElementById("data-count");
    if (!select) return;
    const states = [...new Set(rows.map((row) => row.State).filter(Boolean))];
    const ordered = ["United States", ...states.filter((state) => state !== "United States").sort((a, b) => a.localeCompare(b))];
    select.innerHTML = ordered.map((state) => `<option value="${escapeHtml(state)}">${escapeHtml(state)}</option>`).join("");
    if (ordered.includes("United States")) select.value = "United States";
    let shown = 24;
    const paint = () => {
        const state = select.value || "United States";
        const filtered = rows
            .filter((row) => row.State === state)
            .sort((a, b) => String(b.Month).localeCompare(String(a.Month)));
        const slice = filtered.slice(0, shown);
        fillTable(
            "data-preview",
            ["Month", "Deaths in the month", "What the number is", "Preliminary 12-month total"],
            slice.map((row) => [
                formatMonth(row.Month, "short"),
                deathCell(row["Deaths in the month"]),
                row.Confidence || "",
                num(row["Preliminary 12-month total"]) === null ? "—" : comma(num(row["Preliminary 12-month total"]))
            ]),
            "Deaths for " + state + ", newest month first"
        );
        if (count) {
            count.textContent = "Showing " + slice.length.toLocaleString() + " of " + filtered.length.toLocaleString() + " months for " + state + ".";
        }
        if (more) more.hidden = slice.length >= filtered.length;
    };
    select.addEventListener("change", () => {
        shown = 24;
        paint();
    });
    if (more) {
        more.addEventListener("click", () => {
            shown += 24;
            paint();
        });
    }
    paint();
}

async function renderActionsPage() {
    const [monthly, actions] = await Promise.all([
        loadCsv("deaths_by_month.csv"),
        loadCsv("policy_actions.csv")
    ]);
    summarizeMonths(monthly, "policy-summary", null);
    bindPolicyControls("policy-chart", monthly, actions);
}

async function renderNewsPage() {
    renderNews(await loadCsv("official_announcements.csv"));
}

async function main() {
    bindMenu();
    configureCharts();
    const page = document.body.dataset.page || "home";
    try {
        if (page === "home") await renderHome();
        else if (page === "trend") await renderTrend();
        else if (page === "who") await renderWho();
        else if (page === "actions") await renderActionsPage();
        else if (page === "news") await renderNewsPage();
        else if (page === "download") await renderDownload();
    } catch (error) {
        setStatus("The page could not load a data file. " + error);
        document.querySelectorAll(".answer").forEach((node) => {
            if (String(node.textContent).startsWith("Loading")) {
                node.textContent = "The latest figures did not load. The data page still links to the CSV files.";
            }
        });
    }
}

main();
