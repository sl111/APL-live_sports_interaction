import requests

def get_ball_by_ball(event_id):
    try:
        # ESPN ball-by-ball API
        url = f"https://site.api.espn.com/apis/site/v2/sports/cricket/8048/summary?event={event_id}"
        
        response = requests.get(url)
        data = response.json()

        # Get commentary section
        commentary_data = data.get("commentary", [])

        timeline = []

        # Take last 15 balls/events
        for item in commentary_data[-15:]:
            over = item.get("over", "")
            text = item.get("text", "")

            if over and text:
                timeline.append(f"{over} - {text}")

        return timeline

    except Exception as e:
        return ["No live commentary available"]