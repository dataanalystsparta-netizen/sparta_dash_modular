import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_finance_tab(f2, formatted_live):
    st.subheader("💰 Revenue & Financial Insights (Standardized 20% VAT Inclusive)")
    
    show_live_fin = st.checkbox("Show current roster only", value=False, key="fin_roster_filter")
    
    # Pull data strictly from f2 (Sparta2). Determine whether to use the filtered team or all data.
    fin_df = f2[f2['Advisor'].isin(formatted_live)].copy() if show_live_fin else f2.copy()
    
    # Filter for actual LIVE revenue
    live_df = fin_df[fin_df['P_Status'] == 'Live']
    
    total_committed_mrr = fin_df['Standardized_Rev'].sum()
    total_live_mrr = live_df['Standardized_Rev'].sum()
    total_committed_sales = len(fin_df)
    
    with st.container(border=True):
        fc1, fc2, fc3 = st.columns(3)
        fc1.metric("Gross Committed MRR (Total Value)", f"£{total_committed_mrr:,.2f}")
        fc2.metric("Actual Live MRR (Confirmed Live)", f"£{total_live_mrr:,.2f}")
        fc3.metric("Total Committed Packages", f"{total_committed_sales:,}")
        
    st.divider()
    
    view_mode_fin = st.radio("Financial Breakdown By:", ["Daily", "Monthly", "Advisor"], horizontal=True, key="fin_view")
    
    col_fin1, col_fin2 = st.columns([1, 1.5])
    
    with col_fin1:
        st.markdown(f"#### 📊 {view_mode_fin} Revenue Table")
        
        if view_mode_fin == "Daily":
            group_col = fin_df['Date_Parsed'].dt.date
            group_col_live = live_df['Date_Parsed'].dt.date
        elif view_mode_fin == "Monthly":
            group_col = fin_df['Date_Parsed'].dt.to_period('M')
            group_col_live = live_df['Date_Parsed'].dt.to_period('M')
        else: # Advisor Breakdown
            group_col = fin_df['Advisor']
            group_col_live = live_df['Advisor']
        
        comm_group = fin_df.groupby(group_col)['Standardized_Rev'].sum().to_frame("Committed Revenue (£)")
        live_group = live_df.groupby(group_col_live)['Standardized_Rev'].sum().to_frame("Live Revenue (£)")
        
        # Join the two groups together
        fin_group = comm_group.join(live_group, how='outer').fillna(0)
        
        if view_mode_fin == "Monthly":
            fin_group.index = fin_group.index.strftime('%b %Y')
        elif view_mode_fin == "Advisor":
            fin_group = fin_group.sort_values(by="Committed Revenue (£)", ascending=False)
        
        # Apply styling to highlight both columns appropriately
        st.dataframe(
            fin_group.style.format("£{:,.2f}").background_gradient(cmap='Greens', subset=['Committed Revenue (£)']).background_gradient(cmap='YlOrBr', subset=['Live Revenue (£)']),
            use_container_width=True,
            height=450
        )
        
    with col_fin2:
        st.markdown(f"#### 📈 {view_mode_fin} Revenue Trend")
        if not fin_group.empty:
            chart_df = fin_group.reset_index()
            x_col = chart_df.columns[0]
            
            fig_fin = go.Figure()
            
            # If we are viewing by Advisor, use a Bar Chart for Committed. Otherwise, use an Area Chart.
            if view_mode_fin == "Advisor":
                fig_fin.add_trace(go.Bar(x=chart_df[x_col], y=chart_df['Committed Revenue (£)'], name="Committed Revenue", marker_color='#059669'))
            else:
                fig_fin.add_trace(go.Scatter(x=chart_df[x_col], y=chart_df['Committed Revenue (£)'], name="Committed Revenue", fill='tozeroy', line=dict(color='#059669'), fillcolor='rgba(5, 150, 105, 0.2)'))
            
            # Overlay the Live Revenue as a bold line across all view types
            fig_fin.add_trace(go.Scatter(x=chart_df[x_col], y=chart_df['Live Revenue (£)'], name="Live Revenue", line=dict(color='#D97706', width=3), mode='lines+markers'))
            
            fig_fin.update_layout(xaxis_title="", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.info("No financial data found to plot.")
