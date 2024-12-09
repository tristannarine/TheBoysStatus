from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Load existing statuses from the JSON file
def load_statuses():
    try:
        with open('data/statuses.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save statuses to the JSON file
def save_statuses(statuses):
    with open('data/statuses.json', 'w') as file:
        json.dump(statuses, file, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        activity = request.form.get('activity')
        with_persons = request.form.get('with')

        # Check if a status with the same name already exists
        statuses = load_statuses()
        existing_status = next((status for status in statuses if status['name'] == name), None)

        if existing_status:
            # Remove the first occurrence if the same name is entered again
            statuses = [status for status in statuses if status['name'] != name]

        new_status = {
            'name': name,
            'activity': activity,
            'with': with_persons if with_persons else None  # Only include 'with' if provided
        }

        statuses.append(new_status)
        save_statuses(statuses)
        return redirect(url_for('index'))

    statuses = load_statuses()
    return render_template('index.html', statuses=statuses)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
