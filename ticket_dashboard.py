import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import datetime

# Set up Streamlit page (Light theme, with emoji correctly pasted)
st.set_page_config(
    page_title="📊 Customer Support Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    csv_path = r"C:\Users\madha\Downloads\customer_support_tickets.csv"  # <-- Update your correct path

    try:
        df = pd.read_csv(csv_path)

        # Convert to datetime
        date_cols = ['Date of Purchase', 'First Response Time', 'Time to Resolution']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Create Response Time (hours) if possible
        if 'Time to Resolution' in df.columns and 'First Response Time' in df.columns:
            df['Response Time (hours)'] = (df['Time to Resolution'] - df['First Response Time']).dt.total_seconds() / 3600

        return df

    except FileNotFoundError:
        st.error(f"CSV file not found at {csv_path}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

def main():
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📊 Customer Support Tickets Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Unlock hidden insights and improve your customer service! 🚀</h4>", unsafe_allow_html=True)
    st.write(" ")

    with st.spinner("Loading data... Please wait..."):
        df = load_data()

    # Sidebar Filters
    st.sidebar.header("🛠️ Filters")

    filter_options = {}
    for col in ['Ticket Status', 'Ticket Priority', 'Ticket Channel']:
        if col in df.columns:
            selected = st.sidebar.multiselect(f"Select {col}:", options=df[col].dropna().unique())
            if selected:
                filter_options[col] = selected

    # Apply Filters
    mask = pd.Series(True, index=df.index)
    for col, selected in filter_options.items():
        mask &= df[col].isin(selected)

    df_filtered = df[mask]

    # KPIs
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", len(df_filtered))
    with col2:
        avg_resolution = df_filtered['Response Time (hours)'].mean() if 'Response Time (hours)' in df_filtered else None
        st.metric("Avg Resolution Time (hrs)", f"{avg_resolution:.1f}" if pd.notna(avg_resolution) else "N/A")
    with col3:
        avg_rating = df_filtered['Customer Satisfaction Rating'].mean() if 'Customer Satisfaction Rating' in df_filtered else None
        st.metric("Avg Satisfaction", f"{avg_rating:.1f}/5" if pd.notna(avg_rating) else "N/A")
    with col4:
        unresolved = df_filtered[df_filtered['Ticket Status'] != 'Closed'].shape[0] if 'Ticket Status' in df_filtered else 0
        st.metric("Unresolved Tickets", unresolved)

    st.divider()

    # Visualizations
    if not df_filtered.empty:
        if 'Ticket Status' in df_filtered:
            st.subheader("1️⃣ Ticket Status Distribution")
            fig1 = px.pie(df_filtered, names='Ticket Status', hole=0.4, title="Tickets by Status")
            st.plotly_chart(fig1, use_container_width=True)

        if 'Ticket Type' in df_filtered:
            st.subheader("2️⃣ Ticket Types Analysis")
            type_count = df_filtered['Ticket Type'].value_counts().reset_index()
            type_count.columns = ['Ticket Type', 'Count']
            fig2 = px.bar(type_count, x='Ticket Type', y='Count', title="Tickets by Type", color='Ticket Type')
            st.plotly_chart(fig2, use_container_width=True)

        if 'Customer Satisfaction Rating' in df_filtered:
            st.subheader("3️⃣ Customer Satisfaction Distribution")
            rating_count = df_filtered['Customer Satisfaction Rating'].value_counts().reset_index()
            rating_count.columns = ['Rating', 'Count']
            fig3 = px.bar(rating_count, x='Rating', y='Count', title="Customer Ratings")
            st.plotly_chart(fig3, use_container_width=True)

        if 'Response Time (hours)' in df_filtered:
            st.subheader("4️⃣ Resolution Time Analysis")
            fig4 = px.box(df_filtered, y='Response Time (hours)', title="Resolution Time Distribution")
            st.plotly_chart(fig4, use_container_width=True)

        if 'Product Purchased' in df_filtered:
            st.subheader("5️⃣ Top Products with Issues")
            top_products = df_filtered['Product Purchased'].value_counts().nlargest(10).reset_index()
            top_products.columns = ['Product', 'Count']
            fig5 = px.bar(top_products, x='Product', y='Count', title="Top 10 Products")
            st.plotly_chart(fig5, use_container_width=True)

        if 'Ticket Channel' in df_filtered and 'Customer Satisfaction Rating' in df_filtered:
            st.subheader("6️⃣ Support Channel Performance")
            channel_perf = df_filtered.groupby('Ticket Channel')['Customer Satisfaction Rating'].mean().reset_index()
            fig6 = px.bar(channel_perf, x='Ticket Channel', y='Customer Satisfaction Rating', title="Channel Satisfaction")
            st.plotly_chart(fig6, use_container_width=True)

        if 'Ticket Priority' in df_filtered:
            st.subheader("7️⃣ Ticket Priority Distribution")
            fig7 = px.pie(df_filtered, names='Ticket Priority', hole=0.4, title="Ticket Priority Split")
            st.plotly_chart(fig7, use_container_width=True)

        if 'Customer Age' in df_filtered and 'Customer Satisfaction Rating' in df_filtered:
            st.subheader("8️⃣ Age vs Satisfaction")
            fig8 = px.scatter(df_filtered, x='Customer Age', y='Customer Satisfaction Rating', title="Age vs Satisfaction")
            st.plotly_chart(fig8, use_container_width=True)

        if 'Customer Gender' in df_filtered:
            st.subheader("9️⃣ Ticket Distribution by Gender")
            gender_counts = df_filtered['Customer Gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            fig9 = px.bar(gender_counts, x='Gender', y='Count', title="Tickets by Gender")
            st.plotly_chart(fig9, use_container_width=True)

        if 'Date of Purchase' in df_filtered:
            st.subheader("🔟 Tickets Over Time")
            tickets_time = df_filtered.groupby(df_filtered['Date of Purchase'].dt.to_period('M')).size().reset_index()
            tickets_time['Date of Purchase'] = tickets_time['Date of Purchase'].astype(str)
            fig10 = px.line(tickets_time, x='Date of Purchase', y=0, title="Tickets Over Months")
            st.plotly_chart(fig10, use_container_width=True)
    else:
        st.warning("⚠️ No data available for selected filters.")

    st.divider()

    # Show raw data
    st.subheader("📋 Raw Data")
    if st.checkbox("Show Raw Data"):
        st.dataframe(df_filtered)

    # Download filtered data
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "📥 Download Filtered Data",
        data=convert_df(df_filtered),
        file_name='filtered_customer_support_tickets.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()
# streamlit run ticket_dashboard.py