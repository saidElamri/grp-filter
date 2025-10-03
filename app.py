from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_file
import random
import json
import os
from datetime import datetime
from io import BytesIO
import csv

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

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

def load_json(filename, default):
    """Load JSON file or return default"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
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
            {"name": "Manal", "notes": "", "absent": False, "gender": ""},
            {"name": "Moubarak", "notes": "", "absent": False, "gender": ""},
            {"name": "Lahcen", "notes": "", "absent": False, "gender": ""},
            {"name": "Chami", "notes": "", "absent": False, "gender": ""},
            {"name": "Assma", "notes": "", "absent": False, "gender": ""},
            {"name": "Fatima", "notes": "", "absent": False, "gender": ""},
            {"name": "Rachid", "notes": "", "absent": False, "gender": ""},
            {"name": "Ayoub", "notes": "", "absent": False, "gender": ""},
            {"name": "Ben Ihda", "notes": "", "absent": False, "gender": ""},
            {"name": "Said", "notes": "", "absent": False, "gender": ""},
            {"name": "Mohamed", "notes": "", "absent": False, "gender": ""},
            {"name": "Chaima", "notes": "", "absent": False, "gender": ""},
            {"name": "Saida", "notes": "", "absent": False, "gender": ""},
            {"name": "Youssef Ismail", "notes": "", "absent": False, "gender": ""},
            {"name": "Maryem", "notes": "", "absent": False, "gender": ""},
            {"name": "Maryem Ben", "notes": "", "absent": False, "gender": ""},
            {"name": "El Ouardy", "notes": "", "absent": False, "gender": ""},
            {"name": "Yassine", "notes": "", "absent": False, "gender": ""},
            {"name": "Nouhaila", "notes": "", "absent": False, "gender": ""},
            {"name": "Hamza", "notes": "", "absent": False, "gender": ""},
            {"name": "Khaoula", "notes": "", "absent": False, "gender": ""},
            {"name": "Khadija", "notes": "", "absent": False, "gender": ""}
        ],
        "restrictions": []  # List of pairs that shouldn't be together
    }
    
    data = load_json(STUDENTS_FILE, default)
    
    # Migration: Convert old format (list) to new format (dict with students key)
    if isinstance(data, list):
        print("Migrating old student data format...")
        migrated_data = {
            "students": [
                {"name": name, "notes": "", "absent": False, "gender": ""} 
                for name in data
            ],
            "restrictions": []
        }
        save_json(STUDENTS_FILE, migrated_data)
        return migrated_data
    
    # Migration: Ensure all students have required fields
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
        "assign_roles": True,
        "password": ""
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
<html data-theme="{{ 'dark' if settings.dark_mode else 'light' }}">
<head>
    <title>Student Group Selector Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg-primary: #f5f5f5;
            --bg-secondary: white;
            --bg-tertiary: #f9f9f9;
            --text-primary: #333;
            --text-secondary: #555;
            --border-color: #ddd;
            --accent-blue: #2196f3;
            --accent-green: #4caf50;
            --accent-orange: #ff9800;
            --accent-red: #f44336;
        }
        
        [data-theme="dark"] {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #3a3a3a;
            --text-primary: #e0e0e0;
            --text-secondary: #b0b0b0;
            --border-color: #444;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s, color 0.3s;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 10px;
        }
        
        .container {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .tab {
            padding: 10px 20px;
            background: transparent;
            border: none;
            cursor: pointer;
            color: var(--text-secondary);
            font-size: 16px;
            border-bottom: 3px solid transparent;
        }
        
        .tab.active {
            color: var(--accent-blue);
            border-bottom-color: var(--accent-blue);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .setting-item {
            padding: 15px;
            background: var(--bg-tertiary);
            border-radius: 5px;
        }
        
        .setting-item label {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }
        
        .setting-item input[type="number"] {
            width: 70px;
            padding: 5px;
            border: 1px solid var(--border-color);
            border-radius: 3px;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .add-student {
            margin: 20px 0;
            padding: 20px;
            background: #f0f7ff;
            border-radius: 5px;
            border-left: 4px solid var(--accent-blue);
        }
        
        [data-theme="dark"] .add-student {
            background: #1a2332;
        }
        
        .add-student h3 {
            margin: 0 0 15px 0;
            color: var(--accent-blue);
        }
        
        .add-student form {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .add-student input {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            font-size: 14px;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .add-student select {
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .add-student button {
            padding: 10px 20px;
            background: var(--accent-green);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .student-list {
            margin: 20px 0;
        }
        
        .student-card {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            margin: 5px;
            background: var(--bg-tertiary);
            border-radius: 5px;
            border-left: 3px solid var(--accent-blue);
            position: relative;
        }
        
        .student-card.absent {
            opacity: 0.5;
            border-left-color: #999;
        }
        
        .student-card .name {
            font-weight: 500;
        }
        
        .student-card .gender {
            font-size: 12px;
            padding: 2px 6px;
            background: #e3f2fd;
            border-radius: 3px;
            color: #1976d2;
        }
        
        [data-theme="dark"] .student-card .gender {
            background: #1a2942;
        }
        
        .student-card .notes-icon {
            cursor: help;
            color: var(--accent-orange);
        }
        
        .student-card button {
            background: none;
            border: none;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
        
        .student-card .absence-btn {
            background: #ffa726;
            color: white;
        }
        
        .student-card .edit-btn {
            background: var(--accent-blue);
            color: white;
        }
        
        .student-card .remove-btn {
            background: var(--accent-red);
            color: white;
        }
        
        .group {
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--accent-green);
            position: relative;
        }
        
        .group:nth-child(1) { background: #e8f5e9; border-left-color: #4caf50; }
        .group:nth-child(2) { background: #e3f2fd; border-left-color: #2196f3; }
        .group:nth-child(3) { background: #fff3e0; border-left-color: #ff9800; }
        .group:nth-child(4) { background: #fce4ec; border-left-color: #e91e63; }
        .group:nth-child(5) { background: #f3e5f5; border-left-color: #9c27b0; }
        .group:nth-child(6) { background: #e0f2f1; border-left-color: #009688; }
        
        [data-theme="dark"] .group:nth-child(1) { background: #1b2e1f; }
        [data-theme="dark"] .group:nth-child(2) { background: #1a2332; }
        [data-theme="dark"] .group:nth-child(3) { background: #2e2416; }
        [data-theme="dark"] .group:nth-child(4) { background: #2e1a23; }
        [data-theme="dark"] .group:nth-child(5) { background: #271a2e; }
        [data-theme="dark"] .group:nth-child(6) { background: #1a2826; }
        
        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .seating {
            background: var(--bg-secondary);
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
            color: var(--accent-orange);
            border: 2px solid var(--accent-orange);
            font-size: 14px;
        }
        
        .group-members {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        
        .member-card {
            padding: 10px;
            background: var(--bg-secondary);
            border-radius: 5px;
            min-width: 150px;
        }
        
        .member-role {
            font-size: 11px;
            color: var(--accent-blue);
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: var(--accent-blue);
            color: white;
            width: 100%;
            margin: 10px 0;
        }
        
        .btn-primary:hover {
            background: #1976d2;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: var(--accent-green);
            color: white;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .action-buttons button {
            flex: 1;
            min-width: 150px;
        }
        
        .message {
            padding: 12px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }
        
        .history-item {
            padding: 15px;
            margin: 10px 0;
            background: var(--bg-tertiary);
            border-radius: 5px;
            border-left: 3px solid var(--accent-blue);
        }
        
        .history-date {
            font-weight: bold;
            color: var(--accent-blue);
            margin-bottom: 5px;
        }
        
        .timer-display {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: var(--accent-blue);
            margin: 20px 0;
        }
        
        .timer-controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .random-picker {
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-green));
            border-radius: 10px;
            color: white;
        }
        
        .picked-student {
            font-size: 36px;
            font-weight: bold;
            margin: 20px 0;
            min-height: 50px;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            .container {
                padding: 15px;
            }
            .tabs {
                overflow-x: auto;
            }
            .action-buttons button {
                min-width: 100%;
            }
        }
        
        @media print {
            .no-print {
                display: none !important;
            }
            body {
                background: white;
                color: black;
            }
            .container {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Student Group Selector Pro</h1>
        
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
                    🎲 Generate Random Groups
                </button>
                <button class="btn btn-secondary" onclick="window.print()">
                    🖨️ Print Groups
                </button>
                <button class="btn btn-secondary" onclick="exportCSV()">
                    📥 Export CSV
                </button>
            </div>
            
            <form id="generateForm" method="POST" action="{{ url_for('generate') }}" style="display:none;"></form>
            
            {% if current_timestamp %}
                <p style="text-align: center; color: var(--text-secondary);">
                    Generated on: {{ current_timestamp }}
                </p>
            {% endif %}
            
            {% if groups %}
                <div style="text-align: center; margin: 15px 0; color: var(--text-secondary);">
                    <strong>{{ num_groups }}</strong> groups of {{ settings.group_size }} 
                    {% if settings.balance_gender %}(Gender Balanced){% endif %}
                </div>
                
                {% for i in range(groups|length) %}
                    <div class="group">
                        <div class="group-header">
                            <h3>Group {{ i + 1 }}</h3>
                            <span class="seating">📍 {{ seating[i] }}</span>
                        </div>
                        <div class="group-members">
                            {% for member in groups[i] %}
                                <div class="member-card">
                                    {% if settings.assign_roles and member.role %}
                                        <div class="member-role">{{ member.role }}</div>
                                    {% endif %}
                                    <div class="name">{{ member.name }}</div>
                                    {% if member.gender %}
                                        <span class="gender">{{ member.gender }}</span>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
                
                {% if remaining %}
                    <div style="margin: 15px 0; padding: 15px; background: #fff3e0; border-radius: 5px; border-left: 4px solid var(--accent-orange);">
                        <h3 style="margin: 0 0 10px 0; color: var(--accent-orange);">Remaining Students ({{ remaining|length }})</h3>
                        {% for student in remaining %}
                            <span class="student-card">{{ student }}</span>
                        {% endfor %}
                    </div>
                {% endif %}
            {% else %}
                <p style="text-align: center; color: var(--text-secondary); padding: 40px;">
                    Click "Generate Random Groups" to create groups
                </p>
            {% endif %}
        </div>
        
        <!-- STUDENTS TAB -->
        <div id="students-tab" class="tab-content">
            <div class="add-student">
                <h3>➕ Add New Student</h3>
                <form method="POST" action="{{ url_for('add_student') }}">
                    <input type="text" name="student_name" placeholder="Student name" required>
                    <select name="gender">
                        <option value="">Gender (Optional)</option>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                    </select>
                    <input type="text" name="notes" placeholder="Notes (optional)">
                    <button type="submit">Add Student</button>
                </form>
            </div>
            
            <div class="student-list">
                <h3>All Students ({{ students|length }}) - {{ present_count }} Present</h3>
                {% for student in students %}
                    <div class="student-card {% if student.absent %}absent{% endif %}">
                        <span class="name">{{ student.name }}</span>
                        {% if student.gender %}
                            <span class="gender">{{ student.gender }}</span>
                        {% endif %}
                        {% if student.notes %}
                            <span class="notes-icon" title="{{ student.notes }}">📝</span>
                        {% endif %}
                        <form method="POST" action="{{ url_for('toggle_absence') }}" style="display: inline;">
                            <input type="hidden" name="student_name" value="{{ student.name }}">
                            <button type="submit" class="absence-btn">
                                {% if student.absent %}✓ Present{% else %}✗ Absent{% endif %}
                            </button>
                        </form>
                        <button class="edit-btn" onclick="editStudent('{{ student.name }}')">✏️</button>
                        <form method="POST" action="{{ url_for('remove_student') }}" style="display: inline;">
                            <input type="hidden" name="student_name" value="{{ student.name }}">
                            <button type="submit" class="remove-btn" onclick="return confirm('Remove {{ student.name }}?')">✕</button>
                        </form>
                    </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- HISTORY TAB -->
        <div id="history-tab" class="tab-content">
            <h3>Group History</h3>
            {% if history %}
                {% for record in history[-10:][::-1] %}
                    <div class="history-item">
                        <div class="history-date">{{ record.date }}</div>
                        <div>{{ record.num_groups }} groups of {{ record.group_size }} students</div>
                    </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: var(--text-secondary); padding: 40px;">
                    No history yet. Generate groups to see history.
                </p>
            {% endif %}
        </div>
        
        <!-- TOOLS TAB -->
        <div id="tools-tab" class="tab-content">
            <h3>🎲 Random Student Picker</h3>
            <div class="random-picker">
                <div class="picked-student" id="pickedStudent">Click button below</div>
                <button class="btn btn-primary" onclick="pickRandomStudent()">Pick Random Student</button>
            </div>
            
            <h3 style="margin-top: 30px;">⏱️ Group Activity Timer</h3>
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
        
        <!-- SETTINGS TAB -->
        <div id="settings-tab" class="tab-content">
            <h3>⚙️ Settings</h3>
            <form method="POST" action="{{ url_for('update_settings') }}">
                <div class="settings-grid">
                    <div class="setting-item">
                        <label>
                            <strong>Group Size:</strong>
                            <input type="number" name="group_size" value="{{ settings.group_size }}" min="2" max="10">
                        </label>
                    </div>
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" name="dark_mode" {% if settings.dark_mode %}checked{% endif %}>
                            <strong>Dark Mode</strong>
                        </label>
                    </div>
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" name="balance_gender" {% if settings.balance_gender %}checked{% endif %}>
                            <strong>Balance by Gender</strong>
                        </label>
                    </div>
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" name="assign_roles" {% if settings.assign_roles %}checked{% endif %}>
                            <strong>Assign Group Roles</strong>
                        </label>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">💾 Save Settings</button>
            </form>
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
            const presentStudents = students.filter((s, i) => !{{ students|map(attribute='absent')|list|tojson }}[i]);
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
                        alert('⏰ Time is up!');
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
        
        function editStudent(name) {
            const notes = prompt('Edit notes for ' + name + ':');
            if (notes !== null) {
                fetch('{{ url_for("edit_student") }}', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, notes: notes})
                }).then(() => location.reload());
            }
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
        message = f"✅ {name} has been added and saved!"
    elif any(s['name'] == name for s in STUDENTS_DATA['students']):
        message = f"⚠️ {name} is already in the class!"
    else:
        message = "⚠️ Please enter a valid name!"
    
    return redirect(url_for('index', message=message))

@app.route('/remove_student', methods=['POST'])
def remove_student():
    name = request.form.get('student_name', '').strip()
    STUDENTS_DATA['students'] = [s for s in STUDENTS_DATA['students'] if s['name'] != name]
    save_json(STUDENTS_FILE, STUDENTS_DATA)
    message = f"✅ {name} has been removed and saved!"
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

@app.route('/edit_student', methods=['POST'])
def edit_student():
    data = request.get_json()
    name = data.get('name')
    notes = data.get('notes', '')
    
    for student in STUDENTS_DATA['students']:
        if student['name'] == name:
            student['notes'] = notes
            save_json(STUDENTS_FILE, STUDENTS_DATA)
            break
    
    return jsonify({"status": "success"})

@app.route('/generate', methods=['POST'])
def generate():
    global current_groups, current_seating, current_remaining, current_timestamp
    
    # Get present students only
    present_students = [s for s in STUDENTS_DATA['students'] if not s['absent']]
    
    if len(present_students) == 0:
        return redirect(url_for('index', message="⚠️ No students present to create groups!"))
    
    # Shuffle students
    shuffled = present_students.copy()
    random.shuffle(shuffled)
    
    group_size = SETTINGS['group_size']
    num_groups = len(shuffled) // group_size
    current_groups = []
    
    # Balance by gender if enabled
    if SETTINGS['balance_gender'] and any(s['gender'] for s in shuffled):
        # Separate by gender
        males = [s for s in shuffled if s.get('gender') == 'M']
        females = [s for s in shuffled if s.get('gender') == 'F']
        others = [s for s in shuffled if not s.get('gender')]
        
        random.shuffle(males)
        random.shuffle(females)
        random.shuffle(others)
        
        # Distribute evenly
        for i in range(num_groups):
            group = []
            # Add from each gender pool
            if males:
                group.append(males.pop())
            if females:
                group.append(females.pop())
            if males and len(group) < group_size:
                group.append(males.pop())
            if females and len(group) < group_size:
                group.append(females.pop())
            
            # Fill remaining spots
            while len(group) < group_size and (males or females or others):
                if males:
                    group.append(males.pop())
                elif females:
                    group.append(females.pop())
                elif others:
                    group.append(others.pop())
            
            current_groups.append(group)
        
        current_remaining = [s['name'] for s in males + females + others]
    else:
        # Regular grouping
        for i in range(num_groups):
            group = shuffled[i*group_size:(i+1)*group_size]
            current_groups.append(group)
        
        current_remaining = [s['name'] for s in shuffled[num_groups*group_size:]]
    
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
    current_seating = available_seats[:num_groups]
    
    # Save to history
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    HISTORY.append({
        "date": current_timestamp,
        "num_groups": num_groups,
        "group_size": group_size,
        "groups": [[m['name'] for m in g] for g in current_groups]
    })
    save_json(HISTORY_FILE, HISTORY)
    
    return redirect(url_for('index'))

@app.route('/update_settings', methods=['POST'])
def update_settings():
    SETTINGS['group_size'] = int(request.form.get('group_size', 4))
    SETTINGS['dark_mode'] = 'dark_mode' in request.form
    SETTINGS['balance_gender'] = 'balance_gender' in request.form
    SETTINGS['assign_roles'] = 'assign_roles' in request.form
    save_json(SETTINGS_FILE, SETTINGS)
    return redirect(url_for('index', message="✅ Settings saved!"))


@app.route('/export_csv')
def export_csv():
    if not current_groups:
        return redirect(url_for('index', message="⚠️ Generate groups first!"))
    
    # Use StringIO instead of BytesIO for CSV writing
    from io import StringIO
    
    output = StringIO()
    output.write('\ufeff')  # BOM for Excel UTF-8 (no need to encode)
    
    writer = csv.writer(output)
    writer.writerow(['Group', 'Student Name', 'Role', 'Seating'])
    
    for i, group in enumerate(current_groups):
        seating = current_seating[i] if i < len(current_seating) else ""
        for member in group:
            writer.writerow([
                f"Group {i+1}",
                member['name'],
                member.get('role', ''),
                seating
            ])
    
    # Convert to bytes for sending
    output.seek(0)
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'groups_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)