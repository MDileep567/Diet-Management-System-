from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the food dataset
data_path = r"C:\Users\LENOVO\Downloads\perfect_dataset_for_my_project.xlsx"
df = pd.read_excel(data_path)

# Nutrient requirements based on BMI category,

bmi_nutrient_requirements = {
    'Underweight': {'Calories': 2500, 'Fats': 70, 'Proteins': 90, 'Iron': 18, 'Calcium': 1300, 'Sodium': 2300, 'Potassium': 4700, 'Carbohydrates': 350, 'Fibre': 30, 'Vitamin D': 20, 'Sugars': 50},
    'Normal': {'Calories': 2000, 'Fats': 65, 'Proteins': 75, 'Iron': 15, 'Calcium': 1000, 'Sodium': 2300, 'Potassium': 4700, 'Carbohydrates': 300, 'Fibre': 25, 'Vitamin D': 15, 'Sugars': 40},
    'Overweight': {'Calories': 1800, 'Fats': 60, 'Proteins': 70, 'Iron': 12, 'Calcium': 1000, 'Sodium': 2000, 'Potassium': 4500, 'Carbohydrates': 250, 'Fibre': 20, 'Vitamin D': 15, 'Sugars': 35},
    'Obese': {'Calories': 1600, 'Fats': 55, 'Proteins': 65, 'Iron': 10, 'Calcium': 1200, 'Sodium': 1800, 'Potassium': 4300, 'Carbohydrates': 200, 'Fibre': 15, 'Vitamin D': 15, 'Sugars': 30}
}

# Calculate BMI
def calculate_bmi(weight, height):
    height_m = height / 100  # Convert height to meters
    return round(weight / (height_m ** 2), 2)

# Determine BMI category
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

# Calculate user nutrient intake
def calculate_user_intake(food_log):
    user_intake = {nutrient: 0 for nutrient in next(iter(bmi_nutrient_requirements.values())).keys()}
    
    for entry in food_log:
        if ":" in entry:
            try:
                food_item, quantity = entry.split(":")
                quantity = float(quantity.strip())
                food_item = food_item.strip()
                
                if food_item in df['Food Item'].values:
                    food_data = df[df['Food Item'] == food_item].iloc[0]
                    for nutrient in user_intake.keys():
                        user_intake[nutrient] += food_data.get(nutrient, 0) * quantity
            except ValueError:
                continue  # Ignore invalid input
    return user_intake

# Calculate deficiencies (showing intake vs. target)
def calculate_deficiencies(bmi_category, user_intake):
    target_intake = bmi_nutrient_requirements[bmi_category]
    deficiencies = {}
    
    for nutrient, target in target_intake.items():
        actual = user_intake.get(nutrient, 0)
        deficiencies[nutrient] = {"intake": round(actual, 2), "target": target}
    
    return deficiencies

# Recommend foods based on deficiencies
def recommend_foods(deficiencies):
    recommendations = {}
    for nutrient, values in deficiencies.items():
        if values["intake"] < values["target"] and nutrient in df.columns:
            suitable_foods = df[df[nutrient] > 0][['Food Item', nutrient]].sort_values(by=nutrient, ascending=False)
            recommendations[nutrient] = suitable_foods.head(3).to_dict('records')
    return recommendations

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/input", methods=["POST"])
def input_page():
    try:
        name = request.form.get("name")
        height = float(request.form.get("height"))
        weight = float(request.form.get("weight"))
        gender = request.form.get("gender")
        age = int(request.form.get("age"))
        profession = request.form.get("profession")
        food_log = request.form.get("food_log").strip().split(",")

        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)

        user_intake = calculate_user_intake(food_log)
        deficiencies = calculate_deficiencies(bmi_category, user_intake)
        recommendations = recommend_foods(deficiencies)

        return render_template(
            "results.html",
            name=name,
            bmi=bmi,
            bmi_category=bmi_category,
            deficiencies=deficiencies,
            recommendations=recommendations
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

if __name__ == "__main__":
    app.run(debug=True)
