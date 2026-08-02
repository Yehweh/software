from data_loader import load_data
from rule_engine import detect_technical_debt

def main():

    data = load_data()

    print("\n========== Technical Debt Analysis ==========\n")

    high = 0
    medium = 0
    low = 0

    for i in range(10):

        result = detect_technical_debt(data.iloc[i])

        print(f"\nSoftware Record {i+1}")
        print(f"Debt Score : {result['Debt Score']}/100")
        print(f"Debt Level : {result['Debt Level']}")

        print("Reasons:")
        for reason in result["Reasons"]:
            print(f" - {reason}")

        print("-" * 40)

        if result["Debt Level"] == "High Technical Debt":
            high += 1
        elif result["Debt Level"] == "Medium Technical Debt":
            medium += 1
        else:
            low += 1

    print("\n========== Summary ==========")
    print(f"Total Records Analysed : 10")
    print(f"High Technical Debt    : {high}")
    print(f"Medium Technical Debt  : {medium}")
    print(f"Low Technical Debt     : {low}")
    print("=============================")


if __name__ == "__main__":
    main()