import os
import json
import ollama

# --- 1. DEFINE ACTUAL SYSTEM TOOLS ---
def read_local_file(filepath: str) -> str:
    """Reads content from a local file safely."""
    try:
        # Standard safety check: don't break out of the directory context
        if ".." in filepath or os.path.isabs(filepath):
            return "Error: Access denied. Stay inside the current working directory."
        
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- 2. DEFINE THE SCHEMAS WE PASS TO THE AI ---
tools_schema = [
    {
        'type': 'function',
        'function': {
            'name': 'read_local_file',
            'description': 'Reads the plain text contents of a file in the workspace directory.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'filepath': {
                        'type': 'string',
                        'description': 'The relative path or name of the file to open (e.g., source.py)',
                    }
                },
                'required': ['filepath'],
            },
        },
    }
]

# --- 3. SYSTEM INSTRUCTIONS (THE CAGE) ---
SYSTEM_PROMPT = """
You are an AI engineering agent with file access.
Your primary objective is to inspect workspace files for vulnerabilities using your tools.
When you need to read a file, call the 'read_local_file' function tool.
Once you have read the file contents, analyze it and present your security report to the user.
"""

# Create a sample target file for the agent to inspect
target_filename = "app_code.py"
with open(target_filename, "w") as f:
    f.write("def calculate_admin_hash(salt):\n    password = input('Enter key:')\n    return salt + password\n")

# --- 4. THE EXECUTION TURN LOOP ---
messages = [
    {'role': 'system', 'content': SYSTEM_PROMPT},
    {'role': 'user', 'content': f"Check the file named '{target_filename}' for any security flaws."}
]

print("--- Starting Agent Core Execution Loop ---")

# We loop up to 3 times to allow the model to think, call tools, and respond
for turn in range(3):
    print(f"\n[Turn {turn + 1}] Processing model intent...")
    
    response = ollama.chat(
        model='llama3.2:3b',
        messages=messages,
        tools=tools_schema # Pass the structural tools option to Ollama
    )
    
    # Save the agent's response to maintain conversational context memory
    messages.append(response['message'])
    
    # Check if the model decided to call our tool function
    if response['message'].get('tool_calls'):
        for tool_call in response['message']['tool_calls']:
            function_name = tool_call['function']['name']
            arguments = tool_call['function']['arguments']
            
            print(f"👉 Agent called tool: {function_name} with args: {arguments}")
            
            # Execute the underlying Python tool code
            if function_name == "read_local_file":
                tool_output = read_local_file(arguments['filepath'])
                
                # Append the exact result back to the context string array
                messages.append({
                    'role': 'tool',
                    'name': function_name,
                    'content': tool_output
                })
                print(f"✅ Executed tool successfully. Fed payload back to agent.")
    else:
        # If no tool calls are pending, the agent has delivered its final response text
        print("\n--- Final Agent Analysis Complete ---")
        print(response['message']['content'])
        break

# Clean up sample file
if os.path.exists(target_filename):
    os.remove(target_filename)
