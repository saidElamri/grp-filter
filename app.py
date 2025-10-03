from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

# List of students (stored in memory - will reset when app restarts)
STUDENTS = [
    "Manal", "Moubarak", "Lahcen", "Chami", "Assma", "Fatima",
    "Rachid", "Ayoub", "Ben Ihda", "Said", "Mohamed", "Chaima",
    "Saida", "Youssef", "Ismail", "Maryem", "Maryem Ben", "El Ouardy",
    "Yassine", "Nouhaila", "Hamza", "Khaoula", "Khadija"
]

# Available seating areas
SEATING_AREAS = [
    "Front Left", "Front Center", "Front Right",
    "Middle Left", "Middle Center", "Middle Right",
    "Back Left", "Back Center", "Back Right",
    "Window Side", "Door Side", "Lab Area"
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Group Selector</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .add-student {
            margin: 20px 0;
            padding: 20px;
            background: #f0f7ff;
            border-radius: 5px;
            border-left: 4px solid #2196f3;
        }
        .add-student h3 {
            margin: 0 0 15px 0;
            color: #1976d2;
        }
        .add-student form {
            display: flex;
            gap: 10px;
        }
        .add-student input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .add-student button {
            padding: 10px 20px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .add-student button:hover {
            background: #45a049;
        }
        .student-list {
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }
        .student-list h3 {
            margin-top: 0;
            color: #555;
        }
        .student {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 5px 10px;
            margin: 5px;
            background: #e3f2fd;
            border-radius: 3px;
            font-size: 14px;
        }
        .student .remove-btn {
            background: #f44336;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            margin-left: 5px;
        }
        .student .remove-btn:hover {
            background: #d32f2f;
        }
        .student form {
            display: inline;
            margin: 0;
            padding: 0;
        }
        .group {
            margin: 15px 0;
            padding: 20px;
            background: #e8f5e9;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
        }
        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .group h3 {
            margin: 0;
            color: #2e7d32;
        }
        .seating {
            background: #fff;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
            color: #ff6f00;
            border: 2px solid #ff6f00;
            font-size: 14px;
        }
        .group-members {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .remaining {
            margin: 15px 0;
            padding: 15px;
            background: #fff3e0;
            border-radius: 5px;
            border-left: 4px solid #ff9800;
        }
        .remaining h3 {
            margin: 0 0 10px 0;
            color: #e65100;
        }
        button.generate {
            display: block;
            width: 100%;
            padding: 15px;
            margin: 20px 0;
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button.generate:hover {
            background: #1976d2;
        }
        .info {
            text-align: center;
            color: #666;
            margin: 10px 0;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Student Group Selector</h1>
        
        <div class="add-student">
            <h3>➕ Add New Student</h3>
            <form method="POST" action="{{ url_for('add_student') }}">
                <input type="text" name="student_name" placeholder="Enter student name" required>
                <button type="submit">Add Student</button>
            </form>
        </div>

        {% if message %}
            <div class="success-message">{{ message }}</div>
        {% endif %}

        <div class="student-list">
            <h3>All Students ({{ total_students }})</h3>
            {% for student in students %}
                <span class="student">
                    {{ student }}
                    <form method="POST" action="{{ url_for('remove_student') }}">
                        <input type="hidden" name="student_name" value="{{ student }}">
                        <button type="submit" class="remove-btn" onclick="return confirm('Remove {{ student }}?')">✕</button>
                    </form>
                </span>
            {% endfor %}
        </div>

        <form method="POST" action="{{ url_for('generate') }}">
            <button type="submit" class="generate">Generate Random Groups of 4 with Seating</button>
        </form>

        {% if groups %}
            <div class="info">
                <strong>{{ num_groups }}</strong> groups of 4 students created with assigned seating
            </div>
            
            {% for i in range(groups|length) %}
                <div class="group">
                    <div class="group-header">
                        <h3>Group {{ i + 1 }}</h3>
                        <span class="seating">📍 {{ seating[i] }}</span>
                    </div>
                    <div class="group-members">
                        {% for student in groups[i] %}
                            <span class="student">{{ student }}</span>
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}

            {% if remaining %}
                <div class="remaining">
                    <h3>Remaining Students ({{ remaining|length }})</h3>
                    {% for student in remaining %}
                        <span class="student">{{ student }}</span>
                    {% endfor %}
                </div>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
'''

# Store current groups in memory
current_groups = []
current_seating = []
current_remaining = []

@app.route('/')
def index():
    message = request.args.get('message', '')
    return render_template_string(
        HTML_TEMPLATE,
        students=STUDENTS,
        total_students=len(STUDENTS),
        groups=current_groups,
        seating=current_seating,
        remaining=current_remaining,
        num_groups=len(current_groups),
        message=message
    )

@app.route('/add_student', methods=['POST'])
def add_student():
    student_name = request.form.get('student_name', '').strip()
    if student_name and student_name not in STUDENTS:
        STUDENTS.append(student_name)
        message = f"✅ {student_name} has been added to the class!"
    elif student_name in STUDENTS:
        message = f"⚠️ {student_name} is already in the class!"
    else:
        message = "⚠️ Please enter a valid name!"
    
    return redirect(url_for('index', message=message))

@app.route('/remove_student', methods=['POST'])
def remove_student():
    student_name = request.form.get('student_name', '').strip()
    if student_name in STUDENTS:
        STUDENTS.remove(student_name)
        message = f"✅ {student_name} has been removed from the class!"
    else:
        message = f"⚠️ {student_name} not found!"
    
    return redirect(url_for('index', message=message))

@app.route('/generate', methods=['POST'])
def generate():
    global current_groups, current_seating, current_remaining
    
    # Shuffle students randomly
    shuffled = STUDENTS.copy()
    random.shuffle(shuffled)
    
    # Create groups of 4
    num_groups = len(shuffled) // 4
    current_groups = []
    for i in range(num_groups):
        group = shuffled[i*4:(i+1)*4]
        current_groups.append(group)
    
    # Assign random seating to each group
    available_seats = SEATING_AREAS.copy()
    random.shuffle(available_seats)
    current_seating = available_seats[:num_groups]
    
    # Remaining students
    current_remaining = shuffled[num_groups*4:]
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)