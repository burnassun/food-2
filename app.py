from flask import Flask, request, jsonify
from datetime import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

submitted_names = []  # Temporary storage for submitted names.

# Accept names from the frontend.
@app.route('/submit-name', methods=['POST'])
def submit_name():
    allowed_times = [
        {'day': 3, 'start': 6, 'end': 19},  # Thursday: 6 AM to 7 PM.
        {'day': 5, 'start': 20, 'end': 35}  # Saturday 8 PM to Sunday 11 AM.
    ]
    now = datetime.now()
    current_day = now.weekday()
    current_hour = now.hour

    # Check if submissions are allowed.
    if not any(
        time['day'] == current_day and time['start'] <= current_hour <= time['end']
        for time in allowed_times
    ):
        return jsonify({"status": "error", "message": "Submissions are closed."}), 403

    # Save the name.
    data = request.get_json()
    name = data.get('name')
    if name in submitted_names:
        return jsonify({"status": "error", "message": "Name already submitted."}), 400

    submitted_names.append(name)
    return jsonify({"status": "success", "message": "Name submitted successfully!"})

# Generate pairs and send a PDF.
@app.route('/generate-pairs', methods=['POST'])
def generate_pairs():
    if not submitted_names:
        return jsonify({"status": "error", "message": "No names to pair."}), 400

    pairs = []
    for i in range(0, len(submitted_names), 2):
        pair = submitted_names[i:i + 2]
        if len(pair) == 2:
            pairs.append(f"{pair[0]} - {pair[1]}")
        else:
            pairs.append(f"{pair[0]} - No Match")

    # Write pairs to a PDF.
    pdf_content = "\n".join(pairs)
    with open("pairs.pdf", "w") as f:
        f.write(pdf_content)

    # Send the PDF via email.
    send_email("pairs.pdf")
    return jsonify({"status": "success", "message": "Pairs generated and emailed!"})

def send_email(file_path):
    msg = EmailMessage()
    msg['Subject'] = "Paired Names"
    msg['From'] = "your_email@example.com"
    msg['To'] = "your_email@example.com"

    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='pairs.pdf')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("your_email@example.com", "your_password")
        smtp.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)
