from flask import Flask, render_template
from src.data_loader import load_data
from src.rule_engine import detect_technical_debt

app = Flask(__name__)

@app.route("/")
def index():

    data = load_data()

    results = []

    high = 0
    medium = 0
    low = 0

    for i in range(10):

        result = detect_technical_debt(data.iloc[i])

        results.append({
            "record": i + 1,
            "score": result["Debt Score"],
            "level": result["Debt Level"],
            "reasons": result["Reasons"]
        })

        if result["Debt Level"] == "High Technical Debt":
            high += 1
        elif result["Debt Level"] == "Medium Technical Debt":
            medium += 1
        else:
            low += 1

    return render_template(
        "index.html",
        results=results,
        high=high,
        medium=medium,
        low=low
    )


if __name__ == "__main__":
    app.run(debug=True)