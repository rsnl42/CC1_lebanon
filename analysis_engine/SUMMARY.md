# Analysis Engine: New Capabilities Summary

This document summarizes the new analytical tools developed in the `Post_CC1_exam` branch to support indicator-agnostic, reusable data analysis.

## 1. Modular Engine Architecture
- **Structure:** All core logic is located in `analysis_engine/`, separating analysis engines from project-specific data or scripts.
- **Config-Driven:** Analysis parameters are defined in `config/`, allowing for reuse without code changes.

## 2. Transition Risk Model (`transition_risk.py`)
- **Purpose:** Calculates the progression rate of students from primary to lower-secondary levels (the "dropout cliff").
- **Mechanism:** Uses a `LongDataEngine` to process normalized UNESCO-format data, calculating a year-over-year ratio based on the `VALUE` column. 
- **Status:** Verified with synthetic data.

## 3. Access Decay Model (`access_decay.py`)
- **Purpose:** Measures physical school accessibility by calculating conflict-driven friction surfaces.
- **Mechanism:** Uses a "Weighted Distance Decay" algorithm. It penalizes schools based on the proximity and severity of nearby conflict events, generating a dynamic `access_score` that can be computed annually to track accessibility changes over time.
- **Status:** Verified with synthetic data.

## 4. Reusability Strategy
- The engines are built using standard Python and `pandas`, eliminating heavy geospatial dependencies (like `osmnx`), ensuring they remain highly portable and easy to deploy in any environment.
