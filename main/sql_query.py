# -*- coding: utf-8 -*-
insert_sql_history = "INSERT INTO stock.history " \
                     "(Stock_code," \
                     " Date," \
                     " open," \
                     " high," \
                     " low," \
                     " close," \
                     " volume," \
                     " Dividends," \
                     " Stock_Splits," \
                     " shares_outstanding" \
                     ")" \
                     " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

insert_sql_financials = "INSERT INTO stock.financials " \
                        "(Stock_code," \
                        " date," \
                        " Research_Development," \
                        " Effect_Of_Accounting_Charges," \
                        " Income_Before_Tax," \
                        " Minority_Interest," \
                        " Net_Income," \
                        " Selling_General_Administrative," \
                        " Gross_Profit," \
                        " Ebit," \
                        " Operating_Income," \
                        " Selling_General_Administrative_copy1," \
                        " Interest_Expense," \
                        " Extraordinary_Items," \
                        " Non_Recurring," \
                        " Other_Items," \
                        " Income_Tax_Expense," \
                        " Total_Revenue," \
                        " Total_Operating_Expenses," \
                        " Cost_Of_Revenue," \
                        " Total_Other_Income_Expense_Net," \
                        " Discontinued_Operations," \
                        " Net_Income_From_Continuing_Ops," \
                        " Net_Income_Applicable_To_Common_Shares" \
                        ")" \
                        " VALUES (%s, %s, %s, %s," \
                        " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s," \
                        " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

insert_sql_balance_sheet = "INSERT INTO stock.balance_sheet " \
                           "(Stock_code," \
                           " date," \
                           " Capital_Surplus," \
                           " Total_Liab," \
                           " Total_Stockholder_Equity," \
                           " Minority_Interest," \
                           " Other_Current_Liab," \
                           " Total_Assets," \
                           " Common_Stock," \
                           " Other_Current_Assets," \
                           " Retained_Earnings," \
                           " Other_Liab," \
                           " Treasury_Stock," \
                           " Other_Assets," \
                           " Cash," \
                           " Total_Current_Liabilities," \
                           " Deferred_Long_Term_Asset_Charges," \
                           " Short_Long_Term_Debt," \
                           " Other_Stockholder_Equity," \
                           " Property_Plant_Equipment," \
                           " Total_Current_Assets," \
                           " Long_Term_Investments," \
                           " Net_Tangible_Assets," \
                           " Short_Term_Investments," \
                           " Net_Receivables," \
                           " Long_Term_Debt," \
                           " Inventory," \
                           " Accounts_Payable" \
                           ")" \
                           " VALUES (%s, %s, %s, %s, %s, %s, %s, %s," \
                           " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s," \
                           " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

insert_sql_cashflow = "INSERT INTO stock.cashflow " \
                      "(Stock_code," \
                      " date," \
                      " Investments," \
                      " Change_To_Liabilities," \
                      " Total_Cashflows_From_Investing_Activities," \
                      " Net_Borrowings," \
                      " Total_Cash_From_Financing_Activities," \
                      " Change_To_Operating_Activities," \
                      " Net_Income," \
                      " Change_In_Cash," \
                      " Repurchase_Of_Stock," \
                      " Effect_Of_Exchange_Rate," \
                      " Total_Cash_From_Operating_Activities," \
                      " Depreciation," \
                      " Dividends_Paid," \
                      " Change_To_Inventory," \
                      " Change_To_Account_Receivables," \
                      " Other_Cashflows_From_Financing_Activities," \
                      " Change_To_Netincome," \
                      " Capital_Expenditures" \
                      ")" \
                      " VALUES (%s," \
                      " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s," \
                      " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
