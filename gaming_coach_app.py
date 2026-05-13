# This program helps gamers understand how well they played
# It takes match stats and gives feedback and tips to improve

# This line brings in Tkinter and names it "tk"
# Tkinter helps us build windows and buttons
import tkinter as tk

# These are extra tools from Tkinter:
# ttk = nicer dropdown menus
# messagebox = pop-up messages
# filedialog = lets user choose where to save a file
from tkinter import ttk, messagebox, filedialog

# This lets us save data into a CSV file
import csv

# This lets us record the current date and time
from datetime import datetime


# This function gets a number from a box safely
def get_float(entry_box, field_name):
    try:
        # Get text from the box, remove spaces, turn into a number
        return float(entry_box.get().strip())
    except ValueError:
        # If it fails, show a helpful error message
        raise ValueError(f"Enter a valid number for {field_name}.")


# This function calculates kills divided by deaths
def calculate_kd(kills, deaths):
    # If deaths is 0, divide by 1 so we don’t crash
    return kills / (deaths if deaths > 0 else 1)


# This function creates a performance score
def calculate_score(kills, deaths, assists, accuracy, objectives, kd, playstyle, match_type, game_type, placement):

    # Start score at 0
    score = 0

    # Add points based on stats
    score += kd * 25
    score += accuracy * 0.4
    score += assists * 1.5
    score += objectives * 3
    score += kills * 2

    # Change scoring depending on game type
    if game_type == "Battle Royale":
        score += kills * 1.5
        score += (100 - placement) * 0.5  # better placement = better score

    elif game_type == "MOBA":
        score += assists * 2
        score += objectives * 4

    elif game_type == "FPS":
        score += accuracy * 0.5

    # Small bonus points
    if playstyle == "Balanced":
        score += 4

    if match_type == "Ranked":
        score += 3

    # Keep score between 0 and 100
    return max(0, min(100, round(score, 2)))


# This function decides skill level
def classify_skill(score):
    if score >= 85:
        return "Advanced"
    elif score >= 60:
        return "Intermediate"
    else:
        return "Beginner"


# This function finds weak spots
def detect_weaknesses(kd, accuracy, deaths, kills, role):

    # Start empty list
    issues = []

    if kd < 1:
        issues.append("Low K/D")

    if accuracy < 40:
        issues.append("Low accuracy")

    if deaths > kills:
        issues.append("Too many deaths")

    if role == "Support" and kd < 1.2:
        issues.append("Low support impact")

    # If no issues, return good message
    return issues if issues else ["No major issues"]


# This function gives advice
def generate_tips(issues):

    tips = []

    for issue in issues:
        if issue == "Low K/D":
            tips.append("Pick safer fights and improve positioning")

        if issue == "Low accuracy":
            tips.append("Practice aim training")

        if issue == "Too many deaths":
            tips.append("Use cover and avoid overextending")

        if issue == "Low support impact":
            tips.append("Stay near teammates more")

    return tips if tips else ["Keep up the good performance"]


# This function decides risk level
def calculate_risk(score, issue_count):

    if score < 55 or issue_count >= 3:
        return "High"
    elif score < 70 or issue_count == 2:
        return "Medium"
    else:
        return "Low"


# This function runs when user clicks Analyze
def analyze():

    global latest_record

    try:
        # Get all user inputs
        kills = get_float(kills_entry, "Kills")
        deaths = get_float(deaths_entry, "Deaths")
        assists = get_float(assists_entry, "Assists")
        accuracy = get_float(accuracy_entry, "Accuracy")
        objectives = get_float(objectives_entry, "Objectives")
        placement = get_float(placement_entry, "Placement")

        # Calculate K/D
        kd = round(calculate_kd(kills, deaths), 2)

        # Calculate score
        score = calculate_score(
            kills, deaths, assists, accuracy, objectives, kd,
            playstyle.get(), match_type.get(), game_type.get(), placement
        )

        # Get skill level
        skill = classify_skill(score)

        # Find problems
        issues = detect_weaknesses(kd, accuracy, deaths, kills, role.get())

        # Get advice
        tips = generate_tips(issues)

        # Get risk level
        risk = calculate_risk(score, len(issues))

        # Pick color based on risk
        color = "green" if risk == "Low" else "orange" if risk == "Medium" else "red"

        # Create output text
        output = f"Score: {score}/100\nSkill: {skill}\nRisk: {risk}\n\nIssues:\n- " + "\n- ".join(issues)
        output += "\n\nTips:\n- " + "\n- ".join(tips)

        # Show output in box
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, output)
        result_box.config(state="disabled")

        # Show risk label
        status_label.config(text=f"Risk Level: {risk}", fg=color)

        # Save latest result
        latest_record = [
            datetime.now(), kills, deaths, assists, accuracy, objectives,
            placement, game_type.get(), score, skill, risk
        ]

    except ValueError as e:
        messagebox.showerror("Error", str(e))


# This saves results to CSV
def save():

    if not latest_record:
        messagebox.showwarning("No Data", "Run analysis first")
        return

    file = filedialog.asksaveasfilename(defaultextension=".csv")

    if not file:
        return

    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(latest_record)


# Create main window
root = tk.Tk()
root.title("Game Performance Analyzer")
root.geometry("700x650")


# Create labels and input boxes
labels = ["Kills", "Deaths", "Assists", "Accuracy", "Objectives", "Placement"]
entries = []

for i, text in enumerate(labels):
    tk.Label(root, text=text).grid(row=i, column=0)
    e = tk.Entry(root)
    e.grid(row=i, column=1)
    entries.append(e)

# Assign entry boxes to variables
kills_entry, deaths_entry, assists_entry, accuracy_entry, objectives_entry, placement_entry = entries


# Create dropdowns
game_type = ttk.Combobox(root, values=["FPS", "MOBA", "Battle Royale"])
game_type.grid(row=0, column=2)
game_type.current(0)

playstyle = ttk.Combobox(root, values=["Aggressive", "Balanced", "Defensive"])
playstyle.grid(row=1, column=2)
playstyle.current(0)

role = ttk.Combobox(root, values=["Sniper", "Support", "Tank", "Entry"])
role.grid(row=2, column=2)
role.current(0)

match_type = ttk.Combobox(root, values=["Casual", "Ranked"])
match_type.grid(row=3, column=2)
match_type.current(0)


# Create buttons
tk.Button(root, text="Analyze", command=analyze).grid(row=7, column=0)
tk.Button(root, text="Save", command=save).grid(row=7, column=1)


# Output label
status_label = tk.Label(root, text="Ready")
status_label.grid(row=8, column=0, columnspan=2)

# Output box
result_box = tk.Text(root, height=15, width=60)
result_box.grid(row=9, column=0, columnspan=3)


# Store latest result
latest_record = []

# Keep window running
root.mainloop()
