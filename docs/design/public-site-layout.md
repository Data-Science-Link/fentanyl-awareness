# How this site is laid out

This note decides the structure of the public site. The questions, and their order, come from the [project brief](../Fentanyl_Project_Overview_and_Initial_Design.md). This note decides how those questions are split across pages, and how the pages look.

## What we used as a guide

Strong public-data sites separate a question, a chart, and a source. They treat a death count as people.

- **Our World in Data** puts one question at the top, the chart under it, and the source on the line under the chart. The download sits with the article, not as a prize at the bottom of a long scroll.
- **Office for National Statistics bulletins** open with the question, then the latest figure, then a contents list. A chart has a written equivalent. Methods sit beside the release, not inside the chart.
- **The COVID Tracking Project** and the early New York Times coronavirus pages used a useful order: what is happening, then where, then who. They also showed the failure mode. One page becomes a wall of charts.
- **The Marshall Project**, **The Trace**, and the Washington Post **Fatal Force** database show names, dates, and a way to look someone up. They do not animate a death.
- **Periscopic’s “U.S. Gun Deaths”** is the counterexample. The falling arcs made the data famous and made the deaths a spectacle. This site does not do that.
- **Financial Times and Datawrapper** charts use one type style, few colors, and color only when it means something. A dashed line and a solid line stay different in black and white.
- **CDC data portals** are where these numbers come from. They are a poor first page for a new reader: many filters, and no sentence that says what the chart is for.

## Five pages, in the order of the story

The site is called Fentanyl Awareness. It starts with the question — is the fentanyl crisis getting better or worse? — because that was hard to piece together. The deaths sit in more than one CDC file, recent months are preliminary, and there was no plain dashboard. The first page answers that question, says why the site was built, and then offers two paths. One path explains what fentanyl is, who died, and which public actions people look at. The other is for analysts and developers: a dataset by month, state, and year, or the open source repository that builds it, so they do not have to start from CDC's interfaces. The Monday job refreshes the file when CDC posts a new month. The counts are people. That is the reason to keep them visible.

A single page gave every part the same weight. On a phone, the download sat under the memorial and the charts. A screen reader had one title for several questions.

Each story page has its own title and a next link. The header is the same list on every page, with the current page marked. Agency announcements stay available from the policy page and the download. They are not one of the five story pages.

| Page | File | What the page is for | What the reader does there |
| --- | --- | --- | --- |
| Start | `website/index.html` | The question, why the site was built, and the two paths | Reads whether deaths are lower or higher than a year earlier, then chooses to learn about fentanyl or take the data |
| Better or worse | `website/trend.html` | Is it going up or down? | Reads finished months and later preliminary estimates, and the state change |
| About fentanyl | `website/who.html` | What is fentanyl, and who died? | Reads what fentanyl is, the memorial, age, race, and the death share, then seizures and budget lines |
| Public policy | `website/actions.html` | Did a border, enforcement, supply-chain, or China action line up with a change? | Reads the monthly series with those dates, and the count that month and a year later. The page does not decide whether the action worked |
| Download | `website/download.html` | A file, or the code that builds it | Takes `deaths_by_state_month.csv`, by month, state, and year, and `deaths_by_month.csv`, or opens the repository |

The deaths-per-1,000 comparison with wars is no longer the front page. The inputs remain in `comparison_per_1000.csv`. The events on the chart are public policy actions.

“Use” in the brief is answered with deaths. CDC does not publish a public series of fentanyl use. The pages say the death category includes fentanyl and is not fentanyl alone.

## How a chart is built

Every visual has the same parts: a title, a sentence that says how to read it, the chart, a table of the same numbers, and a source line. The table is there for someone who cannot see the chart, and for someone who wants the figures on a phone. Hovering a month, a policy line, a state, or a bar shows that figure beside the pointer. The table still holds the same numbers.

Type is a serif for the question and the prose, and a sans-serif for navigation, numbers, tables, and charts. They are system fonts, so the page does not wait on a font service.

Color is a paper background and ink text. One dark red marks the subject: the synthetic-opioid share of deaths. On the map only, green means the 12-month total fell and dark red means it rose. Gray means CDC did not publish a number. Finished months are a solid line. Preliminary months are a dashed line. Public policy dates are vertical lines. The legend says this in words, not only in color.

Spacing is the same card, the same chart height, and the same source line on every page.

Three pictures from the brief are not drawn. DEA’s threat assessment names organizations and the southwest border. It does not publish a territory file, so a cartel map, a supply-chain map, or a crossings map would be a guess. The page quotes DEA and shows Customs and Border Protection’s own pounds by region and by component. The share of drug-poisoning deaths is a number and a single bar, not a pie. One death can list more than one drug, so the rest of the bar is not “other drugs” as one slice.

The public memorial listing has a first name, an age, a state, and a DEA photo address. It does not include a video address. The site links to the exhibit. It does not invent a video link.

## Engagement without a spectacle

The engaging part is a question and a sentence that answers it. There is no counting animation and no autoplay. The memorial is a directory: name, age, state, and a link to the exhibit families submitted to. Photos are shown in small groups, uncropped, and a control above them hides the photos without hiding the names.

A change after an official action is shown as two counts: that month, and twelve months later. The page does not turn that pair into a verdict.

## Phone, keyboard, and screen reader

The header collapses to a Menu button. Targets are at least 44 pixels tall. Charts stack in one column. The map is followed by a written list and a full table.

Each page starts with a skip link. The header is a navigation landmark. The current page is marked. Buttons expose a pressed state. Charts are labeled, and the table next to them is the text equivalent. Focus is a visible outline. If the reader asks for less motion, the charts do not animate and the page does not smooth-scroll.

## Sources

The plain-language file is `deaths_by_month.csv`, with a column dictionary on the download page. Every visual names the file or the agency page it comes from. The calculation notes stay in `docs/methods/`.
