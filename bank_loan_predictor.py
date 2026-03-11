#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:42:37 2026

@author: ravneetkaursaini
"""

import streamlit as st
import numpy as np
import pandas as pd

def pmt(rate, nper, pv):
    return (rate * pv) / (1 - (1 + rate)**(-nper))


# Dark brown theme + white text
st.markdown("""
<style>
.disclaimer-text {
    font-family: 'Times New Roman', serif;
    font-size: 10.5pt;
    font-style: italic;
    color: #555555;
    line-height: 1.4;
}
</style>

<div class="disclaimer-text">
⚠️ <strong>Disclaimer</strong><br>
This dashboard is a simplified representation of common lending concepts and is intended solely for informational and educational purposes.<br> It does not constitute financial advice, credit underwriting, or a loan approval system.<br> The scoring logic, recommendations, and outputs are generalized estimates and should not be interpreted as actual bank decisions.<br> Real lenders use proprietary models, regulatory guidelines, and institution‑specific criteria that vary widely.<br> Users should consult qualified financial professionals or lenders for accurate assessments.
</div>
""", unsafe_allow_html=True)


st.title("🏦 BANK LOAN APPROVAL SIMULATOR 2026")
st.markdown("---")

# March 2026 US loan rates
loan_types = {
    "Personal Loan": 0.128,
    "Auto Loan": 0.079, 
    "Mortgage": 0.0665,
    "Student Loan": 0.067,
    "Business Loan": 0.102
}

# Sidebar inputs - ONLY MINIMUM LIMITS
st.sidebar.header("👤 BORROWER PROFILE *")
age = st.sidebar.slider("📅 Age *", 18, 80, 30)
salary = st.sidebar.number_input("💼 Annual Income ($) *", min_value=0, value=75000)
credit_score = st.sidebar.slider("📈 FICO Score *", 300, 850, 700)
existing_emi = st.sidebar.number_input("💳 Current Monthly Debt ($)", min_value=0, value=0)

st.sidebar.header("💰 LOAN REQUEST *")
loan_type = st.sidebar.selectbox("🎯 Loan Purpose *", list(loan_types.keys()))
loan_amount = st.sidebar.number_input("💵 Loan Amount ($) *", min_value=0, value=50000)
term_years = st.sidebar.number_input("📆 Term (Years) *", min_value=1, value=5)
down_payment = st.sidebar.number_input("🏦 Down Payment ($)", min_value=0, value=0)

# Calculate button
if st.button("🚀 RUN BANK UNDERWRITING ANALYSIS", type="primary"):
    if salary <= 0 or loan_amount <= 0:
        st.error("⚠️ **COMPLETE ALL * REQUIRED FIELDS**")
    else:
        # Loan calculations
        rate = loan_types[loan_type]
        monthly_rate = rate / 12
        months = term_years * 12
        principal = max(0, loan_amount - down_payment)
        new_emi = -pmt(monthly_rate, months, principal)


        total_emi = new_emi + existing_emi
        monthly_income = salary / 12
        dti = (total_emi / monthly_income) * 100

        # REAL BANK UNDERWRITING - Add this BEFORE approval_odds calculation:
        bank_score = 0

        # STEP 1: FICO HARD FILTER (banks auto-reject <620)
        if credit_score < 620:
            bank_score -= 60
            st.error("🚨 FICO BELOW 620 = AUTO-REJECT")
        elif credit_score < 680:
            bank_score -= 25

        # STEP 2: INCOME VERIFICATION (salary < $30K = risky)
        if salary < 30000:
            bank_score -= 20
            st.warning("LOW INCOME - Needs 2x verification")

        # STEP 3: AGE / CREDIT HISTORY
        if age < 21:
            bank_score -= 15
            st.warning("UNDER 21 = Needs cosigner")

        # STEP 4: LOAN-TO-INCOME RATIO
        if loan_amount > salary * 5:
            bank_score -= 30
            st.error("LOAN > 5X INCOME = DENIED")

        # STEP 5: DTI CALCULATION (Realistic Bank Scoring)
        if dti > 50:
            bank_score -= 999   # Automatic decline (DTI too high)
        elif dti > 43:
            bank_score -= 40    # High risk zone
        elif dti > 36:
            bank_score -= 20    # Moderate risk zone
        else:
            bank_score += 5     # Reward for strong DTI


        # CREDIT BOOST
        credit_boost = min(25, max(0, (credit_score - 650) / 2))

        # FINAL APPROVAL ODDS
        approval_odds = max(5, min(98, 85 + bank_score + credit_boost))

        # Results metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 APPROVAL PROBABILITY", f"{approval_odds:.0f}%")
        col2.metric("📈 EXPECTED INTEREST RATE", f"{rate*100:.2f}%")
        col3.metric("💳 NEW MONTHLY PAYMENT", f"${new_emi:,.0f}")
        st.metric("💸 TOTAL MONTHLY DEBT", f"${total_emi:,.0f}")
        st.metric("⚖️ DTI RATIO", f"{dti:.1f}%")

        # FANCY VERDICT BAROMETER
        st.subheader("📊 BANK DECISION BAROMETER")
        st.progress(approval_odds / 100)
        st.markdown(f"**{approval_odds:.0f}% APPROVAL ODDS**")

        # Color-coded verdict
        if approval_odds >= 80:
            st.success("✅ **FULL APPROVAL** - Premium borrower status")
        elif approval_odds >= 60:
            st.warning("🟡 **CONDITIONAL APPROVAL** - Modifications needed")
        else:
            st.error("❌ **HIGH RISK / LIKELY DECLINE**")

                # BANKER SUGGESTIONS
        st.subheader("💡 ACTIONABLE BANK RECOMMENDATIONS")
        c1, c2 = st.columns(2)

        with c1:
            # DTI‑BASED SUGGESTIONS (aligned with realistic underwriting)
            if dti > 50:
                st.error("🔴 **DTI ABOVE 50% — AUTO‑DECLINE ZONE. PAY DOWN DEBT IMMEDIATELY.**")
            elif dti > 43:
                st.error(f"🔴 **PAYOFF ${existing_emi:,.0f} EXISTING DEBT TO REDUCE DTI BELOW 43%**")
            elif dti > 36:
                st.warning("🟡 **LOWER DTI BELOW 36% FOR BEST APPROVAL ODDS**")

            # CREDIT SCORE SUGGESTION
            if credit_score < 720:
                st.warning("🟡 **RAISE FICO 30+ POINTS FOR BETTER TERMS**")

            # DOWN PAYMENT SUGGESTION
            if loan_amount > 0 and down_payment / loan_amount < 0.2:
                st.info("🟢 **ADD 20% DOWN PAYMENT TO REDUCE RISK**")

        with c2:
            # LOAN‑TO‑INCOME SUGGESTION
            if loan_amount > salary * 5:
                st.error("🔴 **REDUCE LOAN AMOUNT TO BELOW 5× INCOME**")

            # BUSINESS LOAN SPECIAL RULE
            if loan_type == "Business Loan":
                st.warning("🟡 **PERSONAL GUARANTEE REQUIRED FOR BUSINESS LOANS**")

            # COSIGNER SUGGESTION
            st.success("🟢 **CO‑SIGNER CAN INCREASE APPROVAL BY +15%**")

        # "WHAT IF" OPTIMIZATION GRAPH
        st.subheader("🎯 WHAT IF SCENARIOS")
        scenarios = pd.DataFrame({
            "Scenario": ["Current", "Payoff Debt", "Optimal Loan Size"],
            "Approval %": [approval_odds, min(92, approval_odds + 18), 95],
            "DTI %": [dti, max(28, dti - 14), 28]
        })
        st.bar_chart(scenarios.set_index("Scenario"))

        optimal_loan = salary * 4  # Bank max 4x income
        st.info(f"**Pro Tip: ${loan_amount:,.0f} → ${optimal_loan:,.0f} = 95% approval**")


# Footer
st.markdown("---")
st.markdown("*Built for finance professionals - Real 2026 bank underwriting logic*")


