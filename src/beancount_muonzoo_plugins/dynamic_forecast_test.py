__copyright__ = "Copyright (C) 2014-2017  Martin Blais"
__license__ = "GNU GPLv2"

import textwrap
import unittest

from beancount import loader
from beancount.parser import cmptest


class TestDynamicForecast(cmptest.TestCase):
    def test_forecast(self):
        input_text = textwrap.dedent(
            """

            plugin "beancount_muonzoo_plugins.dynamic_forecast" "{}"
            2011-01-01 open Expenses:Restaurant
            2011-01-01 open Assets:Cash

            2011-05-17 % "Something [MONTHLY UNTIL 2011-12-31]"
              Expenses:Restaurant   50.02 USD
              Assets:Cash

        """
        )
        entries, errors, __ = loader.load_string(input_text)
        self.assertFalse(errors)
        self.assertEqualEntries(
            """

            2011-01-01 open Expenses:Restaurant
            2011-01-01 open Assets:Cash

            2011-05-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-06-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-07-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-08-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-09-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-10-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-11-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

            2011-12-17 % "Something"
              Expenses:Restaurant           50.02 USD
              Assets:Cash                  -50.02 USD

        """,
            entries,
        )

    def test_simple_calc(self):
        input_text = textwrap.dedent(
            """

            plugin "beancount_muonzoo_plugins.dynamic_forecast"  "{ 'debug' : True, 'debug_level': 'DEBUG' }"

            2011-01-01 open Equity:Opening-Balances
            2011-01-01 open Assets:Bank

            2011-01-02 % "Opening Position [MONTHLY REPEAT 1 TIMES]"
              expr_i: "R(A(D(12.00),'USD'),2)"
              Equity:Opening-Balances            0 USD
                expr: "-R(A(D(12.00),'USD'),2)"
              Assets:Bank                        0 USD
                expr: "i"



            2011-01-03 balance Assets:Bank       12.00 USD
        """
        )
        entries, errors, __ = loader.load_string(input_text)
        self.assertFalse(errors)
        self.assertEqualEntries(
            """

            2011-01-01 open Equity:Opening-Balances
            2011-01-01 open Assets:Bank

            2011-01-02 % "Opening Position"
              Equity:Opening-Balances              -12.00 USD
              Assets:Bank                           12.00 USD

            2011-01-03 balance Assets:Bank       12.00 USD

        """,
            entries,
        )

    def test_sample_interest_calc(self):
        input_text = textwrap.dedent(
            """

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

            2011-05-01 % "Interest Charge [MONTHLY REPEAT 1 TIMES]"
              bal_acc_loan:          "Liabilities:Loan"
              event_int_rate:        "loan_rate"
              expr_monthly_interest: "R(div(mul(gcu(loan,'USD'),D(int_rate)),D(12)),2)"
              Expenses:Interest     0 USD
                expr: "-monthly_interest"
              Liabilities:Loan      0 USD
                expr: "monthly_interest"
              Assets:Bank           0 CAD
                expr: "monthly_interest"
              Liabilities:Loan      0 CAD
                expr: "-monthly_interest"

            2011-05-02 balance Liabilities:Loan -1000.00 USD

        """
        )
        entries, errors, __ = loader.load_string(input_text)
        self.assertFalse(errors)
        self.assertEqualEntries(
            """

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
              Expenses:Interest      10.00 USD
              Liabilities:Loan      -10.00 USD
              Assets:Bank           -10.00 USD
              Liabilities:Loan       10.00 USD

            2011-05-02 balance Liabilities:Loan -1000.00 USD

        """,
            entries,
        )


if __name__ == "__main__":
    unittest.main()
