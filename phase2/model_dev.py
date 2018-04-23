import pandas as pd
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
import pickle

"""
    Given the personality insights obtained from IBM Watson's API, 
    predict the GPA. Usage: predict_GPA(insights, 'RF_PI.pkl')
    
    Args:
        pi_response: Response from IBM Watson Personality Insights API in text/csv format. 
                     Directly from the function getpersonalityinsights of speech_analysis.py
        model_filename: filename of the learning model saved in pkl format
    
    Returns:
        class/range of GPA in str format eg: '3.25-3.5'
"""
def predict_GPA(pi_response, model_filename):
    features = ['Agreeableness', 'Altruism', 'Cooperation', 'Modesty', 'Morality',
       'Sympathy', 'Trust', 'Conscientiousness', 'Achievement striving',
       'Cautiousness', 'Dutifulness', 'Orderliness', 'Self-discipline',
       'Self-efficacy', 'Extraversion', 'Activity level', 'Assertiveness',
       'Cheerfulness', 'Excitement-seeking', 'Friendliness',
       'Gregariousness', 'Neuroticism', 'Anger', 'Anxiety', 'Depression',
       'Immoderation', 'Self-consciousness', 'Vulnerability', 'Openness',
       'Adventurousness', 'Artistic interests', 'Emotionality',
       'Imagination', 'Intellect', 'Liberalism', 'Liberty', 'Ideal',
       'Love', 'Practicality', 'Self-expression', 'Stability', 'Structure',
       'Challenge', 'Closeness', 'Curiosity', 'Excitement', 'Harmony',
       'Conservation', 'Hedonism', 'Openness to change',
       'Self-enhancement', 'Self-transcendence']
    # Convert the response text to pandas data frame
    insights_df = pd.read_csv(StringIO(pi_response.text))
    # Retain only the considered features
    insights_df_sub = insights_df[features]
    
    
    # Load the pre-trained model
    with open(model_filename, 'rb') as fid:
        clf_RF = pickle.load(fid)
    
    # Evaluate the model on current personality insights
    predicted_GPA = clf_RF.predict(insights_df_sub)
    
    return predicted_GPA[0]