# Installation

BioPAP is a Python-based preprocessing pipeline that requires **Python 3.9 or higher** and **Jupyter Notebook/Lab**. 

!!! info "Choose One Installation Method"

    Select **either** the command-line method **or** the Anaconda method below, not both. Both will successfully install BioPAP and its requirements.
    
    - **Command Line (Recommended):** Standard development practice, easier to troubleshoot if issues occur
    - **Anaconda:** Simpler GUI-based approach for users unfamiliar with terminals

---

## Install from Command Line

This method guides you through installing Python, pip, Jupyter, and BioPAP directly using terminal commands.

=== ":material-linux: Linux"

    **Step 1: Check Python and pip**

    Verify that Python 3.9+ and pip are installed:

    ```bash
    python3 --version
    pip3 --version
    ```

    If not installed or version is too old, run:

    ```bash
    sudo apt-get update
    sudo apt-get install python3.11 python3-pip
    ```

    **Step 2: Install Jupyter Notebook**

    ```bash
    pip3 install notebook jupyter
    ```

    **Step 3: Install BioPAP**

    Clone the repository and install BioPAP in development mode:

    ```bash
    git clone https://github.com/your-repo/BioPAP.git
    cd BioPAP
    pip3 install -e .
    ```

    **Step 4: Verify Installation**

    ```bash
    python3 --version
    jupyter --version
    python3 -c "import biopap; print(biopap.__version__)"
    ```

=== ":material-apple: macOS"

    **Step 1: Check Python and pip**

    Check if Python 3.9+ and pip are installed:

    ```bash
    python3 --version
    pip3 --version
    ```

    If not installed, install using **Homebrew**:

    ```bash
    brew update
    brew install python@3.11
    ```

    **Step 2: Install Jupyter Notebook**

    ```bash
    pip3 install notebook jupyter
    ```

    **Step 3: Install BioPAP**

    Clone the repository and install BioPAP in development mode:

    ```bash
    git clone https://github.com/your-repo/BioPAP.git
    cd BioPAP
    pip3 install -e .
    ```

    **Step 4: Verify Installation**

    ```bash
    python3 --version
    jupyter --version
    python3 -c "import biopap; print(biopap.__version__)"
    ```

=== ":material-microsoft-windows: Windows"

    **Step 1: Check Python and pip**

    Open **Command Prompt** and verify Python 3.9+ and pip are installed:

    ```bash
    python --version
    pip --version
    ```

    If not installed, download the installer from [python.org](https://www.python.org/downloads/). **Important:** During installation, check the box **"Add Python to PATH"**.

    After installation, verify in Command Prompt:

    ```bash
    python --version
    pip --version
    ```

    **Step 2: Install Jupyter Notebook**

    ```bash
    pip install notebook jupyter
    ```

    **Step 3: Install BioPAP**

    Clone the repository and install BioPAP in development mode:

    ```bash
    git clone https://github.com/your-repo/BioPAP.git
    cd BioPAP
    pip install -e .
    ```

    **Step 4: Verify Installation**

    ```bash
    python --version
    jupyter --version
    python -c "import biopap; print(biopap.__version__)"
    ```

---

## Install with Anaconda

**Anaconda** is a package manager with a graphical interface (Anaconda Navigator) that makes installation possible with minimal usage of the command line. Download it from the [Anaconda website](https://www.anaconda.com/download/).

=== ":material-linux: Linux"

    **Step 1: Install Anaconda**

    1. Download the Anaconda installer and run it.
    2. Follow the installer prompts and accept the defaults.
    3. Close and reopen your terminal when finished.

    **Step 2: Open Anaconda Navigator**

    1. Search for "Anaconda Navigator" in your applications menu and open it.
    2. Wait for it to load (this might take a minute).

    **Step 3: Install Jupyter**

    1. In Anaconda Navigator, look for "Jupyter Notebook" in the home tab.
    2. Click the **Launch** button next to Jupyter Notebook.
    3. Jupyter will open in your web browser.

    **Step 4: Install BioPAP**

    1. Open a terminal and navigate to where you want to store BioPAP:
        ```bash
        git clone https://github.com/your-repo/BioPAP.git
        cd BioPAP
        pip install -e .
        ```

    **Step 5: Open the Example Notebook**

    1. In Jupyter (which should still be open in your browser), navigate to the BioPAP folder you just cloned.
    2. Open the folder: `examples`
    3. Click on `pipeline.ipynb` to open the example notebook.
    4. You're ready to start using BioPAP!

=== ":material-apple: macOS"

    **Step 1: Install Anaconda**

    1. Download and run the Anaconda installer.
    2. Follow the installer prompts with default settings.
    3. Close and reopen your terminal when finished.

    **Step 2: Open Anaconda Navigator**

    1. Look for "Anaconda Navigator" in your Applications folder and open it.
    2. Wait for it to load (this might take a minute).

    **Step 3: Install Jupyter**

    1. In Anaconda Navigator, find "Jupyter Notebook" in the home tab.
    2. Click the **Launch** button next to Jupyter Notebook.
    3. Jupyter will open in your web browser.

    **Step 4: Install BioPAP**

    1. Open a terminal and navigate to where you want to store BioPAP:
        ```bash
        git clone https://github.com/your-repo/BioPAP.git
        cd BioPAP
        pip install -e .
        ```

    **Step 5: Open the Example Notebook**

    1. In Jupyter (which should still be open in your browser), navigate to the BioPAP folder you just cloned.
    2. Open the folder: `examples`
    3. Click on `pipeline.ipynb` to open the example notebook.
    4. You're ready to start using BioPAP!

=== ":material-microsoft-windows: Windows"

    **Step 1: Install Anaconda**

    1. Download the Anaconda installer (.exe) and double-click to run it.
    2. Follow the installer steps with default settings.
    3. **Important:** Check the box **"Register Anaconda3 as my default Python 3.x"** at the Advanced Installation Options.
    4. Close and reopen **Command Prompt** when finished.

    **Step 2: Open Anaconda Navigator**

    1. Click the **Start** menu and search for "Anaconda Navigator".
    2. Click to open Anaconda Navigator.
    3. Wait for it to load (this might take a minute).

    **Step 3: Install Jupyter**

    1. In Anaconda Navigator, find "Jupyter Notebook" in the home tab.
    2. Click the **Launch** button next to Jupyter Notebook.
    3. Jupyter will open in your web browser.

    **Step 4: Install BioPAP**

    1. Open **Command Prompt** and navigate to where you want to store BioPAP:
        ```bash
        git clone https://github.com/your-repo/BioPAP.git
        cd BioPAP
        pip install -e .
        ```

    **Step 5: Open the Example Notebook**

    1. In Jupyter (which should still be open in your browser), navigate to the BioPAP folder you just cloned.
    2. Open the folder: `examples`
    3. Click on `pipeline.ipynb` to open the example notebook.
    4. You're ready to start using BioPAP!

---

## Next Steps

- Read the [Building a Pipeline Tutorial](tutorials/building_pipeline.md) to learn how to set up a preprocessing pipeline.
- Check the [Configuration Tutorial](tutorials/configuration.md) to understand how to customize module parameters.
- Explore the [Modules API Documentation](api/) for detailed information about each module.
    
