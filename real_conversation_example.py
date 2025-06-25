#!/usr/bin/env python3
"""
Real OpenHands conversation example showing actual message structure.
This demonstrates what messages look like in a real OpenHands session.
"""

import json
from typing import Any

from openhands.core.message import Message, TextContent


def show_real_openhands_conversation():
    """Show what a real OpenHands conversation looks like."""
    
    print("=" * 80)
    print("REAL OPENHANDS CONVERSATION MESSAGES")
    print("=" * 80)
    print("This is what the actual messages array looks like when sent to the LLM")
    print("=" * 80)
    
    # This represents the actual messages array that gets sent to the LLM
    # in a typical OpenHands conversation
    messages = [
        # 1. System message - sets up the agent
        Message(
            role='system',
            content=[TextContent(text="""You are OpenHands agent, a helpful AI assistant that can interact with a computer to solve tasks.

<ROLE>
Your primary role is to assist users by executing commands, modifying code, and solving technical problems effectively. You should be thorough, methodical, and prioritize quality over speed.
* If the user asks a question, like "why is X happening", don't try to fix the problem. Just give an answer to the question.
</ROLE>

<EFFICIENCY>
* Each action you take is somewhat expensive. Wherever possible, combine multiple actions into a single action, e.g. combine multiple bash commands into one, using sed and grep to edit/view multiple files at once.
* When exploring the codebase, use efficient tools like find, grep, and git commands with appropriate filters to minimize unnecessary operations.
</EFFICIENCY>

You have access to the following tools:
- execute_bash: Execute bash commands
- str_replace_editor: Create and edit files
- browser: Browse the web
- execute_ipython_cell: Run Python code

Answer the user's request using the relevant tool(s), if they are available.""")]
        ),
        
        # 2. Initial user message
        Message(
            role='user',
            content=[TextContent(text="Hello! Can you help me create a simple Python script that reads a CSV file and prints the first 5 rows?")]
        ),
        
        # 3. Assistant response with plan
        Message(
            role='assistant',
            content=[TextContent(text="""I'll help you create a Python script that reads a CSV file and prints the first 5 rows. Let me create this script for you.

First, I'll create a simple Python script that uses the pandas library to read and display CSV data.""")]
        ),
        
        # 4. Tool response from file creation
        Message(
            role='tool',
            content=[TextContent(text="""File created successfully at /workspace/csv_reader.py

```python
import pandas as pd
import sys

def read_csv_first_rows(filename, num_rows=5):
    \"\"\"
    Read a CSV file and print the first num_rows rows.
    
    Args:
        filename (str): Path to the CSV file
        num_rows (int): Number of rows to display (default: 5)
    \"\"\"
    try:
        # Read the CSV file
        df = pd.read_csv(filename)
        
        # Print basic info about the dataset
        print(f"CSV file: {filename}")
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print(f"Columns: {list(df.columns)}")
        print("\\n" + "="*50)
        print(f"First {num_rows} rows:")
        print("="*50)
        
        # Display the first num_rows rows
        print(df.head(num_rows).to_string(index=True))
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{filename}' is empty.")
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python csv_reader.py <csv_filename>")
        print("Example: python csv_reader.py data.csv")
    else:
        csv_file = sys.argv[1]
        read_csv_first_rows(csv_file)
```""")],
            tool_call_id="call_str_replace_001",
            name="str_replace_editor"
        ),
        
        # 5. Assistant follow-up
        Message(
            role='assistant',
            content=[TextContent(text="""Perfect! I've created a comprehensive CSV reader script for you. Here's what the script does:

**Features:**
- Reads any CSV file using pandas
- Displays file information (total rows, columns, column names)
- Shows the first 5 rows by default
- Includes proper error handling for common issues
- Can be run from command line with: `python csv_reader.py filename.csv`

**Usage:**
```bash
python csv_reader.py your_file.csv
```

The script will automatically display:
1. Basic file statistics
2. Column names
3. The first 5 rows in a nicely formatted table

Would you like me to create a sample CSV file to test it with, or would you like any modifications to the script?""")])
        ),
        
        # 6. User follow-up request
        Message(
            role='user',
            content=[TextContent(text="That looks great! Can you create a sample CSV file with some test data so I can try it out?")]
        ),
        
        # 7. Assistant acknowledgment
        Message(
            role='assistant',
            content=[TextContent(text="I'll create a sample CSV file with some test data for you to try out the script.")]
        ),
        
        # 8. Tool response from sample CSV creation
        Message(
            role='tool',
            content=[TextContent(text="""File created successfully at /workspace/sample_data.csv

```csv
name,age,city,occupation,salary
John Smith,28,New York,Software Engineer,75000
Jane Doe,32,San Francisco,Data Scientist,85000
Mike Johnson,25,Chicago,Web Developer,65000
Sarah Wilson,29,Boston,Product Manager,80000
David Brown,35,Seattle,DevOps Engineer,90000
Lisa Garcia,27,Austin,UX Designer,70000
Tom Anderson,31,Denver,Backend Developer,72000
Emily Davis,26,Portland,Frontend Developer,68000
```""")],
            tool_call_id="call_str_replace_002", 
            name="str_replace_editor"
        ),
        
        # 9. Assistant completion message
        Message(
            role='assistant',
            content=[TextContent(text="""Excellent! I've created a sample CSV file called `sample_data.csv` with employee data including names, ages, cities, occupations, and salaries.

Now you can test the CSV reader script by running:

```bash
python csv_reader.py sample_data.csv
```

This will show you:
- Total rows: 8
- Total columns: 5  
- Column names: name, age, city, occupation, salary
- The first 5 rows of data in a formatted table

The script is ready to use with any CSV file you have! Just replace `sample_data.csv` with your actual CSV filename.""")])
        ),
        
        # 10. User testing the script
        Message(
            role='user',
            content=[TextContent(text="Let me test it now. Can you run the script with the sample data?")]
        ),
        
        # 11. Assistant running the test
        Message(
            role='assistant',
            content=[TextContent(text="I'll run the CSV reader script with the sample data to show you how it works.")]
        ),
        
        # 12. Tool response from script execution
        Message(
            role='tool',
            content=[TextContent(text="""CSV file: sample_data.csv
Total rows: 8
Total columns: 5
Columns: ['name', 'age', 'city', 'occupation', 'salary']

==================================================
First 5 rows:
==================================================
        name  age           city        occupation  salary
0  John Smith   28       New York  Software Engineer   75000
1   Jane Doe   32  San Francisco     Data Scientist   85000
2 Mike Johnson   25        Chicago      Web Developer   65000
3 Sarah Wilson   29         Boston    Product Manager   80000
4  David Brown   35        Seattle    DevOps Engineer   90000""")],
            tool_call_id="call_execute_bash_001",
            name="execute_bash"
        ),
        
        # 13. Final assistant message
        Message(
            role='assistant',
            content=[TextContent(text="""Perfect! The script works exactly as expected. As you can see, it successfully:

✅ **Read the CSV file** (`sample_data.csv`)
✅ **Displayed file statistics** (8 rows, 5 columns)
✅ **Listed all column names** (name, age, city, occupation, salary)
✅ **Showed the first 5 rows** in a clean, formatted table

The script is now ready for you to use with any CSV file. You have both:
1. `csv_reader.py` - The main script
2. `sample_data.csv` - Test data to experiment with

You can use it with your own CSV files by running:
```bash
python csv_reader.py your_file.csv
```

Is there anything else you'd like me to add to the script or any other CSV-related functionality you need?""")])
        )
    ]
    
    return messages


def analyze_message_structure(messages):
    """Analyze the structure of the messages array."""
    
    print(f"\n📊 CONVERSATION ANALYSIS:")
    print(f"   Total messages: {len(messages)}")
    
    role_counts = {}
    for msg in messages:
        role_counts[msg.role] = role_counts.get(msg.role, 0) + 1
    
    print(f"   Message roles: {role_counts}")
    
    # Show content types
    text_only = sum(1 for msg in messages if len(msg.content) == 1 and isinstance(msg.content[0], TextContent))
    with_images = sum(1 for msg in messages if msg.contains_image)
    tool_responses = sum(1 for msg in messages if msg.tool_call_id is not None)
    
    print(f"   Text-only messages: {text_only}")
    print(f"   Messages with images: {with_images}")
    print(f"   Tool response messages: {tool_responses}")
    
    # Show average content length
    total_chars = sum(len(content.text) for msg in messages for content in msg.content if isinstance(content, TextContent))
    avg_length = total_chars // len(messages) if messages else 0
    print(f"   Average message length: {avg_length} characters")


def show_individual_messages(messages):
    """Show each message in detail."""
    
    print(f"\n📝 DETAILED MESSAGE BREAKDOWN:")
    print("=" * 80)
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- MESSAGE {i} ---")
        print(f"Role: {msg.role}")
        
        if msg.tool_call_id:
            print(f"Tool Call ID: {msg.tool_call_id}")
            print(f"Tool Name: {msg.name}")
        
        print(f"Content ({len(msg.content)} item(s)):")
        for j, content in enumerate(msg.content):
            if isinstance(content, TextContent):
                preview = content.text[:150].replace('\n', '\\n')
                if len(content.text) > 150:
                    preview += "..."
                print(f"  [{j+1}] Text: {preview}")
            else:
                print(f"  [{j+1}] {type(content).__name__}: {content}")
        
        # Show serialized format
        serialized = msg.model_dump()
        print(f"Serialized size: {len(json.dumps(serialized))} characters")


if __name__ == "__main__":
    print("OpenHands Real Conversation Example")
    print("This shows what the actual messages array looks like")
    
    # Get the messages
    messages = show_real_openhands_conversation()
    
    # Analyze the structure
    analyze_message_structure(messages)
    
    # Show detailed breakdown
    show_individual_messages(messages)
    
    print("\n" + "=" * 80)
    print("🔑 KEY INSIGHTS:")
    print("=" * 80)
    print("1. Each message has a specific role: system, user, assistant, or tool")
    print("2. System message sets up the agent with instructions and available tools")
    print("3. User messages contain the actual requests from the human")
    print("4. Assistant messages contain the agent's responses and reasoning")
    print("5. Tool messages contain the results of executed actions")
    print("6. Messages are processed by ConversationMemory.process_events()")
    print("7. The final messages array is what gets sent to the LLM")
    print("8. Tool calls create a request-response pattern in the conversation")
    print("9. Content is structured as TextContent and ImageContent objects")
    print("10. Messages are serialized differently based on LLM capabilities")
    
    print(f"\n💡 This conversation would be sent to the LLM as an array of {len(messages)} messages")
    print("   The LLM processes this entire context to generate its next response.")