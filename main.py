from data.fetch_data import get_match_data
from agents.insight_agent import analyze_match
from agents.commentary_agent import generate_commentary
from agents.prediction_agent import predict_winner
import time


def main():
    print("🏏 Starting AI Cricket Live System...\n")

    while True:
        try:
            print("\n==============================")
            print("📡 Fetching match data...")

            data = get_match_data()

            print("🧠 Analyzing match...")
            insights = analyze_match(data)

            if "error" in insights:
                print("❌ Error:", insights["error"])
                break

            print("🎙️ Generating commentary...")
            commentary = generate_commentary(insights)

            print("📊 Predicting winner...")
            prediction = predict_winner(insights)

            # 🖥️ Output
            print("\n🏟️ MATCH:")
            print(f"{insights['team1']} vs {insights['team2']}")

            print("\n📊 SCORE:")
            print(f"{insights['team1']}: {insights['score1']}")
            print(f"{insights['team2']}: {insights['score2']}")

            print("\n📌 STATUS:")
            print(insights["status"])

            print("\n🔥 LIVE COMMENTARY:\n")
            print(commentary)

            print("\n📈 PREDICTION:\n")
            print(prediction)

            # ⏱️ Refresh every 30 sec
            print("\n⏳ Refreshing in 30 seconds...\n")
            time.sleep(30)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            break

        except Exception as e:
            print("\n⚠️ Unexpected Error:", str(e))
            print("Retrying in 20 seconds...")
            time.sleep(20)


if __name__ == "__main__":
    main()