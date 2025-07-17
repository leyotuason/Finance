import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import datetime

# Fixed background image CSS
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

[data-testid="stSidebar"] > div {
    background: rgba(255, 255, 255, 0.05);
}

.main .block-container {
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 10px;
    margin-top: 2rem;
    backdrop-filter: blur(10px);
}

.stMetric {
    background: rgba(255, 255, 255, 0.8);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.stInfo {
    background: rgba(59, 130, 246, 0.1);
    backdrop-filter: blur(5px);
}

.stWarning {
    background: rgba(245, 158, 11, 0.1);
    backdrop-filter: blur(5px);
}

.stSuccess {
    background: rgba(34, 197, 94, 0.1);
    backdrop-filter: blur(5px);
}

/* Form inputs styling */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    color: white;
}

.stTextInput > div > div > input:focus {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    color: white;
}

.stTextArea > div > div > textarea:focus {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.stNumberInput > div > div > input {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    color: white;
}

.stNumberInput > div > div > input:focus {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.stSelectbox > div > div > div {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
}

.stSelectbox > div > div > div > div {
    color: white;
}

/* Button styling */
.stButton > button {
    background: rgba(59, 130, 246, 0.3);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(59, 130, 246, 0.5);
    border-radius: 8px;
    color: white;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: rgba(59, 130, 246, 0.5);
    border-color: rgba(59, 130, 246, 0.7);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.stButton > button:active {
    transform: translateY(0px);
}

/* Form submit button styling */
.stFormSubmitButton > button {
    background: rgba(34, 197, 94, 0.3);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(34, 197, 94, 0.5);
    border-radius: 8px;
    color: white;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}

.stFormSubmitButton > button:hover {
    background: rgba(34, 197, 94, 0.5);
    border-color: rgba(34, 197, 94, 0.7);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.stFormSubmitButton > button:active {
    transform: translateY(0px);
}

/* Form container styling */
.stForm {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
}

/* Labels styling */
.stSelectbox > label,
.stTextInput > label,
.stTextArea > label,
.stNumberInput > label {
    color: white;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

/* Placeholder text styling */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(255, 255, 255, 0.3);
}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

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
            options=["Entry", "Report", "Settings"],
            menu_icon="house-fill",
            icons=["folder-fill", "activity", "gear"]
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
                
        st.write("---")  

        allowance_total = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Allowance"]['Amount'].sum()
        total_expenses = st.session_state.existing_data[st.session_state.existing_data['Type'] == "Expense"]['Amount'].sum()
        remaining_budget = allowance_total - total_expenses

        col = st.columns(1)
        with col[0]:
            st.info('Remaining Balance', icon="💵")
            st.metric(label='Remaining Php', value=f"{remaining_budget:,.2f}")  
        col2 = st.columns(1)
        with col2[0]:
            st.info('  Total Expenses', icon="🛒")
            st.metric(label='Expense Php', value=f"{total_expenses:,.2f}")

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
            st.dataframe(selected_month_expenses, use_column_width=True)
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
