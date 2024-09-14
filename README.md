# Image Process by Local Machine

This project is designed to create a tool for processing images on a local terminal. It is built with a GUI based on PySide6.

## Update plan

### support new process

- [ ] Support new process
  - [X] Remove Background -> [Code Source](https://github.com/danielgatis/rembg)
  - [ ] Rotate
  - [ ] Image shift
  - [ ] Crop

- [ ] Graphic User Interface
  - [ ] Edit image process for each images.

## Install

~~ If you want to use it without any installation, you can download the executable file from the [following path.](./) ~~

~~ However, please note that the initial execution of this executable file is very slow. ~~

### For window (powershell)

1. Install python (If you have previously installed Python, you can skip this step.)

    - Open the "Microsoft Store"
    - Search for "Python"
    - Select and install Python (recommend version 3.10 or higher)

2. Install Module Package  
    After launching PowerShell, navigate to the repository and enter the following command.

    ``` powershell
    pip install -r requirements.txt
    ```

3. Enter the execution command.

    ``` powershell
    python .\app.py
    ```
