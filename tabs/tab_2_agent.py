import streamlit as st
import pandas as pd
import plotly.graph_objects as go 
from config import KPI_DEFS, TABLE_TOOLTIPS
from utils import format_with_pct

def render_agent_tab(f1, f2, all_advisors, formatted_live):
    st.subheader("👤 Detailed Agent Analysis")
    col_check, col_select = st.columns([1, 3])
    show_live_only = col_check.checkbox("Show current roster only", value=False, key="individual_roster_filter")
    dropdown_list = [n for n in all_advisors if n in formatted_live] if show_live_only else all_advisors
    selected_agent = col_select.selectbox("Select Agent:", dropdown_list if dropdown_list else all_advisors)
    
    if selected_agent:
        ag1 = f1[f1['Advisor'] == selected_agent].copy()
        ag2 = f2[f2['Advisor'] == selected_agent].copy()
        total_apps = len(ag1)
        approved = len(ag1[ag1['Q_Status'] == 'Approved'])
        approval_rate = f"{(approved / total_apps * 100):.1f}%" if total_apps > 0 else "0.0%"
        total_committed_apps = len(ag2) 
        committed_rate = f"{(total_committed_apps / total_apps * 100):.1f}%" if total_apps > 0 else "0.0%"
        live = len(ag2[ag2['P_Status'] == 'Live'])
        live_rate = f"{(live / total_committed_apps * 100):.1f}%" if total_committed_apps > 0 else "0.0%"
        
        with st.container(border=True):
            m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
            m1.metric("📝 Tot. Applications", f"{total_apps:,}", help=KPI_DEFS["total_apps"])
            m2.metric("✅ Quality Approv.", f"{approved:,}", help=KPI_DEFS["qual_approved"])
            m3.metric("📈 Approv. Rate", approval_rate, help=KPI_DEFS["approv_rate"])
            m4.metric("📦 Commit. Apps", f"{total_committed_apps:,}", help=KPI_DEFS["commit_apps"])
            m5.metric("📋 Commit. Rate", committed_rate, help=KPI_DEFS["commit_rate"])
            m6.metric("🌐 Total Live", f"{live:,}", help=KPI_DEFS["total_live"])
            m7.metric("🚀 Live Rate", live_rate, help=KPI_DEFS["live_rate"])
        
        st.divider()
        view_mode = st.radio("View Breakdown By:", ["Daily", "Monthly"], horizontal=True)
        if view_mode == "Monthly":
            ag1['Period'] = ag1['Date_Parsed'].dt.to_period('M')
            ag2['Period'] = ag2['Date_Parsed'].dt.to_period('M')
        else:
            ag1['Period'] = ag1['Date_Parsed'].dt.date
            ag2['Period'] = ag2['Date_Parsed'].dt.date
        
        st.write(f"**{view_mode}** breakdown for **{selected_agent}**")
        ca, cb, cc = st.columns([1, 1.8, 1.8])

        with ca:
            st.markdown(f"#### 📊 {view_mode} Applications")
            if not ag1.empty:
                daily_apps = ag1.groupby('Period').size().to_frame('Applications')
                if view_mode == "Monthly": daily_apps.index = daily_apps.index.strftime('%b %Y')
                t_apps = daily_apps.sum().to_frame().T
                t_apps.index = ["TOTAL"]
                df_apps = pd.concat([daily_apps, t_apps])
                st.dataframe(
                    df_apps.style.format("{:,.0f}").background_gradient(cmap='Greens', subset=(daily_apps.index, 'Applications')), 
                    use_container_width=True,
                    column_config={"Applications": st.column_config.Column(help=TABLE_TOOLTIPS["Applications"])}
                )
            else:
                st.info("No applications found.")

        with cb:
            st.markdown("#### ✅ Quality Audit")
            if not ag1.empty:
                daily_qual = ag1.groupby(['Period', 'Q_Status']).size().unstack(fill_value=0)
                q_order = ['Approved', 'Rework', 'Cancelled', 'Others']
                actual_q = [c for c in q_order if c in daily_qual.columns]
                dq_num = daily_qual[actual_q]
                if view_mode == "Monthly": dq_num.index = dq_num.index.strftime('%b %Y')
                row_totals = daily_apps['Applications']
                dq_str = format_with_pct(dq_num, row_totals)
                t_qual_num = dq_num.sum().to_frame().T
                t_qual_num.index = ["TOTAL"]
                t_qual_str = format_with_pct(t_qual_num, pd.Series([total_apps], index=["TOTAL"]))
                final_q_str = pd.concat([dq_str, t_qual_str])
                styler_dq = final_q_str.style
                for col, cmap in [('Approved', 'YlGn'), ('Cancelled', 'Reds'), ('Rework', 'Wistia')]:
                    if col in dq_num.columns:
                        styler_dq = styler_dq.background_gradient(subset=(dq_num.index, col), cmap=cmap, gmap=dq_num[col])
                
                st.dataframe(
                    styler_dq, use_container_width=True,
                    column_config={col: st.column_config.Column(help=TABLE_TOOLTIPS.get(col, "")) for col in dq_num.columns}
                )
            else:
                st.info("No quality records.")

        with cc:
            st.markdown("#### 🌐 Live Status")
            if not ag2.empty:
                daily_port = ag2.groupby(['Period', 'P_Status']).size().unstack(fill_value=0)
                p_order = ['Live', 'Committed', 'Cancelled', 'Others']
                actual_p = [c for c in p_order if c in daily_port.columns]
                dp_num = daily_port[actual_p]
                if view_mode == "Monthly": dp_num.index = dp_num.index.strftime('%b %Y')
                dp_str = format_with_pct(dp_num, row_totals)
                t_port_num = dp_num.sum().to_frame().T
                t_port_num.index = ["TOTAL"]
                t_port_str = format_with_pct(t_port_num, pd.Series([total_apps], index=["TOTAL"]))
                final_p_str = pd.concat([dp_str, t_port_str])
                styler_dp = final_p_str.style
                for col, cmap in [('Live', 'Blues'), ('Cancelled', 'Reds'), ('Committed', 'Purples')]:
                    if col in dp_num.columns:
                        styler_dp = styler_dp.background_gradient(subset=(dp_num.index, col), cmap=cmap, gmap=dp_num[col])
                
                st.dataframe(
                    styler_dp, use_container_width=True,
                    column_config={col: st.column_config.Column(help=TABLE_TOOLTIPS.get(col, "")) for col in dp_num.columns}
                )
            else:
                st.info("No live status records found for this agent.")

        st.divider()
        st.subheader(f"📈 Performance Trends: {selected_agent}")
        if not ag1.empty:
            d_apps = ag1.groupby('Period').size().to_frame('Total Apps')
            d_comm = ag2.groupby('Period').size().to_frame('Committed')
            d_appr = ag1[ag1['Q_Status'] == 'Approved'].groupby('Period').size().to_frame('Approved')
            d_live = ag2[ag2['P_Status'] == 'Live'].groupby('Period').size().to_frame('Live')
            i_comb = d_apps.join([d_comm, d_appr, d_live], how='left').fillna(0).reset_index()
            i_comb['Period'] = i_comb['Period'].astype(str)
            ig1, ig2 = st.columns(2)
            with ig1:
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(x=i_comb['Period'], y=i_comb['Total Apps'], name="Total Apps", marker_color='#60A5FA'))
                fig1.add_trace(go.Scatter(x=i_comb['Period'], y=i_comb['Approved'], name="Quality Approved", line=dict(color='#059669', width=3)))
                fig1.update_layout(title="Apps vs Quality Approved", hovermode="x unified")
                st.plotly_chart(fig1, use_container_width=True)
            with ig2:
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=i_comb['Period'], y=i_comb['Committed'], name="Commit. Apps", marker_color='#8B5CF6'))
                fig2.add_trace(go.Scatter(x=i_comb['Period'], y=i_comb['Live'], name="Live", line=dict(color='#F59E0B', width=3)))
                fig2.update_layout(title="Committed vs Live", hovermode="x unified")
                st.plotly_chart(fig2, use_container_width=True)
