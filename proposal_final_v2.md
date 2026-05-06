# Proposal: Data-Driven Strengthening of Education Continuity in Conflict-Affected Regions

**To:** Education Bridge Initiative (EBI)  
**From:** Sunil Raman  
**Date:** May 6, 2026

---

## 1. Executive Summary
In response to EBI’s Request for Proposals (RFP), this document outlines a framework designed to bridge the gap between field-level expertise and widely available digital data. By integrating granular conflict metrics with longitudinal education data, we propose a system that empowers field staff to visualize hidden vulnerability trends and patterns, and prioritize resources where conflict-driven school dropouts are most imminent

## 2. Context: The Conflict-Education Gap
Our preliminary analysis across 24 conflict-affected countries reveals that traditional metrics often mask the localized reality of school dropouts. While Gross Enrollment may appear stable, children are often quietly dropping out of schools due to localized violence and conflict events, as evidenced in the case of [Burkina Faso](https://github.com/rsnl42/CC1_exam/workspaces/CC1_lebanon/Burkina_Faso_conflict_edu.png).

### Key Insights from Preliminary Research:
*   **Conflict vs. Persistence:** Sharp spikes in localized conflict (granular, historical ACLED data) correlate with immediate drops in 'survival rate' even when 'gross enrollment' numbers remain stable. This results in higher OOS (out-of-school) numbers despite rising population of the 'school age children' demographic.
*   **The "Vulnerability Timeline":** Using proximity analysis, we can identify schools within 10km of recurring conflict hotspots at a very granular level. Whilst currently a descriptive solution, it could be used for real-time monitoring as well with access to the most recent ACLED data.
*   **Gender Neutral Interventions:** In regions with escalating violence, female 'survival rate' are declining at a similar rate to male. This suggests a need for emergency interventions, but not necessarily gender-specific ones (at the preliminary stage at least). Reasons for dropping out of school may vary, but solutions like *implementing School Meal programmes* would improve the 'Survival Rate' metrics across all demographics, as evidenced by the improvements in [Ethiopia and Mali](https://github.com/rsnl42/CC1_exam/blob/3231a8d67f5182ffc81998c02c06994172e9cab9/May_02/meal_prog_impact_chart.png)

---

## 3. Strategic Phasing: Build and Transfer

We propose a streamlined two-phase approach that embeds our unique 'Data/AI differential' directly into EBI operations. This differential leverages automated ingestion pipelines, geospatial risk modeling, and predictive conflict-education correlation to provide insights far beyond static reporting.

### Phase 1: Build (The Monitoring Infrastructure)
We will deploy our data pipeline to automate the ingestion and harmonization of fragmented education and conflict data. By integrating granular conflict metrics (ACLED) with localized school registry data (HDX/OSM), we build a persistent *Data/AI differential* that functions as an effective monitoring tool, as well as an early warning system.

*   **Key Capabilities:**
    *   **Automated Pipeline:** Transforms disparate, siloed data into a unified, clean, and actionable format.
    *   **Predictive Geospatial Modeling:** Maps 'Dynamic Vulnerability' by identifying school proximity to high-risk zones, allowing for proactive, rather than reactive, resource allocation.
    *   **Interactive Insights:** Powered by our centralized dashboard, providing longitudinal analysis (e.g., [Interactive Vulnerability Timeline](https://rsnl42.github.io/CC1_exam/timeline_map/index.html)) to track risk migration patterns across decades.

### Phase 2: Transfer (Capacity & Sustainability)
The final phase focuses on organizational independence. We will deliver a **Methodology Guide** and conduct intensive training for EBI staff, ensuring they can operate and adapt the pipeline. Our system is designed to be "indicator-agnostic," enabling EBI to incorporate new metrics or geographic regions autonomously. The [Humanitarian Pipeline](/workspaces/CC1_lebanon/humanitarian_pipeline/README.md) demonstrates this modularity, ensuring that the 'Data/AI differential' remains an enduring asset, not a project-based deliverable.

---

## 4. Deliverables
The following tangible outputs will be delivered as part of this engagement:

| Category | Deliverable | Description |
| :--- | :--- | :--- |
| **Technical** | **Central Analysis Hub** | An interactive, real-time dashboard for EBI-wide school vulnerability monitoring. |
| **Strategy** | **Methodology Guide** | A comprehensive manual for automating & maintaining the data pipeline. |
| **Capacity** | **Staff Training Workshop** | Hands-on training session for field staff on data interpretation and tool use. |
| **Data** | **Harmonized Dataset** | A cleaned, multi-year dataset of school sites and conflict events for 24 countries, ready for internal analysis. |

---

## 5. Conclusion
By grounding technical innovation in field-level reality, EBI can ensure that education continuity is maintained even in the most volatile environments. This partnership will provide the tools needed to protect the future of children where it is most at risk.

**Explore the Full Prototype:** [Central Analysis Hub](https://htmlpreview.github.io/?https://github.com/rsnl42/CC1_exam/blob/main/dashboard.html)
