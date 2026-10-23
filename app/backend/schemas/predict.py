from pydantic import BaseModel


class PredictionRequest(BaseModel):
    """Non-proxy feature inputs for the Balanced RF model.

    Proxy fields (Previously_Diagnosed, Ever_Sought_Treatment, On_Therapy_Now,
    On_Medication) are intentionally excluded — they are post-hoc treatment
    indicators that would constitute data leakage and are not available at
    inference time for a new respondent.
    """

    # Personal Profile
    Age: float
    Gender: str
    Country: str
    Education: str
    Marital_Status: str
    Income_Level: str
    Employment_Status: str

    # Work Context
    Work_Hours_Per_Week: float
    Remote_Work: str
    Job_Satisfaction: float
    Work_Stress_Level: float
    Work_Life_Balance: float
    Ever_Bullied_At_Work: float
    Company_Mental_Health_Support: str

    # Lifestyle
    Exercise_Per_Week: str
    Sleep_Hours_Night: float
    Caffeine_Drinks_Day: float
    Alcohol_Frequency: str
    Smoking: str
    Screen_Time_Hours_Day: float
    Social_Media_Hours_Day: float
    Hobby_Time_Hours_Week: float
    Diet_Quality: str

    # Symptoms
    Financial_Stress: float
    Feeling_Sad_Down: float
    Loss_Of_Interest: float
    Sleep_Trouble: float
    Fatigue: float
    Poor_Appetite_Or_Overeating: float
    Feeling_Worthless: float
    Concentration_Difficulty: float
    Anxious_Nervous: float
    Panic_Attacks: float
    Mood_Swings: float
    Irritability: float
    Obsessive_Thoughts: float
    Compulsive_Behavior: float
    Self_Harm_Thoughts: float
    Suicidal_Thoughts: float

    # Support System
    Family_History_Mental_Illness: float
    Trauma_History: float
    Social_Support: float
    Close_Friends_Count: float
    Feel_Understood: float
    Loneliness: float
    Discuss_Mental_Health: str


class PredictionResponse(BaseModel):
    predicted_class: int
    probability: float
    probability_label: str
    model_name: str
    disclaimer: str
