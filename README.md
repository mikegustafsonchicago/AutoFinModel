## Overview
This project automates the process of generating financial and private equity summaries using AI. It processes uploaded PDFs, extracts key data, and integrates it into structured JSON files and detailed Excel reports. The software supports two primary projects:
1. **Financial Modeling**: Traditional financial models for businesses, including CAPEX, OPEX, and revenue projections.
2. **Catalyst Partners**: Summarizes private equity firm data, including investment team, firm fundamentals, and fees.

## Table of Contents
1. [Overview](#overview)
2. [Setup](#setup)
3. [Features](#features)
4. [Modules](#modules)
   - [app.py](#app-py)
   - [api_processing.py](#api-processing-py)
   - [prompt_builder.py](#prompt-builder-py)
   - [json_manager.py](#json-manager-py)
   - [catalyst_partners_page.py](#catalyst-partners-page-py)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites
- Python 3.11
- Flask
- XlsxWriter
- Tabulator.js
- Anaconda (optional, for managing Python environments)

### Installation
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd [project-directory]
