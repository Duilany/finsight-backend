def analyze_financial(data):
    income = data["income"]
    expenses = data["expenses"]

    total_expense = sum(expenses.values())
    savings = income - total_expense

    breakdown = {
        k: round((v / income) * 100, 2)
        for k, v in expenses.items()
    }

    return {
        "total_expense": total_expense,
        "savings": savings,
        "breakdown": breakdown
    }