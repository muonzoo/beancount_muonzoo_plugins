# Dynamic Forecast

This plugin extends the (legacy)
[`forecast.py`](https://github.com/beancount/beancount/blob/v2/beancount/plugins/forecast.py)
plugin with context and evaluation of posting capabilities. Using metadata,
beancount users can populate a context dictionary with inventories and balances,
along with track events in order to compute a posting `Amount` that varies with
the up-to-date state of the beancount journal.

## Example

```
    plugin "beancount_muonzoo_plugins.dynamic_forecast" "{}"
    2011-01-01 open Equity:Opening-Balances
    2011-01-01 open Expenses:Interest
    2011-01-01 open Liabilities:Loan
    2011-01-01 open Assets:Bank

    2011-01-02 * "Opening Position"
      Equity:Opening-Balances                  0 USD
      Assets:Bank                        1000.00 USD
      Liabilities:Loan                  -1000.00 USD

    2011-01-03 balance Assets:Bank       1000.00 USD
    2011-01-03 balance Liabilities:Loan -1000.00 USD

    2011-02-01 event "loan_rate" "0.12"

    2011-05-01 % "Interest Charge [MONTHLY REPEAT 2 TIMES]"
      bal_acc_loan:          "Liabilities:Loan"
      event_int_rate:        "loan_rate"
      expr_monthly_interest: "R(div(mul(gcu(loan,'USD'),D(int_rate)),D(12)),2)"
      Expenses:Interest     0 USD
        expr: "-monthly_interest"
      Liabilities:Loan      0 USD
        expr: "monthly_interest"

```

Expands to:


```
    2011-01-01 open Equity:Opening-Balances
    2011-01-01 open Expenses:Interest
    2011-01-01 open Liabilities:Loan
    2011-01-01 open Assets:Bank

    2011-01-02 * "Opening Position"
      Equity:Opening-Balances                  0 USD
      Assets:Bank                        1000.00 USD
      Liabilities:Loan                  -1000.00 USD

    2011-01-03 balance Assets:Bank       1000.00 USD
    2011-01-03 balance Liabilities:Loan -1000.00 USD

    2011-02-01 event "loan_rate" "0.12"

    2011-05-01 % "Interest Charge"
      Expenses:Interest     10.00 USD
      Liabilities:Loan     -10.00 USD

    2011-06-01 % "Interest Charge"
      Expenses:Interest     11.00 USD
      Liabilities:Loan     -11.00 USD

```



::: beancount_muonzoo_plugins.dynamic_forecast_test
