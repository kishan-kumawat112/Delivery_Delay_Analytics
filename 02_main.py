
import pandas as pd
import matplotlib.pyplot as plt

# Step 01: Load the dataset
df = pd.read_csv("data/delivery_delay_dataset.csv")

########  PERFORM FUNCTIONS ############### ""
# Display the first five rows
print("FIRST FIVE ROWS")
print(df.head())

# Check the number of rows and columns
print("\nDATASET SHAPE")
print(df.shape)

# Display column names
print("\nCOLUMN NAMES")
print(df.columns)

#Check dataset information
print("\nDATASET INFORMATION")
df.info()

#Check missing values
print("\nMISSING VALUES")
print(df.isnull().sum())

# Check duplicate rows
print("\nDUPLICATE ROWS")
print(df.duplicated().sum())

############## REMOVE DUPLICATES OR CLEANING THE SHEET ############## "STEP ---> 04"
# Remove duplicate rows
df = df.drop_duplicates()

print("\nDATASET SHAPE AFTER REMOVING DUPLICATES")
print(df.shape)


# Handle missing values

df["Carrier"] = df["Carrier"].fillna("Unknown")
df["Product_Type"] = df["Product_Type"].fillna("Unknown")

df["Distance_KM"] = df["Distance_KM"].fillna(
    df["Distance_KM"].median()
)

print("\nMISSING VALUES AFTER CLEANING")
print(df.isnull().sum())


# Verify duplicates

print("\nDUPLICATES AFTER CLEANING")
print(df.duplicated().sum())



# Display basic statistics
print("\nBASIC STATISTICS")
print(df.describe())

# len(df) — counts the rows in the dataset.
# nunique() — counts distinct values.
# unique() — displays distinct values.
print("\nTOTAL ORDERS")
print(len(df))

print("\nUNIQUE WAREHOUSES")
print(df["Warehouse"].nunique())

print("\nDELIVERY CARRIERS")
print(df["Carrier"].unique())


#count the orders handled by each warehouse and carrier.
print("\nORDERS BY WAREHOUSE")
print(df["Warehouse"].value_counts())

print("\nORDERS BY CARRIER")
print(df["Carrier"].value_counts(dropna=False))


######################## CONVERT DATE COLUMNS #####################  "STEP 05-->"
#Convert date columns

df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Promised_Date"] = pd.to_datetime(df["Promised_Date"])
df["Actual_Delivery_Date"] = pd.to_datetime(
    df["Actual_Delivery_Date"]
)

print("\nUPDATED DATE TYPES")
print(df[[
    "Order_Date",
    "Promised_Date",
    "Actual_Delivery_Date"
]].dtypes)

################################## SAVE CLEANED DATASET #####################"STEP --->06"
#Save cleaned dataset

df.to_csv("data/cleaned_delivery_dataset.csv", index=False)

print("\nCleaned dataset saved successfully!")



# Load the cleaned dataset
df = pd.read_csv("data/cleaned_delivery_dataset.csv")

# Convert date columns into datetime format
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Promised_Date"] = pd.to_datetime(df["Promised_Date"])
df["Actual_Delivery_Date"] = pd.to_datetime(
    df["Actual_Delivery_Date"]
)

print("\n CLEANED DATASET")
print(df.shape)


# Calculate delivery delay in days

df["Delivery_Delay_Days"] = (
    df["Actual_Delivery_Date"] - df["Promised_Date"]
).dt.days

print("\nDELIVERY DELAY ANALYSIS")
print(df[[
    "Promised_Date",
    "Actual_Delivery_Date",
    "Delivery_Delay_Days"
]].head(10))



# Identify late deliveries

df["Delivery_Status"] = df["Delivery_Delay_Days"].apply(
    lambda days: "Late" if days > 0
    else "On Time" if days == 0
    else "Early"
)

print("\nDELIVERY STATUS")
print(df["Delivery_Status"].value_counts())

print("\nFIRST 10 ORDERS WITH DELIVERY STATUS")
print(df[[
    "Delivery_Delay_Days",
    "Delivery_Status"
]].head(10))



#Calculate late delivery percentage

total_orders = len(df)

late_orders = (df["Delivery_Status"] == "Late").sum()

late_percentage = (late_orders / total_orders) * 100

print("\nLATE DELIVERY KPI")
print("Total Orders:", total_orders)
print("Late Orders:", late_orders)
print("Late Delivery Percentage:", round(late_percentage, 2), "%")


# Analyze late deliveries by carrier

late_orders_df = df[df["Delivery_Status"] == "Late"]

print("\nLATE ORDERS BY CARRIER")
print(late_orders_df["Carrier"].value_counts())

print("\nLATE ORDERS BY CARRIER AND WAREHOUSE")
print(
    late_orders_df.groupby(["Carrier", "Warehouse"])
    .size()
    .sort_values(ascending=False)
)




#Calculate late delivery percentage by carrier

total_by_carrier = df.groupby("Carrier").size()

late_by_carrier = (
    df[df["Delivery_Status"] == "Late"]
    .groupby("Carrier")
    .size()
)

carrier_late_percentage = (
    late_by_carrier / total_by_carrier * 100
).round(2)

print("\nLATE DELIVERY PERCENTAGE BY CARRIER")
print(carrier_late_percentage.sort_values(ascending=False))




#Analyze late deliveries by warehouse

total_by_warehouse = df.groupby("Warehouse").size()

late_by_warehouse = (
    df[df["Delivery_Status"] == "Late"]
    .groupby("Warehouse")
    .size()
)

warehouse_late_percentage = (
    late_by_warehouse / total_by_warehouse * 100
).round(2)

print("\nLATE DELIVERY PERCENTAGE BY WAREHOUSE")
print(warehouse_late_percentage.sort_values(ascending=False))




#Calculate average delivery delay

late_orders_df = df[df["Delivery_Delay_Days"] > 0]

average_delay = late_orders_df["Delivery_Delay_Days"].mean()

maximum_delay = late_orders_df["Delivery_Delay_Days"].max()

print("\nDELIVERY DELAY SUMMARY")
print("Number of Late Orders:", len(late_orders_df))
print("Average Delay (Days):", round(average_delay, 2))
print("Maximum Delay (Days):", maximum_delay)



#Analyze delivery delays by route

late_orders_df = df[df["Delivery_Delay_Days"] > 0]

route_delay = (
    late_orders_df.groupby("Route")["Delivery_Delay_Days"]
    .agg(["count", "mean", "max"])
    .round(2)
    .sort_values("mean", ascending=False)
)

print("\nDELIVERY DELAY BY ROUTE")
print(route_delay)


#Calculate late-delivery percentage by route

total_by_route = df.groupby("Route").size()

late_by_route = (
    df[df["Delivery_Delay_Days"] > 0]
    .groupby("Route")
    .size()
)

route_late_percentage = (
    late_by_route / total_by_route * 100
).round(2)

print("\nLATE DELIVERY PERCENTAGE BY ROUTE")
print(route_late_percentage.sort_values(ascending=False))



#Create project KPI summary

total_orders = len(df)
late_orders = (df["Delivery_Status"] == "Late").sum()
on_time_orders = (df["Delivery_Status"] == "On Time").sum()
early_orders = (df["Delivery_Status"] == "Early").sum()

kpi_summary = pd.DataFrame({
    "Metric": [
        "Total Orders",
        "Late Orders",
        "On-Time Orders",
        "Early Orders",
        "Late Delivery Percentage",
        "Average Delay (Late Orders)",
        "Maximum Delay (Late Orders)"
    ],
    "Value": [
        total_orders,
        late_orders,
        on_time_orders,
        early_orders,
        round(late_orders / total_orders * 100, 2),
        round(df.loc[df["Delivery_Delay_Days"] > 0,
                     "Delivery_Delay_Days"].mean(), 2),
        df.loc[df["Delivery_Delay_Days"] > 0,
               "Delivery_Delay_Days"].max()
    ]
})

print("\nPROJECT KPI SUMMARY")
print(kpi_summary.to_string(index=False))


# ==============================
# DATA VISUALIZATION --->
# ==============================

#Pie chart of delivery status

status_counts = df["Delivery_Status"].value_counts()

plt.figure(figsize=(7, 7))

plt.pie(
    status_counts,
    labels=status_counts.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Delivery Status Distribution")
plt.show()


#Bar chart of late delivery percentage by carrier

plt.figure(figsize=(8, 5))

carrier_late_percentage.sort_values().plot(
    kind="bar",
    title="Late Delivery Percentage by Carrier"
)

plt.xlabel("Carrier")
plt.ylabel("Late Delivery Percentage (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


#Bar chart of late delivery percentage by warehouse

plt.figure(figsize=(8, 5))

warehouse_late_percentage.sort_values().plot(
    kind="bar",
    title="Late Delivery Percentage by Warehouse"
)

plt.xlabel("Warehouse")
plt.ylabel("Late Delivery Percentage (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


#Average delivery delay by route

plt.figure(figsize=(10, 6))

route_delay["mean"].sort_values().plot(
    kind="bar",
    title="Average Delivery Delay by Route"
)

plt.xlabel("Route")
plt.ylabel("Average Delay (Days)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()


# ==============================
# DAY 5 - ADVANCED ANALYSIS
# ==============================

#Late delivery percentage by shipping mode

total_by_shipping = df.groupby("Shipping_Mode").size()

late_by_shipping = (
    df[df["Delivery_Status"] == "Late"]
    .groupby("Shipping_Mode")
    .size()
)

shipping_late_percentage = (
    late_by_shipping / total_by_shipping * 100
).round(2)

print("\nLATE DELIVERY PERCENTAGE BY SHIPPING MODE")
print(shipping_late_percentage.sort_values(ascending=False))




#Late delivery percentage by product type

total_by_product = df.groupby("Product_Type").size()

late_by_product = (
    df[df["Delivery_Status"] == "Late"]
    .groupby("Product_Type")
    .size()
)

product_late_percentage = (
    late_by_product / total_by_product * 100
).round(2)

print("\nLATE DELIVERY PERCENTAGE BY PRODUCT TYPE")
print(product_late_percentage.sort_values(ascending=False))


#Business performance summary

business_summary = df.groupby("Shipping_Mode").agg(
    Total_Orders=("Order_ID", "count"),
    Late_Orders=("Delivery_Status", lambda x: (x == "Late").sum()),
    Average_Delay=("Delivery_Delay_Days", lambda x: x[x > 0].mean())
)

business_summary["Late_Percentage"] = (
    business_summary["Late_Orders"]
    / business_summary["Total_Orders"] * 100
).round(2)

business_summary["Average_Delay"] = (
    business_summary["Average_Delay"].round(2)
)

print("\nBUSINESS PERFORMANCE SUMMARY BY SHIPPING MODE")
print(business_summary)



#Business recommendations

print("\nBUSINESS RECOMMENDATIONS")

highest_rate_mode = business_summary["Late_Percentage"].idxmax()
highest_rate = business_summary["Late_Percentage"].max()

highest_delay_mode = business_summary["Average_Delay"].idxmax()
highest_delay = business_summary["Average_Delay"].max()

print(
    f"1. Investigate {highest_rate_mode} shipping, "
    f"which has the highest late-delivery rate of "
    f"{highest_rate:.2f}%."
)

print(
    f"2. Review delays in {highest_delay_mode} shipping, "
    f"which has the highest average delay of "
    f"{highest_delay:.2f} days among late orders."
)

print(
    "3. Improve product-type data quality by checking "
    "orders categorized as Unknown."
)

print(
    "4. Investigate carrier and warehouse performance "
    "to identify possible causes of delays."
)

