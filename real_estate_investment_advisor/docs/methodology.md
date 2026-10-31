# Methodology and implementation status

## Available
The source CSV is preserved in data/raw. The reusable loader checks required columns. The Streamlit app provides city and property-type filters, record counts, average price and CSV export. A profiling script reports missing values, duplicates, invalid prices/areas and floor inconsistencies.

## Before training
Validate floor numbers against total floors. Recalculate INR price per square foot from Price_in_Lakhs × 100,000 / Size_in_SqFt rather than interpreting the supplied rounded field as rupees. Confirm the reference date before using Age_of_Property.

## Planned modelling
Define rule-based Good_Investment labels and assumption-based Future_Price_5Y targets explicitly. Split observations before fitting preprocessors or data-derived label thresholds. Compare at least five classification and five regression models. Record classification and regression metrics, preprocessing and model artifacts in MLflow; register the selected models.

Synthetic targets evaluate reproduction of chosen assumptions, not verified future outcomes. Observed future prices and actual investment outcomes are absent. Crime and infrastructure metrics described in the brief are not supplied as direct columns and must not be invented.

## Pending
Feature engineering, model training, held-out evaluation, MLflow integration, prediction forms and feature importance are not implemented yet.
