WITH base AS (
    SELECT
        CAST(date_received AS DATE) AS date_received,
        DATE_TRUNC('month', CAST(date_received AS DATE)) AS complaint_month,
        product,
        issue,
        company,
        state,
        timely_response,
        consumer_disputed,
        complaint_id
    FROM complaints
    WHERE company IS NOT NULL
),
monthly_company AS (
    SELECT
        complaint_month,
        company,
        COUNT(*) AS monthly_complaints,
        AVG(1 - timely_response) AS monthly_untimely_rate
    FROM base
    GROUP BY 1, 2
),
monthly_trend AS (
    SELECT
        *,
        LAG(monthly_complaints) OVER (
            PARTITION BY company ORDER BY complaint_month
        ) AS prior_month_complaints,
        AVG(monthly_complaints) OVER (
            PARTITION BY company
            ORDER BY complaint_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS complaints_3m_average
    FROM monthly_company
),
product_counts AS (
    SELECT
        company,
        product,
        COUNT(*) AS product_complaints,
        ROW_NUMBER() OVER (
            PARTITION BY company
            ORDER BY COUNT(*) DESC, product ASC
        ) AS product_rank
    FROM base
    GROUP BY 1, 2
),
company_rollup AS (
    SELECT
        b.company,
        MAX(CASE WHEN p.product_rank = 1 THEN p.product END) AS primary_product,
        COUNT(*) AS complaint_count,
        AVG(1 - b.timely_response) AS untimely_rate,
        AVG(b.consumer_disputed) AS dispute_rate,
        COUNT(DISTINCT b.state) AS states,
        MAX(t.monthly_complaints) AS peak_monthly_complaints,
        MAX(
            CASE
                WHEN t.prior_month_complaints > 0
                THEN (t.monthly_complaints - t.prior_month_complaints)
                     / t.prior_month_complaints::DOUBLE
            END
        ) AS maximum_monthly_growth
    FROM base b
    LEFT JOIN monthly_trend t
        ON b.company = t.company
       AND b.complaint_month = t.complaint_month
    LEFT JOIN product_counts p
        ON b.company = p.company
       AND b.product = p.product
    GROUP BY 1
),
scored AS (
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY complaint_count) AS volume_percentile,
        PERCENT_RANK() OVER (ORDER BY untimely_rate) AS untimely_percentile,
        100 * (
            0.55 * PERCENT_RANK() OVER (ORDER BY complaint_count)
          + 0.45 * PERCENT_RANK() OVER (ORDER BY untimely_rate)
        ) AS risk_score
    FROM company_rollup
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY risk_score DESC, complaint_count DESC, company
    ) AS risk_rank,
    company,
    primary_product,
    complaint_count,
    ROUND(100 * untimely_rate, 2) AS untimely_rate_pct,
    ROUND(100 * dispute_rate, 2) AS dispute_rate_pct,
    states,
    peak_monthly_complaints,
    ROUND(100 * COALESCE(maximum_monthly_growth, 0), 2) AS maximum_monthly_growth_pct,
    ROUND(risk_score, 2) AS risk_score
FROM scored
ORDER BY risk_rank;
