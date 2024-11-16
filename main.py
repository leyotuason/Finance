import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import datetime

# Create a connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialize session state for existing data if it doesn't exist
if 'existing_data' not in st.session_state:
    st.session_state.existing_data = conn.read(worksheet="Sheet1", usecols=list(range(5)), ttl=6)
    st.session_state.existing_data = st.session_state.existing_data.dropna(how="all")

# Convert 'Date' column to datetime if not already in datetime format
if 'Date' in st.session_state.existing_data.columns:
    st.session_state.existing_data['Date'] = pd.to_datetime(st.session_state.existing_data['Date'], errors='coerce')

if 'allowance' not in st.session_state:
    st.session_state.allowance = 0.0  # Initialize allowance

CATEGORY = ["Rent", "Utilities", "Load", "Food", "Transportation", "Supplies", "Other", "Cash", "E-money"]
TYPE = ["Expense", "Allowance"]

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "" and password == "":  
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

def dashboard():
    with st.sidebar:
        selected = option_menu(
            menu_title="Finance Tracker",
            options=["Entry", "Budget", "Report", "Settings"],
            menu_icon="house-fill",
            icons=["folder-fill", "list", "activity", "gear"]
        )
    
    if selected == "Entry":
        st.title("Finance Tracker")
        st.markdown("Daily entry")
        with st.form(key="expense_entry"):

            current_date = pd.Timestamp.today()
            entry_date = current_date
            entry_type = st.selectbox("Type", options=TYPE)
            category = st.selectbox("Category", options=CATEGORY, index=None)
            amount = st.number_input(label="Amount")
            note = st.text_area(label="Notes", placeholder="Optional")

            submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not category or not amount or not entry_type:
                st.warning("Please ensure all mandatory fields are filled")
                st.stop()
            else:
                entry_data = pd.DataFrame(
                    [
                        {
                            "Date":entry_date,
                            "Type": entry_type,
                            "Category": category,
                            "Amount": amount,
                            "Note": note,
                        }
                    ]
                )

                # Update existing data and Google Sheets
                st.session_state.existing_data = pd.concat([st.session_state.existing_data, entry_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=st.session_state.existing_data)

                st.success("Successfully submitted!")
        st.markdown("Daily expense list")
        latest_entries = st.session_state.existing_data.tail(3)  
        st.dataframe(latest_entries, width=600)

    if selected == "Budget":
        st.title("Remaining Budget")

        allowance_total = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Allowance"]['Amount'].sum()
        expenses = st.session_state.existing_data[st.session_state.existing_data['Type'] == 'Expense']

        rent_expenses = expenses[expenses['Category'] == 'Rent']['Amount'].sum()
        utilities_expenses = expenses[expenses['Category'] == 'Utilities']['Amount'].sum()
        food_expenses = expenses[expenses['Category'] == 'Food']['Amount'].sum()
        supplies_expenses = expenses[expenses['Category'] == 'Supplies']['Amount'].sum()
        load_expenses = expenses[expenses['Category'] == 'Load']['Amount'].sum()
        transportation_expenses = expenses[expenses['Category'] == 'Transportation']['Amount'].sum()
        other_expenses = expenses[expenses['Category'] == 'Other']['Amount'].sum()

        remaining_rent_budget = st.session_state.rent_budget - rent_expenses
        remaining_utilities_budget = st.session_state.utilities_budget - utilities_expenses
        remaining_food_budget = st.session_state.food_budget - food_expenses
        remaining_transportation_budget = st.session_state.transportation_budget - transportation_expenses
        remaining_supplies_budget = st.session_state.supplies_budget - supplies_expenses
        remaining_load_budget = st.session_state.load_budget - load_expenses
        remaining_other_budget = st.session_state.other_budget - other_expenses
                
                
        allowance_total = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Allowance"]['Amount'].sum()
        total_expenses = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Expense"]['Amount'].sum()
        remaining_budget = allowance_total - total_expenses

        col = st.columns(1)
        with col[0]:
            st.info('Remaining Balance', icon="💰")
            st.metric(label='Remaining Php', value=f"{remaining_budget:,.2f}")       

        st.write("---") 

        st.title("Budget VS Expense")

        total1, total2, total3 = st.columns(3, gap='small')

        with total1:
            st.info(' Rent Budget', icon="🏠")
            st.metric(label="Expenses Php", value=f"{rent_expenses:,.2f}")
            st.metric(label="Remaining Php", value=f"{remaining_rent_budget:,.2f}")


        with total2:
            st.info(' Utilities Budget', icon="💡")
            st.metric(label="Exenses Php", value=f"{utilities_expenses:,.2f}")
            st.metric(label="Remaining Php", value=f"{remaining_utilities_budget:,.2f}")

        with total3:
            st.info(' Food Budget', icon="🍽️")
            st.metric(label="Expenses Php", value=f"{food_expenses:,.2f}")
            st.metric(label="Remaining Php", value=f"{remaining_food_budget:,.2f}")

        total6, total5, total4 = st.columns(3, gap='small')

        with total4:
            st.info('Transportation Budget', icon="🚗")
            st.metric(label="Expenses Php", value=f"{transportation_expenses:,.2f}")
            st.metric(label='Remaining Php', value=f"{remaining_transportation_budget:,.2f}")

        with total5:
            st.info('Supplies Budget', icon="📝")
            st.metric(label="Expenses Php", value=f"{supplies_expenses:,.2f}")
            st.metric(label='Remaining Php', value=f"{remaining_supplies_budget:,.2f}")

        with total6:
            st.info('Load Budget', icon="🌐")
            st.metric(label="Expenses Php", value=f"{load_expenses:,.2f}")
            st.metric(label='Remaining Php', value=f"{remaining_load_budget:,.2f}")

        total7, none1, none2 = st.columns(3, gap='small')

        with total7:
            st.info('Other Budget', icon="🔗")
            st.metric(label="Expenses Php", value=f"{other_expenses:,.2f}")
            st.metric(label='Remaining Php', value=f"{remaining_other_budget:,.2f}")   

    if selected == "Report":
        st.title("Financial Report")

        expenses = st.session_state.existing_data[st.session_state.existing_data['Type'] == 'Expense']

        current_date = pd.Timestamp.now()
        current_day = current_date.day
        current_month = current_date.month
        current_year = current_date.year

        daily_expenses = expenses[(expenses['Date'].dt.day == current_day) & 
                                (expenses['Date'].dt.month == current_month) & 
                                (expenses['Date'].dt.year == current_year)]

        if not daily_expenses.empty:

            total_daily_expense = daily_expenses['Amount'].sum()
            daily_expenses_grouped = daily_expenses.groupby('Category')['Amount'].sum().reset_index()
            
            fig_daily = px.pie(
                daily_expenses_grouped,
                values='Amount',
                names='Category',
                title='Expenses for Today',
                template='plotly',
                hole=0.3  
            )
            
            # Update layout for better readability
            fig_daily.update_traces(
                textposition='outside',
                textinfo='label+percent+value'
            )
            fig_daily.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_daily, use_container_width=True)

            
            
            st.info(' Total Expenses Today', icon="🛒")
            st.metric(
                label="Expenses Php",
                value=f"{total_daily_expense:,.2f}")
        else:
            st.warning("No expense data available for today.")

        st.write('---')

        start_of_week = current_date - pd.Timedelta(days=current_date.dayofweek)
        end_of_week = start_of_week + pd.Timedelta(days=6)
    
        # Filter for expenses in the current week
        weekly_expenses = expenses[
            (expenses['Date'].dt.date >= start_of_week.date()) & 
            (expenses['Date'].dt.date <= end_of_week.date())
        ]
    
        if not weekly_expenses.empty:
            # Calculate total weekly expenses
            total_weekly_expense = weekly_expenses['Amount'].sum()

            daily_breakdown = weekly_expenses.groupby(weekly_expenses['Date'].dt.strftime('%A'))['Amount'].sum().reindex([
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                ])
                
                # Convert to DataFrame for line plot
            daily_breakdown_df = pd.DataFrame({
                    'Day': daily_breakdown.index,
                    'Amount': daily_breakdown.values
                })
            
            
            fig_weekly = px.bar(
                daily_breakdown_df,
                x='Day',
                y='Amount',
                labels={'Day': 'Day of Week', 'Amount': 'Total Amount'},
                title='Expenses for the Week',
                template='plotly'
            )
   
            fig_weekly.update_layout(xaxis_title='Day', yaxis_title='Total Amount', plot_bgcolor='rgba(0,0,0,0)')      
            st.plotly_chart(fig_weekly, use_container_width=True)

            # Weekly Summary Table
            st.write("Weekly Summary by Category")
            weekly_summary = weekly_expenses.groupby('Category').agg({
                'Amount': ['sum', 'count']
            }).round(2)
            
            weekly_summary.columns = ['Total Amount', 'Number of Transactions']
            weekly_summary = weekly_summary.reset_index()
            weekly_summary['Total Amount'] = weekly_summary['Total Amount'].apply(lambda x: f"{x:,.2f}")
            
            st.dataframe(weekly_summary, use_container_width=True)

            st.info(' Total Weekly Expenses', icon="🛒")
            st.metric(
                label="Expenses Php",
                value=f"{total_weekly_expense:,.2f}",
                help=f"Total expenses from {start_of_week.strftime('%B %d')} to {end_of_week.strftime('%B %d')}"
                )
        else:
            st.warning("No expense data available for this week.")



        st.write('---')
    
        # Filter for expenses in the current month
        monthly_expenses = expenses[(expenses['Date'].dt.month == current_month) & (expenses['Date'].dt.year == current_year)]

        if not monthly_expenses.empty:

            total_monthly_expenses = monthly_expenses['Amount'].sum()
            # Group by date and sum the amounts
            monthly_expenses_grouped = monthly_expenses.groupby(monthly_expenses['Date'].dt.date)['Amount'].sum().reset_index()

            # Plotting the monthly expenses as a line graph using Plotly
            fig_monthly = px.line(
                monthly_expenses_grouped,
                x='Date',
                y='Amount',
                labels={'Date': '', 'Amount': ''},
                title='Expenses for the Month',
                template='plotly'
            )
            fig_monthly.update_layout(xaxis_title='Date', yaxis_title='Total Amount', plot_bgcolor='rgba(0,0,0,0)')  # Transparent background
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            st.info('Total Monthly Expenses', icon="🛒")
            st.metric(label='Expense Php', value=f"{total_monthly_expenses:,.2f}")



        else:
            st.warning("No expense data available for this month.")

        st.write("---")  


        allowance_total = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Allowance"]['Amount'].sum()
        
        # Calculate total expenses
        total_expenses = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Expense"]['Amount'].sum()
        remaining_budget = allowance_total - total_expenses

        col3 = st.columns(1)
        with col3[0]:
            st.info('Remaining Budget', icon="💰")
            st.metric(label='Expense Php', value=f"{remaining_budget:,.2f}")       


        col1, col2 = st.columns(2, gap='small')
        
        with col1:
            st.info('  Total Allowance', icon="🪙")
            st.metric(label='Allowance Php', value=f"{allowance_total:,.2f}")

        with col2: 
            st.info('  Total Expenses', icon="🛒")
            st.metric(label='Expense Php', value=f"{total_expenses:,.2f}")


    if selected == "Settings":
        st.subheader("Expense List")
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
                    'August', 'September', 'October', 'November', 'December']
        selected_month = st.selectbox("Select a month", months)

        # Get the month index (0 for January, 11 for December)
        month_index = months.index(selected_month) + 1  # +1 to match with 1-12 month range

        # Filter data for the selected month
        selected_month_expenses = st.session_state.existing_data[
            (st.session_state.existing_data['Date'].dt.month == month_index)
        ]

        # Display filtered expenses
        if not selected_month_expenses.empty:
            st.dataframe(selected_month_expenses, width=600)
        else:
            st.warning(f"No expenses found for {selected_month}.")

        
        if not st.session_state.existing_data.empty:
            # Select an entry to delete
            delete_index = st.selectbox("Select entry to delete", st.session_state.existing_data.index)
            delete_button = st.button("Delete Entry")

            if delete_button:
                # Delete the selected entry
                st.session_state.existing_data = st.session_state.existing_data.drop(delete_index).reset_index(drop=True)

                # Update Google Sheets with the modified DataFrame
                conn.update(worksheet="Sheet1", data=st.session_state.existing_data)

                st.success("Entry deleted successfully!")
        else:
            st.warning("No entries available to delete.")




        st.write("---") 




        st.subheader("Budget Allocation")    

        if 'rent_budget' not in st.session_state:
            st.session_state.rent_budget = 0
        
        rent_budget = st.number_input(
            label="Budget for Rent", 
            value=float(st.session_state.rent_budget), 
            min_value=0.0, 
            step=100.0
        )


        if 'utilities_budget' not in st.session_state:
            st.session_state.utilities_budget = 0
        utilities_budget = st.number_input(
            label="Budget for Utilities", 
            value=float(st.session_state.utilities_budget),  
            min_value=0.0, 
            step=100.0
        )


        if 'food_budget' not in st.session_state:
            st.session_state.food_budget = 0
        food_budget = st.number_input(
            label="Budget for Food", 
            value=float(st.session_state.food_budget),  
            min_value=0.0, 
            step=100.0
        )


        if 'supplies_budget' not in st.session_state:
            st.session_state.supplies_budget = 0
        supplies_budget = st.number_input(
            label="Budget for Supplies", 
            value=float(st.session_state.supplies_budget),  
            min_value=0.0, 
            step=100.0
        )


        if 'load_budget' not in st.session_state:
            st.session_state.load_budget = 0
        load_budget = st.number_input(
            label="Budget for Load", 
            value=float(st.session_state.load_budget),  
            min_value=0.0, 
            step=100.0
        )


        if 'transportation_budget' not in st.session_state:
            st.session_state.transportation_budget = 0
        transportation_budget = st.number_input(
            label="Budget for Transportation", 
            value=float(st.session_state.transportation_budget),  
            min_value=0.0, 
            step=100.0
        )


        if 'other_budget' not in st.session_state:
            st.session_state.other_budget = 0
        other_budget = st.number_input(
            label="Budget for Other", 
            value=float(st.session_state.other_budget),  
            min_value=0.0, 
            step=100.0
        )

        if st.button("Save budget allocation"):
            st.session_state.rent_budget = rent_budget
            st.session_state.utilities_budget = utilities_budget
            st.session_state.food_budget = food_budget
            st.session_state.transportation_budget = transportation_budget
            st.session_state.supplies_budget = supplies_budget
            st.session_state.load_budget = load_budget
            st.session_state.other_budget = other_budget

            st.success("Budget allocations saved successfully!")


# Initialize session state for logged-in status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Main app logic
def main():
    if st.session_state.logged_in:
        dashboard()
    else:
        login()

if __name__ == "__main__":
    main()
