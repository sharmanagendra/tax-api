from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Tax Calculator API is running!"

@app.route('/calculate', methods=['POST'])
def calculate_tax():
    data = request.get_json()
    
    salary = data.get('annual_salary', 0)
    insurance_80c = data.get('insurance_80c', 0)
    loan_interest = data.get('home_loan_interest', 0)
    rent = data.get('rent_paid', 0)
    city = data.get('city_type', 'non-metro').lower()
    
    # Deductions
    std_deduction = 50000
    max_80c = 150000
    max_home_loan = 200000

    hra_limit = 0.5 * salary if city == 'metro' else 0.4 * salary
    hra_exempt = min(hra_limit, rent, 200000)

    deductions = (
        std_deduction +
        min(insurance_80c, max_80c) +
        min(loan_interest, max_home_loan) +
        hra_exempt
    )

    taxable_income = max(0, salary - deductions)

    # Tax Calculation (old regime)
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = 12500 + (taxable_income - 500000) * 0.2
    else:
        tax = 112500 + (taxable_income - 1000000) * 0.3

    # Suggestions
    tips = []
    if insurance_80c < max_80c:
        tips.append(f"Invest ₹{max_80c - insurance_80c} more under Section 80C.")
    if loan_interest < max_home_loan:
        tips.append(f"Claim ₹{max_home_loan - loan_interest} more on home loan interest.")

    return jsonify({
        "taxable_income": round(taxable_income),
        "tax_payable": round(tax),
        "deductions": round(deductions),
        "tips": tips
    })

import openai
import os
import requests
from flask import request, jsonify

openai.api_key = os.getenv("OPENAI_API_KEY")
TAX_API_URL = "https://tax-api-mwr6.onrender.com/calculate"

@app.route('/chat', methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    prompt = """
    Extract this information from the user's message:
    - annual_salary (number)
    - insurance_80c (number)
    - home_loan_interest (number)
    - rent_paid (number)
    - city_type ("metro" or "non-metro")

    Output only a JSON object with those fields.
    """

    # Step 1: Use GPT to parse the message
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3
    )

    try:
        parsed_data = eval(response.choices[0].message['content'])

        # Step 2: Call /calculate API
        tax_response = requests.post(TAX_API_URL, json=parsed_data)

        if tax_response.status_code == 200:
            result = tax_response.json()
            reply = f"Your taxable income is ₹{result['taxable_income']:,}. Tax payable is ₹{result['tax_payable']:,}."
            if result.get("tips"):
                reply += "\nSuggestions:\n" + "\n".join(result["tips"])
        else:
            reply = "Sorry, I couldn't calculate your tax right now."

    except Exception as e:
        reply = f"Failed to understand your input. Error: {str(e)}"

    return jsonify({"response": reply})

