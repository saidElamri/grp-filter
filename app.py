from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_file
import random
import json
import os
from datetime import datetime
from io import BytesIO, StringIO
import csv

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# File paths
STUDENTS_FILE = 'students.json'
HISTORY_FILE = 'group_history.json'
SETTINGS_FILE = 'settings.json'

# Available seating areas
SEATING_AREAS = [
    "Front Left", "Front Center", "Front Right",
    "Middle Left", "Middle Center", "Middle Right",
    "Back Left", "Back Center", "Back Right",
    "Window Side", "Door Side", "Lab Area"
]

GROUP_ROLES = ["Leader", "Note-taker", "Presenter", "Timekeeper"]

# Priority pair students (Lahcen, Said, Youssef, Hamza)
PRIORITY_PAIRS = ["Lahcen", "Said", "Youssef Ismail", "Hamza"]

def load_json(filename, default):
    """Load JSON file or return default"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    save_json(filename, default)
    return default

def save_json(filename, data):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_students():
    """Load students with metadata"""
    default = {
        "students": [
            {"name": "Manal", "notes": "", "absent": False, "gender": "F"},
            {"name": "Moubarak", "notes": "", "absent": False, "gender": "M"},
            {"name": "Lahcen", "notes": "", "absent": False, "gender": "M"},
            {"name": "Chami", "notes": "", "absent": False, "gender": "M"},
            {"name": "Assma", "notes": "", "absent": False, "gender": "F"},
            {"name": "Fatima", "notes": "", "absent": False, "gender": "F"},
            {"name": "Rachid", "notes": "", "absent": False, "gender": "M"},
            {"name": "Ayoub", "notes": "", "absent": False, "gender": "M"},
            {"name": "Ben Ihda", "notes": "", "absent": False, "gender": "M"},
            {"name": "Said", "notes": "", "absent": False, "gender": "M"},
            {"name": "Mohamed", "notes": "", "absent": False, "gender": "M"},
            {"name": "Chaima", "notes": "", "absent": False, "gender": "F"},
            {"name": "Saida", "notes": "", "absent": False, "gender": "F"},
            {"name": "Youssef Ismail", "notes": "", "absent": False, "gender": "M"},
            {"name": "Maryem", "notes": "", "absent": False, "gender": "F"},
            {"name": "Maryem Ben", "notes": "", "absent": False, "gender": "F"},
            {"name": "El Ouardy", "notes": "", "absent": False, "gender": "M"},
            {"name": "Yassine", "notes": "", "absent": False, "gender": "M"},
            {"name": "Nouhaila", "notes": "", "absent": False, "gender": "F"},
            {"name": "Hamza", "notes": "", "absent": False, "gender": "M"},
            {"name": "Khaoula", "notes": "", "absent": False, "gender": "F"},
            {"name": "Khadija", "notes": "", "absent": False, "gender": "F"}
        ],
        "restrictions": []
    }
    
    data = load_json(STUDENTS_FILE, default)
    
    # Migration: Convert old format
    if isinstance(data, list):
        migrated_data = {
            "students": [
                {"name": name, "notes": "", "absent": False, "gender": ""} 
                for name in data
            ],
            "restrictions": []
        }
        save_json(STUDENTS_FILE, migrated_data)
        return migrated_data
    
    # Ensure all students have required fields
    for student in data.get("students", []):
        if "notes" not in student:
            student["notes"] = ""
        if "absent" not in student:
            student["absent"] = False
        if "gender" not in student:
            student["gender"] = ""
    
    return data

def load_settings():
    """Load app settings"""
    default = {
        "group_size": 4,
        "dark_mode": False,
        "balance_gender": False,
        "assign_roles": True
    }
    return load_json(SETTINGS_FILE, default)

# Load data
STUDENTS_DATA = load_students()
HISTORY = load_json(HISTORY_FILE, [])
SETTINGS = load_settings()

# Store current groups
current_groups = []
current_seating = []
current_remaining = []
current_timestamp = ""

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Group Selector Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        
        .stats {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-top: 16px;
        }
        
        .stat-badge {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            color: #555;
        }
        
        .stat-badge.online {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            overflow-x: auto;
            padding-bottom: 8px;
        }
        
        .tab {
            padding: 12px 24px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            color: #666;
            transition: all 0.2s;
            white-space: nowrap;
        }
        
        .tab:hover {
            border-color: #999;
            color: #333;
        }
        
        .tab.active {
            background: #1a1a1a;
            border-color: #1a1a1a;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #1a1a1a;
            color: white;
        }
        
        .btn-primary:hover {
            background: #000;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .btn-success {
            background: #4caf50;
            color: white;
        }
        
        .btn-success:hover {
            background: #45a049;
        }
        
        .btn-danger {
            background: #f44336;
            color: white;
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 13px;
        }
        
        .action-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }
        
        .groups-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .group-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s;
        }
        
        .group-card:hover {
            border-color: #999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .group-title {
            font-size: 20px;
            font-weight: 700;
            color: #1a1a1a;
        }
        
        .seating-badge {
            padding: 6px 12px;
            background: #fff3e0;
            border: 2px solid #ff9800;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            color: #e65100;
        }
        
        .member-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .member-card {
            padding: 12px;
            background: #fafafa;
            border-radius: 8px;
            border-left: 3px solid #1a1a1a;
        }
        
        .member-role {
            font-size: 11px;
            font-weight: 700;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        
        .member-name {
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .member-gender {
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }
        
        .students-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }
        
        .student-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .student-card:hover {
            border-color: #999;
        }
        
        .student-card.absent {
            opacity: 0.5;
            background: #fafafa;
        }
        
        .student-info {
            flex: 1;
        }
        
        .student-name {
            font-size: 15px;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .student-meta {
            font-size: 13px;
            color: #999;
            margin-top: 4px;
        }
        
        .student-actions {
            display: flex;
            gap: 8px;
        }
        
        .add-student-form {
            background: #f9f9f9;
            padding: 24px;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            margin-bottom: 24px;
        }
        
        .add-student-form h3 {
            margin-bottom: 16px;
            color: #1a1a1a;
        }
        
        .form-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .form-input {
            flex: 1;
            min-width: 200px;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 15px;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #1a1a1a;
        }
        
        .form-select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 15px;
            background: white;
        }
        
        .history-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .history-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
        }
        
        .history-item:hover {
            border-color: #999;
        }
        
        .history-date {
            font-weight: 600;
            color: #666;
            font-size: 14px;
        }
        
        .history-details {
            color: #999;
            font-size: 14px;
            margin-top: 4px;
        }
        
        .settings-grid {
            display: grid;
            gap: 16px;
        }
        
        .setting-item {
            padding: 20px;
            background: #f9f9f9;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
        }
        
        .setting-label {
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
        }
        
        .setting-label input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .setting-label input[type="number"] {
            width: 80px;
            padding: 8px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .message {
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 24px;
            font-weight: 500;
        }
        
        .message.success {
            background: #e8f5e9;
            color: #2e7d32;
            border: 2px solid #4caf50;
        }
        
        .message.warning {
            background: #fff3e0;
            color: #e65100;
            border: 2px solid #ff9800;
        }
        
        .timer-display {
            text-align: center;
            font-size: 72px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 40px 0;
            font-family: 'Courier New', monospace;
        }
        
        .timer-controls {
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 24px;
        }
        
        .random-picker {
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            color: white;
            margin-bottom: 24px;
        }
        
        .picked-student {
            font-size: 48px;
            font-weight: 700;
            margin: 32px 0;
            min-height: 60px;
        }
        
        @media (max-width: 768px) {
            .groups-grid {
                grid-template-columns: 1fr;
            }
            
            .students-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .timer-display {
                font-size: 48px;
            }
        }
        
        @media print {
            .no-print {
                display: none !important;
            }
            
            body {
                background: white;
            }
            
            .card, .group-card {
                box-shadow: none;
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Student Group Selector Pro</h1>
            <div class="stats">
                <div class="stat-badge online">{{ present_count }} Present</div>
                <div class="stat-badge">{{ students|length }} Total Students</div>
            </div>
        </div>
        
        <div class="tabs no-print">
            <button class="tab active" onclick="showTab('groups')">📊 Groups</button>
            <button class="tab" onclick="showTab('students')">👥 Students</button>
            <button class="tab" onclick="showTab('history')">📜 History</button>
            <button class="tab" onclick="showTab('tools')">🛠️ Tools</button>
            <button class="tab" onclick="showTab('settings')">⚙️ Settings</button>
        </div>
        
        {% if message %}
            <div class="message {{ 'success' if 'added' in message or 'removed' in message or 'saved' in message else 'warning' }}">
                {{ message }}
            </div>
        {% endif %}
        
        <!-- GROUPS TAB -->
        <div id="groups-tab" class="tab-content active">
            <div class="action-buttons no-print">
                <button class="btn btn-primary" onclick="document.getElementById('generateForm').submit()">
                    🎲 Generate Groups
                </button>
                <button class="btn btn-secondary" onclick="window.print()">
                    🖨️ Print
                </button>
                <button class="btn btn-success" onclick="exportCSV()">
                    📥 Export CSV
                </button>
            </div>
            
            <form id="generateForm" method="POST" action="{{ url_for('generate') }}" style="display:none;"></form>
            
            {% if current_timestamp %}
                <div class="card">
                    <p style="color: #666; text-align: center;">
                        Generated on: {{ current_timestamp }}
                    </p>
                </div>
            {% endif %}
            
            {% if groups %}
                <div class="card">
                    <p style="text-align: center; font-weight: 600; color: #333;">
                        {{ num_groups }} groups of {{ settings.group_size }} students
                        {% if settings.balance_gender %}(Gender Balanced){% endif %}
                    </p>
                </div>
                
                <div class="groups-grid">
                    {% for i in range(groups|length) %}
                        <div class="group-card">
                            <div class="group-header">
                                <h3 class="group-title">Group {{ i + 1 }}</h3>
                                <span class="seating-badge">📍 {{ seating[i] }}</span>
                            </div>
                            <div class="member-list">
                                {% for member in groups[i] %}
                                    <div class="member-card">
                                        {% if settings.assign_roles and member.role %}
                                            <div class="member-role">{{ member.role }}</div>
                                        {% endif %}
                                        <div class="member-name">{{ member.name }}</div>
                                        {% if member.gender %}
                                            <div class="member-gender">{{ member.gender }}</div>
                                        {% endif %}
                                    </div>
                                {% endfor %}
                            </div>
                        </div>
                    {% endfor %}
                </div>
                
                {% if remaining %}
                    <div class="card" style="margin-top: 24px; background: #fff3e0; border: 2px solid #ff9800;">
                        <h3 style="margin-bottom: 12px; color: #e65100;">Remaining Students ({{ remaining|length }})</h3>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            {% for student in remaining %}
                                <span style="padding: 8px 16px; background: white; border-radius: 20px; font-weight: 600;">{{ student }}</span>
                            {% endfor %}
                        </div>
                    </div>
                {% endif %}
            {% else %}
                <div class="card empty-state">
                    <div class="empty-state-icon">📊</div>
                    <p style="font-size: 18px; color: #666;">Click "Generate Groups" to create groups</p>
                </div>
            {% endif %}
        </div>
        
        <!-- STUDENTS TAB -->
        <div id="students-tab" class="tab-content">
            <div class="add-student-form">
                <h3>➕ Add New Student</h3>
                <form method="POST" action="{{ url_for('add_student') }}">
                    <div class="form-row">
                        <input type="text" name="student_name" class="form-input" placeholder="Student name" required>
                        <select name="gender" class="form-select">
                            <option value="">Gender (Optional)</option>
                            <option value="M">Male</option>
                            <option value="F">Female</option>
                        </select>
                        <input type="text" name="notes" class="form-input" placeholder="Notes (optional)">
                        <button type="submit" class="btn btn-success">Add Student</button>
                    </div>
                </form>
            </div>
            
            <div class="students-grid">
                {% for student in students %}
                    <div class="student-card {% if student.absent %}absent{% endif %}">
                        <div class="student-info">
                            <div class="student-name">{{ student.name }}</div>
                            <div class="student-meta">
                                {% if student.gender %}{{ student.gender }} • {% endif %}
                                {% if student.absent %}Absent{% else %}Present{% endif %}
                            </div>
                        </div>
                        <div class="student-actions">
                            <form method="POST" action="{{ url_for('toggle_absence') }}" style="display: inline;">
                                <input type="hidden" name="student_name" value="{{ student.name }}">
                                <button type="submit" class="btn btn-small" style="background: {% if student.absent %}#4caf50{% else %}#ff9800{% endif %}; color: white;">
                                    {% if student.absent %}✓{% else %}✗{% endif %}
                                </button>
                            </form>
                            <form method="POST" action="{{ url_for('remove_student') }}" style="display: inline;">
                                <input type="hidden" name="student_name" value="{{ student.name }}">
                                <button type="submit" class="btn btn-small btn-danger" onclick="return confirm('Remove {{ student.name }}?')">×</button>
                            </form>
                        </div>
                    </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- HISTORY TAB -->
        <div id="history-tab" class="tab-content">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <h3>Group History</h3>
                    {% if history %}
                        <form method="POST" action="{{ url_for('clear_history') }}" style="display: inline;">
                            <button type="submit" class="btn btn-danger btn-small" onclick="return confirm('Clear all history?')">
                                🗑️ Clear All
                            </button>
                        </form>
                    {% endif %}
                </div>
                
                {% if history %}
                    <div class="history-list">
                        {% for record in history[-10:][::-1] %}
                            <div class="history-item">
                                <div>
                                    <div class="history-date">{{ record.date }}</div>
                                    <div class="history-details">{{ record.num_groups }} groups of {{ record.group_size }} students</div>
                                </div>
                                <form method="POST" action="{{ url_for('delete_history') }}" style="display: inline;">
                                    <input type="hidden" name="history_index" value="{{ loop.revindex0 }}">
                                    <button type="submit" class="btn btn-small btn-danger">Delete</button>
                                </form>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="empty-state">
                        <div class="empty-state-icon">📜</div>
                        <p>No history yet. Generate groups to see history.</p>
                    </div>
                {% endif %}
            </div>
        </div>
        
        <!-- TOOLS TAB -->
        <div id="tools-tab" class="tab-content">
            <div class="random-picker">
                <h3 style="font-size: 24px; margin-bottom: 16px;">🎲 Random Student Picker</h3>
                <div class="picked-student" id="pickedStudent">Click button below</div>
                <button class="btn" style="background: white; color: #667eea; font-size: 18px;" onclick="pickRandomStudent()">
                    Pick Random Student
                </button>
            </div>
            
            <div class="card">
                <h3 style="text-align: center; margin-bottom: 24px;">⏱️ Group Activity Timer</h3>
                <div class="timer-display" id="timerDisplay">05:00</div>
                <div class="timer-controls">
                    <button class="btn btn-secondary" onclick="setTimer(5)">5 min</button>
                    <button class="btn btn-secondary" onclick="setTimer(10)">10 min</button>
                    <button class="btn btn-secondary" onclick="setTimer(15)">15 min</button>
                    <button class="btn btn-primary" onclick="startTimer()">▶️ Start</button>
                    <button class="btn btn-secondary" onclick="pauseTimer()">⏸️ Pause</button>
                    <button class="btn btn-secondary" onclick="resetTimer()">🔄 Reset</button>
                </div>
            </div>
        </div>
        
        <!-- SETTINGS TAB -->
        <div id="settings-tab" class="tab-content">
            <div class="card">
                <h3 style="margin-bottom: 24px;">⚙️ Settings</h3>
                <form method="POST" action="{{ url_for('update_settings') }}">
                    <div class="settings-grid">
                        <div class="setting-item">
                            <label class="setting-label">
                                <strong>Group Size:</strong>
                                <input type="number" name="group_size" value="{{ settings.group_size }}" min="2" max="6">
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" name="balance_gender" {% if settings.balance_gender %}checked{% endif %}>
                                <strong>Balance by Gender</strong>
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" name="assign_roles" {% if settings.assign_roles %}checked{% endif %}>
                                <strong>Assign Group Roles</strong>
                            </label>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary" style="margin-top: 24px; width: 100%;">💾 Save Settings</button>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        let timerInterval;
        let timerSeconds = 300;
        let timerRunning = false;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function pickRandomStudent() {
            const students = {{ students|map(attribute='name')|list|tojson }};
            const presentStudents = students.filter((s, i) => !{{ students|map(attribute='absent')|list|tojson }});
            if (presentStudents.length > 0) {
                const picked = presentStudents[Math.floor(Math.random() * presentStudents.length)];
                document.getElementById('pickedStudent').textContent = picked;
            }
        }
        
        function setTimer(minutes) {
            timerSeconds = minutes * 60;
            updateTimerDisplay();
        }
        
        function updateTimerDisplay() {
            const mins = Math.floor(timerSeconds / 60);
            const secs = timerSeconds % 60;
            document.getElementById('timerDisplay').textContent = 
                `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
        
        function startTimer() {
            if (!timerRunning) {
                timerRunning = true;
                timerInterval = setInterval(() => {
                    if (timerSeconds > 0) {
                        timerSeconds--;
                        updateTimerDisplay();
                    } else {
                        pauseTimer();
                        alert('Time is up!');
                    }
                }, 1000);
            }
        }
        
        function pauseTimer() {
            timerRunning = false;
            clearInterval(timerInterval);
        }
        
        function resetTimer() {
            pauseTimer();
            timerSeconds = 300;
            updateTimerDisplay();
        }
        
        function exportCSV() {
            window.location.href = '{{ url_for("export_csv") }}';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    message = request.args.get('message', '')
    present_count = sum(1 for s in STUDENTS_DATA['students'] if not s['absent'])
    
    return render_template_string(
        HTML_TEMPLATE,
        students=STUDENTS_DATA['students'],
        present_count=present_count,
        groups=current_groups,
        seating=current_seating,
        remaining=current_remaining,
        num_groups=len(current_groups),
        current_timestamp=current_timestamp,
        settings=SETTINGS,
        history=HISTORY,
        message=message
    )

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get('student_name', '').strip()
    gender = request.form.get('gender', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if name and not any(s['name'] == name for s in STUDENTS_DATA['students']):
        STUDENTS_DATA['students'].append({
            "name": name,
            "notes": notes,
            "absent": False,
            "gender": gender
        })
        save_json(STUDENTS_FILE, STUDENTS_DATA)
        message = f"Added {name} successfully!"
    elif any(s['name'] == name for s in STUDENTS_DATA['students']):
        message = f"{name} is already in the class!"
    else:
        message = "Please enter a valid name!"
    
    return redirect(url_for('index', message=message))

@app.route('/remove_student', methods=['POST'])
def remove_student():
    name = request.form.get('student_name', '').strip()
    STUDENTS_DATA['students'] = [s for s in STUDENTS_DATA['students'] if s['name'] != name]
    save_json(STUDENTS_FILE, STUDENTS_DATA)
    message = f"Removed {name} successfully!"
    return redirect(url_for('index', message=message))

@app.route('/toggle_absence', methods=['POST'])
def toggle_absence():
    name = request.form.get('student_name', '').strip()
    for student in STUDENTS_DATA['students']:
        if student['name'] == name:
            student['absent'] = not student['absent']
            save_json(STUDENTS_FILE, STUDENTS_DATA)
            break
    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate():
    global current_groups, current_seating, current_remaining, current_timestamp
    
    present_students = [s for s in STUDENTS_DATA['students'] if not s['absent']]
    
    if len(present_students) == 0:
        return redirect(url_for('index', message="No students present to create groups!"))
    
    group_size = SETTINGS['group_size']
    
    if len(present_students) < group_size:
        return redirect(url_for('index', message=f"Not enough students! Need at least {group_size} present students."))
    
    # Separate priority pair students from regular students
    priority_students = [s for s in present_students if s['name'] in PRIORITY_PAIRS]
    regular_students = [s for s in present_students if s['name'] not in PRIORITY_PAIRS]
    
    # Shuffle both groups
    random.shuffle(priority_students)
    random.shuffle(regular_students)
    
    num_groups = len(present_students) // group_size
    current_groups = []
    
    if SETTINGS['balance_gender'] and any(s.get('gender') for s in present_students):
        # Separate regular students by gender
        males = [s for s in regular_students if s.get('gender') == 'M']
        females = [s for s in regular_students if s.get('gender') == 'F']
        others = [s for s in regular_students if not s.get('gender')]
        
        random.shuffle(males)
        random.shuffle(females)
        random.shuffle(others)
        
        # Create groups
        for i in range(num_groups):
            group = []
            
            # Add 2 priority students per group (if available)
            for _ in range(2):
                if priority_students:
                    group.append(priority_students.pop())
            
            # Fill remaining spots with gender balance
            while len(group) < group_size and (males or females or others):
                if males and len(group) < group_size:
                    group.append(males.pop())
                if females and len(group) < group_size:
                    group.append(females.pop())
                if others and len(group) < group_size:
                    group.append(others.pop())
            
            if len(group) >= 2:  # Allow groups of at least 2
                current_groups.append(group)
        
        current_remaining = [s['name'] for s in males + females + others + priority_students]
    else:
        # Regular grouping - distribute 2 priority students per group
        for i in range(num_groups):
            group = []
            
            # Add 2 priority students per group (if available)
            for _ in range(2):
                if priority_students:
                    group.append(priority_students.pop())
            
            # Fill remaining spots with regular students
            while len(group) < group_size and regular_students:
                group.append(regular_students.pop())
            
            if len(group) >= 2:
                current_groups.append(group)
        
        current_remaining = [s['name'] for s in regular_students + priority_students]
    
    # Assign roles if enabled
    if SETTINGS['assign_roles']:
        for group in current_groups:
            roles = GROUP_ROLES.copy()
            random.shuffle(roles)
            for j, member in enumerate(group):
                member['role'] = roles[j] if j < len(roles) else ""
    
    # Assign seating
    available_seats = SEATING_AREAS.copy()
    random.shuffle(available_seats)
    current_seating = available_seats[:len(current_groups)]
    
    # Save to history
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    HISTORY.append({
        "date": current_timestamp,
        "num_groups": len(current_groups),
        "group_size": group_size,
        "groups": [[m['name'] for m in g] for g in current_groups]
    })
    
    # Keep only last 100 history entries
    if len(HISTORY) > 100:
        HISTORY[:] = HISTORY[-100:]
    
    save_json(HISTORY_FILE, HISTORY)
    
    return redirect(url_for('index'))

@app.route('/update_settings', methods=['POST'])
def update_settings():
    SETTINGS['group_size'] = int(request.form.get('group_size', 4))
    SETTINGS['dark_mode'] = 'dark_mode' in request.form
    SETTINGS['balance_gender'] = 'balance_gender' in request.form
    SETTINGS['assign_roles'] = 'assign_roles' in request.form
    save_json(SETTINGS_FILE, SETTINGS)
    return redirect(url_for('index', message="Settings saved!"))

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global HISTORY
    HISTORY = []
    save_json(HISTORY_FILE, HISTORY)
    return redirect(url_for('index', message="History cleared!"))

@app.route('/delete_history', methods=['POST'])
def delete_history():
    global HISTORY
    index = int(request.form.get('history_index', -1))
    if 0 <= index < len(HISTORY):
        # Reverse index because we display reversed
        actual_index = len(HISTORY) - 1 - index
        HISTORY.pop(actual_index)
        save_json(HISTORY_FILE, HISTORY)
    return redirect(url_for('index', message="History item deleted!"))

@app.route('/export_csv')
def export_csv():
    if not current_groups:
        return redirect(url_for('index', message="Generate groups first!"))
    
    output = StringIO()
    output.write('\ufeff')  # BOM for Excel UTF-8
    
    writer = csv.writer(output)
    writer.writerow(['Group', 'Student Name', 'Role', 'Gender', 'Seating'])
    
    for i, group in enumerate(current_groups):
        seating = current_seating[i] if i < len(current_seating) else ""
        for member in group:
            writer.writerow([
                f"Group {i+1}",
                member['name'],
                member.get('role', ''),
                member.get('gender', ''),
                seating
            ])
    
    output.seek(0)
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'groups_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)