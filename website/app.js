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

const charts = {};

if (window["chartjs-plugin-annotation"]) {
    Chart.register(window["chartjs-plugin-annotation"]);
}

function loadCsv(name) {
    return new Promise((resolve, reject) => {
        Papa.parse(name, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: (result) => resolve(result.data || []),
            error: reject
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

function destroyChart(id) {
    if (charts[id]) {
        charts[id].destroy();
        delete charts[id];
    }
}

function monthLabel(value) {
    return String(value).slice(0, 7);
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
            borderColor: "rgba(140, 47, 47, 0.85)",
            borderWidth: 1.5,
            label: { display: false }
        };
    });
    return annotations;
}

function drawMonthly(canvasId, rows, actions, fromYear) {
    const shown = rows.filter((row) => Number(String(row.Month).slice(0, 4)) >= fromYear);
    const labels = shown.map((row) => row.Month);
    const deaths = shown.map((row) => {
        const note = String(row.Note || "");
        if (note.includes("below zero")) return null;
        return num(row["Estimated deaths"]);
    });
    destroyChart(canvasId);
    charts[canvasId] = new Chart(document.getElementById(canvasId), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Deaths that month",
                data: deaths,
                borderColor: "#1c1915",
                backgroundColor: "rgba(140, 47, 47, 0.12)",
                fill: true,
                pointRadius: 0,
                tension: 0.15,
                spanGaps: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                annotation: { annotations: policyAnnotations(actions, labels) },
                tooltip: {
                    callbacks: {
                        afterLabel(item) {
                            const row = shown[item.dataIndex];
                            return row["How this number was produced"];
                        }
                    }
                }
            },
            scales: {
                y: { title: { display: true, text: "Deaths that month" } },
                x: { ticks: { maxTicksLimit: 8 } }
            }
        }
    });
}

function renderStats(monthly, provisional) {
    const usable = monthly.filter((row) => num(row["Estimated deaths"]) !== null && !String(row.Note || "").includes("below zero"));
    const latest = usable[usable.length - 1];
    const nation = provisional
        .filter((row) => row.geo_type === "nation")
        .sort((a, b) => String(a.month).localeCompare(String(b.month)));
    const latestNation = nation[nation.length - 1];
    const prior = latest ? usable.find((row) => row.Month === monthShift(latest.Month, -12)) : null;
    const yearChange = latest && prior ? num(latest["Estimated deaths"]) - num(prior["Estimated deaths"]) : null;
    const cards = [
        ["Deaths in the latest month", latest ? comma(num(latest["Estimated deaths"])) : "—", latest ? latest.Month + " · " + latest["How this number was produced"] : ""],
        ["Change from a year earlier", yearChange === null ? "—" : (yearChange > 0 ? "+" : "") + comma(yearChange), "Same month, previous year"],
        ["Deaths in the last 12 months", latestNation ? comma(num(latestNation.headline_deaths)) : "—", latestNation ? "12 months ending " + monthLabel(latestNation.month) : ""]
    ];
    document.getElementById("stats").innerHTML = cards.map(([label, value, detail]) =>
        `<div class="stat"><span>${label}</span><b>${value}</b><span>${detail}</span></div>`
    ).join("");
    const extracted = latestNation && latestNation.extracted_at;
    document.getElementById("as-of").textContent = extracted
        ? "Provisional CDC extract " + extracted + ". Final months use CDC WONDER."
        : "Latest month in the spreadsheet: " + (latest ? latest.Month : "");
}

function monthShift(label, delta) {
    const [year, month] = label.split("-").map(Number);
    const date = new Date(Date.UTC(year, month - 1 + delta, 1));
    return date.getUTCFullYear() + "-" + String(date.getUTCMonth() + 1).padStart(2, "0");
}

function renderComparison(rows) {
    destroyChart("comparison");
    charts.comparison = new Chart(document.getElementById("comparison-chart"), {
        type: "bar",
        data: {
            labels: rows.map((row) => row.event),
            datasets: [{
                label: "Deaths per 1,000 people per year",
                data: rows.map((row) => num(row.deaths_per_1000_per_year)),
                backgroundColor: "#8c2f2f"
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
    const fentanyl = rows.find((row) => row.event.startsWith("Synthetic"));
    document.getElementById("comparison-summary").textContent = fentanyl
        ? "In " + fentanyl.start_date.slice(0, 4) + ", the synthetic-opioid category was " + fentanyl.deaths_per_1000_per_year + " deaths per 1,000 people. The other bars use the years and populations in the source file."
        : "";
}

function renderAge(rows) {
    destroyChart("age");
    charts.age = new Chart(document.getElementById("age-chart"), {
        type: "bar",
        data: {
            labels: rows.map((row) => row.group),
            datasets: [{
                label: "Deaths",
                data: rows.map((row) => num(row.deaths)),
                backgroundColor: "#1c1915"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function renderRace(deaths, population) {
    const popByGroup = Object.fromEntries(population.map((row) => [row.wonder_group, row]));
    const deathTotal = deaths.reduce((sum, row) => sum + (num(row.deaths) || 0), 0);
    const popTotal = population.reduce((sum, row) => sum + (num(row.population) || 0), 0);
    const labels = deaths.map((row) => row.group);
    destroyChart("race");
    charts.race = new Chart(document.getElementById("race-chart"), {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Share of deaths",
                    data: deaths.map((row) => deathTotal ? (num(row.deaths) / deathTotal) * 100 : null),
                    backgroundColor: "#8c2f2f"
                },
                {
                    label: "Share of population",
                    data: deaths.map((row) => {
                        const pop = popByGroup[row.group];
                        return pop && popTotal ? (num(pop.population) / popTotal) * 100 : null;
                    }),
                    backgroundColor: "#c4b8a5"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { title: { display: true, text: "Percent" } } }
        }
    });
}

function renderShare(rows) {
    const row = rows[0];
    const node = document.getElementById("share-text");
    if (!row) {
        node.textContent = "The share is not in this extract yet.";
        return;
    }
    const share = num(row.share_of_drug_poisoning_deaths);
    node.textContent = "In " + row.year + ", " + (share * 100).toFixed(1) + "% of U.S. drug-poisoning deaths also listed a synthetic opioid other than methadone ("
        + comma(num(row.t40_4_deaths)) + " of " + comma(num(row.drug_poisoning_deaths)) + "). "
        + row.note;
}

function renderSeizures(rows) {
    const years = [...new Set(rows.map((row) => row.fiscal_year))];
    const components = [...new Set(rows.map((row) => row.component))];
    const colors = ["#1c1915", "#8c2f2f", "#c4b8a5"];
    destroyChart("seizure");
    charts.seizure = new Chart(document.getElementById("seizure-chart"), {
        type: "bar",
        data: {
            labels: years,
            datasets: components.map((component, index) => ({
                label: component,
                data: years.map((year) => rows
                    .filter((row) => row.fiscal_year === year && row.component === component)
                    .reduce((sum, row) => sum + (num(row.pounds) || 0), 0)),
                backgroundColor: colors[index % colors.length]
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { title: { display: true, text: "Pounds" } } }
        }
    });
    const regions = [...new Set(rows.map((row) => row.region))];
    destroyChart("region");
    charts.region = new Chart(document.getElementById("region-chart"), {
        type: "bar",
        data: {
            labels: regions,
            datasets: [{
                label: "Pounds",
                data: regions.map((region) => rows
                    .filter((row) => row.region === region)
                    .reduce((sum, row) => sum + (num(row.pounds) || 0), 0)),
                backgroundColor: "#1f6b4a"
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function renderBudgets(rows) {
    destroyChart("budget");
    charts.budget = new Chart(document.getElementById("budget-chart"), {
        type: "bar",
        data: {
            labels: rows.map((row) => row.agency + " · FY" + row.fiscal_year),
            datasets: [{
                label: "Dollars",
                data: rows.map((row) => num(row.amount_dollars)),
                backgroundColor: "#1c1915"
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
            }
        }
    });
}

function stateChanges(provisional) {
    const states = provisional.filter((row) => row.geo_type === "state");
    const latest = states.reduce((max, row) => row.month > max ? row.month : max, "");
    const priorMonth = monthShift(monthLabel(latest), -12) + "-01";
    const changes = [];
    const names = [...new Set(states.map((row) => row.state))];
    names.forEach((name) => {
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
        return `rgb(${Math.round(244 - t * 213)}, ${Math.round(241 - t * 134)}, ${Math.round(232 - t * 158)})`;
    }
    const t = clamped / 40;
    return `rgb(${Math.round(244 - t * 104)}, ${Math.round(241 - t * 194)}, ${Math.round(232 - t * 185)})`;
}

async function renderMap(provisional) {
    const { latest, changes } = stateChanges(provisional);
    const byName = Object.fromEntries(changes.map((row) => [row.state, row.pct]));
    const ranked = changes.filter((row) => row.pct !== null).sort((a, b) => a.pct - b.pct);
    const down = ranked.filter((row) => row.pct < 0).slice(0, 5);
    const up = ranked.filter((row) => row.pct > 0).reverse().slice(0, 5);
    const list = document.getElementById("state-list");
    const line = (row) => `<li>${row.state}: ${row.pct > 0 ? "+" : ""}${row.pct.toFixed(0)}%</li>`;
    list.innerHTML = `<p class="note">12 months ending ${latest}, compared with a year earlier.</p>
        <p><strong>Largest decreases</strong></p><ul>${down.map(line).join("")}</ul>
        <p><strong>Largest increases</strong></p><ul>${up.map(line).join("")}</ul>`;
    const svg = d3.select("#state-map");
    svg.selectAll("*").remove();
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
                const pct = byName[name];
                return pct === null || pct === undefined ? name + ": not published" : name + ": " + (pct > 0 ? "+" : "") + pct.toFixed(0) + "%";
            });
    } catch (error) {
        svg.append("text").attr("x", 20).attr("y", 40).text("The map could not be loaded. The list is still complete.");
    }
}

function renderActions(actions) {
    const body = document.querySelector("#action-table tbody");
    body.innerHTML = actions
        .slice()
        .sort((a, b) => String(a.action_date).localeCompare(String(b.action_date)))
        .map((row) => `<tr><td>${row.action_date}</td><td>${row.title}<br><span class="note">${row.summary}</span></td><td>${row.actor}</td><td><a href="${row.source_url}">${row.source_title}</a></td></tr>`)
        .join("");
}

function renderNews(rows) {
    document.getElementById("news-list").innerHTML = "<ul>" + rows.map((row) =>
        `<li>${row.published || "Date on the page"} · ${row.publisher}: <a href="${row.url}">${row.title}</a></li>`
    ).join("") + "</ul>";
}

function renderSupply() {
    document.getElementById("supply").innerHTML = `
        <h3>What DEA's threat assessment says</h3>
        <p class="note">Quoted from the 2025 National Drug Threat Assessment. A territory map is not drawn here, because DEA did not publish one as a dataset. <a href="sources/supply_context.md">Full quotations and page context</a>.</p>
        <blockquote><p>The Sinaloa Cartel and Jalisco New Generation Cartel … are the primary groups producing the illicit synthetic drugs driving U.S. drug poisoning deaths and trafficking these drugs into the United States.</p></blockquote>
        <blockquote><p>Mexican TCOs dominate fentanyl transportation into and through the United States, with the Southwest Border (SWB) as the main entry point for fentanyl entering the United States.</p></blockquote>
        <p class="note">The seizure chart above is Customs and Border Protection's own pounds, by region. It is a separate series from the kilogram figure in the DEA report.</p>
    `;
}

let people = [];
let peoplePage = 0;
const PEOPLE_PAGE = 8;

function renderPeople() {
    const start = peoplePage * PEOPLE_PAGE;
    const slice = people.slice(start, start + PEOPLE_PAGE);
    document.getElementById("people").innerHTML = slice.map((person) => {
        const age = person.age_description || person.age || "";
        const state = person.state || "";
        const detail = [age ? "Age " + String(age).replace(/\.0$/, "") : "", state].filter(Boolean).join(" · ");
        return `<article class="person"><a href="${person.exhibit_url}"><img src="${person.image_url}" alt="Photo of ${person.first_name} on the DEA exhibit"></a><p><strong>${person.first_name}</strong><br>${detail}</p></article>`;
    }).join("");
    const pages = Math.max(1, Math.ceil(people.length / PEOPLE_PAGE));
    document.getElementById("people-count").textContent = people.length
        ? `Showing ${start + 1}–${Math.min(start + PEOPLE_PAGE, people.length)} of ${people.length}`
        : "The exhibit listing is not in this copy of the site.";
    document.getElementById("people-prev").disabled = peoplePage === 0;
    document.getElementById("people-next").disabled = peoplePage >= pages - 1;
}

function summarizeMonths(rows) {
    const usable = rows.filter((row) => num(row["Estimated deaths"]) !== null && !String(row.Note || "").includes("below zero"));
    if (!usable.length) return;
    let peak = usable[0];
    usable.forEach((row) => {
        if (num(row["Estimated deaths"]) > num(peak["Estimated deaths"])) peak = row;
    });
    const latest = usable[usable.length - 1];
    document.getElementById("monthly-summary").textContent =
        "The highest month in this file is " + peak.Month + " (" + comma(num(peak["Estimated deaths"])) + " deaths). The latest month is "
        + latest.Month + " (" + comma(num(latest["Estimated deaths"])) + "). Red lines mark official actions.";
}

async function main() {
    const [monthly, provisional, comparison, actions, age, raceDeaths, racePop, share, seizures, budgets, news, memorials] = await Promise.all([
        loadCsv("deaths_by_month.csv"),
        loadCsv("fact_fentanyl_deaths_over_time.csv"),
        loadCsv("comparison_per_1000.csv"),
        loadCsv("policy_actions.csv"),
        loadCsv("wonder_age.csv"),
        loadCsv("wonder_race.csv"),
        loadCsv("census_race_2024.csv"),
        loadCsv("wonder_drug_share.csv"),
        loadCsv("cbp_fentanyl_seizures.csv"),
        loadCsv("agency_budgets.csv"),
        loadCsv("official_announcements.csv"),
        loadCsv("faces_of_fentanyl.csv")
    ]);
    renderStats(monthly, provisional);
    renderComparison(comparison);
    summarizeMonths(monthly);
    drawMonthly("monthly-chart", monthly, actions, 2015);
    drawMonthly("policy-chart", monthly, actions, 2015);
    renderAge(age);
    renderRace(raceDeaths, racePop);
    renderShare(share);
    renderSeizures(seizures);
    renderBudgets(budgets);
    renderActions(actions);
    renderNews(news);
    renderSupply();
    await renderMap(provisional);
    people = memorials.filter((row) => row.first_name && row.image_url);
    renderPeople();

    document.getElementById("range-recent").addEventListener("click", () => {
        document.getElementById("range-recent").setAttribute("aria-pressed", "true");
        document.getElementById("range-all").setAttribute("aria-pressed", "false");
        drawMonthly("monthly-chart", monthly, actions, 2015);
        drawMonthly("policy-chart", monthly, actions, 2015);
    });
    document.getElementById("range-all").addEventListener("click", () => {
        document.getElementById("range-all").setAttribute("aria-pressed", "true");
        document.getElementById("range-recent").setAttribute("aria-pressed", "false");
        drawMonthly("monthly-chart", monthly, actions, 1999);
        drawMonthly("policy-chart", monthly, actions, 1999);
    });
    document.getElementById("people-prev").addEventListener("click", () => {
        peoplePage = Math.max(0, peoplePage - 1);
        renderPeople();
    });
    document.getElementById("people-next").addEventListener("click", () => {
        peoplePage += 1;
        renderPeople();
    });
}

main().catch((error) => {
    document.getElementById("as-of").textContent = "The page could not load a data file. " + error;
});
