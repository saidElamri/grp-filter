# 🎓 Student Group Selector

A simple Flask web application to randomly organize students into groups of 4 with assigned seating locations.

## Features

✨ **Random Group Generation** - Automatically creates groups of 4 students from your class roster

📍 **Seating Assignment** - Each group gets a random seating location in the classroom

➕ **Add Students** - Easily add new students to the class roster

✕ **Remove Students** - Remove students who are no longer in the class

🎲 **Randomization** - Click to regenerate groups with different combinations anytime

## Requirements

- Python 3.6 or higher
- Flask

## Installation

### Step 1: Install Python
Make sure Python is installed on your system. Check by running:
```bash
python --version
```
or
```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Create Project Directory
```bash
mkdir student_groups
cd student_groups
```

### Step 3: Install Flask
```bash
pip install flask
```
or
```bash
pip3 install flask
```

### Step 4: Save the Application
Create a file named `app.py` and paste the application code into it.

## Usage

### Running the Application

1. Open terminal/command prompt in the project directory
2. Run the application:
   ```bash
   python app.py
   ```
   or
   ```bash
   python3 app.py
   ```

3. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```
   or
   ```
   http://localhost:5000
   ```

### Using the Application

1. **View Students**: All current students are displayed at the top of the page

2. **Add a Student**:
   - Type the student's name in the input box
   - Click "Add Student"
   - The student will be added to the roster

3. **Remove a Student**:
   - Click the red **✕** button next to any student's name
   - Confirm the removal in the popup dialog

4. **Generate Groups**:
   - Click "Generate Random Groups of 4 with Seating"
   - The app will create random groups of 4 students
   - Each group gets assigned a random seating location
   - Any remaining students (not divisible by 4) will be shown separately

5. **Regenerate Groups**:
   - Click the generate button again to create new random combinations

### Stopping the Application
- Go back to the terminal
- Press `Ctrl + C`

## Seating Locations

The application includes these seating areas:
- Front Left, Front Center, Front Right
- Middle Left, Middle Center, Middle Right
- Back Left, Back Center, Back Right
- Window Side, Door Side, Lab Area

You can customize these locations by editing the `SEATING_AREAS` list in `app.py`.

## Customization

### Adding/Changing Initial Students
Edit the `STUDENTS` list in `app.py`:
```python
STUDENTS = [
    "Manal", "Moubarak", "Lahcen", "Chami", "Assma", "Fatima",
    # Add or remove names here
]
```

### Customizing Seating Areas
Edit the `SEATING_AREAS` list in `app.py`:
```python
SEATING_AREAS = [
    "Your Custom Location 1",
    "Your Custom Location 2",
    # Add your classroom locations here
]
```

### Changing Group Size
To change from groups of 4 to another size, modify this line in the `generate()` function:
```python
num_groups = len(shuffled) // 4  # Change 4 to your desired group size
```

## Notes

⚠️ **Important**: Student data is stored in memory only. When you restart the application, any students added or removed during the session will be reset to the original list defined in the code.

If you need persistent storage (saving students permanently), consider adding a database or file storage system.

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Install Flask using `pip install flask` or `pip3 install flask`

**Problem**: Port already in use
- **Solution**: Stop other applications using port 5000, or change the port in the last line of `app.py`:
  ```python
  app.run(debug=True, port=5001)  # Use a different port
  ```

**Problem**: "Not Found" error when clicking buttons
- **Solution**: Make sure you're using the latest version of the code with `url_for()` functions

## License

This project is free to use and modify for educational purposes.

## Support

For issues or questions, please check that:
1. Flask is properly installed
2. You're running the correct Python version
3. The application is running before opening the browser
4. You're using the correct URL (http://127.0.0.1:5000)

---

Made with ❤️ for classroom management