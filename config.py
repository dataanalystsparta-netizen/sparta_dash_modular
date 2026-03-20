LIVE_AGENTS = [
   "Anshu","Anjali", "Aman", "Frogh", "Gaurav", "Guru", 
   "Naveen", "Krrish", "Niki", "Manmeet","Sangeeta","Gungun",
   "Animesh","Ajay","Shaheen"
]

KPI_DEFS = {
   "total_apps": "Total Applications.",
   "qual_approved": "Applications that have successfully passed the Quality Audit process.",
   "approv_rate": "Percentage of total applications that reached 'Approved' status.",
   "commit_apps": "Total applications that got 'Committed'.",
   "commit_rate": "Percentage of applications that got 'Committed'",
   "total_live": "Total applications that got 'Live'.",
   "live_rate": "Conversion rate from Committed applications to confirmed Live records."
}

TABLE_TOOLTIPS = {
    "Total Applications": "Grand total of all applications logged by the advisor.",
    "Applications": "Number of applications logged for this specific period.",
    "Approved": "Applications that have cleared the Quality Audit process.",
    "Rework": "Applications requiring corrections/rework or missing information.",
    "Cancelled": "Applications that were rejected or did not proceed.",
    "Others": "These applications are pending, hold or other miscellaneous statuses.",
    "Live": "Applications successfully activated and confirmed.",
    "Committed": "Applications that are currently in a 'committed' state."
}

CSS_STYLE = """
   <style>
   .block-container { max-width: 98%; padding-top: 5rem; }
    h3 { margin-bottom: 0.5rem !important; font-size: 1.2rem !important; color: #1E3A8A; }
   .last-updated { font-size: 0.8rem; color: gray; text-align: right; }
   [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #059669; }
   [data-testid="stMetricLabel"] { font-size: 0.85rem !important; white-space: nowrap; }
   </style>
"""
