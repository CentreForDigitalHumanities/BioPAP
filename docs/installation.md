# Installation

This project uses **Python** and **Jupyter Notebooks**. Follow one of the installation methods below. We recommend you to install via the command line with the operation system that you use. If you prefer a simpler, guided installation you can use the Anaconda installation method.

---
## Install from Command Line



=== ":material-linux: Linux"

    **1. Install Python and pip (Linux)**

    Check if Python and pip are already installed, and check the version:

    ```bash
    python3 --version
    pip3 --version
    ```

    If Python or pip is not installed, or the version is lower than the required minimal version (`python3.?`), run:

    ```bash
    sudo apt-get update
    sudo apt-get install python3-pip
    ```

    **2. Install Jupyter Notebook**

    ```bash
    pip3 install notebook
    ```

    **3. Verify the installations**

    ```bash
    python3 --version
    pip3 --version
    jupyter-notebook --version
    ```

=== ":material-apple: macOS"

    **1. Install Python and pip**

    Check if Python and pip are already installed, and check the version:

    ```bash
    python3 --version
    pip3 --version
    ```

    If Python is not installed, install it using **Homebrew**:

    ```bash
    brew update
    brew install python
    ```

    **2. Install Jupyter Notebook**

    ```bash
    pip3 install notebook
    ```

    **3. Verify the installations**

    ```bash
    python3 --version
    pip3 --version
    jupyter-notebook --version
    ```

=== ":material-microsoft-windows: Windows"

    **1. Install Python and pip**

    First check if Python and pip are already installed:

    ```bash
    python3 --version
    pip3 --version
    ```

    If Python is not installed, download it from:

    https://www.python.org/downloads/

    Run the installer and make sure to enable:

    "Add Python to PATH"

    After installation, open **Command Prompt** again and verify that Python and pip are available:

    ```bash
    python3 --version
    pip3 --version
    ```

    **2. Install Jupyter Notebook**

    ```bash
    pip install notebook
    ```

    **3. Verify the installation**

    ```bash
    jupyter-notebook --version
    ```
---

## Install with Anaconda

