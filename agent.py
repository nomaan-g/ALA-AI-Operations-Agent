import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv


# ---------------------------------------
# LOAD API KEY
# ---------------------------------------

load_dotenv()

api_key = os.getenv("AGIONE_API_KEY")

if not api_key:
    print("ERROR: AGIONE_API_KEY was not found.")
    exit()


# ---------------------------------------
# AGIOne CONFIGURATION
# ---------------------------------------

url = "https://agione.pro/hyperone/xapi/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

MODEL = "deepseek/deepseek-v4-flash/02acd"


# ---------------------------------------
# TOOL 1: SUPPLIER ANALYSIS
# ---------------------------------------

def analyze_supplier_data():

    df = pd.read_csv("ala_supplier_data.csv")

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

    return {
        "total_quantity": int(total_quantity),
        "average_price": round(float(weighted_average_price), 2),
        "average_quality": round(float(average_quality), 2),
        "highest_volume_supplier": highest_volume["supplier"],
        "highest_volume_quantity": int(
            highest_volume["quantity_kg"]
        ),
        "lowest_quality_supplier": lowest_quality["supplier"],
        "lowest_quality": int(
            lowest_quality["quality_percent"]
        )
    }


# ---------------------------------------
# TOOL 2: CALCULATOR
# ---------------------------------------

def calculate_total(quantity, price):

    return round(quantity * price, 2)


# ---------------------------------------
# ASK AI WHICH TOOL TO USE
# ---------------------------------------

def ask_agent(user_question):

    prompt = f"""
You are an AI operations agent.

The user asked:

"{user_question}"

Available tools:

1. analyze_supplier_data
   Use this for supplier quantities,
   prices, quality and supplier analysis.

2. calculate_total
   Use this for mathematical calculations
   involving quantity and price.

Decide which tool is needed.

Respond with ONLY:

SUPPLIER_ANALYSIS

CALCULATOR

NO_TOOL
"""

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 100
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    if response.status_code != 200:

        print("AGIOne Error:")
        print(response.text)

        return None

    result = response.json()

    return result[
        "choices"
    ][0]["message"]["content"].strip()


# ---------------------------------------
# ASK USER
# ---------------------------------------

user_question = input(
    "\nWhat would you like to know? "
)

print("\nAgent is thinking...")

decision = ask_agent(user_question)

print("\nAgent decision:")
print(decision)


# ---------------------------------------
# SUPPLIER ANALYSIS
# ---------------------------------------

if "SUPPLIER_ANALYSIS" in decision:

    print("\nCalling Supplier Analysis Tool...")

    result = analyze_supplier_data()

    print("\nTool Result:")
    print(json.dumps(result, indent=2))


    # -----------------------------------
    # SEND TOOL RESULT BACK TO AI
    # -----------------------------------

    final_prompt = f"""
You are an AI operations assistant.

The user asked:

"{user_question}"

You used the supplier analysis tool.

The tool returned:

{json.dumps(result, indent=2)}

Create a short professional management
answer.

Explain the important findings in simple
business language.

Do not invent information.

Do not make final procurement decisions.

If something deserves attention, say it
"may warrant review".
"""

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        "max_tokens": 500
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )


    # -----------------------------------
    # DISPLAY FINAL ANSWER
    # -----------------------------------

    if response.status_code == 200:

        final_result = response.json()

        final_answer = final_result[
            "choices"
        ][0]["message"]["content"]

        print("\n===================================")
        print("       ALA AI AGENT RESPONSE")
        print("===================================\n")

        print(final_answer)

    else:

        print("\nAGIOne Error:")
        print(response.text)


# ---------------------------------------
# CALCULATOR
# ---------------------------------------

elif "CALCULATOR" in decision:

    print("\nCalling Calculator Tool...")

    quantity = 53000
    price = 1.85

    result = calculate_total(
        quantity,
        price
    )

    print(
        f"\nTotal purchase value: ${result}"
    )


# ---------------------------------------
# NO TOOL
# ---------------------------------------

else:

    print(
        "\nThe agent determined that "
        "no tool is required."
    )