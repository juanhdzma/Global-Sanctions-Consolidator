# API-Sanciones-OFAC

## Overview

This project queries the **OFAC public API** to retrieve the latest sanctions report. It extracts and analyzes key information about each entity, including:

-   **Full Name**
-   **Document Type**
-   **Document ID**
-   **Action Type** (Add or Remove)
-   **Sanctions List**

## Functionality

The system continuously monitors and compares successive reports to detect changes, such as:

-   Newly sanctioned entities
-   Entities removed from the list
-   Modifications in entity details

By automating this process, the project ensures up-to-date compliance tracking and enhances risk management.
