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
    Chart.defaults.plugins.tooltip.backgroundColor = INK;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    Chart.defaults.animation = reduce ? false : { duration: 280 };
}

function valueAxis(title) {
    const scale = {
        grid: { color: "#efe8dc" },
        border: { display: false },
        ticks: { color: INK, maxTicksLimit: 6 }
    };
    if (title) scale.title = { display: true, text: title, color: "#5c564c" };
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

function policyAnnotations(actions, labels) {
    const annotations = {};
    actions.forEach((action, index) => {
        const label = monthLabel(action.action_date);
        if (!labels.includes(label)) return;
        annotations["line" + index] = {
            type: "line",
            xMin: label,
            xMax: label,
            borderColor: ACCENT,
            borderWidth: 1.5,
            label: { display: false }
        };
    });
    return annotations;
}

function drawMonthly(canvasId, rows, actions, fromYear) {
    const canvas = document.getElementById(canvasId);
    const shown = rows.filter((row) => Number(String(row.Month).slice(0, 4)) >= fromYear);
    const labels = shown.map((row) => row.Month);
    const deaths = shown.map((row) => (isGap(row) ? null : num(row["Estimated deaths"])));
    fillTable(
        canvasId + "-data",
        ["Month", "Deaths", "How this number was produced"],
        shown.map((row) => [
            row.Month,
            isGap(row) ? "Not plotted. The estimate fell below zero." : comma(num(row["Estimated deaths"])),
            row["How this number was produced"] || ""
        ]),
        "Deaths in each month"
    );
    if (!canvas || !window.Chart) return;
    destroyChart(canvasId);
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
                pointHoverRadius: 4,
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
            plugins: {
                legend: { display: false },
                annotation: { annotations: policyAnnotations(actions, labels) },
                tooltip: {
                    callbacks: {
                        label(item) {
                            const value = item.parsed.y;
                            return value === null || Number.isNaN(value) ? "Not plotted" : comma(value) + " deaths";
                        },
                        afterLabel(item) {
                            const row = shown[item.dataIndex];
                            return row["How this number was produced"];
                        }
                    }
                }
            },
            scales: {
                y: valueAxis("Deaths that month"),
                x: categoryAxis({ ticks: { color: INK, maxTicksLimit: 8 } })
            }
        }
    });
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
        summary.textContent = "The highest month in this file is " + peak.Month + " (" + comma(num(peak["Estimated deaths"]))
            + " deaths). The latest month is " + latest.Month + " (" + comma(num(latest["Estimated deaths"])) + ").";
    }
    const answer = document.getElementById(answerId);
    if (!answer) return;
    const latestDeaths = num(latest["Estimated deaths"]);
    const peakDeaths = num(peak["Estimated deaths"]);
    if (latest.Month === peak.Month) {
        answer.textContent = "The latest month in this file, " + latest.Month + ", is the highest month.";
        return;
    }
    const relation = latestDeaths < peakDeaths ? "lower than" : "higher than";
    answer.textContent = "The latest month, " + latest.Month + ", is " + relation + " the highest month in this file (" + peak.Month + ").";
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
        ["Deaths in the latest month", latest ? comma(num(latest["Estimated deaths"])) : "—", latest ? latest.Month + " · " + latest["How this number was produced"] : ""],
        ["Compared with a year earlier", changeText, prior ? "Against " + prior.Month : "Same month, previous year"],
        ["Deaths in the last 12 months", latestNation ? comma(num(latestNation.headline_deaths)) : "—", latestNation ? "CDC 12-month total ending " + monthLabel(latestNation.month) + ". Not a sum of the monthly chart." : ""]
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

function deathsInMonth(monthly, month) {
    const row = monthly.find((item) => item.Month === month);
    if (!row || isGap(row)) return null;
    const value = num(row["Estimated deaths"]);
    if (value === null) return null;
    const kind = isEstimated(row) ? "estimated" : "official";
    return comma(value) + " (" + kind + ")";
}

function renderComparison(rows) {
    const summary = document.getElementById("comparison-summary");
    fillTable(
        "comparison-table",
        ["Event", "Deaths per 1,000 people per year", "What is counted", "Death source"],
        rows.map((row) => [row.event, row.deaths_per_1000_per_year, row.what_is_counted, row.death_source_title]),
        "Deaths per 1,000 people per year"
    );
    const fentanyl = rows.find((row) => String(row.event || "").startsWith("Synthetic"));
    if (summary) {
        summary.textContent = fentanyl
            ? "In " + String(fentanyl.start_date).slice(0, 4) + ", the synthetic-opioid category was " + fentanyl.deaths_per_1000_per_year + " deaths per 1,000 people. The dark red bar is that category. The other bars use the same formula for the years in the source file."
            : "The comparison file had no synthetic-opioid row.";
    }
    const canvas = document.getElementById("comparison-chart");
    if (!canvas || !window.Chart || !rows.length) return;
    destroyChart("comparison");
    charts.comparison = new Chart(canvas, {
        type: "bar",
        data: {
            labels: rows.map((row) => row.event),
            datasets: [{
                label: "Deaths per 1,000 people per year",
                data: rows.map((row) => num(row.deaths_per_1000_per_year)),
                backgroundColor: rows.map((row) => String(row.event || "").startsWith("Synthetic") ? ACCENT : STONE)
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: valueAxis("Deaths per 1,000 people per year"),
                y: categoryAxis()
            }
        }
    });
}

function renderAge(rows) {
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
        summary.textContent = "The largest ten-year group in " + rows[0].year + " was " + peak.group + " (" + comma(num(peak.deaths)) + " deaths).";
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
                backgroundColor: INK
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: categoryAxis(),
                y: valueAxis("Deaths")
            }
        }
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
            labels: deaths.map((row) => row.group),
            datasets: [
                { label: "Share of deaths", data: deathShare, backgroundColor: ACCENT },
                { label: "Share of population", data: popShare, backgroundColor: STONE }
            ]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true } },
            scales: {
                x: valueAxis("Percent"),
                y: categoryAxis()
            }
        }
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
                    backgroundColor: colors[index % colors.length]
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: true } },
                scales: {
                    x: categoryAxis(),
                    y: valueAxis("Pounds")
                }
            }
        });
    }
    const regionCanvas = document.getElementById("region-chart");
    if (regionCanvas) {
        destroyChart("region");
        charts.region = new Chart(regionCanvas, {
            type: "bar",
            data: {
                labels: regions,
                datasets: [{ label: "Pounds", data: regionTotals, backgroundColor: INK }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
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
                backgroundColor: INK
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
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

function stateChanges(provisional) {
    const states = provisional.filter((row) => row.geo_type === "state");
    const latest = states.reduce((max, row) => (row.month > max ? row.month : max), "");
    const priorMonth = monthShift(monthLabel(latest), -12) + "-01";
    const changes = [];
    [...new Set(states.map((row) => row.state))].forEach((name) => {
        const current = states.find((row) => row.state === name && row.month === latest);
        const prior = states.find((row) => row.state === name && row.month === priorMonth);
        if (!current || current.reporting_status === "not_reportable" || String(current.is_suppressed) === "true") {
            changes.push({ state: name, pct: null });
            return;
        }
        const now = num(current.headline_deaths);
        const then = prior ? num(prior.headline_deaths) : null;
        if (now === null || then === null || then === 0) {
            changes.push({ state: name, pct: null });
            return;
        }
        changes.push({ state: name, pct: ((now - then) / then) * 100 });
    });
    return { latest: monthLabel(latest), changes };
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

async function renderMap(provisional) {
    const { latest, changes } = stateChanges(provisional);
    const byName = Object.fromEntries(changes.map((row) => [row.state, row.pct]));
    const ranked = changes.filter((row) => row.pct !== null).sort((a, b) => a.pct - b.pct);
    const down = ranked.filter((row) => row.pct < 0).slice(0, 5);
    const up = ranked.filter((row) => row.pct > 0).reverse().slice(0, 5);
    const list = document.getElementById("state-list");
    const item = (row) => `<li>${escapeHtml(row.state)}: ${escapeHtml(formatPercent(row.pct))}</li>`;
    if (list) {
        list.innerHTML = `<p class="note">12 months ending ${escapeHtml(latest)}, compared with a year earlier.</p>
            <p><strong>Largest decreases</strong></p><ul>${down.map(item).join("")}</ul>
            <p><strong>Largest increases</strong></p><ul>${up.map(item).join("")}</ul>`;
    }
    fillTable(
        "state-table",
        ["State", "Change in the 12-month total"],
        changes.slice().sort((a, b) => a.state.localeCompare(b.state)).map((row) => [row.state, formatPercent(row.pct)]),
        "Percent change by state, 12 months ending " + latest
    );
    const svg = window.d3 ? d3.select("#state-map") : null;
    if (!svg || svg.empty()) return;
    svg.selectAll("*").remove();
    svg.attr("aria-label", "Map of the percent change in the 12-month death total by state, ending " + latest + ". Gray means not published.");
    try {
        const atlas = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json");
        const states = topojson.feature(atlas, atlas.objects.states);
        const path = d3.geoPath(d3.geoAlbersUsa());
        svg.selectAll("path")
            .data(states.features)
            .join("path")
            .attr("d", path)
            .attr("fill", (feature) => colorFor(byName[FIPS[String(feature.id).padStart(2, "0")]] ?? null))
            .attr("stroke", "#fffdf8")
            .append("title")
            .text((feature) => {
                const name = FIPS[String(feature.id).padStart(2, "0")] || "Unknown";
                return name + ": " + formatPercent(byName[name]);
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
            <th scope="row">${escapeHtml(row.action_date)}</th>
            <td>${escapeHtml(row.title)}<br><span class="note">${escapeHtml(row.summary)}</span></td>
            <td>${escapeHtml(row.actor)}</td>
            <td>${escapeHtml(deathsInMonth(monthly, month) || "Not in the file")}</td>
            <td>${escapeHtml(deathsInMonth(monthly, later) || "Not in the file yet")}</td>
            <td>${source}</td>
        </tr>`;
    }).join("");
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
}

async function renderHome() {
    const comparison = await loadCsv("comparison_per_1000.csv");
    renderComparison(comparison);
}

async function renderTrend() {
    const [monthly, provisional, actions] = await Promise.all([
        loadCsv("deaths_by_month.csv"),
        loadCsv("fact_fentanyl_deaths_over_time.csv"),
        loadCsv("policy_actions.csv")
    ]);
    renderStats(monthly, provisional);
    summarizeMonths(monthly, "monthly-summary", "trend-answer");
    drawMonthly("monthly-chart", monthly, actions, 2015);
    bindRange("monthly-chart", monthly, actions);
    await renderMap(provisional);
}

async function renderWho() {
    const [age, raceDeaths, racePop, share, seizures, budgets, memorials] = await Promise.all([
        loadCsv("wonder_age.csv"),
        loadCsv("wonder_race.csv"),
        loadCsv("census_race_2024.csv"),
        loadCsv("wonder_drug_share.csv"),
        loadCsv("cbp_fentanyl_seizures.csv"),
        loadCsv("agency_budgets.csv"),
        loadCsv("faces_of_fentanyl.csv")
    ]);
    people = memorials
        .filter((row) => row.first_name)
        .sort((a, b) => String(a.first_name).localeCompare(String(b.first_name)) || String(a.state).localeCompare(String(b.state)));
    setupPeople();
    renderPeople();
    renderAge(age);
    renderRace(raceDeaths, racePop);
    renderShare(share);
    renderSeizures(seizures);
    renderBudgets(budgets);
}

async function renderActionsPage() {
    const [monthly, actions] = await Promise.all([
        loadCsv("deaths_by_month.csv"),
        loadCsv("policy_actions.csv")
    ]);
    summarizeMonths(monthly, "policy-summary", null);
    drawMonthly("policy-chart", monthly, actions, 2015);
    bindRange("policy-chart", monthly, actions);
    renderActions(actions, monthly);
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
    } catch (error) {
        setStatus("The page could not load a data file. " + error);
    }
}

main();
