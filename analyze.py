import pandas as pd

# Read the supplier data
df = pd.read_csv("ala_supplier_data.csv")

# Total quantity
total_quantity = df["quantity_kg"].sum()

# Weighted average price
weighted_average_price = (
    (df["quantity_kg"] * df["price_per_kg"]).sum()
    / total_quantity
)

# Average quality
average_quality = df["quality_percent"].mean()

# Supplier with highest quantity
highest_volume = df.loc[
    df["quantity_kg"].idxmax()
]

# Supplier with lowest quality
lowest_quality = df.loc[
    df["quality_percent"].idxmin()
]

print("\n=== ALA SUPPLIER ANALYSIS ===\n")

print(f"Total material: {total_quantity:,} kg")

print(
    f"Average price: "
    f"${weighted_average_price:.2f}/kg"
)

print(
    f"Average quality: "
    f"{average_quality:.2f}%"
)

print(
    f"Highest volume supplier: "
    f"{highest_volume['supplier']}"
)

print(
    f"Lowest quality supplier: "
    f"{lowest_quality['supplier']}"
)

print("\nSupplier Details:\n")

print(df.to_string(index=False))