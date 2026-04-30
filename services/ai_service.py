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
You are an AI Financial Coach for users in Indonesia.

Kamu adalah AI Financial Coach untuk pengguna di Indonesia.

Analyze the following financial data / Analisis data berikut:

Income / Pendapatan: {format_rupiah(income)}

Expenses / Pengeluaran:
- Food / Makanan: {format_rupiah(expenses['food'])}
- Transport / Transportasi: {format_rupiah(expenses['transport'])}
- Entertainment / Hiburan: {format_rupiah(expenses['entertainment'])}

Total Expense / Total Pengeluaran: {format_rupiah(total_expense)}
Savings / Tabungan: {format_rupiah(savings)}

Additional Data (MUST BE USED / WAJIB DIGUNAKAN):
- Saving rate: {saving_rate}%
- Simulation 10% / Simulasi 10%: {format_rupiah(saving_10)}
- Simulation 20% / Simulasi 20%: {format_rupiah(saving_20)}

Your Tasks / Tugas kamu:
1. Evaluate financial condition (Healthy / Moderate / Needs Improvement)
   Evaluasi kondisi keuangan (Sehat / Cukup / Perlu Perbaikan)

2. Identify main problems (specific, not generic)
   Identifikasi masalah utama (spesifik, jangan umum)

3. Explain saving rate (DO NOT recalculate)
   Jelaskan saving rate (JANGAN menghitung ulang)

4. Provide 3–5 CONCRETE and ACTIONABLE recommendations
   Berikan 3–5 rekomendasi KONKRET

5. Explain simulation results (DO NOT recalculate)
   Jelaskan simulasi (JANGAN menghitung ulang)

Rules / Aturan:
- DO NOT recalculate any numbers
- DILARANG menghitung ulang angka
- Use only the provided data
- Gunakan data yang diberikan saja
- Use Bahasa Indonesia as the main output language
- Gunakan Bahasa Indonesia sebagai output utama
- Use bullet points (clear and structured)
- Gunakan bullet point
- Avoid generic advice
- Hindari saran umum

STRICT FORMAT:

1. Evaluasi Kondisi Keuangan:
- ...

2. Masalah Utama:
- ...
- ...

3. Saving Rate:
- ...

4. Rekomendasi:
- ...
- ...
- ...

5. Simulasi:
- Jika pengeluaran turun 10% → ...
- Jika pengeluaran turun 20% → ...
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