import os
import sys
import json
from openai import OpenAI

def run_test():
    # Make sure we read GROQ_API_KEY
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.")
        sys.exit(1)
        
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    # We will use llama-3.1-8b-instant for text connectivity test
    model_name = "llama-3.1-8b-instant"
    prompt = 'Return ONLY: {"status":"connected"}'
    
    print(f"Connecting to Groq using model: {model_name}...")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        output = response.choices[0].message.content.strip()
        print("Connection successful! Response received:")
        print(output)
        
        # Save results to evaluation/groq_connection_test.md
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "groq_connection_test.md")
        
        md_content = f"""# Groq Connectivity Test Results

## Configuration
- **Model:** {model_name}
- **Status:** Connected successfully

## Response
```json
{output}
```
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Results saved to {output_path}")
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
