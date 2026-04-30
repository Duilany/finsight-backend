import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def format_rupiah(value):
    return f"Rp{int(value):,}".replace(",", ".")


def generate_insight(data, analysis):
    income = data['income']
    expenses = data['expenses']
    savings = analysis['savings']
    total_expense = analysis['total_expense']

    # 🔥 VALIDASI
    if income == 0:
        return {
            "insight": "Pendapatan tidak boleh 0.",
            "profile": "Unknown"
        }

    # 🔥 HITUNG
    saving_rate = (savings / income) * 100

    if isinstance(saving_rate, float) and saving_rate.is_integer():
        saving_rate = int(saving_rate)
    else:
        saving_rate = round(saving_rate, 1)

    saving_10 = int(income - (total_expense * 0.9))
    saving_20 = int(income - (total_expense * 0.8))

    # 🔥 PERSONALIZATION PROFILE
    if saving_rate >= 40:
        profile = "Frugal Saver"
    elif saving_rate >= 20:
        profile = "Balanced Spender"
    else:
        profile = "High Spender"

    # 🔥 PROMPT
    prompt = f"""
You are an AI Financial Coach for users.

Analyze the following financial data:

Income: {format_rupiah(income)}
Expenses:
- Food: {format_rupiah(expenses['food'])}
- Transport: {format_rupiah(expenses['transport'])}
- Entertainment: {format_rupiah(expenses['entertainment'])}
Total Expense: {format_rupiah(total_expense)}
Savings: {format_rupiah(savings)}

Additional Data (MUST BE USED):
- Saving rate: {saving_rate}%
- Simulation 10%: {format_rupiah(saving_10)}
- Simulation 20%: {format_rupiah(saving_20)}

Your tasks:
1. Evaluate financial condition (Healthy / Moderate / Needs Improvement)
2. Identify main problems (specific, not generic)
3. Explain saving rate (DO NOT recalculate)
4. Provide 3–5 CONCRETE & ACTIONABLE recommendations
5. Explain simulation impact (DO NOT recalculate)

Rules:
- DO NOT recalculate numbers
- Use only provided data
- Use English
- Use bullet points
- Avoid generic advice
- Be specific (e.g., percentages, not vague suggestions)

REQUIRED FORMAT:

1. Financial Condition:
- ...

2. Main Issues:
- ...
- ...

3. Saving Rate:
- ...

4. Recommendations:
- ...
- ...
- ...

5. Simulation:
- If expenses decrease by 10% → ...
- If expenses decrease by 20% → ...
"""

    # 🔥 CALL AI + ERROR HANDLING
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Kamu adalah financial advisor profesional yang fokus pada insight praktis, akurat, dan actionable."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        insight_text = response.choices[0].message.content

    except Exception as e:
        print("ERROR AI:", str(e))
        insight_text = "Terjadi kesalahan saat menghasilkan insight. Silakan coba lagi."

    return {
        "insight": insight_text,
        "profile": profile
    }