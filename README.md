# Python System Monitor Widget

A simple, lightweight, frameless, transparent desktop widget for Windows (and potentially other platforms...haven't tested tbh) that displays live CPU and Memory usage. Sits unobtrusively in the corner of your desktop.

---
<div align="left">
  <div width="500px" align="right">
    <span>Displays here by default &#8595;</span>
  </div>
 <img src="assets/desktop_screenshot.png" alt="Desktop Image">
</div>

## Features

- Displays current **CPU and Memory** utilization percentage.
- **Frameless window** (no title bar or borders).
- **Transparent background.**
- Configurable update interval and text color.
- Configurable initial position (top-right or top-left corner).
- Draggable: **Click and drag** to reposition.
- Easy **closing via a right-click**.
- Attempts to stay off the taskbar.

## Requirements

- Python 3.x
- Required libraries:
  - `PyQt6`
  - `psutil`

You can find these listed in the `requirements.txt` file.

## Installation

1.  **Install Python:** Ensure you have Python 3 installed and added to your system's PATH.
2.  **Clone/Download:** Get the script file (`system_widget.py` or similar) and the `requirements.txt` file.
3.  **Install Dependencies:** Open a terminal or command prompt in the project directory and run:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Widget

Navigate to the project directory in your terminal or command prompt and run the script:

  ```bash
  python system_widget.py
  ```

The widget should appear in the configured screen corner.

## Configuration

You can customize the widget's behavior by editing the configuration variables at the **top** of the Python script (`system_widget.py`):

- `UPDATE_INTERVAL_MS`: Sets how often the CPU and Memory stats refresh, in milliseconds. (Default: `2000`ms = 2 seconds). Lower values mean faster updates but slightly higher resource usage.
- `TEXT_COLOR`: Sets the color of the displayed text. Use standard color names (e.g., `"white"`, `"black"`, `"lime"`) or hex codes (e.g., `"#FF0000"` for red). (Default: `"white"`).
- `DEFAULT_CORNER`: Determines the initial screen corner where the widget appears. Options are `"top-right"` or `"top-left"`. (Default: `"top-right"`).
- `CORNER_MARGIN`: Sets the padding (in pixels) between the widget and the screen edges when initially positioned. (Default: `10`).

## Usage

- **Moving:** Click anywhere on the widget with the left mouse button and drag it to the desired position.
- **Closing:** Right-click anywhere on the widget to open a context menu, then select "Close Widget".

## Notes

- **Platform Behavior:** While using cross-platform libraries, the visual appearance and behavior of frameless, transparent windows can sometimes vary between operating systems (Windows, macOS, Linux).
- **Click-Through:** Clicks on the transparent background area of the widget will _not_ pass through to the desktop or windows underneath it.
- **Resource Usage:** The widget polls system information periodically and will consume a small amount of CPU and memory.

---

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">
<div align="center">
  <a href="https://seperet.com">
    <img src=https://github.com/denv3rr/denv3rr/blob/main/Seperet_Slam_White.gif/>
  </a>
</div>
<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif">
