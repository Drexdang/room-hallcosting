import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Function to calculate daily depreciation
def calculate_depreciation(asset_cost, lifespan):
    """Calculates daily depreciation."""
    days_in_year = 365
    return asset_cost / (lifespan * days_in_year) if lifespan > 0 else 0

# Function to calculate total unit cost
def calculate_unit_cost(utility_cost, maintenance_cost, staffing_cost, consumable_cost, marketing_cost, daily_depreciation):
    """Calculates total unit cost per day."""
    return utility_cost + maintenance_cost + staffing_cost + consumable_cost + marketing_cost + daily_depreciation

# Function to calculate total costs, revenue, and profit
def calculate_financials(selling_rate, unit_cost, number_of_days, number_of_people):
    """Calculates total cost, total revenue, and profit margin."""
    total_cost = unit_cost * number_of_days * number_of_people
    total_revenue = selling_rate * number_of_days * number_of_people
    profit_margin = total_revenue - total_cost
    return total_cost, total_revenue, profit_margin

# Connect to SQLite database
conn = sqlite3.connect('sale_dat.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute(''' 
    CREATE TABLE IF NOT EXISTS sale (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        day_of_week TEXT,
        customer_name TEXT,
        category TEXT,
        room_or_hall_name TEXT,
        number_of_days INTEGER,
        number_of_people INTEGER,
        selling_rate REAL,
        total_unit_cost REAL,
        total_cost REAL,
        total_revenue REAL,
        profit_margin REAL,
        status TEXT
    )
''')

c.execute(''' 
    CREATE TABLE IF NOT EXISTS costs (
        name TEXT PRIMARY KEY,
        category TEXT,
        utility_cost REAL,
        maintenance_cost REAL,
        staffing_cost REAL,
        consumable_cost REAL,
        marketing_cost REAL,
        asset_cost REAL,
        lifespan REAL
    )
''')

# Hall-specific costs (default values)
hall_costs = {
    "ACROBAT HALL": {"utility_cost": 7000.0, "maintenance_cost": 4000.0, "staffing_cost": 10000.0, "consumable_cost": 1500.0, "marketing_cost": 2500.0, "asset_cost": 15000.0, "lifespan": 10},
    "UNITY HALL": {"utility_cost": 6000.0, "maintenance_cost": 3500.0, "staffing_cost": 9000.0, "consumable_cost": 1400.0, "marketing_cost": 2300.0, "asset_cost": 12000.0, "lifespan": 8},
    "AZIKIWE HALL": {"utility_cost": 6500.0, "maintenance_cost": 3700.0, "staffing_cost": 9500.0, "consumable_cost": 1600.0, "marketing_cost": 2200.0, "asset_cost": 13000.0, "lifespan": 9},
    "EMERALD HALL": {"utility_cost": 7200.0, "maintenance_cost": 4200.0, "staffing_cost": 11000.0, "consumable_cost": 1800.0, "marketing_cost": 2800.0, "asset_cost": 16000.0, "lifespan": 11},
    "DIAMOND HALL": {"utility_cost": 7000.0, "maintenance_cost": 4000.0, "staffing_cost": 10000.0, "consumable_cost": 1500.0, "marketing_cost": 2500.0, "asset_cost": 15000.0, "lifespan": 10},
    "GOLDEN HALL": {"utility_cost": 6800.0, "maintenance_cost": 3800.0, "staffing_cost": 9500.0, "consumable_cost": 1700.0, "marketing_cost": 2400.0, "asset_cost": 14000.0, "lifespan": 9},
    "LIBERTY HALL": {"utility_cost": 7100.0, "maintenance_cost": 3900.0, "staffing_cost": 10000.0, "consumable_cost": 1600.0, "marketing_cost": 2600.0, "asset_cost": 14500.0, "lifespan": 10},
    "CRYSTAL HALL": {"utility_cost": 7500.0, "maintenance_cost": 4300.0, "staffing_cost": 10500.0, "consumable_cost": 1900.0, "marketing_cost": 2700.0, "asset_cost": 15500.0, "lifespan": 10},
    "PEARL HALL": {"utility_cost": 6400.0, "maintenance_cost": 3600.0, "staffing_cost": 9200.0, "consumable_cost": 1400.0, "marketing_cost": 2200.0, "asset_cost": 12500.0, "lifespan": 8},
    "GOWON HALL": {"utility_cost": 6900.0, "maintenance_cost": 3700.0, "staffing_cost": 9800.0, "consumable_cost": 1550.0, "marketing_cost": 2350.0, "asset_cost": 13500.0, "lifespan": 9},
    "PATRICK HALL": {"utility_cost": 7100.0, "maintenance_cost": 3900.0, "staffing_cost": 10000.0, "consumable_cost": 1650.0, "marketing_cost": 2400.0, "asset_cost": 14500.0, "lifespan": 10},
    "CECILIA HALL": {"utility_cost": 7300.0, "maintenance_cost": 4000.0, "staffing_cost": 10200.0, "consumable_cost": 1700.0, "marketing_cost": 2500.0, "asset_cost": 15000.0, "lifespan": 10}
}

# Room-specific costs (default values)
room_costs = {
    "Deluxe": {"utility_cost": 3000.0, "maintenance_cost": 1500.0, "staffing_cost": 4000.0, "consumable_cost": 500.0, "marketing_cost": 800.0, "asset_cost": 5000.0, "lifespan": 6},
    "Executive": {"utility_cost": 3500.0, "maintenance_cost": 1700.0, "staffing_cost": 4500.0, "consumable_cost": 600.0, "marketing_cost": 900.0, "asset_cost": 5500.0, "lifespan": 7},
    "Royal": {"utility_cost": 4000.0, "maintenance_cost": 1800.0, "staffing_cost": 5000.0, "consumable_cost": 650.0, "marketing_cost": 1000.0, "asset_cost": 6000.0, "lifespan": 8},
    "Royal Single": {"utility_cost": 3800.0, "maintenance_cost": 1700.0, "staffing_cost": 4600.0, "consumable_cost": 600.0, "marketing_cost": 950.0, "asset_cost": 5600.0, "lifespan": 7},
    "Ambassadorial Suite": {"utility_cost": 5000.0, "maintenance_cost": 2500.0, "staffing_cost": 6000.0, "consumable_cost": 800.0, "marketing_cost": 1200.0, "asset_cost": 8000.0, "lifespan": 9},
    "Royal Double": {"utility_cost": 4200.0, "maintenance_cost": 1900.0, "staffing_cost": 5300.0, "consumable_cost": 700.0, "marketing_cost": 1100.0, "asset_cost": 6500.0, "lifespan": 8},
    "Presidential Suite": {"utility_cost": 5500.0, "maintenance_cost": 2700.0, "staffing_cost": 6500.0, "consumable_cost": 900.0, "marketing_cost": 1300.0, "asset_cost": 9000.0, "lifespan": 10}
}

# Insert default costs into the database if they don't exist
for category, costs in [("Hall", hall_costs), ("Room", room_costs)]:
    for name, values in costs.items():
        c.execute('''INSERT OR IGNORE INTO costs (name, category, utility_cost, maintenance_cost, staffing_cost, consumable_cost, marketing_cost, asset_cost, lifespan) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (name, category, values["utility_cost"], values["maintenance_cost"], values["staffing_cost"],
                   values["consumable_cost"], values["marketing_cost"], values["asset_cost"], values["lifespan"]))

conn.commit()

# Streamlit App Layout
st.set_page_config(page_title="Profitability Management", page_icon="💰")
st.title("Room and Hall Profitability Manager")

# Sidebar navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio(
    "Choose a section",
    [
        "📊 Profitability Calculator",
        "📂 View Database",
        "🔧 Update Costs",
        "✏️ Edit Sales Records",
        "🔍 Search Database"
    ]
)

if option == "📊 Profitability Calculator":
    st.header("Calculate Profitability")

    category = st.selectbox("Select Category", ["Hall", "Room"])

    # Display Hall or Room names based on the category
    if category == "Hall":
        item_name = st.selectbox("Select Hall", list(hall_costs.keys()))
        selected_costs = hall_costs[item_name]
    else:
        item_name = st.selectbox("Select Room", list(room_costs.keys()))
        selected_costs = room_costs[item_name]

    # Add the Customer Name input field
    customer_name = st.text_input("Enter Customer Name")

    # Calculate depreciation, unit cost, and financials
    daily_depreciation = calculate_depreciation(selected_costs["asset_cost"], selected_costs["lifespan"])
    unit_cost = calculate_unit_cost(
        selected_costs["utility_cost"], selected_costs["maintenance_cost"], selected_costs["staffing_cost"],
        selected_costs["consumable_cost"], selected_costs["marketing_cost"], daily_depreciation
    )

    number_of_days = st.number_input("Number of Days", min_value=1, step=1)
    number_of_people = st.number_input("Number of People", min_value=1, step=1)
    selling_rate = st.number_input("Enter Selling Rate (per day)", min_value=0.0, step=100.0)

    if selling_rate > 0:
        total_cost, total_revenue, profit_margin = calculate_financials(selling_rate, unit_cost, number_of_days, number_of_people)

        st.write(f"**Unit Cost per Day:** N{unit_cost:.2f}")
        st.write(f"**Total Cost:** N{total_cost:.2f}")
        st.write(f"**Total Revenue:** N{total_revenue:.2f}")
        st.write(f"**Profit Margin:** N{profit_margin:.2f}")

        # Status check for profitability
        status = "Profitable" if profit_margin / total_revenue > 0.7 else "Not Profitable"
        st.write(f"**Status:** {status}")

        # Save to the database
        if st.button("Save Record"):
            today = datetime.now().strftime("%Y-%m-%d")
            day_of_week = datetime.now().strftime("%A")
            c.execute('''INSERT INTO sale (date, day_of_week, customer_name, category, room_or_hall_name, 
                          number_of_days, number_of_people, selling_rate, total_unit_cost, total_cost, total_revenue, 
                          profit_margin, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (today, day_of_week, customer_name, category, item_name, number_of_days, number_of_people, 
                       selling_rate, unit_cost, total_cost, total_revenue, profit_margin, status))
            conn.commit()
            st.success("Record saved successfully!")

elif option == "📂 View Database":
    st.header("Database Records")
    sales_df = pd.read_sql_query("SELECT * FROM sale", conn)
    st.dataframe(sales_df)

elif option == "🔧 Update Costs":
    st.header("Update Costs")
    costs_df = pd.read_sql_query("SELECT * FROM costs", conn)
    st.dataframe(costs_df)
    
    with st.form("update_costs_form"):
        name = st.selectbox("Select Item to Update", costs_df["name"].tolist())
        category = st.text_input("Category", value=costs_df[costs_df["name"] == name]["category"].values[0])
        utility_cost = st.number_input("Utility Cost", min_value=0.0, value=float(costs_df[costs_df["name"] == name]["utility_cost"].values[0]))
        maintenance_cost = st.number_input("Maintenance Cost", min_value=0.0, value=float(costs_df[costs_df["name"] == name]["maintenance_cost"].values[0]))
        staffing_cost = st.number_input("Staffing Cost", min_value=0.0, value=float(costs_df[costs_df["name"] == name]["staffing_cost"].values[0]))
        consumable_cost = st.number_input("Consumable Cost", min_value=0.0, value=float(costs_df[costs_df["name"] == name]["consumable_cost"].values[0]))
        marketing_cost = st.number_input("Marketing Cost", min_value=0.0, value=float(costs_df[costs_df["name"] == name]["marketing_cost"].values[0]))
        asset_cost = st.number_input("Asset Cost", min_value=0.0, value=float(costs_df[costs_df["name"] == name]["asset_cost"].values[0]))
        lifespan = st.number_input("Lifespan (in years)", min_value=1, value=int(costs_df[costs_df["name"] == name]["lifespan"].values[0]))

        submitted = st.form_submit_button("Update")
        if submitted:
            c.execute('''UPDATE costs SET category=?, utility_cost=?, maintenance_cost=?, staffing_cost=?, consumable_cost=?, marketing_cost=?, asset_cost=?, lifespan=? WHERE name=?''', 
                      (category, utility_cost, maintenance_cost, staffing_cost, consumable_cost, marketing_cost, asset_cost, lifespan, name))
            conn.commit()
            st.success("Costs updated successfully!")

elif option == "✏️ Edit Sales Records":
    st.header("Edit Sales Records")

    # Begin the form
    with st.form(key='edit_sales_form'):
        # Fetch all records from the sales table
        sale_dat = pd.read_sql_query("SELECT * FROM sale", conn)
        
        # Select a sales record ID
        sale_id = st.selectbox("Select Record to Edit", sale_dat['id'].tolist())

        # Fetch the record based on the selected sales ID
        record = sale_dat[sale_dat['id'] == sale_id]

        if not record.empty:
            # Display the information for editing
            new_customer_name = st.text_input("Customer Name", value=record['customer_name'].values[0])
            new_category = st.selectbox("Category", ["Hall", "Room"], index=["Hall", "Room"].index(record['category'].values[0]))
            new_room_hall_name = st.selectbox("Room/Hall Name", sale_dat['room_or_hall_name'].unique().tolist(), index=list(sale_dat['room_or_hall_name'].unique()).index(record['room_or_hall_name'].values[0]))
            new_selling_rate = st.number_input("Selling Rate", value=record['selling_rate'].values[0], min_value=0.0)

            # Submit the form to save changes
            submit_edit = st.form_submit_button("Save Changes")
            if submit_edit:
                # Update the record in the database
                c.execute('''UPDATE sale SET customer_name=?, category=?, room_or_hall_name=?, selling_rate=? WHERE id=?''', 
                          (new_customer_name, new_category, new_room_hall_name, new_selling_rate, sale_id))
                conn.commit()
                st.success("Sales record updated successfully!")
        else:
            st.error("No record found for the selected ID.")

elif option == "🔍 Search Database":
    st.header("Search Database")

    # Search by customer name or room/hall name
    search_query = st.text_input("Enter your search query")
    if search_query:
        search_result = pd.read_sql_query(f"SELECT * FROM sale WHERE customer_name LIKE '%{search_query}%' OR room_or_hall_name LIKE '%{search_query}%'", conn)
        st.dataframe(search_result)

    # Search by date range
    st.subheader("Search by Date Range")
    start_date = st.date_input("Start Date", datetime(2024, 1, 1))  # Set default start date
    end_date = st.date_input("End Date", datetime.today())  # Set default end date as today

    if start_date and end_date:
        # Ensure that end date is not before start date
        if end_date >= start_date:
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            date_range_query = f"SELECT * FROM sale WHERE date BETWEEN '{start_date_str}' AND '{end_date_str}'"
            date_search_result = pd.read_sql_query(date_range_query, conn)
            if not date_search_result.empty:
                st.dataframe(date_search_result)
            else:
                st.warning("No records found for the selected date range.")
        else:
            st.error("End date must be greater than or equal to the start date.")
    else:
        st.warning("Please select both start and end dates.")