Anime Player
A modern, Material 3-inspired GUI application for streaming anime using ani-cli. Built with Python and Tkinter, this application offers a visually appealing interface with dynamic theming, accessibility features, and a smooth user experience.
Features

Search and Play Anime: Easily search for anime titles and stream episodes using ani-cli.
Material 3 Design: A bold, expressive UI inspired by Google's Material 3 (Material You) design system, featuring:
Dynamic color theming with pre-defined palettes (Teal, Purple, Amber) and a custom color picker.
Modern typography with the Roboto font (falls back to Arial if unavailable).
Card-like surfaces with simulated elevation for a polished look.


Progress Bar: Visual feedback with a loading progress bar when selecting an episode.
Accessibility: High-contrast mode toggle for improved readability.
Quality Selection: Choose streaming quality (e.g., "best", "1080", "720").
Playback Controls: Play, replay, change quality, and quit playback with intuitive buttons.
Debug Logging: A log area displays detailed debug information for troubleshooting.

Screenshots
Coming soon!
Requirements

Python 3.6+: Ensure Python is installed on your system.
Tkinter: Comes pre-installed with Python on most systems. If not, install it:
On Windows: Tkinter is included with Python.
On Linux: sudo apt-get install python3-tk
On macOS: Tkinter is typically included with Python.


Git Bash: Required to run ani-cli commands (Windows users).
Download and install from git-scm.com.


ani-cli: A command-line tool for streaming anime.
Install using Scoop (Windows) or your package manager:scoop install ani-cli


Or follow the instructions at ani-cli GitHub.


Roboto Font (Optional): For the best visual experience, install the Roboto font on your system.
Download from Google Fonts and install.



Installation

Clone the Repository:
git clone https://github.com/your-username/anime-player.git
cd anime-player


Install Dependencies:Ensure Python, Tkinter, Git Bash, and ani-cli are installed as per the requirements above.

Update Paths in gui_update.py:

Open gui_update.py and update the following paths to match your system:self.git_bash_path = r"C:\\Program Files\\Git\\bin\\bash.exe"
self.ani_cli_path = r"/c/Users/Victus/scoop/apps/ani-cli/current/ani-cli"


Replace C:\\Program Files\\Git\\bin\\bash.exe with your Git Bash installation path.
Replace /c/Users/Victus/scoop/apps/ani-cli/current/ani-cli with your ani-cli path.



Usage

Run the Application:
python gui_update.py

Or on Windows:
& C:/path/to/python.exe gui_update.py


Search for Anime:

Enter an anime title in the search bar (e.g., "1P") and click "Search".
Select an anime from the list to fetch episodes.


Select an Episode:

A dialog will appear listing available episodes.
Choose an episode (e.g., "Episode 8") and click "Select".
A progress bar will show loading progress before playback starts.


Customize the Theme:

Use the dropdown in the top bar to switch between "Teal", "Purple", "Amber", or "Custom" themes.
Select "Custom" to pick your own primary color using the color chooser.
Toggle high-contrast mode for better readability.


Control Playback:

Play: Start streaming the selected episode.
Replay: Replay the last selected episode.
Change Quality: Adjust streaming quality (e.g., "best", "1080").
Quit: Stop playback if an episode is currently playing.



Troubleshooting

Progress Bar Not Showing:
Ensure the episode selection dialog is working correctly. If the dialog closes prematurely, check for Tkinter threading issues.


Theme Not Applying:
Verify that the apply_theme method is updating all widgets. Restart the app after changing themes if needed.


ani-cli Errors:
Check the log area for debug messages. Ensure ani-cli is installed and accessible in your system’s PATH.
Update the ani_cli_path in the script to match your installation.


Font Issues:
If the Roboto font isn’t available, the UI will fall back to Arial. Install Roboto for the intended design.



Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. Ensure your code follows the existing style and doesn’t break core functionality.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

ani-cli: For providing the backend functionality to stream anime.
Material 3: For the design inspiration.
Tkinter: For the GUI framework.

Last updated: June 03, 2025
