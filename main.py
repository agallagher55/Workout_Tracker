"""
Using the Nutritionix "Natural Language for Exercise" API, figure out how to print the exercise stats for a plain
text input.
Q: Tell me what exercise you did? A: I ran for 15 minutes.
"""

import requests

from configparser import ConfigParser
parser = ConfigParser()
parser.read("secrets.ini")

TRACK_API_ID = parser.get('API_KEYS', 'TRACK_API_ID')
TRACK_API_KEY = parser.get('API_KEYS', 'TRACK_API_KEY')
TRACK_API_TOKEN = parser.get('API_KEYS', 'TRACK_API_TOKEN')

PROXY = parser.get('PROXIES', 'PROXY')

SHEET_ENDPOINT = 'https://api.sheety.co/56d511913289266ae6d1bc8b86685e5e/myWorkouts/workouts'

GENDER = "male"
HEIGHT_CM = "178"
AGE = "28"


def get_exercise_data():
    endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"

    user_exercise = input("\nTell me which exercise you did: ")

    headers = {
        "x-app-id": TRACK_API_ID,
        "x-app-key": TRACK_API_KEY,
        'x-remote-user-id': '0',
        'Content-Type': "application/json",
        "Authorization": f"Bearer {TRACK_API_TOKEN}"
    }

    parameters = {
        "query": user_exercise,
        "gender": GENDER,
        "height_cm": HEIGHT_CM,
        "age": AGE
    }

    response = requests.post(
        url=endpoint,
        json=parameters,
        headers=headers,
        proxies={"https": PROXY} if PROXY else dict()
    )
    response.raise_for_status()

    data = response.json()

    calories = round(data['exercises'][0]['nf_calories'], 2)
    activity = data['exercises'][0]['name']
    duration = data['exercises'][0]['duration_min']

    feedback = f"\tCongrats, you burned approx. {calories} calories while {activity}!"
    print(feedback)
    return [activity, duration, calories]


def post_workout(workout, duration, calories):
    from datetime import datetime

    print("\nPosting workout to google sheet...")

    headers = {
        'Content-Type': "application/json",
        "Authorization": f"Bearer {TRACK_API_TOKEN}"
    }
    date = datetime.now().date().strftime("%d/%m/%Y")
    time = datetime.now().time().strftime("%H:%M:%S")

    body = {
        "workout": {
            "date": str(date),  # 21/07/2020
            "time": str(time),  # 15:00:00
            "exercise": workout,
            "duration": duration,
            "calories": calories
        }
    }
    response = requests.post(
        url=SHEET_ENDPOINT,
        json=body,
        headers=headers,
        proxies={"https": PROXY} if PROXY else dict()
    )

    response.raise_for_status()


if __name__ == "__main__":
    activity, duration, calories = get_exercise_data()
    post_workout(activity, duration, calories)

