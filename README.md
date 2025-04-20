# Gemini Multimodal Playground 🤖🎤📹

A desktop application built with Python and Tkinter that allows real-time, bidirectional voice conversations with Google's Gemini large language models. It supports optional video input (camera or screen sharing) and features various configurable "modes" with distinct personalities and parameters.

## Features

*   **Real-time Voice Interaction:** Speak directly to Gemini and hear its responses streamed back.
*   **Multimodal Input:** Optionally send video frames from your camera or screen along with your voice.
*   **Configurable Modes:** Choose from various preset modes (e.g., "Analytical Genius", "Dark Philosopher", "Just a Joker", "Code Expert") which define the system prompt and model parameters (temperature, top_p, top_k).
*   **Voice Selection:** Choose different voices for Gemini's audio output.
*   **Voice Activity Detection (VAD):** Uses Silero VAD to detect speech, reducing unnecessary data transmission.
*   **Audio Input Visualization:** A real-time equalizer visualizes your microphone input.
*   **Interruption Control:** Option to allow speaking over Gemini's response (interruptions).
*   **Dark Theme GUI:** A modern, dark-themed interface built with Tkinter.
*   **Easy Configuration:** Simple setup using a `.env` file for your API key.

## Requirements

*   Python 3.8+
*   `pip` (Python package installer)
*   A Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))
*   Microphone access
*   (Optional) Camera access or Screen Recording permissions for video modes.
*   (Potentially) System libraries for PyAudio (like `portaudio`). See [PyAudio documentation](https://people.csail.mit.edu/hubert/pyaudio/) for platform-specific requirements if you encounter installation issues.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    python-dotenv
    websockets
    pyaudio
    numpy
    torch
    torchaudio # Ensure compatibility with torch version if needed
    opencv-python
    Pillow
    mss
    # tkinter is usually built-in with Python
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Installing PyTorch (`torch`, `torchaudio`) might take some time and disk space. If you encounter issues with Silero VAD, check the [Silero VAD repository](https://github.com/snakers4/silero-vad) for specific version compatibility.*

## Configuration

1.  Create a file named `.env` in the root directory of the project.
2.  Add your Gemini API key to the `.env` file:
    ```env
    GEMINI_API_KEY=YOUR_API_KEY_HERE
    ```
    Replace `YOUR_API_KEY_HERE` with your actual API key.

## Usage

1.  Make sure your virtual environment is activated.
2.  Run the application:
    ```bash
    python standalone.py
    ```
3.  The GUI window will appear.
4.  **Configure your session:**
    *   **Mode:** Select the desired Gemini personality/mode from the dropdown. The system prompt and model parameters will update automatically.
    *   **Voice:** Choose the voice for Gemini's audio output.
    *   **Video Mode:** Select 'none', 'camera', or 'screen' if you want to send video input.
    *   **Allow Interruptions:** Check this box if you want to be able to speak while Gemini is responding.
5.  **Start the connection:** Click the "▶️ Start Gemini" button.
6.  **Interact:** Once the status shows "Connected!", speak into your microphone. The equalizer should react to your voice. Gemini will process your input and respond with audio.
7.  **Stop the connection:** Click the "⏹️ Stop Gemini" button to disconnect and clean up resources.

## Available Modes

The application includes several preset modes, each with a unique system prompt and fine-tuned parameters:

*   **Analytical Genius:** Logical, step-by-step reasoning.
*   **Dark Philosopher:** Cynical, explores deeper/darker themes.
*   **Scientific Maverick:** Unconventional, pushes scientific boundaries.
*   **Just a Joker:** Hilarious, dark, twisted, and unpredictable humor.
*   **Streetwear Fashion Designer:** Edgy, urban fashion focus.
*   **Ladies Fashion Designer:** Creative, practical women's fashion insights.
*   **Code Expert:** Provides coding solutions and explanations.
*   **Business Consultant:** Actionable business strategies and analysis.
*   **CPA Accountant Tutor:** Quiz-based CPA exam preparation tutor.
*   **General Tutor:** Versatile tutor across various subjects.
*   **Hypebeast:** Edgy, hippy-influenced streetwear advisor.
*   **Guided Meditation:** Calm, wise life advice rooted in mindfulness principles.

*(Feel free to customize these modes or add your own in `config_gui.py`!)*

## Troubleshooting

*   **Audio Issues:** If you have problems with microphone input or audio output, ensure the correct devices are selected in your operating system's sound settings. Check PyAudio documentation for platform-specific troubleshooting.
*   **VAD Issues:** If speech isn't being detected correctly, you might need to adjust the `speech_prob` threshold within the `is_speech` method in `voice_activity_detector.py`.
*   **Connection Errors:** Verify your `GEMINI_API_KEY` is correct and active. Check your internet connection.

---

Enjoy your conversations with Gemini!
