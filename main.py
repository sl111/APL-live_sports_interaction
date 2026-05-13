from data.fetch_data import get_match_data
from agents.insight_agent import analyze_match
from agents.commentary_agent import generate_commentary
from agents.prediction_agent import predict_winner

def main():
    print("📡 Fetching match data...")
    data = get_match_data()

    print("🧠 Analyzing match...")
    insights = analyze_match(data)

    if "error" in insights:
        print("Error:", insights["error"])
        return

    print("🎙️ Generating commentary...")
    commentary = generate_commentary(insights)

    print("\n🔥 LIVE COMMENTARY:\n")
    print(commentary)


if __name__ == "__main__":
    main()