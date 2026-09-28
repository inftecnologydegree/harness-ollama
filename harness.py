import ollama

# 1. System instruction acts as the rigid guardrail for the model's behavior
SYSTEM_PROMPT = """
You are a strict security code reviewer agent. 
Analyze the code provided by the user. 
List any potential flaws and provide a secure fix.
Keep your answer brief, objective, and structured.
"""

# 2. Mimic an incoming user request (e.g., a vulnerable code snippet)
user_code = """
def login(username, password):
    # Vulnerable SQL execution
    query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
    return execute_sql(query)
"""

print("--- Sending task to local model ---")

# 3. Execute the payload through your local API server
response = ollama.chat(
    model='llama3.2:3b',
    messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f"Review this code:\n{user_code}"}
    ]
)

# 4. Display the output captured by your harness
print("\n--- Agent Response ---")
print(response['message']['content'])
