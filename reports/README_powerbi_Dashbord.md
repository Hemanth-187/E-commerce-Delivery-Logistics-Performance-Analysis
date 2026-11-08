# E-Commerce Delivery & Logistics Performance Dashboard

## Overview

This Power BI report provides a visual overview of e-commerce order and
delivery performance. It brings together order trends, delivery
outcomes, shipping modes, and key delivery indicators in one place,
making it easier to explore how orders are moving through the delivery
process.

The report contains a single page called **Logistic Overview**.

## What the dashboard shows

The dashboard includes the following visuals:

-   **Delivery on time** -- a headline metric for on-time delivery.
-   **Late Delivery** -- highlights late deliveries.
-   **Advance Shipping** -- shows the advance-shipping measure included
    in the report.
-   **Total Distinct Order IDs** -- displays the distinct order count.
-   **Shipping Canceled** -- highlights canceled shipping.
-   **Monthly Order Trends** -- shows order activity over time.
-   **Shipping Mode Comparison** -- compares order volume across
    shipping modes.
-   **Delivery Status Analysis** -- gives a breakdown of delivery
    status.
-   **Delivery Status Performance** -- compares orders across
    delivery-status categories.

## Filters and interaction

The page includes slicers for:

-   **Order Date**
-   **Shipping Mode**
-   **Delivery Status**

Use these slicers to narrow the report to a particular time period,
shipping method, or delivery status. The visuals are designed to be
explored together, so selecting a filter can help reveal patterns across
the dashboard.

## Data model

The report visuals use a table named **Dashboard Dataset**. Fields
referenced in the report include order ID, order date, year-month,
shipping mode, delivery status, late-delivery information, and
cancellation information.

The exact business definitions and calculation logic for the headline
measures should be confirmed against the underlying dataset and DAX
measures before using the figures for formal reporting.

## File

-   `Dashboard.pbix` -- Power BI report file.
