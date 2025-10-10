import sys
import json

# This function reads the JSON data that n8n sends to the script
def get_n8n_input():
    try:
        # sys.stdin is the "inbox" where n8n's data arrives
        line = sys.stdin.readline()
        return json.loads(line)
    except:
        # If n8n sends bad data, return an error message
        return {"error": "Invalid or missing JSON input from n8n."}

# This is the main part of your script
if __name__ == '__main__':
    # 1. Get the data from the n8n webhook
    input_data = get_n8n_input()

    # --- YOUR SMS LOGIC GOES HERE ---
    # This is where you would use the data to send an actual SMS
    # using a service like Twilio, Vonage, etc.
    
    # We safely get the phone number and message from the input data
    to_number = input_data.get("phone_number", None)
    message_body = input_data.get("message", "This is a test message from n8n.")

    # For now, we will just prepare a success message.
    # In a real script, you would add your API call here.
    # Example: send_sms(to_number, message_body)
    
    if to_number:
        status_message = f"SMS prepared for {to_number}."
        final_status = "success"
    else:
        status_message = "Error: No phone_number was provided in the webhook data."
        final_status = "error"
    
    # --- END OF YOUR LOGIC ---

    # 2. Prepare the result to send back to n8n
    output_data = {
        "status": final_status,
        "detail": status_message
    }

    # 3. Print the result as a JSON string.
    # This sends the data back to n8n through the "outbox" (stdout).
    print(json.dumps(output_data))
