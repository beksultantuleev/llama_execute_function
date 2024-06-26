import requests
import pandas as pd

# Create a DataFrame with SMS messages
data = {
    'SMS': [
        # "I'm very interested in learning more about your loan options.",
        # "I need a loan for my new business venture. How can I apply?",
        # "Can you provide details on your loan interest rates?",
        # "I'm not interested in any loans at this moment.",
        # "I don't need any financial services right now."
        "your code is 5654.",
        "Верни пожалуйста деньги",
        'ваш кредит одобрен в банке'
    ]
}

df = pd.DataFrame(data)
print(df)
print(df.shape)


# Define the IP and port of the remote machine hosting the LLaMA model
server_url = "http://192.168.88.106:11434/api/generate"

# Define the classification task prompt
prompt_template = """
# Text Classification
# Classify the following SMS messages as 'interested' or 'not interested' in obtaining loans. 
# Text could be in russian. 
# Please do not write reasoning and just provide labels all in lower caps.

SMS: "{}"
Label:
"""

# Function to classify messages using LLaMA
def classify_sms(messages, server_url):
    labels = []
    
    for sms in messages:
        prompt = prompt_template.format(sms)
        
        # Create the request payload
        payload = {
            "prompt": prompt,
            "model": "llama3",
            'stream': False,
            "max_tokens": 10,
            "temperature": 0.7
        }
        
        # Send the request to the remote LLaMA model
        response = requests.post(server_url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Extract the generated label
                generated_response = response.json().get('response', '').strip()
                
                # Extract the label from the response
                label = generated_response.split('\n')[-1].strip()
                labels.append(label)
            except requests.exceptions.JSONDecodeError as e:
                print(f"Failed to decode JSON response: {e}")
                labels.append("unknown")
        else:
            print(f"Failed to generate label. Status code: {response.status_code}")
            labels.append("unknown")
    
    return labels

# Classify the messages in the DataFrame
df['Label'] = classify_sms(df['SMS'], server_url)
print(df)
