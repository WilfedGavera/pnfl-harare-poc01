import streamlit as st
import pandas as pd
import os
import time

# Import helper engines
from utils.payment_calculator import calculate_pay_in_4, calculate_monthly_loan, calculate_layaway_vault
from utils.credit_engine import evaluate_credit_risk

# ------------------------------------------------------------------------------
# 1. Page Configuration & Theme
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Pay Now, Fly Later (PNFL) — Harare",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Session State Initialization
# ------------------------------------------------------------------------------
if "active_bookings" not in st.session_state:
    st.session_state.active_bookings = [
        {
            "booking_id": "PNFL-8821",
            "passenger": "Tendai Moyo",
            "route": "Harare (HRE) ➔ Johannesburg (JNB)",
            "airline": "Fastjet",
            "flight_date": "2026-11-20",
            "total_price_usd": 220.0,
            "plan_type": "Pay-in-4 (0% Interest)",
            "amount_paid_usd": 55.0,
            "next_due_date": "2026-11-05",
            "next_amount_usd": 55.0,
            "status": "Active (25% Paid)"
        }
    ]

if "currency" not in st.session_state:
    st.session_state.currency = "USD ($)"

# ------------------------------------------------------------------------------
# 3. Sidebar Navigation & Global Controls
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/airplane-take-off.png", width=64)
    st.title("PNFL Harare")
    st.caption("Point-of-Sale Travel Financing PoC")
    st.divider()

    selected_page = st.radio(
        "Navigation Menu",
        [
            "🛫 Customer Booking Portal",
            "💳 My Active Plans",
            "📊 Admin & Merchant Analytics"
        ],
        index=0
    )

    st.divider()
    st.subheader("⚙️ Regional Settings")
    st.session_state.currency = st.selectbox(
        "Display Currency",
        ["USD ($)", "ZiG (ZWL Equiv.)", "ZAR (R)"],
        index=0
    )
    st.info("💡 **Harare Hub:** EcoCash & InnBucks Simulators Active.")

# ------------------------------------------------------------------------------
# 4. Main Header
# ------------------------------------------------------------------------------
st.markdown('<p class="main-header">🛫 Pay Now, Fly Later (PNFL)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Travel Micro-Financing & Alternative Underwriting Portal — Harare (HRE)</p>', unsafe_allow_html=True)
st.divider()

# ------------------------------------------------------------------------------
# PAGE 1: CUSTOMER BOOKING PORTAL & CHECKOUT SIMULATION
# ------------------------------------------------------------------------------
if selected_page == "🛫 Customer Booking Portal":
    st.subheader("1. Flight Selection & Destination Explorer")
    
    data_path = "data/flights.csv"
    if os.path.exists(data_path):
        df_flights = pd.read_csv(data_path)
    else:
        st.error("Flight database `data/flights.csv` not found! Please ensure your mock dataset is generated.")
        df_flights = pd.DataFrame(columns=["flight_id", "airline", "flight_number", "origin", "destination", "dest_code", "flight_date", "departure_time", "flight_type", "price_usd"])

    if not df_flights.empty:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            destinations = sorted(df_flights["destination"].unique())
            selected_dest = st.selectbox("Select Destination", destinations)
        with col_f2:
            flight_types = ["All", "Domestic", "Regional", "International"]
            selected_type = st.selectbox("Flight Category", flight_types)
        with col_f3:
            max_price_val = int(df_flights["price_usd"].max())
            min_price_val = int(df_flights["price_usd"].min())
            price_filter = st.slider("Max Ticket Price (USD)", min_value=min_price_val, max_value=max_price_val, value=max_price_val)

        filtered_flights = df_flights[df_flights["destination"] == selected_dest]
        if selected_type != "All":
            filtered_flights = filtered_flights[filtered_flights["flight_type"] == selected_type]
        filtered_flights = filtered_flights[filtered_flights["price_usd"] <= price_filter]

        st.markdown(f"**Found {len(filtered_flights)} available flights matching your criteria:**")

        if not filtered_flights.empty:
            flight_options = filtered_flights.apply(
                lambda row: f"{row['flight_id']} | {row['airline']} ({row['flight_number']}) | 📅 {row['flight_date']} @ {row['departure_time']} | 💰 ${row['price_usd']}",
                axis=1
            )
            selected_flight_str = st.radio("Select Flight Option", flight_options)
            
            selected_flight_id = selected_flight_str.split(" | ")[0]
            flight_row = filtered_flights[filtered_flights["flight_id"] == selected_flight_id].iloc[0]
            ticket_price = float(flight_row["price_usd"])

            st.divider()
            st.subheader("📋 2. Passenger Alternative Underwriting Eligibility Check")
            
            with st.form("booking_underwriting_form"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    passenger_name = st.text_input("Full Name (as per Passport)", value="Kuda Chigwida")
                    ecocash_number = st.text_input("EcoCash / Mobile Number", value="+263 77 123 4567")
                    monthly_inc = st.number_input("Estimated Monthly Income (USD)", min_value=50, value=550, step=50)
                with col_u2:
                    wallet_vol = st.number_input("Avg. Monthly EcoCash Volume (USD)", min_value=0, value=750, step=50)
                    diaspora = st.checkbox("Supported by Diaspora Family Sponsor?")
                    trader = st.checkbox("Cross-Border Trader (Import/Export)?")

                submitted_underwriting = st.form_submit_button("Evaluate Credit Risk & Terms")

            if submitted_underwriting:
                credit_result = evaluate_credit_risk(
                    monthly_income_usd=monthly_inc,
                    avg_mobile_wallet_vol_usd=wallet_vol,
                    requested_loan_amount_usd=ticket_price,
                    has_diaspora_sponsor=diaspora,
                    is_cross_border_trader=trader
                )
                st.session_state.last_underwriting = credit_result
                st.session_state.selected_flight = flight_row

            if "last_underwriting" in st.session_state and "selected_flight" in st.session_state:
                res = st.session_state.last_underwriting
                f_row = st.session_state.selected_flight
                
                st.divider()
                st.subheader("💳 3. Choose Repayment Plan & Secure Checkout")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Alternative Risk Score", f"{res['score']} / 850", delta=res['tier'])
                col_m2.metric("Max Loan Limit", f"${res['max_loan_limit_usd']}")
                col_m3.metric("Ticket Value", f"${f_row['price_usd']}")

                if res["approved"]:
                    st.success(f"✅ Approved for installment financing! Required Down Payment: {int(res['min_down_payment_pct']*100)}%")
                    
                    plan_choice = st.selectbox(
                        "Select Approved Repayment Structure",
                        res["recommended_plans"]
                    )

                    if "Pay-in-4" in plan_choice:
                        plan_calc = calculate_pay_in_4(ticket_price)
                    elif "3-Month" in plan_choice:
                        plan_calc = calculate_monthly_loan(ticket_price, months=3, annual_apr=0.18, down_payment_pct=res['min_down_payment_pct'])
                    elif "6-Month" in plan_choice:
                        plan_calc = calculate_monthly_loan(ticket_price, months=6, annual_apr=0.24, down_payment_pct=res['min_down_payment_pct'])
                    else:
                        plan_calc = calculate_layaway_vault(ticket_price)

                    st.write(f"**Selected Plan Details:** {plan_calc['plan_type']}")
                    st.dataframe(plan_calc['schedule_df'], use_container_width=True)

                    st.markdown("### 📱 Mobile Money Gateway Simulation")
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        gateway = st.selectbox("Select Gateway", ["EcoCash USD Wallet", "InnBucks Instant", "ZimSwitch Debit Card"])
                    with col_p2:
                        phone_input = st.text_input("Wallet Confirmation Number", value=ecocash_number)
                    
                    agree_terms = st.checkbox("I authorize PNFL to set up automated recurring payment mandates.")

                    if st.button("🚀 Authorize & Pay Down Payment", type="primary"):
                        if not agree_terms:
                            st.warning("Please check the authorization box to proceed.")
                        else:
                            with st.spinner(f"Connecting to {gateway} USSD gateway..."):
                                time.sleep(1.2)
                            with st.spinner("Processing biometric token and locking seat..."):
                                time.sleep(0.8)

                            pnr_code = f"PNFL-{int(time.time()) % 100000}"
                            first_payment = float(plan_calc['schedule_df'].iloc[0]["Amount (USD)"])
                            
                            new_booking = {
                                "booking_id": pnr_code,
                                "passenger": passenger_name,
                                "route": f"{f_row['origin']} ➔ {f_row['destination']}",
                                "airline": f_row['airline'],
                                "flight_date": f_row['flight_date'],
                                "total_price_usd": float(f_row['price_usd']),
                                "plan_type": plan_calc['plan_type'],
                                "amount_paid_usd": first_payment,
                                "next_due_date": str(plan_calc['schedule_df'].iloc[1]["Due Date"]) if len(plan_calc['schedule_df']) > 1 else "Completed",
                                "next_amount_usd": float(plan_calc['schedule_df'].iloc[1]["Amount (USD)"]) if len(plan_calc['schedule_df']) > 1 else 0.0,
                                "status": "Active (PNR Ticket Issued)"
                            }
                            st.session_state.active_bookings.append(new_booking)
                            st.balloons()
                            st.success(f"🎉 Payment successful! E-Ticket PNR Code: `{pnr_code}` generated. Check 'My Active Plans'.")

                else:
                    st.warning("⚠️ Traditional credit financing was not approved based on your current cashflow profile.")
                    st.info("💡 You can securely book using our **Layaway Savings Vault** model below:")
                    
                    layaway_calc = calculate_layaway_vault(ticket_price, weeks=8)
                    st.dataframe(layaway_calc['schedule_df'], use_container_width=True)
                    
                    if st.button("🔒 Start Layaway Vault (First Deposit)"):
                        pnr_code = f"PNFL-{int(time.time()) % 100000}"
                        first_deposit = float(layaway_calc['schedule_df'].iloc[0]["Amount (USD)"])
                        
                        new_booking = {
                            "booking_id": pnr_code,
                            "passenger": passenger_name,
                            "route": f"{f_row['origin']} ➔ {f_row['destination']}",
                            "airline": f_row['airline'],
                            "flight_date": f_row['flight_date'],
                            "total_price_usd": float(f_row['price_usd']),
                            "plan_type": layaway_calc['plan_type'],
                            "amount_paid_usd": first_deposit,
                            "next_due_date": str(layaway_calc['schedule_df'].iloc[1]["Due Date"]),
                            "next_amount_usd": float(layaway_calc['schedule_df'].iloc[1]["Amount (USD)"]),
                            "status": "Active (Vault Savings)"
                        }
                        st.session_state.active_bookings.append(new_booking)
                        st.balloons()
                        st.success(f"🔒 Layaway Vault opened! PNR `{pnr_code}`. Ticket will issue upon 100% completion.")
        else:
            st.info("No flights match your filter criteria.")

# ==============================================================================
# PAGE 2: MY ACTIVE PLANS (Enhanced)
# ==============================================================================
elif selected_page == "💳 My Active Plans":
    st.subheader("💳 Customer Dashboard — Active Installments & Savings")
    st.caption("Manage your flight loans, track payment progress, and simulate installment settlements.")
    
    if len(st.session_state.active_bookings) == 0:
        st.info("No active booking plans found. Head over to the **Customer Booking Portal** to finance a flight!")
    else:
        for idx, booking in enumerate(st.session_state.active_bookings):
            # Determine Ticket Status based on payments made
            paid_pct = (booking['amount_paid_usd'] / booking['total_price_usd']) * 100
            
            if "Vault" in booking['plan_type']:
                ticket_status = "🔒 Locked (Issued at 100% Savings)" if paid_pct < 100 else "🎫 PNR Ticket Issued!"
            else:
                ticket_status = "🎫 PNR Ticket Issued (Secured by BNPL)"

            with st.expander(f"🎫 {booking['booking_id']} | {booking['route']} ({booking['airline']}) — {ticket_status}", expanded=True):
                col_d1, col_d2, col_d3 = st.columns(3)
                
                with col_d1:
                    st.write(f"**Passenger:** {booking['passenger']}")
                    st.write(f"**Airline & Route:** {booking['airline']} | {booking['route']}")
                    st.write(f"**Flight Date:** {booking['flight_date']}")
                
                with col_d2:
                    st.write(f"**Plan Type:** {booking['plan_type']}")
                    st.write(f"**Total Ticket Value:** `${booking['total_price_usd']}`")
                    st.write(f"**Current Status:** {booking['status']}")
                
                with col_d3:
                    st.metric("Total Paid So Far", f"${booking['amount_paid_usd']}", delta=f"{int(paid_pct)}% Settled")

                # Visual progress bar
                progress_val = min(float(booking['amount_paid_usd'] / booking['total_price_usd']), 1.0)
                st.progress(progress_val, text=f"Repayment / Savings Progress: {int(progress_val * 100)}%")
                
                # Next payment details
                col_n1, col_n2 = st.columns([2, 1])
                with col_n1:
                    if paid_pct < 100:
                        st.info(f"📅 **Next Due Date:** {booking['next_due_date']} | **Amount:** `${booking['next_amount_usd']}`")
                    else:
                        st.success("🎉 Plan Fully Settled! Enjoy your trip out of Harare.")

                with col_n2:
                    if paid_pct < 100:
                        if st.button(f"📱 Pay Installment (${booking['next_amount_usd']})", key=f"pay_inst_{idx}"):
                            # Simulate installment payment
                            remaining_left = round(booking['total_price_usd'] - booking['amount_paid_usd'], 2)
                            payment_chunk = min(booking['next_amount_usd'], remaining_left)
                            
                            booking['amount_paid_usd'] = round(booking['amount_paid_usd'] + payment_chunk, 2)
                            new_paid_pct = (booking['amount_paid_usd'] / booking['total_price_usd']) * 100
                            
                            if new_paid_pct >= 100:
                                booking['status'] = "Completed & Fully Settled"
                                booking['next_due_date'] = "N/A"
                                booking['next_amount_usd'] = 0.0
                                st.balloons()
                            else:
                                # Increment mock due date by 14 days
                                try:
                                    next_dt = pd.to_datetime(booking['next_due_date']) + pd.Timedelta(days=14)
                                    booking['next_due_date'] = next_dt.strftime("%Y-%m-%d")
                                except:
                                    pass
                            
                            st.success(f"Successfully processed `${payment_chunk}` via EcoCash!")
                            st.rerun()
# ==============================================================================
# PAGE 3: ADMIN & MERCHANT ANALYTICS (Enhanced)
# ==============================================================================
elif selected_page == "📊 Admin & Merchant Analytics":
    st.subheader("📊 Merchant Discount & Platform Financial Dashboard")
    st.caption("Real-time telemetry tracking Gross Merchandise Value (GMV), MDR commission yields, and portfolio risk metrics.")
    
    # Calculate portfolio metrics dynamically from session state
    total_bookings_count = len(st.session_state.active_bookings)
    total_gmv = sum([b['total_price_usd'] for b in st.session_state.active_bookings])
    total_collected = sum([b['amount_paid_usd'] for b in st.session_state.active_bookings])
    
    # Revenue models: 5.5% average MDR + $10 origination fee + interest
    estimated_mdr_revenue = total_gmv * 0.055
    estimated_origination_fees = total_bookings_count * 10.0
    estimated_interest = total_gmv * 0.04
    total_net_revenue = estimated_mdr_revenue + estimated_origination_fees + estimated_interest

    # Top-line KPI metrics
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("Gross Merchandise Value (GMV)", f"${total_gmv:,.2f}", delta="+24.2% MoM")
    col_a2.metric("Total Net Platform Revenue", f"${total_net_revenue:,.2f}", delta="+19.8% MoM")
    col_a3.metric("Active Financed Bookings", f"{total_bookings_count}", delta="Harare Hub")
    col_a4.metric("Simulated Non-Performing Loans", "1.8%", delta="-0.5% (Low Risk)")
    
    st.divider()

    # Layout charts and master ledger
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("📈 Revenue Stream Breakdown")
        revenue_breakdown = pd.DataFrame({
            "Revenue Stream": [
                "Merchant Discount Rate (MDR ~5.5%)", 
                "Origination / Admin Fees", 
                "Long-Term Loan Interest (APR)", 
                "Ancillary Insurance Commissions"
            ],
            "Earnings (USD)": [
                round(estimated_mdr_revenue, 2), 
                round(estimated_origination_fees, 2), 
                round(estimated_interest, 2), 
                round(total_bookings_count * 12.5, 2)
            ]
        })
        st.bar_chart(revenue_breakdown, x="Revenue Stream", y="Earnings (USD)")

    with col_c2:
        st.subheader("🛫 Bookings by Payment Model")
        if total_bookings_count > 0:
            df_ledger_summary = pd.DataFrame(st.session_state.active_bookings)
            plan_counts = df_ledger_summary["plan_type"].value_counts().reset_index()
            plan_counts.columns = ["Plan Type", "Count"]
            st.dataframe(plan_counts, use_container_width=True, hide_index=True)
        else:
            st.info("No bookings recorded yet.")

    st.divider()
    st.subheader("📋 Master Portfolio Ledger")
    if total_bookings_count > 0:
        st.dataframe(pd.DataFrame(st.session_state.active_bookings), use_container_width=True)
    else:
        st.info("Master ledger is currently empty.")