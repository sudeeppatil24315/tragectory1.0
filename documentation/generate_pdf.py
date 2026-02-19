"""
Generate HTML version of the complete project report for PDF conversion
"""

import markdown
from datetime import datetime

# Read the markdown file
with open('COMPLETE-PROJECT-REPORT.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert markdown to HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])

# Create full HTML document with styling
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trajectory Engine MVP - Complete Project Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-before: always;
        }}
        
        h1:first-of-type {{
            page-break-before: avoid;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .status-success {{
            background-color: #2ecc71;
            color: white;
        }}
        
        .status-warning {{
            background-color: #f39c12;
            color: white;
        }}
        
        .status-info {{
            background-color: #3498db;
            color: white;
        }}
        
        .page-break {{
            page-break-after: always;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            
            a {{
                color: #000;
                text-decoration: none;
            }}
            
            .no-print {{
                display: none;
            }}
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        
        .header h1 {{
            margin: 0;
            border: none;
            color: white;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Trajectory Engine MVP</h1>
        <p>Complete Project Report</p>
        <p>February 9-16, 2026</p>
    </div>
    
    {html_content}
    
    <div class="footer">
        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p><strong>Document Version:</strong> 1.0</p>
        <p><strong>Classification:</strong> Internal Project Documentation</p>
    </div>
    
    <script>
        // Add print button
        window.onload = function() {{
            const printBtn = document.createElement('button');
            printBtn.textContent = '🖨️ Print to PDF';
            printBtn.className = 'no-print';
            printBtn.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; z-index: 1000;';
            printBtn.onclick = function() {{ window.print(); }};
            document.body.appendChild(printBtn);
        }};
    </script>
</body>
</html>
"""

# Write HTML file
with open('COMPLETE-PROJECT-REPORT.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ HTML report generated: COMPLETE-PROJECT-REPORT.html")
print()
print("To convert to PDF:")
print("1. Open COMPLETE-PROJECT-REPORT.html in your browser")
print("2. Press Ctrl+P (or click the Print button)")
print("3. Select 'Save as PDF' as the printer")
print("4. Click 'Save'")
print()
print("Or use this command if you have wkhtmltopdf installed:")
print("wkhtmltopdf COMPLETE-PROJECT-REPORT.html COMPLETE-PROJECT-REPORT.pdf")
