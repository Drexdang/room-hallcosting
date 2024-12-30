import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Function to calculate daily depreciation
def calculate_depreciation(asset_cost, lifespan):
    days_in_year = 365
    return asset_cost / (lifespan * days_in_year) if lifespan > 0 else 0

# Function to calculate total cost for room/hall
def calculate_total_cost(utility_cost, maintenance_cost, staffing_cost, consumable_cost, marketing_cost, daily_depreciation, number_of_days):
    return (utility_cost + maintenance_cost + staffing_cost + consumable_cost + marketing_cost + daily_depreciation * number_of_days)

# Connect to SQLite database
conn = sqlite3.connect('sale_data.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute(''' 
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        day_of_week TEXT,
        customer_name TEXT,
        category TEXT,
        room_or_hall_name TEXT,
        number_of_days INTEGER,
        number_of_people INTEGER,
        selling_rate REAL,
        total_cost REAL,
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

    daily_depreciation = calculate_depreciation(selected_costs["asset_cost"], selected_costs["lifespan"])
    number_of_days = st.number_input("Number of Days", min_value=1, step=1)

    total_cost = calculate_total_cost(
        selected_costs["utility_cost"], selected_costs["maintenance_cost"], selected_costs["staffing_cost"],
        selected_costs["consumable_cost"], selected_costs["marketing_cost"], daily_depreciation, number_of_days
    )
    st.write(f"Total Cost: N{total_cost:.2f}")

    selling_rate = st.number_input("Enter Selling Rate (per day)", min_value=0.0, step=100.0)
    
    if selling_rate > 0:
        total_revenue = selling_rate * number_of_days
        profit_margin = ((total_revenue - total_cost) / total_revenue) * 100
        
        # Debugging: Show calculated profit margin and revenue for verification
        st.write(f"Total Revenue: N{total_revenue:.2f}")
        st.write(f"Profit Margin: {profit_margin:.2f}%")
        
        # Determine if the sale is profitable based on the 30% threshold
        if profit_margin > 70:
            status = "Profitable"
        else:
            status = "Not Profitable"
    else:
        profit_margin, status = 0, "Selling rate must be greater than 0!"
    
    st.write(f"Profit Margin: {profit_margin:.2f}%")
    st.write(f"Status: {status}")

    customer_name = st.text_input("Enter Customer Name")
    number_of_people = st.number_input("Number of People", min_value=1)

    if st.button("Record Sale"):
        if customer_name:
            c.execute('''INSERT INTO sales (date, day_of_week, customer_name, category, room_or_hall_name, number_of_days, number_of_people, selling_rate, total_cost, profit_margin, status) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%A"), customer_name,
                       category, item_name, number_of_days, number_of_people, selling_rate, total_cost, profit_margin, status))
            conn.commit()
            st.success("Sale recorded successfully!")
        else:
            st.error("Customer name is required.")

elif option == "📂 View Database":
    st.header("Sales Database")
    c.execute("SELECT * FROM sales")
    rows = c.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "Date", "Day", "Customer Name", "Category", "Room/Hall", "Days", "People", "Selling Rate", "Total Cost", "Profit Margin", "Status"])
    st.write(df)

elif option == "🔧 Update Costs":
    st.header("Update Costs")
    c.execute("SELECT DISTINCT category FROM costs")
    categories = [row[0] for row in c.fetchall()]
    update_category = st.selectbox("Select Category to Update", categories)

    c.execute("SELECT name FROM costs WHERE category = ?", (update_category,))
    items = [row[0] for row in c.fetchall()]
    selected_item = st.selectbox(f"Select {update_category} to Update", items)

    c.execute("SELECT * FROM costs WHERE name = ?", (selected_item,))
    item_data = c.fetchone()
    
    utility_cost = st.number_input("Utility Cost", value=item_data[2])
    maintenance_cost = st.number_input("Maintenance Cost", value=item_data[3])
    staffing_cost = st.number_input("Staffing Cost", value=item_data[4])
    consumable_cost = st.number_input("Consumable Cost", value=item_data[5])
    marketing_cost = st.number_input("Marketing Cost", value=item_data[6])
    asset_cost = st.number_input("Asset Cost", value=item_data[7])
    lifespan = st.number_input("Lifespan (years)", value=item_data[8])

    if st.button("Update Costs"):
        c.execute('''UPDATE costs SET utility_cost = ?, maintenance_cost = ?, staffing_cost = ?, consumable_cost = ?, marketing_cost = ?, asset_cost = ?, lifespan = ? WHERE name = ?''',
                  (utility_cost, maintenance_cost, staffing_cost, consumable_cost, marketing_cost, asset_cost, lifespan, selected_item))
        conn.commit()
        st.success(f"Updated costs for {selected_item}")

elif option == "✏️ Edit Sales Records":
    st.header("Edit Sales Records")
    record_id = st.number_input("Enter Record ID to Edit", min_value=1)
    if st.button("Load Record"):
        c.execute("SELECT * FROM sales WHERE id = ?", (record_id,))
        record = c.fetchone()
        if record:
            new_name = st.text_input("Customer Name", value=record[3])
            new_selling_rate = st.number_input("Selling Rate", value=record[8])
            if st.button("Update Record"):
                c.execute("UPDATE sales SET customer_name = ?, selling_rate = ? WHERE id = ?", (new_name, new_selling_rate, record_id))
                conn.commit()
                st.success("Record updated successfully!")
        else:
            st.error("Record not found.")

elif option == "🔍 Search Database":
    st.header("Search Sales Records")
    search_date = st.date_input("Select Date")
    search_name = st.text_input("Enter Customer Name")
    if st.button("Search"):
        search_query = "SELECT * FROM sales WHERE date = ? OR customer_name = ?"
        c.execute(search_query, (search_date.strftime("%Y-%m-%d"), search_name))
        search_results = c.fetchall()
        if search_results:
            st.write(pd.DataFrame(search_results, columns=["ID", "Date", "Day", "Customer Name", "Category", "Room/Hall", "Days", "People", "Selling Rate", "Total Cost", "Profit Margin", "Status"]))
        else:
            st.error("No records found.")

# Close database connection
conn.close()