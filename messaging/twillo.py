from twilio.rest import Client
import json

# Step 1: Load JSON message
with open("../data/tji_daily_message.json", "r") as f:
    data = json.load(f)
    message_body = data["drafted_message"]

# Step 2: Twilio credentials (replace with your actual values)
account_sid = "AC185a7783037edc716eaff3ca28a5993c"
auth_token = "a48df63098f045e09f4db5ce5c881207"
client = Client(account_sid, auth_token)

# Step 3: Send WhatsApp message
message = client.messages.create(
    from_="whatsapp:+14155238886",  # Twilio sandbox number
    to="whatsapp:+918179399260",    # Your verified WhatsApp number
    body=message_body
)

print(f"Message sent! SID: {message.sid}")

