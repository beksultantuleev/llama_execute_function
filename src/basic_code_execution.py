import requests

# Define the IP and port of the remote machine hosting the LLaMA model
server_url = "http://192.168.88.106:11434/api/generate"

# Define a prompt for code generation
function_name = 'summation'
prompt = f"""
# Write a Python function to calculate the sumation of a number from 1 to 15
def {function_name}():
"""

# Create the request payload
payload = {
    "prompt": prompt,
    "model": "llama3",
    'stream': False,
    "max_tokens": 50,
    "temperature": 0.7
}

# Send the request to the remote LLaMA model
response = requests.post(server_url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    try:
        # Extract the generated response
        generated_response = response.json().get('response', '')
        
        # Extract the code block from the response
        import re
        code_block = re.search(r'```(.*?)```', generated_response, re.DOTALL)
        
        if code_block:
            generated_code = code_block.group(1).strip()
            print(f"Generated Code:\n{generated_code}")

            # Prepare the environment for exec
            exec_locals = {}

            # Execute the generated code in exec_locals
            exec(generated_code, globals(), exec_locals)

            # Test the generated function (assuming the function is named 'xxx')
            if function_name in exec_locals:
                function_to_execute = exec_locals[function_name]
                print(function_to_execute()) 
            else:
                print(f"Generated code does not define '{function_name}' function.")
        else:
            print("No code block found in the response.")
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
else:
    print(f"Failed to generate code. Status code: {response.status_code}")
    print(response.text)
