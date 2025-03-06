import streamlit as st
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import json
import requests
import matplotlib.pyplot as plt


# Data Handling
with open("data.json", "r") as file:
    data = json.load(file)
years = data["years"]
skill_levels = data["skill_levels"]
manpower_requirements = {
    (skill, year): data["manpower_requirements"][skill][year]
    for skill in skill_levels for year in range(len(data["manpower_requirements"][skill]))
}
wastage_rates = data["wastage_rates"]
recruitment_capacity = data["recruitment_capacity"]
retraining_capacity = data["retraining_capacity"]
retraining_cost = data["retraining_cost"]
downgrade_wastage = data["downgrade_wastage"]
redundancy_cost = data["redundancy_cost"]
overmanning_cost = data["overmanning_cost"]
overmanning_limit = data["overmanning_limit"]
short_time_limit = data["short_time_limit"]
short_time_cost = data["short_time_cost"]


# Streamlit Layout
st.set_page_config(page_title="Manpower Optimization", page_icon="👷‍♂️", layout="wide")

st.markdown("""
    <style>
        .title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f4f4f9;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            color: #333;
        }
        .title-bar h1 {
            margin: 0;
            font-size: 49px;
            color: #333;
            margin-left: 20px;
        }
        .title-bar .logo1 {
            max-width: auto;
            height: 60px;
            margin-right: 20px;
        }
        .title-bar a {
            text-decoration: none;
            color: #0073e6;
            font-size: 16px;
        }
        .footer-text {
            font-size: 20px;
            background-color: #f4f4f9;
            text-align: left;
            color: #333;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
        }
    </style>
    <div class="title-bar">
        <h1>Problem 12.5 <br> Manpower Planning</h1>
        <div>
            <a href="https://decisionopt.com" target="_blank">
                <img src="https://decisionopt.com/static/media/DecisionOptLogo.7023a4e646b230de9fb8ff2717782860.svg" class="logo1" alt="Logo"/>
            </a>
        </div>
    </div>
    <div class="footer-text">
    <p style="margin-left:20px;">  'Model Building in Mathematical Programming, Fifth Edition' by H. Paul Williams</p>
    </div>    
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
        .button {
            background-color: #FFFFFF;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        .button:hover {
            background-color: #FFFFFF;
             box-shadow: 1px 1px 4px rgb(255, 75, 75); /* Shadow effect on hover */
        }
    </style>
    <div class="container-c1">
        <br><p> For a detailed view of the mathematical formulation, please visit my 
        <a href="https://github.com/Ash7erix/Model_Building_Assignments/tree/main/12.5_Manpower_Planning">Github</a> page.</p>

    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
    </style>
    <div class="container-c1">
        <br><p>This app helps optimize workforce planning by determining the optimal number of employees to hire, 
        retain, or lay off each month while minimizing costs and meeting operational requirements. It uses Gurobi 
        for optimization, considering factors such as labor demand, hiring costs, layoff costs,and workforce 
        availability.</p>  
        <br><p>You can customize key parameters like hiring costs, layoff costs, and workforce demand using the 
        options on the left side. The app provides detailed insights, including the number of employees hired, 
        retained, or laid off each month, helping you make data-driven staffing decisions.</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
    </style>
    <div class="container-c1">
        <br><p> You can view the mathematical formulation below by clicking the button.</p>
    </div>
""", unsafe_allow_html=True)
if st.button('Display Formulation'):
    def fetch_readme(repo_url):
        raw_url = f"{repo_url}/raw/main/12.5_Manpower_Planning/README.md"  # Adjust path if necessary
        response = requests.get(raw_url)
        return response.text
    repo_url = "https://github.com/Ash7erix/Model_Building_Assignments"
    try:
        readme_content = fetch_readme(repo_url)
        st.markdown(readme_content)
        st.markdown("""---""")
    except Exception as e:
        st.error(f"Could not fetch README: {e}")
        st.markdown("""---""")


#SIDEBAR
st.sidebar.markdown(f"<h2>Objective of the Problem :</h2>",unsafe_allow_html=True)
st.sidebar.markdown(f"<p>By default the objective of the problem is set to Minimizing Redundancy.</p>",unsafe_allow_html=True)
st.sidebar.markdown(f"<p>Please select the box below to keep the primary objective of the problem to Minimize Cost:</p>",unsafe_allow_html=True)
objective_check = st.sidebar.checkbox("Apply Cost Minimization", value=False)
st.sidebar.markdown("""---""")
st.sidebar.markdown(f"<h1><b>Optimization Parameters:</b></h1>",unsafe_allow_html=True)
st.sidebar.subheader("Manpower Requirements:")
manpower_requirements = {
    (skill, 0): data["manpower_requirements"][skill][0]  # Ensure Year 0 is always included
    for skill in skill_levels
}
for skill in skill_levels:
    for year in years:  # Only update for Years 1, 2, 3
        manpower_requirements[(skill, year)] = st.sidebar.number_input(
            f"{skill} (Year {year})", min_value=0, value=data["manpower_requirements"][skill][year]
        )
st.sidebar.subheader("Recruitment Capacity:")
recruitment_capacity = {skill: st.sidebar.number_input(f"Max Recruit ({skill})", min_value=0, value=data["recruitment_capacity"][skill]) for skill in skill_levels}
st.sidebar.subheader("Retraining Constraints:")
retraining_capacity = {"UnskilledToSemi": st.sidebar.number_input("Max Unskilled → Semi-Skilled", min_value=0, value=data["retraining_capacity"]["UnskilledToSemi"]),
                       "SemiToSkilled": st.sidebar.number_input("Max Semi-Skilled → Skilled (%)", min_value=0.0, max_value=1.0, value=data["retraining_capacity"]["SemiToSkilled"])}
retraining_cost = { "UnskilledToSemi": st.sidebar.number_input("Cost Unskilled → Semi-Skilled (£)", min_value=0, value=data["retraining_cost"]["UnskilledToSemi"]),
                    "SemiToSkilled": st.sidebar.number_input("Cost Semi-Skilled → Skilled (£)", min_value=0, value=data["retraining_cost"]["SemiToSkilled"])}
st.sidebar.subheader("Redundancy Cost:")
redundancy_cost = { skill: st.sidebar.number_input(f"Redundancy Cost ({skill}) (£)", min_value=0, value=data["redundancy_cost"][skill]) for skill in skill_levels}
st.sidebar.subheader("Overmanning Costs & Limits")
overmanning_cost = { skill: st.sidebar.number_input(f"Overmanning Cost ({skill}) (£)", min_value=0, value=data["overmanning_cost"][skill]) for skill in skill_levels}
overmanning_limit = st.sidebar.number_input("Max Overmanning Allowed", min_value=0, value=data["overmanning_limit"])
short_time_limit = st.sidebar.number_input("Max Short-Time Workers per Skill", min_value=0, value=data["short_time_limit"])
short_time_cost = { skill: st.sidebar.number_input(f"Short-Time Cost ({skill}) (£)", min_value=0, value=data["short_time_cost"][skill]) for skill in skill_levels}


# Display Optimization Data in Tables
st.title("Optimization Data and Constraints:")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Manpower Requirements")
    manpower_df = pd.DataFrame(data["manpower_requirements"]).T
    manpower_df.columns = ["Current Strength", "Year 1", "Year 2", "Year 3"]
    st.dataframe(manpower_df)
with col2:
    st.subheader("Redundancy & Overmanning Cost")
    redundancy_df = pd.DataFrame.from_dict(data["redundancy_cost"], orient="index", columns=["Redundancy Cost (£)"])
    redundancy_df["Overmanning Cost (£)"] = redundancy_df.index.map(data["overmanning_cost"])
    st.dataframe(redundancy_df)
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Wastage Rates")
    wastage_df = pd.DataFrame(data["wastage_rates"]).T
    wastage_df.index.name = "Service Time"
    st.dataframe(wastage_df)
with col2:
    st.subheader("Retraining Capacity & Cost")
    retraining_df = pd.DataFrame.from_dict(data["retraining_capacity"], orient="index", columns=["Max Workers"])
    retraining_df["Cost (£)"] = retraining_df.index.map(data["retraining_cost"])
    retraining_df.index.name = "Retraining Type"
    st.dataframe(retraining_df)
with col3:
    st.subheader("Recruitment Capacity")
    recruitment_df = pd.DataFrame(list(data["recruitment_capacity"].items()), columns=["Skill Level", "Max Recruited"])
    recruitment_df.index = range(1, len(recruitment_df) + 1)
    st.dataframe(recruitment_df)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Overmanning & Short-Time Work Limits")
    limits_df = pd.DataFrame({
        "Constraint": ["Overmanning Limit", "Short-Time Work Limit"],
        "Value": [data["overmanning_limit"], data["short_time_limit"]]
    })
    st.dataframe(limits_df)
with col2:
    st.subheader("Short-Time Work Cost")
    short_time_cost_df = pd.DataFrame(list(data["short_time_cost"].items()), columns=["Skill Level", "Cost per Worker (£)"])
    short_time_cost_df.index = range(1, len(short_time_cost_df) + 1)
    st.dataframe(short_time_cost_df)
st.markdown("""---""")


# MODEL SETUP
model = gp.Model('Manpower_Optimization')


# Decision Variables
TotalWorkers = model.addVars(skill_levels, [0] + list(years), name="TotalWorkers")
RecruitedWorkers = model.addVars(skill_levels, years, name="RecruitedWorkers")
RetrainedWorkers = model.addVars(['UnskilledToSemi', 'SemiToSkilled'], years, name="RetrainedWorkers")
DowngradedWorkers = model.addVars(['SkilledToSemi', 'SkilledToUnskilled', 'SemiToUnskilled'], years, name="DowngradedWorkers")
RedundantWorkers = model.addVars(skill_levels, years, name="RedundantWorkers")
ShortTimeWorkers = model.addVars(skill_levels, years, name="ShortTimeWorkers")
OvermannedWorkers = model.addVars(skill_levels, years, name="OvermannedWorkers")


# CONSTRAINTS
# Initial Workforce Levels
for skill in skill_levels:
    TotalWorkers[skill, 0] = manpower_requirements[skill, 0]

# Upper bounds on recruitment and short-time working
for year in years:
    for skill in skill_levels:
        RecruitedWorkers[skill, year].ub = recruitment_capacity[skill]
        ShortTimeWorkers[skill, year].ub = short_time_limit
    RetrainedWorkers['UnskilledToSemi', year].ub = retraining_capacity['UnskilledToSemi']

# Workforce Balance Constraints
for year in years:
    model.addConstr(
        (0.95 * TotalWorkers['Skilled', year - 1] +
         0.90 * RecruitedWorkers['Skilled', year] +
         0.95 * RetrainedWorkers['SemiToSkilled', year] -
         DowngradedWorkers['SkilledToSemi', year] -
         DowngradedWorkers['SkilledToUnskilled', year] -
         RedundantWorkers['Skilled', year]
         == TotalWorkers['Skilled', year]),
        name=f"Skilled_Workforce_Balance_{year}"
    )

    model.addConstr(
        (0.95 * TotalWorkers['SemiSkilled', year - 1] +
         0.80 * RecruitedWorkers['SemiSkilled', year] +
         0.95 * RetrainedWorkers['UnskilledToSemi', year] -
         RetrainedWorkers['SemiToSkilled', year] +
         0.5 * DowngradedWorkers['SkilledToSemi', year] -
         DowngradedWorkers['SemiToUnskilled', year] -
         RedundantWorkers['SemiSkilled', year]
         == TotalWorkers['SemiSkilled', year]),
        name=f"SemiSkilled_Workforce_Balance_{year}"
    )

    model.addConstr(
        (0.90 * TotalWorkers['Unskilled', year - 1] +
         0.75 * RecruitedWorkers['Unskilled', year] -
         RetrainedWorkers['UnskilledToSemi', year] +
         0.5 * DowngradedWorkers['SkilledToUnskilled', year] +
         0.5 * DowngradedWorkers['SemiToUnskilled', year] -
         RedundantWorkers['Unskilled', year]
         == TotalWorkers['Unskilled', year]),
        name=f"Unskilled_Workforce_Balance_{year}"
    )

# Workforce Requirement Constraints
for skill in skill_levels:
    for year in years:
        model.addConstr(
            (TotalWorkers[skill, year] - OvermannedWorkers[skill, year] - 0.5 * ShortTimeWorkers[skill, year] ==
             manpower_requirements[skill, year]),
            name=f"Workforce_Requirement_{skill}_{year}"
        )

# Overmanning Limit
for year in years:
    model.addConstr(
        gp.quicksum(OvermannedWorkers[skill, year] for skill in skill_levels) <= overmanning_limit,
        name=f"Overmanning_Limit_{year}"
    )


# OBJECTIVE FUNCTION: Minimize Total Cost
if objective_check:
    model.setObjective(
        gp.quicksum(
            retraining_cost['UnskilledToSemi'] * RetrainedWorkers['UnskilledToSemi', year] +
            retraining_cost['SemiToSkilled'] * RetrainedWorkers['SemiToSkilled', year] +
            redundancy_cost['Unskilled'] * RedundantWorkers['Unskilled', year] +
            redundancy_cost['SemiSkilled'] * RedundantWorkers['SemiSkilled', year] +
            redundancy_cost['Skilled'] * RedundantWorkers['Skilled', year] +
            short_time_cost['Unskilled'] * ShortTimeWorkers['Unskilled', year] +
            short_time_cost['SemiSkilled'] * ShortTimeWorkers['SemiSkilled', year] +
            short_time_cost['Skilled'] * ShortTimeWorkers['Skilled', year] +
            overmanning_cost['Unskilled'] * OvermannedWorkers['Unskilled', year] +
            overmanning_cost['SemiSkilled'] * OvermannedWorkers['SemiSkilled', year] +
            overmanning_cost['Skilled'] * OvermannedWorkers['Skilled', year]
            for year in years
        ),
        GRB.MINIMIZE
    )
else:
    model.setObjective(
        gp.quicksum(RedundantWorkers[skill, year] for skill in skill_levels for year in years),
        GRB.MINIMIZE
    )


# SOLVE MODEL
st.markdown("""
    <style>
        .container-c2 p {
            font-size: 20px;
            margin-bottom: 20px;
        }
    </style>
    <div class="container-c2">
        <br><p>Click on the button below to solve the optimization problem.</p>
    </div>
""", unsafe_allow_html=True)
if st.button("Solve Optimization"):
    model.optimize()
    if model.status == GRB.OPTIMAL:
        st.markdown("""---""")
        total = model.objVal
        if objective_check:
            st.markdown(
                f"<h3>Total Profit : <span style='color:rgba(255, 75, 75, 1)  ;'> <b>£{total:.2f}</b></span></h3>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<h3>Total Redundant Workers : <span style='color:rgba(255, 75, 75, 1)  ;'> <b>{total:.2f}</b></span></h3>",
                unsafe_allow_html=True)
        st.markdown("""---""")

        def display_results(var_dict, title, is_training_downgrading=False):
            st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)  # Two-column layout

            # Column 1: Plot the Bar Graph
            with col1:
                fig, ax = plt.subplots(figsize=(4, 3))  # Smaller plot size

                # Prepare Data
                df = pd.DataFrame([], columns=skill_levels, index=years)
                for (skill, year), var in var_dict.items():
                    if year > 0:
                        df.loc[year, skill] = var.x  # Store values in DataFrame

                # Plot the Bar Chart
                df.plot(kind='bar', ax=ax)

                # Formatting
                ax.set_title(title, fontsize=8)
                ax.set_xlabel("Years", fontsize=7)
                ax.set_ylabel("Workers", fontsize=7)
                ax.tick_params(axis='both', labelsize=6)
                ax.legend(fontsize=6, loc='upper left', bbox_to_anchor=(1, 1))

                plt.tight_layout(pad=1.0)  # Adjust layout for a compact fit
                st.pyplot(fig, use_container_width=False)

            # Column 2: Show the Data Table
            with col2:
                rename_dict = {"SemiSkilled": "Semi-Skilled",
                               "UnskilledToSemi": "Unskilled → Semi",
                               "SemiToSkilled": "Semi → Skilled",
                               "SkilledToSemi": "Skilled → Semi",
                               "SkilledToUnskilled": "Skilled → Unskilled",
                               "SemiToUnskilled": "Semi → Unskilled"
                               }
                df.rename(columns=rename_dict, inplace=True)
                df.index = [f"Year {y}" for y in df.index]
                if is_training_downgrading:
                    df = df[["Unskilled → Semi", "Semi → Skilled",
                             "Skilled → Semi", "Skilled → Unskilled",
                             "Semi → Unskilled"]]
                st.dataframe(df)
            st.markdown("""---""")

        # Display Outputs
        display_results(TotalWorkers, "Available Workforce")
        display_results(RecruitedWorkers, "Recruitment Plan")
        combined_training_downgrading = {**RetrainedWorkers, **DowngradedWorkers}
        display_results(combined_training_downgrading, "Training & Downgrading Plan", is_training_downgrading=True)
        display_results(RedundantWorkers, "Redundancy Plan")
        display_results(ShortTimeWorkers, "Short-Time Working Plan")
        display_results(OvermannedWorkers, "Overmanning Plan")
    else:
        st.error("No optimal solution found!")
    st.markdown("""
                                <style>
                                    footer {
                                        text-align: center;
                                        background-color: #f1f1f1;
                                        color: #333;
                                        font-size: 19px;
                                        margin-bottom:0px;
                                    }
                                    footer img {
                                        width: 44px; /* Adjust size of the logo */
                                        height: 44px;
                                    }
                                </style>
                                <footer>
                                    <h1>Author- Ashutosh <a href="https://www.linkedin.com/in/ashutoshpatel24x7/" target="_blank">
                                    <img src="https://decisionopt.com/static/media/LinkedIn.a6ad49e25c9a6b06030ba1b949fcd1f4.svg" class="img" alt="Logo"/></h1>
                                </footer>
                            """, unsafe_allow_html=True)
    st.markdown("""---""")
