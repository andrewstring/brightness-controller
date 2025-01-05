import os
import urwid

# Function to get brightness for a monitor
def get_brightness(monitor_index):
    monitor_index_correct = monitor_index + 1
    try:
        output = os.popen(f"sudo ddcutil getvcp 10 --display {monitor_index_correct}").read()
        for line in output.split("\n"):
            if "value" in line:
                return int(line.split("current value =")[1].strip().split(",")[0])
    except Exception:
        return 0
    return 0

# Function to get the max brightness for a monitor
def get_max_brightness(monitor_index):
    monitor_index_correct = monitor_index + 1
    try:
        output = os.popen(f"sudo ddcutil getvcp 10 --display {monitor_index_correct}").read()
        for line in output.split("\n"):
            if "value" in line:
                return int(line.split("max value =")[1].strip())
    except Exception:
        return 0
    return 0

# Function to set brightness for a monitor
def set_brightness(value):
    global active_row
    monitor_index_correct = active_row + 1
    command = f"sudo ddcutil setvcp 10 {value} --display {monitor_index_correct}"
    os.system(command)

# Function to increase brightness for a monitor
def increase_brightness():
    global active_row
    global brightness_levels
    # print("DEBUG:BRIGHTNESS")
    # print(brightness_levels)
    brightness = ((brightness_levels[active_row] // 10) * 10) + 10
    if brightness > 100:
        brightness = 100
    brightness_levels[active_row] = brightness
    update_brightness()
    set_brightness(brightness)

# Function to decrease brightness for a monitor
def decrease_brightness():
    global active_row
    global brightness_levels
    brightness = ((brightness_levels[active_row] // 10) * 10) - 10
    if brightness < 0:
        brightness = 0
    brightness_levels[active_row] = brightness
    update_brightness()
    set_brightness(brightness)


# Function to fetch all monitors
def fetch_monitors():
    output = os.popen("sudo ddcutil detect").read()
    monitors = []
    for line in output.split("\n"):
        if line.strip().startswith("Model:"):
            monitors.append(line.strip().split(":")[1].strip())
    return monitors

# Function to update the display to reflect the active monitor
def update_active_inactive():
    global display_columns
    global active_row

    for i, column in enumerate(display_columns):
        row1 = column.contents[0][0]
        if i == active_row:
            row1.set_text("ACTIVE")
        else:
            row1.set_text("INACTIVE")

# Function to update the display to reflect the updated brightness value
def update_brightness():
    global display_columns
    global brightness_levels

    for i, column in enumerate(display_columns):
        row3 = column.contents[2][0]
        row3.set_text("Current: " + str(brightness_levels[i]))


# Input handler
def handle_input(key):
    global monitors
    global brightness_levels
    global max_brightness_levels
    global active_row
    # Make monitor to the left the active monitor
    if key == "left":
        if active_row > 0:
            active_row -= 1
            update_active_inactive()
    # Make monitor to the right the active monitor
    elif key == "right":
        if active_row < len(monitors)-1:
            active_row += 1
            update_active_inactive()
    # Increase the brightness of the active monitor
    elif key == "up":
        if brightness_levels[active_row] < max_brightness_levels[active_row]:
            increase_brightness()
    # Decrease the brightness of the active monitor
    elif key == "down":
        if brightness_levels[active_row] > 0:
            decrease_brightness()
    # Terminate the application
    elif key == "q":
        raise urwid.ExitMainLoop()

# Initial display generation
def generate_display_columns():
    global monitors
    global brightness_levels
    global max_brightness_levels
    global active_row

    display_columns = []

    for i, monitor in enumerate(monitors):
        row1 = urwid.Text("ACTIVE" if active_row == i else "INACTIVE", align="center")
        row2 = urwid.Text(monitor, align="center")
        row3 = urwid.Text("Current: " + str(brightness_levels[i]), align="center")
        row4 = urwid.Text("Max: " + str(max_brightness_levels[i]), align="center")
        col = urwid.Pile([row1,row2,row3,row4])
        display_columns.append(col)

    return display_columns


# Fetch monitors and initialize brightness levels
monitors = fetch_monitors()
brightness_levels = [get_brightness(i) for i in range(len(monitors))]
max_brightness_levels = [get_max_brightness(i) for i in range(len(monitors))]
active_row = 0



# Build UI
display_columns = generate_display_columns()
print("DEBUG:DISPLAY_COLUMNS")
print(display_columns)


columns = urwid.Columns(display_columns, dividechars=1)
header = urwid.Text("Use arrow keys to adjust brightness. Press 'q' to quit.", align="center")
layout = urwid.Pile([header, urwid.Text("\n\n\n"), columns])
filler = urwid.Filler(layout, valign="top")
main_loop = None

palette = [("highlight", "light cyan", "")]

# Start the application
if __name__ == "__main__":
    main_loop = urwid.MainLoop(filler, palette, unhandled_input=handle_input).run()

if __debug__:
    urwid.MainLoop(filler, palette, unhandled_input=handle_input).run()
