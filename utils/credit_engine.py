import math

def evaluate_credit_risk(
    monthly_income_usd,
    avg_mobile_wallet_vol_usd,
    requested_loan_amount_usd,
    has_diaspora_sponsor=False,
    is_cross_border_trader=False,
    existing_active_loans_usd=0.0
):
    """
    Evaluates alternative credit risk using local fintech parameters (EcoCash flow, DTI, cross-border signal).
    Returns a structured decision dictionary with approval status, score, max financing limit, and tier.
    """
    score = 500  # Base score out of 850
    rejection_reasons = []

    # 1. Income to Requested Flight Ratio Assessment
    dti_ratio = (requested_loan_amount_usd + existing_active_loans_usd) / max(monthly_income_usd, 1.0)
    
    if dti_ratio <= 0.30:
        score += 120
    elif dti_ratio <= 0.50:
        score += 60
    elif dti_ratio <= 0.70:
        score += 20
    else:
        rejection_reasons.append(f"High Debt-to-Income: Requested loan exceeds safe monthly income limit (DTI: {round(dti_ratio*100)}%).")

    # 2. Alternative Data: Mobile Money (EcoCash/OneMoney) Velocity & Consistency
    # High mobile wallet turnover indicates active cashflow in informal/formal sectors
    wallet_to_loan_ratio = avg_mobile_wallet_vol_usd / max(requested_loan_amount_usd, 1.0)
    
    if wallet_to_loan_ratio >= 2.0:
        score += 100
    elif wallet_to_loan_ratio >= 1.0:
        score += 50
    elif wallet_to_loan_ratio >= 0.5:
        score += 20
    else:
        score -= 40
        rejection_reasons.append("Low monthly mobile money transaction volume relative to ticket price.")

    # 3. Diaspora Sponsor Multiplier (Lowers Default Risk significantly)
    if has_diaspora_sponsor:
        score += 80

    # 4. Cross-Border Trader Signal (Generates immediate revenue upon return)
    if is_cross_border_trader:
        score += 40

    # Score Cap
    score = min(max(score, 300), 850)

    # Calculate Max Approved Loan Amount based on income & score tier
    max_loan_limit = round(monthly_income_usd * (score / 850) * 0.8, 2)

    # Decision Matrix Tiers
    if score >= 700:
        tier = "Tier 1 - Low Risk"
        approved = True
        recommended_plans = ["Pay-in-4 (0% Interest)", "3-Month Loan (18% APR)", "6-Month Loan (24% APR)"]
        min_down_payment_pct = 0.20  # 20% upfront required
    elif score >= 580:
        tier = "Tier 2 - Medium Risk"
        approved = True
        recommended_plans = ["Pay-in-4 (0% Interest)", "3-Month Loan (18% APR)"]
        min_down_payment_pct = 0.35  # 35% upfront required
    elif score >= 480:
        tier = "Tier 3 - High Risk / Restricted"
        approved = True
        recommended_plans = ["Pay-in-4 (Higher Down Payment)", "Layaway Vault (0% Risk)"]
        min_down_payment_pct = 0.50  # 50% upfront required to lock seat
    else:
        tier = "Tier 4 - Declined for Credit Financing"
        approved = False
        recommended_plans = ["Layaway Vault (100% Savings Model Only)"]
        min_down_payment_pct = 1.0

    return {
        "approved": approved,
        "score": score,
        "tier": tier,
        "max_loan_limit_usd": max_loan_limit,
        "min_down_payment_pct": min_down_payment_pct,
        "recommended_plans": recommended_plans,
        "rejection_reasons": rejection_reasons
    }