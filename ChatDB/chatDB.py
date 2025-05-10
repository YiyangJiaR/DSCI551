import pandas as pd
from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, inspect, text
from openai import OpenAI
import json

DB_URL = "mysql+pymysql://root@localhost:3306/Project"
OPENAI_API_KEY = ""
# ---------- DeepSeek configuration --------
client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")
app = Flask(__name__)
engine = create_engine(DB_URL)
inspector = inspect(engine)

# Define function schemas for OpenAI function-calling
FUNCTIONS = [
    {
        "name": "run_select",
        "description": "Executes a SQL SELECT query and returns results",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "The SELECT statement to execute"}
            },
            "required": ["sql"]
        }
    },
    {
        "name": "run_dml",
        "description": "Executes an INSERT, UPDATE, or DELETE statement and returns affected rows",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "The DML statement to execute"}
            },
            "required": ["sql"]
        }
    }
]

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/schema", methods=["GET"])
def get_schema():
    """List all tables and their columns in the database."""
    schema = {}
    for table in inspector.get_table_names():
        cols = inspector.get_columns(table)
        schema[table] = [col['name'] for col in cols]
    return jsonify(schema)

@app.route("/nl_query", methods=["POST"])
def nl_query():
    """Accepts a natural language query, translates to SQL via LLM models, executes, and returns results."""
    data = request.get_json()
    user_query = data.get("query")
    if not user_query:
        return jsonify({"error": "Missing 'query' in request"}), 400
    
    # Build the prompt for the LLM
    tables = inspector.get_table_names()
    schema_description = []
    for table in tables:
        cols = [col['name'] for col in inspector.get_columns(table)]
        schema_description.append(f"{table}({', '.join(cols)})")
    schema_context = "; ".join(schema_description)
    
    SYSTEM_PROMPT = f"""
        You are a backend SQL assistant.

        Your only job is to convert user questions into valid SQL using the provided schema:
        {schema_context}

        STRICTLY follow these rules:
        1. Use ONLY the schema provided above — do not invent tables or columns.
        2. Your response MUST following structure:
        {{
            "function": "<function_name>",
            "parameters": {{
            "sql": "<SQL_QUERY>"
            }}
        }}
        3. Use ONLY these function names:
        - run_select → for SELECT queries
        - run_dml → for INSERT, UPDATE, or DELETE queries
        4. Format SQL with:
        - UPPERCASE keywords (e.g., SELECT, FROM, WHERE)
        - Proper quoting of string literals (use single quotes: '...')
        - Always end SQL with a semicolon (;)
        """

    # Call the LLM to translate the natural language query to SQL
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            # functions = FUNCTIONS,
            # function_call= "auto"
        )
        message = response.choices[0].message
    except Exception as e:
        print(f"DeepSeek call failed: {e}")
        return jsonify({"error": "LLM call failed", "details": str(e)}), 500
    print(message)
    
    parsed = json.loads(message.content)
    sql = parsed["parameters"]["sql"]
    func_name = parsed["function"]
    print(sql)
    print(func_name) 
    try:
        if func_name == "run_select":
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = [dict(row._mapping) for row in result]
                return jsonify({"sql": sql, "rows": rows})
        else: # DML operations
            with engine.begin() as conn:
                result = conn.execute(text(sql))
                print(f"Executed DML: {sql}")
                return jsonify({"sql": sql, "affected_rows": result.rowcount})
    except Exception as e:
        return jsonify({"error": str(e), "sql": sql}), 500
        # Fallback: no function call
    return jsonify({"error": "Could not parse query into SQL."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)