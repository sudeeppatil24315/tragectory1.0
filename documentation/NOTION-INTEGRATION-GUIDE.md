# Notion Integration Guide - Push Student Analysis

## Step 1: Get Notion API Key

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it: "Trajectory Engine"
4. Select your workspace
5. Click "Submit"
6. Copy the "Internal Integration Token" (starts with `secret_`)

## Step 2: Configure MCP Server

1. Open `.kiro/settings/mcp.json`
2. Replace `YOUR_NOTION_API_KEY_HERE` with your actual API key
3. Save the file

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-notion"
      ],
      "env": {
        "NOTION_API_KEY": "secret_your_actual_key_here"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Step 3: Share Notion Page with Integration

1. Open your Notion workspace
2. Create a new page called "Trajectory Engine - Student Analysis"
3. Click "Share" in the top right
4. Click "Invite"
5. Search for "Trajectory Engine" (your integration name)
6. Click "Invite"
7. Copy the page URL (you'll need the page ID)

**Page ID Example:**
- URL: `https://www.notion.so/My-Page-123abc456def789`
- Page ID: `123abc456def789`

## Step 4: Restart Kiro

1. Close and reopen Kiro
2. Or use Command Palette: "MCP: Reconnect All Servers"

## Step 5: Verify Connection

Ask me to:
```
List my Notion pages
```

If successful, you'll see your pages listed.

## Step 6: Push Student Analysis

Once configured, you can ask me to:

```
Push the student analysis to Notion
```

Or:

```
Create a Notion database with all 7 students
```

---

## Alternative: Manual Export

If MCP setup is complex, you can manually export:

### Option 1: Copy Markdown to Notion

1. Open `ALL-7-STUDENTS-DETAILED-ANALYSIS.md`
2. Copy all content (Ctrl+A, Ctrl+C)
3. Go to Notion
4. Create new page
5. Paste (Ctrl+V)
6. Notion will auto-format the markdown

### Option 2: Import as CSV

1. Open `all_students_analysis.json`
2. Convert to CSV using this script:

```python
import json
import csv

# Read JSON
with open('all_students_analysis.json', 'r') as f:
    data = json.load(f)

# Write CSV
with open('students_for_notion.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'name', 'gpa', 'major', 'trajectory_score', 
        'placement_likelihood', 'academic', 'behavioral', 'skills'
    ])
    writer.writeheader()
    for student in data:
        writer.writerow({
            'name': student['name'],
            'gpa': student['gpa'],
            'major': student['major'],
            'trajectory_score': student['trajectory_score'],
            'placement_likelihood': student['placement_likelihood'],
            'academic': student['academic'],
            'behavioral': student['behavioral'],
            'skills': student['skills']
        })

print("✅ Created students_for_notion.csv")
```

3. In Notion, create a database
4. Click "..." → "Import" → "CSV"
5. Select `students_for_notion.csv`

### Option 3: Use Notion API Directly

I can create a Python script that uses Notion API directly:

```python
import requests
import json

NOTION_API_KEY = "your_key_here"
DATABASE_ID = "your_database_id_here"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Read student data
with open('all_students_analysis.json', 'r') as f:
    students = json.load(f)

# Create page for each student
for student in students:
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": student['name']}}]},
            "GPA": {"number": student['gpa']},
            "Score": {"number": student['trajectory_score']},
            "Major": {"select": {"name": student['major']}},
            "Likelihood": {"rich_text": [{"text": {"content": student['placement_likelihood']}}]}
        }
    }
    
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print(f"✅ Added {student['name']}")
    else:
        print(f"❌ Failed to add {student['name']}: {response.text}")
```

---

## Troubleshooting

### MCP Server Not Starting

**Error:** "Command not found: npx"

**Solution:** Install Node.js
```bash
# Download from https://nodejs.org
# Or use package manager
winget install OpenJS.NodeJS
```

### Notion API Key Invalid

**Error:** "Unauthorized"

**Solution:**
1. Check API key is correct (starts with `secret_`)
2. Ensure integration is added to the page
3. Verify workspace permissions

### Page Not Found

**Error:** "Could not find page"

**Solution:**
1. Share the page with your integration
2. Use correct page ID
3. Check integration has access to workspace

---

## What Gets Pushed to Notion

When you push the analysis, I'll create:

### 1. Main Page: "Trajectory Engine Analysis"
- Executive summary
- Ranking table
- Key insights

### 2. Database: "Students"
Columns:
- Name
- GPA
- Major
- Trajectory Score
- Academic Score
- Behavioral Score
- Skills Score
- Placement Likelihood
- Status (Student/Alumni)

### 3. Individual Pages (7 pages)
For each student:
- Full profile
- Detailed scores
- Strengths (top 3)
- Improvements (top 3)
- Recommendations (top 5)
- Self-assessment

### 4. Comparison Page
- Academic comparison table
- Behavioral comparison table
- Skills comparison table
- Charts and visualizations

---

## Next Steps

1. **Get Notion API key** (5 minutes)
2. **Update mcp.json** with your key
3. **Share Notion page** with integration
4. **Restart Kiro**
5. **Ask me to push data** to Notion

Or use the manual export options above if you prefer!

---

**Need Help?**
- Notion API Docs: https://developers.notion.com
- MCP Notion Server: https://github.com/modelcontextprotocol/servers/tree/main/src/notion
- Kiro MCP Guide: Search "MCP" in Command Palette
