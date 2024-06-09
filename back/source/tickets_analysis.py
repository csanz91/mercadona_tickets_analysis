import pandas as pd


# Most popular products
def most_popular_products(df, top_values):
    popular_products = (
        df.groupby("Product_Name")["Product_Qty"]
        .sum()
        .sort_values(ascending=False)
        .head(top_values)
    )
    return popular_products


# Mean ticket cost
def get_mean_ticket_cost(df) -> float:
    mean_cost = df.groupby("Ticket_Number")["Total_Price"].first().mean()
    return mean_cost


def top_price_variations(df, top_values):
    price_changes = df.groupby(by=["Product_Name"])[["Product_Unit_Price", "Date"]]
    last_prices = price_changes.last().rename(
        columns={"Product_Unit_Price": "Final_Unit_Price", "Date": "Final_Date"}
    )
    first_prices = price_changes.first().rename(
        columns={"Product_Unit_Price": "Initial_Unit_Price", "Date": "Initial_Date"}
    )
    price_changes = pd.merge(last_prices, first_prices, on="Product_Name")
    price_changes["Diff_Unit_Price"] = (
        price_changes["Final_Unit_Price"] - price_changes["Initial_Unit_Price"]
    )
    price_changes["Diff_Time"] = (
        price_changes["Final_Date"] - price_changes["Initial_Date"]
    )
    prices_increases = price_changes.nlargest(top_values, "Diff_Unit_Price")
    prices_reductions = price_changes.nsmallest(top_values, "Diff_Unit_Price")
    return prices_reductions, prices_increases


# Price evolution of a product by name
def price_evolution(df, product_name):
    product_prices = (
        df[df["Product_Name"] == product_name]
        .groupby("Date")["Product_Unit_Price"]
        .mean()
    )
    return product_prices


# Avg number of shoppings every month and its cost
def get_avg_shoppings_per_month(df):
    df["Month"] = df["Date"].dt.to_period("M")
    monthly_shopping = df.groupby("Month")["Ticket_Number"].nunique()
    monthly_cost = df.groupby("Month")["Product_Total_Price"].sum()
    avg_shoppings = monthly_shopping.mean()
    avg_cost = monthly_cost.mean()
    return avg_shoppings, avg_cost


def get_most_frequent_products(df, top_values):
    product_frequencies = (
        df["Product_Name"].value_counts() / df["Ticket_Number"].nunique() * 100
    )
    return product_frequencies.nlargest(top_values)


def get_most_expensive_products(df, top_values):
    return (
        df.groupby(by=["Product_Name"])["Product_Unit_Price"].max().nlargest(top_values)
    )


def get_chepeast_products(df, top_values):
    return (
        df.groupby(by=["Product_Name"])["Product_Unit_Price"]
        .min()
        .nsmallest(top_values)
    )


def anaylis(df, top_values=10):

    total_shoppings = df["Ticket_Number"].nunique()
    total_spent = df["Product_Total_Price"].sum()
    mean_ticket_cost = get_mean_ticket_cost(df)
    avg_shoppings_per_month, avg_cost_per_month = get_avg_shoppings_per_month(df)
    popular_products = most_popular_products(df, top_values)
    top_prices_reductions, top_prices_increases = top_price_variations(df, top_values)
    most_frequent_products = get_most_frequent_products(df, top_values)
    most_expensive_products = get_most_expensive_products(df, top_values)
    chepeast_products = get_chepeast_products(df, top_values)

    return {
        "num_shoppings": total_shoppings,
        "total_spent": total_spent,
        "mean_ticket_cost": mean_ticket_cost,
        "avg_shoppings_per_month": avg_shoppings_per_month,
        "avg_cost_per_month": avg_cost_per_month,
        "popular_products": popular_products.to_dict(),
        "top_prices_reductions": top_prices_reductions.to_dict(orient="index"),
        "top_prices_increses": top_prices_increases.to_dict(orient="index"),
        "most_frequent_products": most_frequent_products.to_dict(),
        "most_expensive_products": most_expensive_products.to_dict(),
        "chepeast_products": chepeast_products.to_dict(),
    }
