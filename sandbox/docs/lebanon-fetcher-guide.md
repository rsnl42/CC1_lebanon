# lebanon-education-fetcher — Usage Guide

## Setup

Drop `lebanon-education-fetcher.js` into your project, e.g.:
```
your-repo/
└── data/
    └── lebanon-education-fetcher.js
```

---

## 1. Fetch Everything (Recommended)

```javascript
import { fetchAll } from './data/lebanon-education-fetcher.js';

const dataset = await fetchAll();

console.log(dataset.meta);
// {
//   fetchedAt: '2026-04-23T...',
//   country: 'Lebanon',
//   iso3: 'LBN',
//   sources: ['worldbank', 'uis', 'unicef', 'unhcr'],
//   totalIndicators: 58,
//   errorCount: 2
// }

console.log(Object.keys(dataset.indicators));
// ['SE.PRM.ENRR', 'SE.SEC.ENRR', ..., 'UNHCR_SYR_REFUGEES_LBN', ...]
```

---

## 2. Fetch a Single Source

```javascript
import { fetchSource } from './data/lebanon-education-fetcher.js';

const wbOnly = await fetchSource('worldbank');  // 'worldbank' | 'uis' | 'unicef' | 'unhcr'
```

---

## 3. Get a Single Indicator's Time Series

```javascript
import { fetchAll, getSeries } from './data/lebanon-education-fetcher.js';

const dataset = await fetchAll();

// Primary enrollment trend
const series = getSeries(dataset, 'SE.PRM.ENRR');
// [{ year: 2005, value: 82.3 }, { year: 2006, value: 84.1 }, ...]
```

---

## 4. Filter by Thematic Angle

```javascript
import { fetchAll, filterByAngle } from './data/lebanon-education-fetcher.js';

const dataset = await fetchAll();

const teacherIndicators  = filterByAngle(dataset, 'teacher');
const displacementData   = filterByAngle(dataset, 'displacement');
const learningOutcomes   = filterByAngle(dataset, 'learning');

// Available angles:
// 'access' | 'teacher' | 'learning' | 'gender'
// 'expenditure' | 'economic' | 'displacement' | 'wellbeing'
```

---

## 5. Pre/Post Conflict Analysis

```javascript
import { fetchAll, getPrePost } from './data/lebanon-education-fetcher.js';

const dataset = await fetchAll();

// All indicators spanning the 2019 collapse (±3 years)
const collapse = getPrePost(dataset, 2019, 3);

Object.entries(collapse).forEach(([code, ind]) => {
  const preAvg  = ind.pre.reduce((s, d) => s + d.value, 0) / ind.pre.length;
  const postAvg = ind.post.reduce((s, d) => s + d.value, 0) / ind.post.length;
  const change  = ((postAvg - preAvg) / preAvg * 100).toFixed(1);
  console.log(`${ind.label}: ${change}% change post-2019`);
});
```

---

## 6. Use Breakpoints for Chart Annotations

```javascript
const dataset = await fetchAll();

// dataset.breakpoints = [
//   { year: 2011, label: 'Syrian civil war begins — refugee influx' },
//   { year: 2015, label: 'Peak Syrian refugee arrivals' },
//   { year: 2019, label: 'Lebanese financial collapse' },
//   { year: 2020, label: 'COVID-19 + Beirut port explosion' },
//   { year: 2021, label: 'Currency collapse — teacher strikes' },
//   { year: 2024, label: 'Southern Lebanon war — mass displacement' },
// ]

// Example with Chart.js annotations plugin:
const annotations = dataset.breakpoints.reduce((acc, bp) => {
  acc[`line_${bp.year}`] = {
    type: 'line',
    xMin: bp.year,
    xMax: bp.year,
    borderColor: 'rgba(255, 99, 132, 0.6)',
    borderWidth: 1.5,
    borderDash: [4, 4],
    label: { content: bp.label, enabled: true, position: 'top', font: { size: 10 } }
  };
  return acc;
}, {});
```

---

## 7. Cache to localStorage (for GitHub Pages)

Avoid re-fetching on every page load:

```javascript
import { fetchAll } from './data/lebanon-education-fetcher.js';

const CACHE_KEY     = 'lbn_edu_dataset_v1';  // bump version when you want fresh data
const CACHE_TTL_MS  = 1000 * 60 * 60 * 24;  // 24 hours

async function getDataset() {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      const { timestamp, data } = JSON.parse(cached);
      if (Date.now() - timestamp < CACHE_TTL_MS) {
        console.log('Using cached dataset');
        return data;
      }
    }
  } catch (_) {}

  console.log('Fetching fresh data...');
  const data = await fetchAll();

  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({ timestamp: Date.now(), data }));
  } catch (e) {
    console.warn('Could not cache to localStorage:', e);
  }

  return data;
}

// Usage
const dataset = await getDataset();
```

---

## 8. Example: Chart with Chart.js

```html
<canvas id="enrollmentChart"></canvas>
<script type="module">
  import { fetchAll, getSeries } from './data/lebanon-education-fetcher.js';
  import * as Chart from 'https://cdn.jsdelivr.net/npm/chart.js/auto/auto.esm.js';

  const dataset = await fetchAll();
  const primary = getSeries(dataset, 'SE.PRM.ENRR');
  const syrian  = getSeries(dataset, 'UNHCR_SYR_REFUGEES_LBN');

  new Chart(document.getElementById('enrollmentChart'), {
    type: 'line',
    data: {
      labels: primary.map(d => d.year),
      datasets: [
        {
          label: 'Primary Enrollment (gross %)',
          data:  primary.map(d => d.value),
          borderColor: '#2563eb',
          tension: 0.3,
          yAxisID: 'y',
        },
        {
          label: 'Syrian Refugees in Lebanon',
          data:  syrian.map(d => ({ x: d.year, y: d.value })),
          borderColor: '#dc2626',
          tension: 0.3,
          yAxisID: 'y2',
        }
      ]
    },
    options: {
      scales: {
        y:  { title: { display: true, text: 'Enrollment (%)' } },
        y2: { position: 'right', title: { display: true, text: 'Refugees' } }
      }
    }
  });
</script>
```

---

## Data Source Summary

| Source | Indicators | Covers | Notes |
|--------|-----------|--------|-------|
| World Bank | 31 | 2000–2023 | Economic context, enrollment, gender, expenditure |
| UNESCO UIS | 16 | 2000–2023 | Learning outcomes, repetition, trained teachers |
| UNICEF | 5 | 2000–2023 | Child labour, early childhood, adolescent births |
| UNHCR | 2 | 2000–present | Syrian + total refugees in Lebanon |
| **Total** | **54** | **2000–2024** | |

## Indicator Angles

| Angle | What it covers |
|-------|---------------|
| `access` | Enrollment rates, out-of-school counts, pre-primary |
| `teacher` | Pupil ratios, trained teachers, teacher counts |
| `learning` | Completion, proficiency, repetition, survival rates |
| `gender` | Gender parity, female vs. male enrollment/completion |
| `expenditure` | Education spending as % GDP / govt budget |
| `economic` | GDP, inflation, poverty, unemployment |
| `displacement` | Refugee counts, net migration |
| `wellbeing` | Child mortality, psychosocial support |
