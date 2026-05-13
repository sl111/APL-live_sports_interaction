def analyze_match(data):
    try:
        if not data or "events" not in data or not data["events"]:
            return {"error": "No match data available"}

        event = data["events"][0]
        comp = event["competitions"][0]
        teams = comp["competitors"]

        team1 = teams[0]["team"]["name"]
        team2 = teams[1]["team"]["name"]
        team1_short = teams[0]["team"].get("abbreviation", team1[:3].upper())
        team2_short = teams[1]["team"].get("abbreviation", team2[:3].upper())

        score1 = teams[0].get("score") or "Yet to bat"
        score2 = teams[1].get("score") or "Yet to bat"

        # Fallback logo (Placeholder)
        placeholder = "https://a.espncdn.com/combiner/i?img=/i/teamlogos/cricket/500/default.png"
        team1_logo = teams[0]["team"].get("logo") or placeholder
        team2_logo = teams[1]["team"].get("logo") or placeholder

        state = comp["status"]["type"]["state"] # 'pre', 'in', 'post'
        date = event.get("date")

        # Determine winner
        winner_name = None
        if state == "post":
            winner_name = team1 if teams[0].get("winner") else team2 if teams[1].get("winner") else None

        # Extract detailed status/result
        status = comp["status"]["type"].get("detail") or comp["status"]["type"].get("shortDetail") or comp["status"]["type"].get("description")
        
        if comp.get("notes"):
            status = comp["notes"][0].get("headline", status)
        
        # If it just says 'Final', make it more descriptive
        if status.lower() == "final" and winner_name:
            status = f"{winner_name} won"
            
        venue = comp.get("venue", {}).get("fullName", "Unknown Venue")

        return {
            "team1": team1,
            "team2": team2,
            "team1_short": team1_short,
            "team2_short": team2_short,
            "team1_logo": team1_logo,
            "team2_logo": team2_logo,
            "score1": score1,
            "score2": score2,
            "status": status,
            "state": state,
            "winner_name": winner_name,
            "venue": venue,
            "date": date
        }

    except Exception as e:
        return {"error": f"Analysis Error: {str(e)}"}