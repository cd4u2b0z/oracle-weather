# Oracle Weather Demo
Output assets/demo.gif
Set FontSize 14
Set Width 1200
Set Height 700
Set Theme "Dracula"

Type "cd ~/oracle-weather && source .venv/bin/activate"
Enter
Sleep 500ms

Type "python weather_dashboard.py"
Enter
Sleep 6s

# Let it run and show the weather
Sleep 3s

# Press ? to show help
Type "?"
Sleep 2s

# Dismiss help
Type " "
Sleep 2s

# Show a quip with space
Type " "
Sleep 2s

# Quit
Type "q"
Sleep 500ms
