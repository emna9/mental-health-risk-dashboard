from __future__ import annotations

APP_TITLE = "Mental Health Risk Insight Dashboard"
APP_SUBTITLE = (
    "An educational analytics product for exploring stress, support, symptoms, and"
    " model behavior in a synthetic mental health survey dataset."
)
MODEL_NAME = "Balanced RF (tuned)"
DISCLAIMER = (
    "This dashboard is for educational and analytical purposes only. It does not"
    " provide medical advice, mental health diagnosis, or treatment recommendations."
)
RANKING_RULE = (
    "Balanced_Accuracy > Recall_0 > F1_0 > PR_AUC_0 > ROC_AUC_1 > F1_1"
)
TARGET_COL = "Has_Mental_Health_Issue"
PROXY_DROP_COLS = [
    "Previously_Diagnosed",
    "Ever_Sought_Treatment",
    "On_Therapy_Now",
    "On_Medication",
]
ORDINAL_COLS = [
    "Education",
    "Income_Level",
    "Exercise_Per_Week",
    "Diet_Quality",
    "Alcohol_Frequency",
    "Discuss_Mental_Health",
]
NOMINAL_COLS = [
    "Gender",
    "Country",
    "Marital_Status",
    "Employment_Status",
    "Remote_Work",
    "Company_Mental_Health_Support",
    "Smoking",
]
ORDINAL_CATEGORIES = [
    ["High School", "Some College", "Bachelor", "Master", "PhD"],
    ["Low", "Middle", "High"],
    ["Never", "1-2 times", "3-4 times", "5+ times"],
    ["Poor", "Average", "Good", "Excellent"],
    ["Never", "Rarely", "Weekly", "Daily"],
    ["Never", "Rarely", "Sometimes", "Yes easily"],
]

DEMOGRAPHIC_COLS = [
    "Age",
    "Gender",
    "Country",
    "Education",
    "Employment_Status",
    "Marital_Status",
]
RISK_FACTOR_COLS = [
    "Work_Stress_Level",
    "Financial_Stress",
    "Sleep_Hours_Night",
    "Social_Support",
    "Loneliness",
    "Trauma_History",
    "Family_History_Mental_Illness",
    "Job_Satisfaction",
    "Work_Life_Balance",
]
SYMPTOM_COLS = [
    "Feeling_Sad_Down",
    "Loss_Of_Interest",
    "Sleep_Trouble",
    "Fatigue",
    "Poor_Appetite_Or_Overeating",
    "Feeling_Worthless",
    "Concentration_Difficulty",
    "Anxious_Nervous",
    "Panic_Attacks",
    "Mood_Swings",
    "Irritability",
    "Obsessive_Thoughts",
    "Compulsive_Behavior",
    "Self_Harm_Thoughts",
    "Suicidal_Thoughts",
]
SUPPORT_PATTERN_COLS = [
    "Previously_Diagnosed",
    "Ever_Sought_Treatment",
    "On_Therapy_Now",
    "On_Medication",
    "Discuss_Mental_Health",
    "Company_Mental_Health_Support",
    "Feel_Understood",
    "Social_Support",
    "Close_Friends_Count",
]

PERSONAL_INPUT_GROUPS = {
    "Personal Profile": [
        "Age",
        "Gender",
        "Country",
        "Education",
        "Marital_Status",
        "Income_Level",
        "Employment_Status",
    ],
    "Work Context": [
        "Work_Hours_Per_Week",
        "Remote_Work",
        "Job_Satisfaction",
        "Work_Stress_Level",
        "Work_Life_Balance",
        "Ever_Bullied_At_Work",
        "Company_Mental_Health_Support",
    ],
    "Lifestyle": [
        "Exercise_Per_Week",
        "Sleep_Hours_Night",
        "Caffeine_Drinks_Day",
        "Alcohol_Frequency",
        "Smoking",
        "Screen_Time_Hours_Day",
        "Social_Media_Hours_Day",
        "Hobby_Time_Hours_Week",
        "Diet_Quality",
    ],
    "Symptoms": [
        "Financial_Stress",
        "Feeling_Sad_Down",
        "Loss_Of_Interest",
        "Sleep_Trouble",
        "Fatigue",
        "Poor_Appetite_Or_Overeating",
        "Feeling_Worthless",
        "Concentration_Difficulty",
        "Anxious_Nervous",
        "Panic_Attacks",
        "Mood_Swings",
        "Irritability",
        "Obsessive_Thoughts",
        "Compulsive_Behavior",
        "Self_Harm_Thoughts",
        "Suicidal_Thoughts",
    ],
    "Support System": [
        "Family_History_Mental_Illness",
        "Trauma_History",
        "Social_Support",
        "Close_Friends_Count",
        "Feel_Understood",
        "Loneliness",
        "Discuss_Mental_Health",
    ],
}
