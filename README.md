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



### Step 1: Install Flask
```bash
pip install flask
```
or
```bash
pip3 install flask
```

### Step 2: Save the Application
Create a file named `app.py` and paste the application code into it.

## Usage


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


## License

This project is free to use and modify for educational purposes.


---

Made with ❤️ for classroom management
