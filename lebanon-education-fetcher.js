/**
 * lebanon-education-fetcher.js
 * 
 * Unified fetcher for Lebanon education crisis data.
 * Sources: World Bank · UNESCO UIS · UNICEF (SDMX) · UNHCR
 * 
 * USAGE:
 *   import { fetchAll, fetchSource } from './lebanon-education-fetcher.js';
 * 
 *   // Fetch everything and get a merged dataset
 *   const dataset = await fetchAll();
 * 
 *   // Or fetch a single source
 *   const wb = await fetchSource('worldbank');
 * 
 * OUTPUT SHAPE:
 *   {
 *     meta: { fetchedAt, country, sources },
 *     indicators: {
 *       'SE.PRM.ENRR': {
 *         source: 'worldbank',
 *         label: 'Primary school enrollment (gross %)',
 *         unit: '%',
 *         series: [{ year: 2005, value: 82.3 }, ...]
 *       },
 *       ...
 *     },
 *     errors: [{ source, indicator, message }]
 *   }
 */

// ─── CONFIGURATION ────────────────────────────────────────────────────────────

const CONFIG = {
  country: {
    iso2: 'LB',
    iso3: 'LBN',
    worldbank: 'LBN',
    uis: 'LBN',
    unicef: 'LBN',
    unhcr: '422',        // UNHCR country ID for Lebanon
  },
  startYear: 2000,
  endYear: new Date().getFullYear(),

  // Conflict breakpoints — annotate these on charts
  breakpoints: [
    { year: 2011, label: 'Syrian civil war begins — refugee influx' },
    { year: 2015, label: 'Peak Syrian refugee arrivals' },
    { year: 2019, label: 'Lebanese financial collapse' },
    { year: 2020, label: 'COVID-19 + Beirut port explosion' },
    { year: 2021, label: 'Currency collapse — teacher strikes' },
    { year: 2024, label: 'Southern Lebanon war — mass displacement' },
  ],

  // Rate limiting delays (ms)
  delay: {
    worldbank: 200,
    uis: 150,
    unicef: 200,
    unhcr: 300,
  }
};

// ─── WORLD BANK INDICATORS ────────────────────────────────────────────────────

const WB_INDICATORS = [
  // Enrollment
  { code: 'SE.PRM.ENRR',        label: 'Primary enrollment, gross (%)',             unit: '%',     angle: 'access' },
  { code: 'SE.SEC.ENRR',        label: 'Secondary enrollment, gross (%)',           unit: '%',     angle: 'access' },
  { code: 'SE.PRM.NENR',        label: 'Primary enrollment, net (%)',               unit: '%',     angle: 'access' },
  { code: 'SE.SEC.NENR',        label: 'Secondary enrollment, net (%)',             unit: '%',     angle: 'access' },
  { code: 'SE.PRM.UNER.ZS',     label: 'Out-of-school children, primary (%)',       unit: '%',     angle: 'access' },
  { code: 'SE.SEC.UNER.ZS',     label: 'Out-of-school adolescents, secondary (%)', unit: '%',     angle: 'access' },
  { code: 'SE.PRM.UNER',        label: 'Out-of-school children, primary (count)',   unit: 'count', angle: 'access' },
  // Teachers
  { code: 'SE.PRM.ENRL.TC.ZS',  label: 'Pupil-teacher ratio, primary',             unit: 'ratio', angle: 'teacher' },
  { code: 'SE.SEC.ENRL.TC.ZS',  label: 'Pupil-teacher ratio, secondary',           unit: 'ratio', angle: 'teacher' },
  { code: 'SE.PRM.TCAQ.ZS',     label: 'Trained teachers, primary (%)',             unit: '%',     angle: 'teacher' },
  { code: 'SE.SEC.TCAQ.ZS',     label: 'Trained teachers, secondary (%)',           unit: '%',     angle: 'teacher' },
  { code: 'SE.PRM.TCHR',        label: 'Teachers in primary (count)',               unit: 'count', angle: 'teacher' },
  { code: 'SE.SEC.TCHR',        label: 'Teachers in secondary (count)',             unit: 'count', angle: 'teacher' },
  // Learning
  { code: 'SE.LPV.PRIM',        label: 'Learning poverty rate (%)',                 unit: '%',     angle: 'learning' },
  { code: 'SE.PRM.CMPT.ZS',     label: 'Primary completion rate (%)',               unit: '%',     angle: 'learning' },
  { code: 'SE.SEC.CMPT.LO.ZS',  label: 'Lower secondary completion rate (%)',       unit: '%',     angle: 'learning' },
  { code: 'SE.ADT.1524.LT.ZS',  label: 'Youth literacy rate 15–24 (%)',             unit: '%',     angle: 'learning' },
  // Gender
  { code: 'SE.ENR.PRIM.FM.ZS',  label: 'Gender parity index, primary',             unit: 'index', angle: 'gender' },
  { code: 'SE.ENR.SECO.FM.ZS',  label: 'Gender parity index, secondary',           unit: 'index', angle: 'gender' },
  { code: 'SE.PRM.UNER.FE.ZS',  label: 'Out-of-school girls, primary (%)',         unit: '%',     angle: 'gender' },
  { code: 'SE.PRM.UNER.MA.ZS',  label: 'Out-of-school boys, primary (%)',          unit: '%',     angle: 'gender' },
  { code: 'SE.PRM.CMPT.FE.ZS',  label: 'Female primary completion rate (%)',       unit: '%',     angle: 'gender' },
  { code: 'SE.PRM.CMPT.MA.ZS',  label: 'Male primary completion rate (%)',         unit: '%',     angle: 'gender' },
  // Expenditure
  { code: 'SE.XPD.TOTL.GD.ZS',  label: 'Education expenditure (% of GDP)',         unit: '%',     angle: 'expenditure' },
  { code: 'SE.XPD.TOTL.GB.ZS',  label: 'Education expenditure (% of govt spend)',  unit: '%',     angle: 'expenditure' },
  // Economic context
  { code: 'NY.GDP.PCAP.CD',     label: 'GDP per capita (USD)',                      unit: 'USD',   angle: 'economic' },
  { code: 'FP.CPI.TOTL.ZG',     label: 'Inflation (%)',                             unit: '%',     angle: 'economic' },
  { code: 'SI.POV.DDAY',        label: 'Poverty headcount ($2.15/day) (%)',         unit: '%',     angle: 'economic' },
  { code: 'SL.UEM.TOTL.ZS',     label: 'Unemployment rate (%)',                     unit: '%',     angle: 'economic' },
  { code: 'SL.UEM.1524.ZS',     label: 'Youth unemployment rate (%)',               unit: '%',     angle: 'economic' },
  { code: 'SM.POP.NETM',        label: 'Net migration (count)',                     unit: 'count', angle: 'displacement' },
  { code: 'SM.POP.REFG',        label: 'Refugee population in Lebanon',             unit: 'count', angle: 'displacement' },
];

// ─── UNESCO UIS INDICATORS ────────────────────────────────────────────────────

const UIS_INDICATORS = [
  { code: 'ROFST.1.CP',         label: 'Out-of-school rate, primary (%)',           unit: '%',     angle: 'access' },
  { code: 'ROFST.2.CP',         label: 'Out-of-school rate, lower secondary (%)',   unit: '%',     angle: 'access' },
  { code: 'ROFST.1.F',          label: 'Out-of-school rate, primary girls (%)',     unit: '%',     angle: 'gender' },
  { code: 'ROFST.1.M',          label: 'Out-of-school rate, primary boys (%)',      unit: '%',     angle: 'gender' },
  { code: 'GER.02',             label: 'Gross enrollment ratio, pre-primary (%)',   unit: '%',     angle: 'access' },
  { code: 'NERA.1',             label: 'Adjusted net enrollment ratio, primary (%)',unit: '%',     angle: 'access' },
  { code: 'REPRT.1',            label: 'Repetition rate, primary (%)',              unit: '%',     angle: 'learning' },
  { code: 'SR.1',               label: 'Survival rate to last grade, primary (%)', unit: '%',     angle: 'learning' },
  { code: 'TRTP.1',             label: 'Trained teachers, primary (%)',             unit: '%',     angle: 'teacher' },
  { code: 'PTRHC.1',            label: 'Pupil-trained teacher ratio, primary',      unit: 'ratio', angle: 'teacher' },
  { code: 'LO.PRIM.ALT.MAT',   label: 'Min. proficiency in math, primary (%)',     unit: '%',     angle: 'learning' },
  { code: 'LO.PRIM.ALT.REA',   label: 'Min. proficiency in reading, primary (%)',  unit: '%',     angle: 'learning' },
  { code: 'CR.1',               label: 'Completion rate, primary (%)',              unit: '%',     angle: 'learning' },
  { code: 'CR.2',               label: 'Completion rate, lower secondary (%)',      unit: '%',     angle: 'learning' },
  { code: 'NISC.1',             label: 'Children in non-formal education (%)',      unit: '%',     angle: 'access' },
  { code: 'XGDP.FSGOV.FFNTR.1',label: 'Govt expenditure per pupil (% GDP p.c.)',   unit: '%',     angle: 'expenditure' },
];

// ─── UNICEF SDMX INDICATORS ───────────────────────────────────────────────────

const UNICEF_INDICATORS = [
  { code: 'CME_OFST',                   label: 'Out-of-school children (all levels)', unit: '%',     angle: 'access' },
  { code: 'PT_CHLD_5-17_LBR_ECON',     label: 'Child labour rate (%)',               unit: '%',     angle: 'economic' },
  { code: 'CME_MRY0T4',                 label: 'Under-5 mortality rate',              unit: 'per 1k',angle: 'wellbeing' },
  { code: 'ED_ANAR_L02',                label: 'Early childhood education attendance',unit: '%',     angle: 'access' },
  { code: 'PT_F_15-19_BIRTH_BY_AGE',   label: 'Adolescent birth rate (girls 15–19)', unit: 'per 1k',angle: 'gender' },
];

// ─── UTILITY FUNCTIONS ────────────────────────────────────────────────────────

const sleep = ms => new Promise(r => setTimeout(r, ms));

function cleanSeries(arr) {
  return arr
    .filter(d => d.value !== null && d.value !== undefined)
    .sort((a, b) => a.year - b.year);
}

function logProgress(source, indicator, status) {
  const icon = status === 'ok' ? '✓' : status === 'skip' ? '–' : '✗';
  console.log(`  [${source}] ${icon} ${indicator}`);
}

// ─── WORLD BANK FETCHER ───────────────────────────────────────────────────────

async function fetchWorldBank() {
  console.log('\n📦 Fetching World Bank...');
  const results = {};
  const errors  = [];
  const codes   = WB_INDICATORS.map(i => i.code);
  const meta    = Object.fromEntries(WB_INDICATORS.map(i => [i.code, i]));

  // WB supports semicolon-batched indicators
  const BATCH = 5;
  for (let i = 0; i < codes.length; i += BATCH) {
    const batch    = codes.slice(i, i + BATCH);
    const joined   = batch.join(';');
    const url      = `https://api.worldbank.org/v2/country/${CONFIG.country.worldbank}` +
                     `/indicator/${joined}` +
                     `?format=json&date=${CONFIG.startYear}:${CONFIG.endYear}&per_page=500`;
    try {
      const res        = await fetch(url);
      const [, data]   = await res.json();

      (data || []).forEach(d => {
        const code = d.indicator.id;
        if (!results[code]) {
          results[code] = {
            source:  'worldbank',
            label:   meta[code]?.label || d.indicator.value,
            unit:    meta[code]?.unit  || '',
            angle:   meta[code]?.angle || 'other',
            series:  []
          };
        }
        if (d.value !== null) {
          results[code].series.push({ year: +d.date, value: d.value });
        }
      });

      batch.forEach(c => {
        if (results[c]) {
          results[c].series = cleanSeries(results[c].series);
          logProgress('WB', c, 'ok');
        } else {
          logProgress('WB', c, 'skip');
        }
      });

    } catch (e) {
      batch.forEach(c => {
        errors.push({ source: 'worldbank', indicator: c, message: e.message });
        logProgress('WB', c, 'error');
      });
    }

    await sleep(CONFIG.delay.worldbank);
  }

  return { results, errors };
}

// ─── UNESCO UIS FETCHER ───────────────────────────────────────────────────────

async function fetchUIS() {
  console.log('\n📚 Fetching UNESCO UIS...');
  const results = {};
  const errors  = [];

  for (const ind of UIS_INDICATORS) {
    const url = `https://api.uis.unesco.org/api/public/data/indicators` +
                `?indicator=${ind.code}` +
                `&country=${CONFIG.country.uis}` +
                `&start=${CONFIG.startYear}` +
                `&end=${CONFIG.endYear}` +
                `&format=json`;
    try {
      const res  = await fetch(url);
      const data = await res.json();

      // UIS response shape: { data: [{ geoUnit, indicator, year, value }] }
      const rows = data?.data || data?.value || [];

      if (rows.length > 0) {
        results[ind.code] = {
          source: 'uis',
          label:  ind.label,
          unit:   ind.unit,
          angle:  ind.angle,
          series: cleanSeries(
            rows
              .filter(r => r.value !== null && r.value !== undefined)
              .map(r => ({ year: +r.year, value: +r.value }))
          )
        };
        logProgress('UIS', ind.code, 'ok');
      } else {
        logProgress('UIS', ind.code, 'skip');
      }

    } catch (e) {
      errors.push({ source: 'uis', indicator: ind.code, message: e.message });
      logProgress('UIS', ind.code, 'error');
    }

    await sleep(CONFIG.delay.uis);
  }

  return { results, errors };
}

// ─── UNICEF SDMX FETCHER ─────────────────────────────────────────────────────

async function fetchUNICEF() {
  console.log('\n🟦 Fetching UNICEF...');
  const results = {};
  const errors  = [];

  for (const ind of UNICEF_INDICATORS) {
    const url = `https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/` +
                `UNICEF,${ind.code},1.0/${CONFIG.country.unicef}..` +
                `?format=sdmx-json` +
                `&startPeriod=${CONFIG.startYear}` +
                `&endPeriod=${CONFIG.endYear}`;
    try {
      const res  = await fetch(url);
      const data = await res.json();

      // SDMX JSON shape — extract observations
      const obs     = data?.data?.dataSets?.[0]?.observations || {};
      const periods = data?.data?.structure?.dimensions?.observation
                       ?.find(d => d.id === 'TIME_PERIOD')?.values || [];

      const series = Object.entries(obs)
        .map(([key, val]) => {
          const timeIdx = +key.split(':').pop();
          const period  = periods[timeIdx];
          return period
            ? { year: +period.id.slice(0, 4), value: val[0] }
            : null;
        })
        .filter(Boolean);

      if (series.length > 0) {
        results[ind.code] = {
          source: 'unicef',
          label:  ind.label,
          unit:   ind.unit,
          angle:  ind.angle,
          series: cleanSeries(series)
        };
        logProgress('UNICEF', ind.code, 'ok');
      } else {
        logProgress('UNICEF', ind.code, 'skip');
      }

    } catch (e) {
      errors.push({ source: 'unicef', indicator: ind.code, message: e.message });
      logProgress('UNICEF', ind.code, 'error');
    }

    await sleep(CONFIG.delay.unicef);
  }

  return { results, errors };
}

// ─── UNHCR FETCHER ────────────────────────────────────────────────────────────

async function fetchUNHCR() {
  console.log('\n🔵 Fetching UNHCR...');
  const results = {};
  const errors  = [];

  try {
    // Syrian refugees in Lebanon by year
    const url = `https://api.unhcr.org/population/v1/population/` +
                `?limit=100&dataset=population&displayType=totals` +
                `&yearFrom=${CONFIG.startYear}&yearTo=${CONFIG.endYear}` +
                `&coo=SYR&coa=LBN&cf_type=REF`;

    const res  = await fetch(url);
    const data = await res.json();
    const rows = data?.items || [];

    if (rows.length > 0) {
      results['UNHCR_SYR_REFUGEES_LBN'] = {
        source: 'unhcr',
        label:  'Syrian refugees in Lebanon (count)',
        unit:   'count',
        angle:  'displacement',
        series: cleanSeries(
          rows.map(r => ({ year: +r.year, value: r.refugees || r.totalPopulation || null }))
        )
      };
      logProgress('UNHCR', 'SYR_REFUGEES_LBN', 'ok');
    }

    // All refugees in Lebanon (all origins)
    const url2 = `https://api.unhcr.org/population/v1/population/` +
                 `?limit=100&dataset=population&displayType=totals` +
                 `&yearFrom=${CONFIG.startYear}&yearTo=${CONFIG.endYear}` +
                 `&coa=LBN&cf_type=REF`;

    const res2  = await fetch(url2);
    const data2 = await res2.json();

    // Aggregate by year
    const byYear = {};
    (data2?.items || []).forEach(r => {
      const y = +r.year;
      byYear[y] = (byYear[y] || 0) + (r.refugees || r.totalPopulation || 0);
    });

    results['UNHCR_ALL_REFUGEES_LBN'] = {
      source: 'unhcr',
      label:  'Total refugees in Lebanon, all origins (count)',
      unit:   'count',
      angle:  'displacement',
      series: cleanSeries(
        Object.entries(byYear).map(([year, value]) => ({ year: +year, value }))
      )
    };
    logProgress('UNHCR', 'ALL_REFUGEES_LBN', 'ok');

  } catch (e) {
    errors.push({ source: 'unhcr', indicator: 'refugees', message: e.message });
    logProgress('UNHCR', 'refugees', 'error');
  }

  await sleep(CONFIG.delay.unhcr);
  return { results, errors };
}

// ─── MAIN FETCH ORCHESTRATOR ──────────────────────────────────────────────────

/**
 * Fetch a single source.
 * @param {'worldbank'|'uis'|'unicef'|'unhcr'} source
 */
export async function fetchSource(source) {
  const fetchers = { worldbank: fetchWorldBank, uis: fetchUIS, unicef: fetchUNICEF, unhcr: fetchUNHCR };
  if (!fetchers[source]) throw new Error(`Unknown source: ${source}`);
  const { results, errors } = await fetchers[source]();
  return {
    meta: { fetchedAt: new Date().toISOString(), country: 'LBN', sources: [source] },
    indicators: results,
    errors,
    breakpoints: CONFIG.breakpoints,
  };
}

/**
 * Fetch all sources and merge into a single dataset.
 * Deduplicates by indicator code — first source wins.
 */
export async function fetchAll() {
  const allErrors = [];
  const merged    = {};

  const sources = [
    fetchWorldBank,
    fetchUIS,
    fetchUNICEF,
    fetchUNHCR,
  ];

  for (const fetcher of sources) {
    const { results, errors } = await fetcher();
    errors.forEach(e => allErrors.push(e));

    Object.entries(results).forEach(([code, data]) => {
      if (!merged[code]) {
        // New indicator — add it
        merged[code] = data;
      } else if (data.series.length > merged[code].series.length) {
        // Same indicator from a different source with more data points — prefer it
        console.log(`  [merge] ${code}: replacing ${merged[code].source} with ${data.source} (more data)`);
        merged[code] = data;
      }
    });
  }

  const dataset = {
    meta: {
      fetchedAt:   new Date().toISOString(),
      country:     'Lebanon',
      iso3:        'LBN',
      sources:     ['worldbank', 'uis', 'unicef', 'unhcr'],
      totalIndicators: Object.keys(merged).length,
      errorCount:  allErrors.length,
    },
    breakpoints: CONFIG.breakpoints,
    indicators:  merged,
    errors:      allErrors,
  };

  console.log(`\n✅ Done. ${dataset.meta.totalIndicators} indicators fetched. ${allErrors.length} errors.`);
  return dataset;
}

// ─── HELPER: FILTER BY ANGLE ──────────────────────────────────────────────────

/**
 * Filter the merged dataset by thematic angle.
 * @param {object} dataset  - output of fetchAll()
 * @param {string} angle    - 'access' | 'teacher' | 'learning' | 'gender' | 'expenditure' | 'economic' | 'displacement' | 'wellbeing'
 */
export function filterByAngle(dataset, angle) {
  return Object.fromEntries(
    Object.entries(dataset.indicators).filter(([, v]) => v.angle === angle)
  );
}

/**
 * Get a flat time series for a single indicator, ready for charting.
 * @param {object} dataset
 * @param {string} code     - indicator code, e.g. 'SE.PRM.ENRR'
 * @returns {{ year, value }[]}
 */
export function getSeries(dataset, code) {
  return dataset.indicators[code]?.series || [];
}

/**
 * Get all indicator series that span a breakpoint year — useful for pre/post analysis.
 * @param {object} dataset
 * @param {number} breakYear  - e.g. 2019
 * @param {number} windowYrs  - years before and after to include (default 3)
 */
export function getPrePost(dataset, breakYear, windowYrs = 3) {
  const result = {};
  Object.entries(dataset.indicators).forEach(([code, ind]) => {
    const pre  = ind.series.filter(d => d.year >= breakYear - windowYrs && d.year < breakYear);
    const post = ind.series.filter(d => d.year >= breakYear && d.year <= breakYear + windowYrs);
    if (pre.length > 0 && post.length > 0) {
      result[code] = { ...ind, pre, post };
    }
  });
  return result;
}

// ─── STANDALONE USAGE (browser console / Node) ────────────────────────────────
// If not using as a module, call fetchAll() directly:
//
//   fetchAll().then(d => {
//     console.log(JSON.stringify(d.meta, null, 2));
//     console.log('Available indicators:', Object.keys(d.indicators));
//   });
