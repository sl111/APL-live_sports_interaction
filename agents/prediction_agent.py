def predict_winner(insights):
    try:
        team1 = insights["team1"]
        team2 = insights["team2"]
        score_text = insights["score1"]
        
        if "Yet to bat" in score_text:
            return "📊 Match yet to start..."

        runs = int(score_text.split("/")[0])

        if "target" in score_text:
            target = int(score_text.split("target")[1].strip().replace(")", ""))
            runs_needed = target - runs

            if runs_needed <= 0: return f"🏆 {team1} WON!"

            overs_part = score_text.split("(")[1].split("/")[0]
            over_parts = overs_part.split(".")
            over = int(over_parts[0])
            ball = int(over_parts[1]) if len(over_parts) > 1 else 0
            
            balls_left = 120 - (over * 6 + ball)
            if balls_left <= 0: return f"🏆 {team2} WON (Defended)!"
            
            req_rr = (runs_needed / balls_left) * 6
            return f"🔥 {team2} leading (RR: {req_rr:.2f})" if req_rr > 12 else f"✅ {team1} cruising (RR: {req_rr:.2f})"

        # 1st Innings
        if "(" in score_text:
            overs_part = score_text.split("(")[1].split("/")[0]
            over_parts = overs_part.split(".")
            over = int(over_parts[0])
            ball = int(over_parts[1]) if len(over_parts) > 1 else 0
            
            balls_bowled = over * 6 + ball
            if balls_bowled > 0:
                crr = (runs / balls_bowled) * 6
                projected = int(crr * 20)
                return f"📈 Projected: {projected} (CRR: {crr:.2f})"
        
        return "📊 Match just started..."

    except:
        return "📊 Analytics loading..."