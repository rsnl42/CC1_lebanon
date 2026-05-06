# Proposal: Data-Driven Strengthening of Education Continuity in Conflict-Affected Regions

**To:** Education Bridge Initiative (EBI)  
**From:** Sunil Raman  
**Date:** May 6, 2026

---

## 1. Executive Summary
In response to EBI’s Request for Proposals (RFP), this document outlines a framework designed to bridge the gap between field-level expertise and widely available digital data. By integrating granular conflict metrics with longitudinal education data, we propose a system that empowers field staff to

## 2. Context: The Conflict-Education Gap
Our preliminary analysis across 24 conflict-affected countries reveals that traditional metrics often mask the localized reality of school dropouts. While Gross Enrollment may appear stable, children are often "quietly" dropping out due to localized violence, as evidenced in the case of Burkina Faso.

### Key Insights from Preliminary Research:
*   **Conflict vs. Persistence:** Sharp spikes in localized conflict (granular, historical ACLED data) correlate with immediate drops in 'survival rate' even when 'gross enrollment' numbers remain stable. This results in higher OOS (out-of-school) numbers despite rising population of the 'school age children' demographic.
*   **The "Vulnerability Timeline":** Using proximity analysis, we can identify schools within 10km of recurring conflict hotspots at a very granular level. Whilst currently a descriptive solution, it could be used for real-time monitoring as well with access to the most recent ACLED data.
*   **Gender Neutral Interventions:** In regions with escalating violence, female 'survival rate' are declining at a similar rate to male. This suggests a need for emergency interventions, but not necessarily gender-specific ones (at the preliminary stage at least). Reasons for dropping out of school may vary, but solutions like *implementing School Meal programmes* would improve the 'Survival Rate' metrics across all demographics, as evidenced by the improvements in [Ethiopia and Mali](https://github.com/rsnl42/CC1_exam/blob/3231a8d67f5182ffc81998c02c06994172e9cab9/May_02/meal_prog_impact_chart.png)

---

## 3. Strategic Phasing: Pilot, Build, Transfer
We propose a three-phase approach designed to ensure immediate value while building long-term organizational independence.

### Phase 1: Pilot (The Data Foundation)
We will begin by harmonizing existing school registries with open-source HDX and Overpass-API metrics. This phase focuses on calculating the **Dynamic Vulnerability Index** for a select region to validate field-level intuition with hard data.
*   **Proof of Concept:** [Conflict vs. Education Survival Dashboard](https://rsnl42.github.io/CC1_exam/conflict_edu_analysis.html)
### Phase 2: Build (The Monitoring Infrastructure)
Once validated, we will build a scalable pipeline that automates the ingestion of fragmented reports. This phase introduces AI-assisted tools to clean and pivot disparate data sources into a unified format, powering an **Early Warning System**.
*   **Narrative Enabler:** [Interactive Vulnerability Timeline](https://rsnl42.github.io/CC1_exam/timeline_map/index.html) – Demonstrating our ability to track risk migration across borders over two decades.
### Phase 3: Transfer (Capacity & Sustainability)
The final phase focuses on hand-over. We will deliver a **Methodology Guide** and conduct training sessions for EBI field staff. The goal is to ensure the system is "indicator-agnostic"—allowing EBI to pivot the analysis to new metrics or countries without external support. The [Humanitarian Pipeline](/workspaces/CC1_lebanon/humanitarian_pipeline/README.md) is a sample demonstration of this process.

---

## 4. Deliverables
The following tangible outputs will be delivered as part of this engagement:

| Category | Deliverable | Description |
| :--- | :--- | :--- |
| **Strategy** | **Methodology Guide** | A comprehensive manual for automating & maintaining the data pipeline. |
| **Technical** | **Central Analysis Hub** | An interactive, real-time dashboard for EBI-wide school vulnerability monitoring. |
| **Capacity** | **Staff Training Workshop** | Hands-on training session for field staff on data interpretation and tool use. |
| **Data** | **Harmonized Dataset** | A cleaned, multi-year dataset of school sites and conflict events for 24 countries, ready for internal analysis. |

---

## 5. Conclusion
By grounding technical innovation in field-level reality, EBI can ensure that education continuity is maintained even in the most volatile environments. This partnership will provide the tools needed to protect the future of children where it is most at risk.

**Explore the Full Prototype:** [Central Analysis Hub](https://htmlpreview.github.io/?https://github.com/rsnl42/CC1_exam/blob/main/dashboard.html)
