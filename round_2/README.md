# Round 2: SQL Intelligence & Advanced Analytics Suite

Welcome to the **Round 2** workspace. All files, reports, SQL queries, datasets, and interactive notebooks for Round 2 analytics challenges are consolidated here.

---

## 📁 Folder Contents

### 1. 📓 Interactive Jupyter Notebook
- **[`Round2_SQL_Analytics_and_Solutions.ipynb`](Round2_SQL_Analytics_and_Solutions.ipynb)**: Complete, standalone Jupyter Notebook with in-memory SQLite querying across all **16 challenges** (E1–E5, M1–M5, H1–H6). Generates styled Pandas tables and Matplotlib/Seaborn visualization charts.

### 2. 📊 Reports & Query Explanations
- **[`Round2_SQL_Solutions_and_Outputs.md`](Round2_SQL_Solutions_and_Outputs.md)**: Full challenge statements, SQL solutions, and verified markdown output tables.
- **[`Round2_Human_Query_Logic_Explanation.md`](Round2_Human_Query_Logic_Explanation.md)** (and [PDF](Round2_Human_Query_Logic_Explanation.pdf)): Comprehensive human query logic, business context, edge-case rationale, and step-by-step SQL explanations.
- **[`Round2_Insights_Report.md`](Round2_Insights_Report.md)** (and [PDF](Round2_Insights_Report.pdf)): Executive forensics report uncovering platform dynamics, viral anomalies, and bot syndicate behaviors.
- **[`Round2_Query_Logic_Explanations.md`](Round2_Query_Logic_Explanations.md)** (and [PDF](Round2_Query_Logic_Explanations.pdf)): Technical logic breakdown.
- **[`Round2_SQL_Queries_Only.md`](Round2_SQL_Queries_Only.md)** (and [PDF](Round2_SQL_Queries_Only.pdf)): Compact reference containing strictly the raw SQL query code blocks.

### 3. 💾 SQL Scripts
- **[`round2_solutions.sql`](round2_solutions.sql)**: Complete executable SQL queries for all 16 challenges.
- **[`round2_oracle.sql`](round2_oracle.sql)**: Oracle-compliant syntax for all queries.
- **[`setup_oracle_tables.sql`](setup_oracle_tables.sql)**: External table DDL scripts to mount the CSV files into Oracle Database.

### 4. 🗄️ Datasets
- **`Social_Engine_Posts_Cleaned.csv`**: 12,000 cleaned post records.
- **`Social_Engine_Users_Cleaned.csv`**: 1,500 validated creator records.
- **`Social_Engine_Posts_Corrupted.csv`**: 9,500 raw corrupted intake stream posts (used for H5 corruption audit).
- **`cleaned_dataset.csv`**: Joined posts + creator demographic records.

---

## 🚀 Quickstart

To run the interactive notebook:
```bash
jupyter notebook Round2_SQL_Analytics_and_Solutions.ipynb
```
All datasets are available in this directory, so the notebook executes without any additional configuration.
