def predict_winner(insights):
    try:
        team1 = insights["team1"]
        team2 = insights["team2"]
        score_text = insights["score1"]

        runs = int(score_text.split("/")[0])

        if "target" in score_text:
            target = int(score_text.split("target")[1].strip().replace(")", ""))
            runs_needed = target - runs

            # ✅ MATCH FINISHED
            if runs_needed <= 0:
                return f"🏆 {team1} WON the match!"

            # Extract overs
            overs_part = score_text.split("(")[1].split("/")[0]
            over, ball = overs_part.split(".")
            balls_bowled = int(over) * 6 + int(ball)

            balls_left = 120 - balls_bowled

            if balls_left <= 0:
                return f"🏆 {team2} defended successfully!"

            req_rr = (runs_needed / balls_left) * 6

            if req_rr > 12:
                return f"🔥 {team2} in control (RR: {req_rr:.2f})"
            elif req_rr > 8:
                return f"⚠️ Tight game (RR: {req_rr:.2f})"
            else:
                return f"✅ {team1} in strong position (RR: {req_rr:.2f})"

        return "📊 Match prediction in progress..."

    except:
        return "📊 Prediction unavailable."