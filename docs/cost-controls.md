# Cost controls

The default project path is free: DuckDB, dbt, Chart.js, and public GitHub
Actions/Pages require no cloud warehouse.

For BigQuery deployments:

1. Use on-demand analysis rather than slot reservations.
2. Configure project-level and user-level query quotas.
3. Create a Cloud Billing budget with alerts before the first workflow run.
4. Keep the BigQuery workflow manual.
5. Query marts instead of repeatedly scanning the raw table.
6. Keep raw and dbt datasets in the same region to avoid transfer charges.

This dataset and its derived tables are comfortably inside BigQuery's free
storage and query allowances under ordinary portfolio use. Budgets are alerts,
not hard spending caps; quotas provide the stronger guardrail.

