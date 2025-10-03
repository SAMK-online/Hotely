#!/usr/bin/env python3
"""
Hotely - Web Interface Demo
===========================
A simple web interface to interact with Hotely AI system.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv('hotelpilot/.env')

def setup_ai():
    """Setup the AI model"""
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        return None, "❌ No API key found. Please check hotelpilot/.env file"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        return model, f"✅ Hotely AI initialized with API key: {api_key[:10]}..."
    except Exception as e:
        return None, f"❌ Error initializing AI: {e}"

def get_scenarios():
    """Get predefined scenarios"""
    return {
        "pricing": {
            "title": "🏷️ Dynamic Pricing Analysis",
            "description": "Analyze flight demand and recommend optimal room rates",
            "prompt": """You are the Revenue Manager for Arlington Suites (120 rooms).

Analyze this pricing scenario:
- Current rate: $129 standard, $189 deluxe
- Date: Tomorrow (Friday, December 20, 2024)
- Current occupancy: 78%

Flight data shows:
- DCA airport: +18% capacity (1,200 extra seats)
- IAD airport: +12% capacity (1,500 extra seats)
- No major events scheduled

Policy constraints:
- Max weekday increase: 10%
- Max weekend increase: 12%

Provide specific rate recommendations with rationale."""
        },
        
        "guest": {
            "title": "💬 Guest Communication Flow",
            "description": "Generate personalized guest messages and service communications",
            "prompt": """You are the Guest Services Manager for Arlington Suites.

Create guest communications for:
- Guest: John Smith (john@example.com)
- Reservation: RES-2024-1220
- Check-in: December 20, Check-out: December 22
- Room: Deluxe King, Rate: $189/night

Create:
1. Pre-arrival welcome message
2. Early check-in offer
3. Deposit collection request

Keep messages professional and concise."""
        },
        
        "housekeeping": {
            "title": "🧹 Housekeeping Optimization",
            "description": "Optimize daily cleaning schedules with staff and priority constraints",
            "prompt": """You are the Housekeeping Supervisor for Arlington Suites.

Optimize today's schedule:
- 15 checkouts by 11 AM
- 18 arrivals starting 3 PM (2 VIP guests)
- 32 stayovers
- 3 housekeeping staff available
- Room 305 needs early check-in by 1 PM

Timing: Standard clean 24.5 min, VIP +10 min
Create detailed schedule with staff assignments."""
        },
        
        "payment": {
            "title": "💳 Payment Recovery Strategy",
            "description": "Develop intelligent recovery plans for failed payments",
            "prompt": """You are the Revenue Recovery Manager for Arlington Suites.

Develop recovery plan for:
- Guest: Sarah Johnson (reliable guest, 4 previous stays)
- Amount: $378 (2 nights + taxes)
- Failure code: insufficient_funds
- Failed at: 9:15 AM today

Create timeline with specific communications and recovery actions."""
        }
    }

def run_scenario(model, scenario_key):
    """Run a specific scenario"""
    scenarios = get_scenarios()
    if scenario_key not in scenarios:
        return "❌ Invalid scenario"
    
    scenario = scenarios[scenario_key]
    
    try:
        response = model.generate_content(scenario["prompt"])
        return response.text
    except Exception as e:
        return f"❌ Error: {e}"

def create_html_interface():
    """Create HTML interface"""
    scenarios = get_scenarios()
    
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotely - AI Hotel Operations Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #7f8c8d;
            font-size: 1.2em;
            margin: 10px 0;
        }
        .scenarios {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .scenario-card {
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        .scenario-card:hover {
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .scenario-card.active {
            border-color: #2ecc71;
            background: #e8f5e8;
        }
        .scenario-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        .scenario-desc {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .controls {
            text-align: center;
            margin: 30px 0;
        }
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: background 0.3s ease;
            margin: 0 10px;
        }
        .btn:hover {
            background: #2980b9;
        }
        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        .result {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            display: none;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
        }
        .status {
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .custom-input {
            width: 100%;
            min-height: 100px;
            padding: 15px;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            font-family: inherit;
            font-size: 1em;
            margin: 10px 0;
            resize: vertical;
        }
        .custom-input:focus {
            border-color: #3498db;
            outline: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏨 Hotely</h1>
            <p>AI-Powered Hotel Operations System</p>
            <p>Automate pricing, guest services, housekeeping & payments</p>
        </div>

        <div id="status" class="status"></div>

        <div class="scenarios">
"""
    
    for key, scenario in scenarios.items():
        html += f"""
            <div class="scenario-card" onclick="selectScenario('{key}')">
                <div class="scenario-title">{scenario['title']}</div>
                <div class="scenario-desc">{scenario['description']}</div>
            </div>
        """
    
    html += """
        </div>

        <div class="controls">
            <button class="btn" onclick="runSelected()" id="runBtn" disabled>Run Selected Scenario</button>
            <button class="btn" onclick="runAll()">Run All Scenarios</button>
            <button class="btn" onclick="showCustom()">Custom Prompt</button>
        </div>

        <div id="customSection" style="display: none;">
            <h3>Custom Hotel Operations Scenario</h3>
            <textarea id="customPrompt" class="custom-input" placeholder="Enter your custom hotel operations scenario here...

Example:
A VIP guest is complaining about noise from construction next door. They want compensation or a room change. The hotel is 95% occupied. Guest has 12 previous stays. Provide a solution that maintains guest satisfaction while protecting revenue."></textarea>
            <button class="btn" onclick="runCustom()">Run Custom Scenario</button>
        </div>

        <div id="result" class="result"></div>
    </div>

    <script>
        let selectedScenario = null;
        let isRunning = false;

        function selectScenario(key) {
            // Remove active class from all cards
            document.querySelectorAll('.scenario-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Add active class to selected card
            event.target.closest('.scenario-card').classList.add('active');
            
            selectedScenario = key;
            document.getElementById('runBtn').disabled = false;
            
            // Hide custom section
            document.getElementById('customSection').style.display = 'none';
        }

        function showCustom() {
            document.getElementById('customSection').style.display = 'block';
            // Deselect scenarios
            document.querySelectorAll('.scenario-card').forEach(card => {
                card.classList.remove('active');
            });
            selectedScenario = null;
            document.getElementById('runBtn').disabled = true;
        }

        async function runSelected() {
            if (!selectedScenario || isRunning) return;
            
            isRunning = true;
            document.getElementById('runBtn').disabled = true;
            
            showStatus('Running scenario...', 'loading');
            showResult('🔄 Processing your request...');
            
            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({scenario: selectedScenario})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showStatus('✅ Scenario completed successfully!', 'success');
                    showResult(data.result);
                } else {
                    showStatus('❌ Error: ' + data.error, 'error');
                    showResult('');
                }
            } catch (error) {
                showStatus('❌ Connection error: ' + error.message, 'error');
                showResult('');
            }
            
            isRunning = false;
            document.getElementById('runBtn').disabled = false;
        }

        async function runCustom() {
            const prompt = document.getElementById('customPrompt').value.trim();
            if (!prompt || isRunning) return;
            
            isRunning = true;
            showStatus('Running custom scenario...', 'loading');
            showResult('🔄 Processing your custom request...');
            
            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({custom: prompt})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showStatus('✅ Custom scenario completed!', 'success');
                    showResult(data.result);
                } else {
                    showStatus('❌ Error: ' + data.error, 'error');
                    showResult('');
                }
            } catch (error) {
                showStatus('❌ Connection error: ' + error.message, 'error');
                showResult('');
            }
            
            isRunning = false;
        }

        async function runAll() {
            if (isRunning) return;
            
            isRunning = true;
            showStatus('Running all scenarios...', 'loading');
            showResult('🔄 Running all Hotely scenarios...');
            
            try {
                const response = await fetch('/run_all', {method: 'POST'});
                const data = await response.json();
                
                if (data.success) {
                    showStatus('✅ All scenarios completed!', 'success');
                    showResult(data.result);
                } else {
                    showStatus('❌ Error: ' + data.error, 'error');
                    showResult('');
                }
            } catch (error) {
                showStatus('❌ Connection error: ' + error.message, 'error');
                showResult('');
            }
            
            isRunning = false;
        }

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }

        function showResult(text) {
            const result = document.getElementById('result');
            result.textContent = text;
            result.style.display = text ? 'block' : 'none';
        }

        // Initialize
        showStatus('🚀 Hotely AI system ready!', 'success');
    </script>
</body>
</html>
"""
    
    return html

def main():
    """Main web server"""
    try:
        from flask import Flask, request, jsonify, render_template_string
        
        app = Flask(__name__)
        
        # Setup AI
        model, status = setup_ai()
        print(status)
        
        if model is None:
            print("❌ Cannot start web server without AI model")
            return
        
        @app.route('/')
        def index():
            return render_template_string(create_html_interface())
        
        @app.route('/run', methods=['POST'])
        def run_scenario_endpoint():
            try:
                data = request.json
                
                if 'scenario' in data:
                    # Run predefined scenario
                    result = run_scenario(model, data['scenario'])
                    scenarios = get_scenarios()
                    scenario_title = scenarios.get(data['scenario'], {}).get('title', 'Unknown')
                    formatted_result = f"{scenario_title}\n{'='*50}\n\n💡 AI Response:\n{'-'*40}\n{result}"
                    
                elif 'custom' in data:
                    # Run custom prompt
                    custom_prompt = f"""You are the Operations Manager for Arlington Suites hotel.

Handle this situation:
{data['custom']}

Provide a professional, actionable solution."""
                    
                    try:
                        response = model.generate_content(custom_prompt)
                        result = response.text
                        formatted_result = f"🎯 Custom Scenario\n{'='*50}\n\n💡 AI Response:\n{'-'*40}\n{result}"
                    except Exception as e:
                        return jsonify({'success': False, 'error': str(e)})
                else:
                    return jsonify({'success': False, 'error': 'No scenario or custom prompt provided'})
                
                return jsonify({'success': True, 'result': formatted_result})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @app.route('/run_all', methods=['POST'])
        def run_all_scenarios():
            try:
                scenarios = get_scenarios()
                all_results = []
                
                for key, scenario in scenarios.items():
                    result = run_scenario(model, key)
                    all_results.append(f"{scenario['title']}\n{'='*60}\n\n💡 AI Response:\n{'-'*40}\n{result}\n\n")
                
                final_result = "\n".join(all_results)
                final_result += "\n🎉 All Hotely scenarios completed successfully!\n\n"
                final_result += "The system demonstrated:\n"
                final_result += "• Dynamic pricing based on flight demand\n"
                final_result += "• Guest communication workflows\n"
                final_result += "• Housekeeping optimization\n"
                final_result += "• Payment recovery strategies\n"
                final_result += "\n✨ Hotely is ready for hotel operations!"
                
                return jsonify({'success': True, 'result': final_result})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        print("\n🌐 Starting Hotely Web Interface...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError:
        print("❌ Flask not installed. Install with: pip install flask")
        print("💡 Or use the terminal version: python demo_hotelpilot.py")

if __name__ == "__main__":
    main()
