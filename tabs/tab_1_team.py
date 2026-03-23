import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import io

from config import KPI_DEFS, TABLE_TOOLTIPS
from utils import format_with_pct
from pdf_engine import generate_formatted_pdf

def render_team_tab(f1, f2, all_advisors, formatted_live, start_date, end_date):
    
    # Sort Options specifically for the team tables
    sort_options = {
        "Total Applications (High to Low)": "Total Applications", 
        "Quality: Approved": "Qual_Approved", 
        "Quality: Cancelled": "Qual_Cancelled", 
        "Live Status: Live": "Port_Live", 
        "Advisor Name (A-Z)": "index"
    }

    col_sort, col_check = st.columns([1.5, 2])
    
    # Calculate base arrays just to feed the sorter keys accurately
    app_counts_base = f1.groupby('Advisor').size().to_frame('Total Applications')
    qual_counts_base = f1.groupby(['Advisor', 'Q_Status']).size().unstack(fill_value=0).add_prefix('Qual_')
    port_counts_base = f2.groupby(['Advisor', 'P_Status']).size().unstack(fill_value=0).add_prefix('Port_')
    master_base = pd.DataFrame(index=all_advisors).join([app_counts_base, qual_counts_base, port_counts_base]).fillna(0)
    
    available_sorts = [k for k, v in sort_options.items() if v == "index" or v in master_base.columns]
    selected_sort_label = col_sort.selectbox("Master Sort (Aligns all tables):", available_sorts)
    
    show_live_team = col_check.checkbox("Show current roster only", value=False, key="team_roster_filter")
    
    if show_live_team:
        f1_team = f1[f1['Advisor'].isin(formatted_live)].copy()
        f2_team = f2[f2['Advisor'].isin(formatted_live)].copy()
        active_advisors_team = [name for name in all_advisors if name in formatted_live]
    else:
        f1_team = f1.copy()
        f2_team = f2.copy()
        active_advisors_team = all_advisors

    team_apps = len(f1_team)
    team_approved = len(f1_team[f1_team['Q_Status'] == 'Approved'])
    team_approv_rate = f"{(team_approved / team_apps * 100):.1f}%" if team_apps > 0 else "0.0%"
    team_committed = len(f2_team)
    team_commit_rate = f"{(team_committed / team_apps * 100):.1f}%" if team_apps > 0 else "0.0%"
    team_live = len(f2_team[f2_team['P_Status'] == 'Live'])
    team_live_rate = f"{(team_live / team_committed * 100):.1f}%" if team_committed > 0 else "0.0%"

    with st.container(border=True):
        tm1, tm2, tm3, tm4, tm5, tm6, tm7 = st.columns(7)
        tm1.metric("📝 Tot. Applications", f"{team_apps:,}", help=KPI_DEFS["total_apps"])
        tm2.metric("✅ Quality Approv.", f"{team_approved:,}", help=KPI_DEFS["qual_approved"])
        tm3.metric("📈 Approv. Rate", team_approv_rate, help=KPI_DEFS["approv_rate"])
        tm4.metric("📦 Commit. Apps", f"{team_committed:,}", help=KPI_DEFS["commit_apps"])
        tm5.metric("📋 Commit. Rate", team_commit_rate, help=KPI_DEFS["commit_rate"])
        tm6.metric("🌐 Total Live", f"{team_live:,}", help=KPI_DEFS["total_live"])
        tm7.metric("🚀 Live Rate", team_live_rate, help=KPI_DEFS["live_rate"])

    app_counts = f1_team.groupby('Advisor').size().to_frame('Total Applications')
    qual_counts = f1_team.groupby(['Advisor', 'Q_Status']).size().unstack(fill_value=0).add_prefix('Qual_')
    port_counts = f2_team.groupby(['Advisor', 'P_Status']).size().unstack(fill_value=0).add_prefix('Port_')
    
    tab_master = pd.DataFrame(index=active_advisors_team).join([app_counts, qual_counts, port_counts]).fillna(0)
    sort_col = sort_options[selected_sort_label]
    master = tab_master.sort_index() if sort_col == "index" else tab_master.sort_values(sort_col, ascending=False)
    
    totals_row = master.sum().to_frame().T
    totals_row.index = ["GRAND TOTAL"]
    final_df = pd.concat([master, totals_row])
    advisor_indices = master.index

    st.divider()
    c1, c2, c3 = st.columns([1, 1.8, 1.8])
    
    with c1:
        st.subheader("📊 Applications")
        st.dataframe(
            final_df[['Total Applications']].style.format("{:,.0f}").background_gradient(cmap='Greens', subset=(advisor_indices, 'Total Applications')), 
            use_container_width=True, height=500,
            column_config={"Total Applications": st.column_config.Column(help=TABLE_TOOLTIPS["Total Applications"])}
        )
    
    with c2:
        st.subheader("✅ Quality Audit")
        q_cols = [c for c in final_df.columns if c.startswith('Qual_')]
        disp_qual_str = pd.DataFrame()
        if q_cols:
            q_order = ['Qual_Approved', 'Qual_Rework', 'Qual_Cancelled', 'Qual_Others']
            actual_q_order = [c for c in q_order if c in q_cols]
            disp_qual_num = final_df[actual_q_order].rename(columns=lambda x: x.replace('Qual_', ''))
            disp_qual_str = format_with_pct(disp_qual_num, final_df['Total Applications'])
            styler_q = disp_qual_str.style
            for col, cmap in [('Approved', 'YlGn'), ('Cancelled', 'Reds'), ('Rework', 'Wistia')]:
                if col in disp_qual_num.columns:
                    styler_q = styler_q.background_gradient(subset=(advisor_indices, col), cmap=cmap, gmap=disp_qual_num[col])
            
            st.dataframe(
                styler_q, use_container_width=True, height=500,
                column_config={col: st.column_config.Column(help=TABLE_TOOLTIPS.get(col, "")) for col in disp_qual_num.columns}
            )
        else:
            st.info("No quality data available.")
        
    with c3:
        st.subheader("🌐 Live Status")
        p_cols = [c for c in final_df.columns if c.startswith('Port_')]
        disp_port_str = pd.DataFrame()
        if p_cols:
            p_order = ['Port_Live', 'Port_Committed', 'Port_Cancelled', 'Port_Others']
            actual_p_order = [c for c in p_order if c in p_cols]
            disp_port_num = final_df[actual_p_order].rename(columns=lambda x: x.replace('Port_', ''))
            disp_port_str = format_with_pct(disp_port_num, final_df['Total Applications'])
            styler_p = disp_port_str.style
            for col, cmap in [('Live', 'Blues'), ('Cancelled', 'Reds'), ('Committed', 'Purples')]:
                if col in disp_port_num.columns:
                    styler_p = styler_p.background_gradient(subset=(advisor_indices, col), cmap=cmap, gmap=disp_port_num[col])
            
            st.dataframe(
                styler_p, use_container_width=True, height=500,
                column_config={col: st.column_config.Column(help=TABLE_TOOLTIPS.get(col, "")) for col in disp_port_num.columns}
            )
        else:
            st.info("No live status data available.")

    # --- EXPORT SECTION ---
    st.write("### 📥 Download Team Report")
    e_col1, e_col2, e_col3 = st.columns(3)
    export_vol = final_df[['Total Applications']]
    export_qual = disp_qual_str if q_cols else pd.DataFrame()
    export_live = disp_port_str if p_cols else pd.DataFrame()
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_vol.to_excel(writer, sheet_name='Applications_Volume')
        if not export_qual.empty: export_qual.to_excel(writer, sheet_name='Quality_Audit')
        if not export_live.empty: export_live.to_excel(writer, sheet_name='Live_Status')
    
    e_col1.download_button(label="Excel (All Tables)", data=output.getvalue(), file_name=f"Sparta_Team_Report_{start_date}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    combined_csv = "APPLICATIONS VOLUME\n" + export_vol.to_csv() + "\nQUALITY AUDIT\n" + export_qual.to_csv() + "\nLIVE STATUS\n" + export_live.to_csv()
    e_col2.download_button(label="CSV (Combined Tables)", data=combined_csv, file_name=f"Sparta_Team_Report_{start_date}.csv", mime="text/csv")
    
    pdf_bytes = generate_formatted_pdf(start_date, end_date, export_vol, export_qual, export_live)
    e_col3.download_button(label="PDF (Formatted Tables)", data=pdf_bytes, file_name=f"Sparta_Team_Report_{start_date}.pdf", mime="application/pdf")

    st.divider()
    st.subheader("📈 Team Performance Trends")
    tg_1, tg_2 = st.columns(2)
    with tg_1:
        if not f1_team.empty:
            daily_v = f1_team.groupby(f1_team['Date_Parsed'].dt.date).size().reset_index(name='Apps')
            daily_q = f1_team[f1_team['Q_Status'] == 'Approved'].groupby(f1_team['Date_Parsed'].dt.date).size().reset_index(name='Approved')
            combined = pd.merge(daily_v, daily_q, on='Date_Parsed', how='left').fillna(0)
            combined['Date_Parsed'] = combined['Date_Parsed'].astype(str)
            fig_single = go.Figure()
            fig_single.add_trace(go.Bar(x=combined['Date_Parsed'], y=combined['Apps'], name="Total Apps", marker_color='#1E3A8A'))
            fig_single.add_trace(go.Scatter(x=combined['Date_Parsed'], y=combined['Approved'], name="Approved (Audit)", line=dict(color='#2E7D32', width=3)))
            fig_single.update_layout(title_text="Daily Apps vs. Quality Approval", hovermode="x unified")
            st.plotly_chart(fig_single, use_container_width=True)
        else:
            st.info("No application trend data for this period.")
    with tg_2:
        available_cols = [c for c in ['Port_Live', 'Port_Cancelled'] if c in master.columns]
        if available_cols:
            status_plot = master[available_cols].rename(columns={'Port_Live':'Live', 'Port_Cancelled':'Cancelled'}).reset_index()
            fig_status = px.bar(status_plot, x='index', y=[c.replace('Port_', '') for c in available_cols], barmode='group', color_discrete_map={'Live': '#2563EB', 'Cancelled': '#DC2626'}, title="Agent-wise Live vs. Cancelled Volume")
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No Live/Cancelled records found for this selection.")
