import pandas as pd

# Define the project timeline data
data = {
    "Week": [
        "Week 1: Oct 21 - Oct 27", "Week 1: Oct 21 - Oct 27", "Week 1: Oct 21 - Oct 27", "Week 1: Oct 21 - Oct 27", "Week 1: Oct 21 - Oct 27", 
        "Week 2: Oct 28 - Nov 3", "Week 2: Oct 28 - Nov 3", "Week 2: Oct 28 - Nov 3", "Week 2: Oct 28 - Nov 3", "Week 2: Oct 28 - Nov 3", 
        "Week 3: Nov 4 - Nov 10", "Week 3: Nov 4 - Nov 10", "Week 3: Nov 4 - Nov 10", "Week 3: Nov 4 - Nov 10", "Week 3: Nov 4 - Nov 10",
        "Week 4: Nov 11 - Nov 17", "Week 4: Nov 11 - Nov 17", "Week 4: Nov 11 - Nov 17", "Week 4: Nov 11 - Nov 17", "Week 4: Nov 11 - Nov 17",
        "Week 5: Nov 18 - Nov 25", "Week 5: Nov 18 - Nov 25", "Week 5: Nov 18 - Nov 25", "Week 5: Nov 18 - Nov 25", "Week 5: Nov 18 - Nov 25"
    ],
    "Day": [
        "Day 1-2", "Day 3-4", "Day 5-7", "Day 5-7", "Day 6-7",
        "Day 1-2", "Day 3-5", "Day 6-7", "Day 6-7", "Day 6-7",
        "Day 1-3", "Day 4-5", "Day 6-7", "Day 6-7", "Day 6-7",
        "Day 1-4", "Day 5-7", "Day 5-7", "Day 5-7", "Day 5-7",
        "Day 1-4", "Day 1-4", "Day 5-7", "Day 5-7", "Day 5-7"
    ],
    "Task": [
        "Project Setup", "Raw Material (Requisition, Base Material, etc.)", "Purchase (Stock Mgmt, Stock Receive, etc.)", "Opening Balance Count, Finished Goods Report", "Complete database schema",
        "Sales Return", "Delivery Status (VAT, Tax)", "Financial Accounts (like Tally)", "Accounting tables", "Integration with Purchase",
        "HRM (Dept, Shift Mgmt)", "Petty Cash Management", "Line Management", "Start Testing", "Begin bug fixing",
        "Complete Line Management", "Continue Testing", "Debugging", "Final Testing", "Polish UI/UX",
        "Final Testing", "Bug Fixing", "Deployment", "Final Adjustments", "Project Handover"
    ],
    "Developer Responsible": [
        "All", "Dev 1 & 2", "Dev 3 & 4", "Dev 4", "All",
        "Dev 1", "Dev 2", "Dev 3", "Dev 4", "All",
        "Dev 1", "Dev 3", "Dev 4", "Dev 2 & 3", "All",
        "Dev 1 & 4", "All", "All", "All", "All",
        "All", "All", "All", "All", "All"
    ]
}

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Save to Excel file
file_path = '../public/Laravel_Project_Timeline.xlsx'
df.to_excel(file_path, index=False)

file_path