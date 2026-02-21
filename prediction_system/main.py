import os
from datetime import datetime
from dotenv import load_dotenv
from google.genai import Client



load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = Client(api_key=api_key)



def convert_to_minutes(duration_str):
    try:
        duration_str = duration_str.lower().replace(" ", "")
        hours, minutes = duration_str.split("h")
        minutes = minutes.replace("m", "")
        return int(hours) * 60 + int(minutes)
    except Exception:
        raise ValueError(f"Invalid duration format: {duration_str}")


def format_hours(minutes):
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m"


def calculate_sleep_score(avg_minutes):
    IDEAL = 480
    deviation = abs(avg_minutes - IDEAL)
    penalty = min((deviation / IDEAL) * 100, 100)
    score = max(100 - penalty, 0)
    return round(score, 1)


def detect_sleep_pattern(minute_values):
    if len(minute_values) < 2:
        return "Insufficient Data"

    trend_change = minute_values[-1] - minute_values[0]
    variability = max(minute_values) - min(minute_values)

    if variability < 45:
        return "Consistent Sleep Pattern"
    elif trend_change > 30:
        return "Improving Sleep Habit"
    elif trend_change < -30:
        return "Declining Sleep Habit"
    else:
        return "Irregular Sleep Pattern"



def analyze_sleep(data):
    minute_values = []

    for entry in data:
        duration = entry.get("total_duration") or entry.get("average_duration")
        if not duration:
            continue
        minute_values.append(convert_to_minutes(duration))

    if not minute_values:
        raise ValueError("No valid sleep duration data found.")

    avg = sum(minute_values) / len(minute_values)

    return {
        "average_minutes": avg,
        "min_minutes": min(minute_values),
        "max_minutes": max(minute_values),
        "trend_change": minute_values[-1] - minute_values[0],
        "pattern": detect_sleep_pattern(minute_values),
    }



def sleep_deficit_engine(avg_minutes):
    IDEAL_SLEEP = 480
    deficit = IDEAL_SLEEP - avg_minutes

    if deficit > 90:
        severity = "Severe"
    elif deficit > 45:
        severity = "Moderate"
    elif deficit > 0:
        severity = "Mild"
    else:
        severity = "Healthy"

    return {
        "deficit_minutes": max(deficit, 0),
        "severity": severity,
    }



def generate_ai_advice(stats, deficit_data, sleep_score):

    severity = deficit_data["severity"]
    trend = stats["pattern"]

    prompt = f"""
You are an intelligent adaptive sleep health coach.

User Sleep Data:
- Average Sleep: {stats['average_minutes']/60:.2f} hours
- Minimum Sleep: {stats['min_minutes']/60:.2f} hours
- Maximum Sleep: {stats['max_minutes']/60:.2f} hours
- Sleep Score: {sleep_score}%
- Trend Pattern: {trend}
- Severity Level: {severity}

TASK:

1. Write a professional Summary paragraph (2–4 sentences).
   - Mention actual numeric values (like sleep score or hours).
   - Explain health impact.
   - Adjust tone based on severity.

2. Write a Recommendation paragraph (2–4 sentences).
   - Personalize advice based on severity and trend.
   - If severe → strong corrective tone.
   - If improving → encouraging tone.
   - If healthy → reinforcement tone.
   - Use natural paragraph style (NOT bullet points).

FORMAT:

Summary:
<paragraph>

Recommendation:
<paragraph>
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            config={
                "temperature": 0.6,  # 🔥 more creative / dynamic
                "max_output_tokens": 350,
                "system_instruction":
                "You must personalize output using numeric values provided. Avoid generic statements."
            }
        )

        raw = response.text.strip()

        if "Recommendation:" in raw:
            parts = raw.split("Recommendation:")
            summary = parts[0].replace("Summary:", "").strip()
            recommendation = parts[1].strip()
        else:
            # only if model completely breaks
            summary = raw
            recommendation = "Consider improving sleep duration and consistency."

        return {
            "summary": summary,
            "recommendation": recommendation
        }

    except Exception:
        return {
            "summary": "Sleep data indicates imbalance that may affect recovery and daily performance.",
            "recommendation": "Focus on structured sleep improvements."
        }


def generate_data_summary(stats, deficit_data, sleep_score):

    avg_hours = stats["average_minutes"] / 60
    severity = deficit_data["severity"]

    if sleep_score < 40:
        condition = "critically low"
    elif sleep_score < 70:
        condition = "below recommended"
    elif sleep_score < 90:
        condition = "fair but could improve"
    else:
        condition = "within healthy range"

    summary = (
        f"Your average sleep duration is {avg_hours:.2f} hours, resulting in a sleep score of {sleep_score}%. "
        f"This places your sleep quality in the {condition} category. "
        f"The detected pattern is '{stats['pattern']}', which indicates overall sleep stability status."
    )

    return summary


def sleep_prediction_pipeline(user_data):

    stats = analyze_sleep(user_data)
    deficit_data = sleep_deficit_engine(stats["average_minutes"])
    sleep_score = calculate_sleep_score(stats["average_minutes"])

    trend_direction = (
        "Improving ⬆"
        if stats["trend_change"] > 0
        else "Declining ⬇"
        if stats["trend_change"] < 0
        else "Stable ➖"
    )

    # NEW: Deterministic data summary
    data_summary = generate_data_summary(stats, deficit_data, sleep_score)

    # AI Personal Advice
    ai_response = generate_ai_advice(stats, deficit_data, sleep_score)

    # Final merged recommendation
    final_recommendation = (
        f"{ai_response['recommendation']} "
        "Consistency and gradual improvement remain key to restoring healthy sleep balance."
    )

    return {
        "generated_at": datetime.utcnow().isoformat(),

        "statistics": {
            "average_sleep": format_hours(stats["average_minutes"]),
            "minimum_sleep": format_hours(stats["min_minutes"]),
            "maximum_sleep": format_hours(stats["max_minutes"]),
            "trend": {
                "direction": trend_direction,
                "change": format_hours(abs(stats["trend_change"]))
            },
            "sleep_pattern": stats["pattern"],
            "sleep_score_percent": sleep_score,
            "sleep_grade": (
                "Excellent" if sleep_score >= 95 else
                "Good" if sleep_score >= 80 else
                "Moderate" if sleep_score >= 60 else
                "Poor"
            ),
        },

        # NEW SECTION
        "data_summary": data_summary,

        "ai_analysis": {
            "summary": ai_response["summary"],
            "recommendation": ai_response["recommendation"]
        },

        "final_recommendation": final_recommendation
    }

