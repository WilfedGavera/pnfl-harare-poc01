import pandas as pd
from datetime import datetime, timedelta

def calculate_pay_in_4(ticket_price_usd, admin_fee=5.0):
    """
    Calculates a standard 6-week Pay-in-4 schedule.
    25% upfront + 3 equal bi-weekly payments.
    """
    down_payment = round(ticket_price_usd * 0.25, 2)
    remaining_balance = ticket_price_usd - down_payment
    installment_amount = round(remaining_balance / 3, 2)
    
    # Adjust for rounding on the final installment
    total_calculated = down_payment + (installment_amount * 3)
    diff = round(ticket_price_usd - total_calculated, 2)
    installment_3 = round(installment_amount + diff, 2)

    today = datetime.now()
    schedule = [
        {"Installment": "Down Payment (Today)", "Due Date": today.strftime("%Y-%m-%d"), "Amount (USD)": down_payment, "Status": "Due Now"},
        {"Installment": "Payment 2 (Bi-weekly)", "Due Date": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "Amount (USD)": installment_amount, "Status": "Pending"},
        {"Installment": "Payment 3 (Bi-weekly)", "Due Date": (today + timedelta(days=28)).strftime("%Y-%m-%d"), "Amount (USD)": installment_amount, "Status": "Pending"},
        {"Installment": "Final Payment (6 Weeks)", "Due Date": (today + timedelta(days=42)).strftime("%Y-%m-%d"), "Amount (USD)": installment_3, "Status": "Pending"}
    ]
    
    total_payable = ticket_price_usd + admin_fee
    
    return {
        "plan_type": "Pay-in-4 (0% Interest)",
        "ticket_price": ticket_price_usd,
        "admin_fee": admin_fee,
        "total_payable": total_payable,
        "schedule_df": pd.DataFrame(schedule)
    }

def calculate_monthly_loan(ticket_price_usd, months=3, annual_apr=0.18, down_payment_pct=0.30):
    """
    Calculates a longer-term monthly loan (3 to 6 months) with interest.
    """
    down_payment = round(ticket_price_usd * down_payment_pct, 2)
    principal_financed = ticket_price_usd - down_payment
    
    # Simple monthly interest calculation
    monthly_interest_rate = annual_apr / 12
    # Amortization formula for fixed monthly payments
    if monthly_interest_rate > 0:
        monthly_payment = principal_financed * (monthly_interest_rate * (1 + monthly_interest_rate)**months) / ((1 + monthly_interest_rate)**months - 1)
    else:
        monthly_payment = principal_financed / months
        
    monthly_payment = round(monthly_payment, 2)
    total_interest = round((monthly_payment * months) - principal_financed, 2)
    total_payable = round(down_payment + (monthly_payment * months), 2)
    
    today = datetime.now()
    schedule = [{
        "Installment": "Down Payment (Today)", 
        "Due Date": today.strftime("%Y-%m-%d"), 
        "Amount (USD)": down_payment, 
        "Status": "Due Now"
    }]
    
    for m in range(1, months + 1):
        due_date = today + timedelta(days=30 * m)
        schedule.append({
            "Installment": f"Month {m} Installment",
            "Due Date": due_date.strftime("%Y-%m-%d"),
            "Amount (USD)": monthly_payment,
            "Status": "Pending"
        })
        
    return {
        "plan_type": f"{months}-Month Travel Loan ({int(annual_apr*100)}% APR)",
        "ticket_price": ticket_price_usd,
        "down_payment": down_payment,
        "total_interest": total_interest,
        "total_payable": total_payable,
        "schedule_df": pd.DataFrame(schedule)
    }

def calculate_layaway_vault(ticket_price_usd, weeks=8):
    """
    Calculates a true Layaway Savings Vault. No interest, ticket issued upon 100% completion.
    """
    weekly_deposit = round(ticket_price_usd / weeks, 2)
    today = datetime.now()
    
    schedule = []
    for w in range(1, weeks + 1):
        due_date = today + timedelta(days=7 * w)
        schedule.append({
            "Installment": f"Savings Vault - Week {w}",
            "Due Date": due_date.strftime("%Y-%m-%d"),
            "Amount (USD)": weekly_deposit,
            "Status": "Vault Deposit"
        })
        
    return {
        "plan_type": f"Layaway Vault ({weeks} Weeks / 0% Interest)",
        "ticket_price": ticket_price_usd,
        "total_payable": ticket_price_usd,
        "schedule_df": pd.DataFrame(schedule)
    }