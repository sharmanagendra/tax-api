{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask import Flask, request, jsonify\
\
app = Flask(__name__)\
\
@app.route('/')\
def home():\
    return "Tax Calculator API is running!"\
\
@app.route('/calculate', methods=['POST'])\
def calculate_tax():\
    data = request.get_json()\
    \
    salary = data.get('annual_salary', 0)\
    insurance_80c = data.get('insurance_80c', 0)\
    loan_interest = data.get('home_loan_interest', 0)\
    rent = data.get('rent_paid', 0)\
    city = data.get('city_type', 'non-metro').lower()\
    \
    # Deductions\
    std_deduction = 50000\
    max_80c = 150000\
    max_home_loan = 200000\
\
    hra_limit = 0.5 * salary if city == 'metro' else 0.4 * salary\
    hra_exempt = min(hra_limit, rent, 200000)\
\
    deductions = (\
        std_deduction +\
        min(insurance_80c, max_80c) +\
        min(loan_interest, max_home_loan) +\
        hra_exempt\
    )\
\
    taxable_income = max(0, salary - deductions)\
\
    # Tax Calculation (old regime)\
    if taxable_income <= 250000:\
        tax = 0\
    elif taxable_income <= 500000:\
        tax = (taxable_income - 250000) * 0.05\
    elif taxable_income <= 1000000:\
        tax = 12500 + (taxable_income - 500000) * 0.2\
    else:\
        tax = 112500 + (taxable_income - 1000000) * 0.3\
\
    # Suggestions\
    tips = []\
    if insurance_80c < max_80c:\
        tips.append(f"Invest \uc0\u8377 \{max_80c - insurance_80c\} more under Section 80C.")\
    if loan_interest < max_home_loan:\
        tips.append(f"Claim \uc0\u8377 \{max_home_loan - loan_interest\} more on home loan interest.")\
\
    return jsonify(\{\
        "taxable_income": round(taxable_income),\
        "tax_payable": round(tax),\
        "deductions": round(deductions),\
        "tips": tips\
    \})\
}