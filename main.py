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
    background: rgba(255, 255, 255, 0.5);
    padding: 2rem;
    border-radius: 10px;
    margin-top: 2rem;
    backdrop-filter: blur(10px);
}

.stMetric {
    background: rgba(255, 255, 255, 0.1);
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
    width: 100% !important;
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
    color: rgba(255, 255, 255, 0.1);
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

def dashboard():
    with st.sidebar:
        selected = option_menu(
            menu_title="Finance Tracker",
            options=["Entry", "Report", "Data"],
            menu_icon="house-fill",
            icons=["folder-fill", "activity", "list"]
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

        # Calculate start and end of current week (Monday to Sunday)
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

            # Group by day of week and sum amounts
            daily_breakdown = weekly_expenses.groupby(weekly_expenses['Date'].dt.strftime('%A'))['Amount'].sum()
            
            # Reindex to ensure all days are present with 0 if no data
            all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_breakdown = daily_breakdown.reindex(all_days, fill_value=0)
                
            # Convert to DataFrame for bar plot
            daily_breakdown_df = pd.DataFrame({
                'Day': daily_breakdown.index,
                'Amount': daily_breakdown.values
            })
            
            # Create bar chart
            fig_weekly = px.bar(
                daily_breakdown_df,
                x='Day',
                y='Amount',
                labels={'Day': 'Day of Week', 'Amount': 'Total Amount (Php)'},
                title='Daily Expenses for This Week',
                template='plotly',
                color='Amount',
                color_continuous_scale='viridis'
            )
            
            # Update layout for better appearance
            fig_weekly.update_layout(
                xaxis_title='Day of the Week',
                yaxis_title='Total Amount (Php)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis={'categoryorder': 'array', 'categoryarray': all_days}
            )
            
            # Add value labels on top of bars
            fig_weekly.update_traces(
                texttemplate='₱%{y:,.0f}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_weekly, use_container_width=True)

            # Weekly Summary Table
            st.write("Weekly Summary by Category")
            weekly_summary = weekly_expenses.groupby('Category').agg({
                'Amount': ['sum', 'count']
            }).round(2)
            
            weekly_summary.columns = ['Total Amount', 'Number of Transactions']
            weekly_summary = weekly_summary.reset_index()
            weekly_summary['Total Amount'] = weekly_summary['Total Amount'].apply(lambda x: f"₱{x:,.2f}")
            
            st.dataframe(weekly_summary, use_container_width=True)

            st.info(' Total Weekly Expenses', icon="🛒")
            st.metric(
                label="Expenses Php",
                value=f"{total_weekly_expense:,.2f}",
                help=f"Total expenses from {start_of_week.strftime('%d/%m/%Y')} to {end_of_week.strftime('%d/%m/%Y')}"
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
            
            # Format the dates to dd/mm/yyyy for display
            monthly_expenses_grouped['Date_formatted'] = monthly_expenses_grouped['Date'].apply(lambda x: x.strftime('%d/%m/%Y'))

            # Plotting the monthly expenses as a line graph using Plotly
            fig_monthly = px.line(
                monthly_expenses_grouped,
                x='Date_formatted',
                y='Amount',
                labels={'Date_formatted': 'Date', 'Amount': 'Amount'},
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
            st.metric(label='Remaining Php', value=f"{remaining_budget:,.2f}")       

        col1, col2 = st.columns(2, gap='small')
        
        with col1:
            st.info('  Total Allowance', icon="🪙")
            st.metric(label='Allowance Php', value=f"{allowance_total:,.2f}")

        with col2: 
            st.info('  Total Expenses', icon="🛒")
            st.metric(label='Expense Php', value=f"{total_expenses:,.2f}")

    if selected == "Data":
        st.title("Data Management")
        
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Filtered Analysis", "📅 Monthly View", "👁️ View All", "🗑️ Delete Entry"])
        
        with tab1:
            st.subheader("Expense Analysis with Filters")
            
            # Create filter columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Date range filter
                st.write("**Date Range Filter**")
                date_filter_type = st.radio(
                    "Select date filter type:",
                    ["All Time", "Date Range", "Specific Month", "Specific Year"],
                    horizontal=True
                )
                
                start_date = None
                end_date = None
                filter_month = None
                filter_year = None
                
                if date_filter_type == "Date Range":
                    col_start, col_end = st.columns(2)
                    with col_start:
                        start_date = st.date_input("Start Date")
                    with col_end:
                        end_date = st.date_input("End Date")
                elif date_filter_type == "Specific Month":
                    col_month, col_year = st.columns(2)
                    with col_month:
                        filter_month = st.selectbox("Month", range(1, 13), format_func=lambda x: datetime.date(2000, x, 1).strftime('%B'))
                    with col_year:
                        filter_year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.datetime.now().year)
                elif date_filter_type == "Specific Year":
                    filter_year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.datetime.now().year)
            
            with col2:
                # Category and Type filters
                st.write("**Category & Type Filters**")
                
                # Category filter
                available_categories = st.session_state.existing_data['Category'].unique().tolist() if not st.session_state.existing_data.empty else CATEGORY
                selected_categories = st.multiselect("Select Categories", available_categories, default=available_categories)
                
                # Type filter
                selected_types = st.multiselect("Select Types", TYPE, default=TYPE)
                
                # Amount range filter
                st.write("**Amount Range Filter**")
                if not st.session_state.existing_data.empty:
                    min_amount = float(st.session_state.existing_data['Amount'].min())
                    max_amount = float(st.session_state.existing_data['Amount'].max())
                    amount_range = st.slider("Amount Range", min_value=min_amount, max_value=max_amount, value=(min_amount, max_amount))
                else:
                    amount_range = (0.0, 1000.0)
            
            # Apply filters button
            if st.button("Apply Filters", type="primary"):
                if not st.session_state.existing_data.empty:
                    filtered_data = st.session_state.existing_data.copy()
                    
                    # Apply date filters
                    if date_filter_type == "Date Range" and start_date and end_date:
                        filtered_data = filtered_data[
                            (filtered_data['Date'].dt.date >= start_date) & 
                            (filtered_data['Date'].dt.date <= end_date)
                        ]
                    elif date_filter_type == "Specific Month" and filter_month and filter_year:
                        filtered_data = filtered_data[
                            (filtered_data['Date'].dt.month == filter_month) & 
                            (filtered_data['Date'].dt.year == filter_year)
                        ]
                    elif date_filter_type == "Specific Year" and filter_year:
                        filtered_data = filtered_data[filtered_data['Date'].dt.year == filter_year]
                    
                    # Apply category filter
                    if selected_categories:
                        filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]
                    
                    # Apply type filter
                    if selected_types:
                        filtered_data = filtered_data[filtered_data['Type'].isin(selected_types)]
                    
                    # Apply amount range filter
                    filtered_data = filtered_data[
                        (filtered_data['Amount'] >= amount_range[0]) & 
                        (filtered_data['Amount'] <= amount_range[1])
                    ]
                    
                    if not filtered_data.empty:
                        st.write("---")
                        
                        # Summary metrics
                        total_filtered = filtered_data['Amount'].sum()
                        count_filtered = len(filtered_data)
                        avg_filtered = filtered_data['Amount'].mean()
                        
                        # Display summary metrics
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.info("Total Amount", icon="💰")
                            st.metric("Amount (Php)", f"{total_filtered:,.2f}")
                        
                        with metric_col2:
                            st.info("Transaction Count", icon="📊")
                            st.metric("Transactions", f"{count_filtered}")
                        
                        with metric_col3:
                            st.info("Average Amount", icon="📈")
                            st.metric("Average (Php)", f"{avg_filtered:,.2f}")
                        
                        st.write("---")
                        
                        # Category breakdown for filtered data
                        if len(filtered_data['Category'].unique()) > 1:
                            st.write("**Category Breakdown**")
                            category_summary = filtered_data.groupby('Category').agg({
                                'Amount': ['sum', 'count', 'mean']
                            }).round(2)
                            
                            category_summary.columns = ['Total Amount', 'Count', 'Average']
                            category_summary = category_summary.reset_index()
                            category_summary['Total Amount'] = category_summary['Total Amount'].apply(lambda x: f"₱{x:,.2f}")
                            category_summary['Average'] = category_summary['Average'].apply(lambda x: f"₱{x:,.2f}")
                            
                            st.dataframe(category_summary, use_container_width=True)
                            
                            # Category pie chart
                            category_chart_data = filtered_data.groupby('Category')['Amount'].sum().reset_index()
                            fig_category = px.pie(
                                category_chart_data,
                                values='Amount',
                                names='Category',
                                title='Filtered Expenses by Category',
                                template='plotly'
                            )
                            st.plotly_chart(fig_category, use_container_width=True)
                        
                        st.write("---")
                        
                        # Display filtered data
                        st.write("**Filtered Transaction Details**")
                        display_filtered = filtered_data.copy()
                        display_filtered['Date'] = display_filtered['Date'].dt.strftime('%d/%m/%Y')
                        display_filtered = display_filtered.sort_values('Date', ascending=False)
                        st.dataframe(display_filtered, use_container_width=True)
                        
                        # Download option
                        csv = display_filtered.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Filtered Data as CSV",
                            data=csv,
                            file_name=f"filtered_expenses_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No data found with the applied filters.")
                else:
                    st.warning("No data available to filter.")
        
        with tab2:
            st.subheader("Monthly Expense View")
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
                        'August', 'September', 'October', 'November', 'December']
            selected_month = st.selectbox("Select a month", months)

            # Get the month index (0 for January, 11 for December)
            month_index = months.index(selected_month) + 1  # +1 to match with 1-12 month range
            
            # Filter data for the selected month
            selected_month_expenses = st.session_state.existing_data[
                (st.session_state.existing_data['Date'].dt.month == month_index)
            ].copy()
    
            # Display filtered expenses with formatted dates
            if not selected_month_expenses.empty:
                # Calculate monthly summary
                monthly_total = selected_month_expenses['Amount'].sum()
                monthly_count = len(selected_month_expenses)
                monthly_avg = selected_month_expenses['Amount'].mean()
                
                # Display summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Amount", f"₱{monthly_total:,.2f}")
                with col2:
                    st.metric("Transactions", f"{monthly_count}")
                with col3:
                    st.metric("Average", f"₱{monthly_avg:,.2f}")
                
                st.write("---")
                
                # Format the Date column for display
                selected_month_expenses['Date'] = selected_month_expenses['Date'].dt.strftime('%d/%m/%Y')
                st.dataframe(selected_month_expenses, use_container_width=True)
            else:
                st.warning(f"No expenses found for {selected_month}.")
        
        with tab3:
            st.subheader("All Transactions")
            if not st.session_state.existing_data.empty:
                # Display all data with summary
                total_all = st.session_state.existing_data['Amount'].sum()
                count_all = len(st.session_state.existing_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Amount", f"₱{total_all:,.2f}")
                with col2:
                    st.metric("Total Transactions", f"{count_all}")
                
                st.write("---")
                
                # Format dates for display
                display_all = st.session_state.existing_data.copy()
                display_all['Date'] = display_all['Date'].dt.strftime('%d/%m/%Y')
                display_all = display_all.sort_values('Date', ascending=False)
                
                st.dataframe(display_all, use_container_width=True)
            else:
                st.warning("No data available.")

        with tab4:
            st.subheader("Delete Entry")
            if not st.session_state.existing_data.empty:
                # Create a copy for display with formatted dates
                display_data = st.session_state.existing_data.copy()
                display_data['Date'] = display_data['Date'].dt.strftime('%d/%m/%Y')
                
                # Create options for the selectbox with formatted dates
                options = [f"{idx}: {row['Date']} - {row['Category']} - ₱{row['Amount']:.2f}" 
                          for idx, row in display_data.iterrows()]
                
                # Select an entry to delete
                selected_option = st.selectbox("Select entry to delete", options)
                delete_index = int(selected_option.split(':')[0])
                
                # Show selected entry details
                selected_entry = display_data.loc[delete_index]
                st.write("**Selected Entry Details:**")
                st.write(f"Date: {selected_entry['Date']}")
                st.write(f"Type: {selected_entry['Type']}")
                st.write(f"Category: {selected_entry['Category']}")
                st.write(f"Amount: ₱{selected_entry['Amount']:.2f}")
                st.write(f"Note: {selected_entry['Note']}")
                
                st.write("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    delete_button = st.button("🗑️ Delete Entry", type="secondary")
                with col2:
                    if st.button("❌ Cancel", type="primary"):
                        st.info("Deletion cancelled.")
    
                if delete_button:
                    # Delete the selected entry
                    st.session_state.existing_data = st.session_state.existing_data.drop(delete_index).reset_index(drop=True)
    
                    # Update Google Sheets with the modified DataFrame
                    conn.update(worksheet="Sheet1", data=st.session_state.existing_data)
    
                    st.success("Entry deleted successfully!")
                    st.rerun()
            else:
                st.warning("No entries available to delete.")

        st.write("---")

# Main app logic - directly show dashboard (no login required)
def main():
    dashboard()

if __name__ == "__main__":
    main()
