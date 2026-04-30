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
Kamu adalah AI Financial Coach untuk pengguna di Indonesia.

Analisis data berikut:

Pendapatan: {format_rupiah(income)}
Pengeluaran:
- Makanan: {format_rupiah(expenses['food'])}
- Transportasi: {format_rupiah(expenses['transport'])}
- Hiburan: {format_rupiah(expenses['entertainment'])}
Total Pengeluaran: {format_rupiah(total_expense)}
Tabungan: {format_rupiah(savings)}

Data tambahan (WAJIB DIGUNAKAN):
- Saving rate: {saving_rate}%
- Simulasi 10%: {format_rupiah(saving_10)}
- Simulasi 20%: {format_rupiah(saving_20)}

Tugas kamu:
1. Evaluasi kondisi keuangan (Sehat / Cukup / Perlu Perbaikan)
2. Identifikasi masalah utama (spesifik)
3. Jelaskan saving rate (JANGAN menghitung ulang)
4. Berikan 3–5 rekomendasi KONKRET
5. Jelaskan simulasi (JANGAN menghitung ulang)

Aturan:
- DILARANG menghitung ulang angka
- Gunakan angka yang diberikan saja
- Gunakan Bahasa Indonesia
- Gunakan bullet point
- Hindari saran umum

Format WAJIB:

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