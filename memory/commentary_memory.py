commentary_history = []

def add_commentary(text):
    if not commentary_history or text != commentary_history[-1]:
        commentary_history.append(text)
        if len(commentary_history) > 10:
            commentary_history.pop(0)

def get_history():
    return commentary_history[-3:]