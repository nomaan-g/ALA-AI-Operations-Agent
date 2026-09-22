import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load API key
load_dotenv()

api_key = os.getenv("AGIONE_API_KEY")

if not api_key:
    print("ERROR: AGIONE_API_KEY was not found.")
    exit()

# --------------------------------------------------
# 1. READ SUPPLIER DATA
# --------------------------------------------------

df = pd.read_csv("ala_supplier_data.csv")

# --------------------------------------------------
# 2. CALCULATE RELIABLE BUSINESS METRICS
# --------------------------------------------------

total_quantity = df["quantity_kg"].sum()

weighted_average_price = (
    (df["quantity_kg"] * df["price_per_kg"]).sum()
    / total_quantity
)

average_quality = df["quality_percent"].mean()

highest_volume = df.loc[
    df["quantity_kg"].idxmax()
]

lowest_quality = df.loc[
    df["quality_percent"].idxmin()
]

# --------------------------------------------------
# 3. CREATE INFORMATION FOR THE AI
# --------------------------------------------------

supplier_summary = f"""
Supplier Analysis:

Total material: {total_quantity:,} kg
Average purchase price: ${weighted_average_price:.2f}/kg
Average quality: {average_quality:.2f}%

Highest volume supplier:
{highest_volume['supplier']}
Quantity: {highest_volume['quantity_kg']:,} kg

Lowest quality supplier:
{lowest_quality['supplier']}
Quality: {lowest_quality['quality_percent']}%
"""

# --------------------------------------------------
# 4. SEND RESULTS TO DEEPSEEK THROUGH AGIONE
# --------------------------------------------------

url = "https://agione.pro/hyperone/xapi/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

prompt = f"""
You are an AI operations assistant for a metals trading
and recycling company.

Analyze the following supplier data:

{supplier_summary}

Create a short management summary.

Include:

1. Overall situation
2. Important observations
3. Suppliers that may need review
4. Possible areas for further investigation

Do not make final procurement decisions.
Use phrases such as "may warrant review" or
"could be investigated further".

Keep the answer professional and easy to understand.
"""

data = {
    "model": "deepseek/deepseek-v4-flash/02acd",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "max_tokens": 800
}

print("\nSending supplier analysis to AGIOne...\n")

response = requests.post(
    url,
    headers=headers,
    json=data
)

print("Status code:", response.status_code)

if response.status_code == 200:

    result = response.json()

    ai_answer = result["choices"][0]["message"]["content"]

    print("\n========================================")
    print("       ALA AI OPERATIONS REPORT")
    print("========================================\n")

    print(supplier_summary)

    print("\nAI MANAGEMENT SUMMARY")
    print("---------------------")

    print(ai_answer)

else:

    print("\nAGIOne Error:")
    print(response.text)