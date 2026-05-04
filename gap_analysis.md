# Strategic Gap Analysis: Missing Dimensions & Future Research Angles

While the preliminary proposal provides a robust foundation for data-driven prioritization, several critical "blind spots" remain that could significantly strengthen EBI's strategic planning if addressed.

## 1. Missing Data Dimensions

### A. Internal Displacement (IDPs)
Conflict data (Fatalities/Events) tells us where the violence is, but not where the students *go*. 
*   **Gap:** We currently lack real-time data on internal displacement flows. A spike in conflict in one district might lead to an enrollment surge in a neighboring "safe" district, overwhelming infrastructure.
*   **Proposed Angle:** Integrate IOM Displacement Tracking Matrix (DTM) data to map student movement alongside conflict events.

### B. Teacher Attendance & Strikes
EBI provides teacher training, but conflict often leads to non-payment of salaries or strikes.
*   **Gap:** Our current metrics (Survival/Enrollment) are student-centric. We lack high-frequency data on teacher absenteeism or school closures due to labor disputes.
*   **Proposed Angle:** Implement a "Pulse Check" mobile reporting tool for field teams to report school-day availability, correlating this with financial collapse indicators (e.g., Lebanon's inflation rate).

### C. Infrastructure & Repurposing
The RFP mentions schools being "repurposed for military or shelter use."
*   **Gap:** ACLED data captures "events," but not necessarily the *duration* of school occupation. 
*   **Proposed Angle:** Utilize high-resolution satellite imagery (e.g., Sentinel-2) to detect structural damage or unusual activity around known school coordinates identified in the `calculate_vulnerability_years.py` script.

## 2. Alternative Analytical Angles

### A. The "Economic Conflict" Multiplier
In Lebanon, the financial collapse has arguably been as damaging to education as the southern border conflict.
*   **Angle:** Analyze the correlation between currency devaluation and the "Out-of-School Rate." In many contexts, children drop out not because of bombs, but because they must enter the informal labor market to support their families during hyperinflation.

### B. Secondary Education & Recruitment Risk
The RFP highlights that children out of school are vulnerable to recruitment.
*   **Angle:** Shift focus to **Lower Secondary (Ages 12-15)**. While primary schooling often has better data density, the risk of armed group recruitment and early marriage peaks at the transition to secondary school. Analyzing the "Transition Rate" from primary to secondary in conflict zones would be a high-impact indicator for EBI.

### C. Proximity "Heat-Mapping"
Instead of simple 50km buffers, we can develop **Access Decay Models**.
*   **Angle:** Model the "Route to School." If a major road is blocked by a conflict event, a school may be physically intact but effectively "dead" because the catchment area is cut off. This requires integrating road network data (OpenStreetMap) with conflict coordinates.

## 3. Data Quality & Fragmentations
*   **Observation:** The "Survival Rate" indicator is currently sparse in UNESCO datasets.
*   **Recommendation:** EBI should transition from relying solely on global open data to a **Hybrid Data Strategy**, where global data (ACLED/UIS) provides the macro context, and EBI's field teams provide the micro data (monthly attendance) to fill the gaps in the `opri_pivoted.csv` framework.
