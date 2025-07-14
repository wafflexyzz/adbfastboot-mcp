import os
import sys
import yaml
from mcp.server.fastmcp import FastMCP, Image

from adbdevicemanager import AdbDeviceManager
from fastbootdevicemanager import FastbootDeviceManager

CONFIG_FILE = "config.yaml"
CONFIG_FILE_EXAMPLE = "config.yaml.example"

# Azure OpenAI config (o4-mini)
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = "https://matth-mbfouljr-swedencentral.cognitiveservices.azure.com/"
AZURE_OPENAI_DEPLOYMENT = "o4-mini"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"

# Utility: Call Azure OpenAI chat completion

def call_azure_openai(messages):
    if not AZURE_OPENAI_KEY:
        return "Error: AZURE_OPENAI_KEY environment variable not set."
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
        )
        response = client.chat.completions.create(
            messages=messages,
            max_completion_tokens=512,
            model=AZURE_OPENAI_DEPLOYMENT
        )
        content = response.choices[0].message.content
        
        # Debug: Log what we're getting back
        if not content:
            return f"Error: Azure OpenAI returned None/empty content. Response object: {response.choices[0]}"
        
        return content
    except Exception as e:
        return f"LLM API Error: {e}"

# Load config (make config file optional)
config = {}
device_name = None

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f.read()) or {}
        device_config = config.get("device", {})
        configured_device_name = device_config.get(
            "name") if device_config else None

        # Support multiple ways to specify auto-selection:
        # 1. name: null (None in Python)
        # 2. name: "" (empty string)
        # 3. name field completely missing
        if configured_device_name and configured_device_name.strip():
            device_name = configured_device_name.strip()
            print(f"Loaded config from {CONFIG_FILE}")
            print(f"Configured device: {device_name}")
        else:
            print(f"Loaded config from {CONFIG_FILE}")
            print(
                "No device specified in config, will auto-select if only one device connected")
    except Exception as e:
        print(f"Error loading config file {CONFIG_FILE}: {e}", file=sys.stderr)
        print(
            f"Please check the format of your config file or recreate it from {CONFIG_FILE_EXAMPLE}", file=sys.stderr)
        sys.exit(1)
else:
    print(
        f"Config file {CONFIG_FILE} not found, using auto-selection for device")

# Initialize MCP only (no device managers yet)
mcp = FastMCP("android")

@mcp.tool()
def get_packages() -> str:
    try:
        deviceManager = AdbDeviceManager(device_name)
        return deviceManager.get_packages()
    except Exception as e:
        return f"ADB Error: {e}"

@mcp.tool()
def execute_adb_shell_command(command: str) -> str:
    try:
        deviceManager = AdbDeviceManager(device_name)
        return deviceManager.execute_adb_shell_command(command)
    except Exception as e:
        return f"ADB Error: {e}"

@mcp.tool()
def get_uilayout() -> str:
    try:
        deviceManager = AdbDeviceManager(device_name)
        return deviceManager.get_uilayout()
    except Exception as e:
        return f"ADB Error: {e}"

@mcp.tool()
def get_screenshot() -> Image:
    try:
        deviceManager = AdbDeviceManager(device_name)
        deviceManager.take_screenshot()
        return Image(path="compressed_screenshot.png")
    except Exception as e:
        return Image(path="")  # Return empty image path on error

@mcp.tool()
def get_package_action_intents(package_name: str) -> list[str]:
    try:
        deviceManager = AdbDeviceManager(device_name)
        return deviceManager.get_package_action_intents(package_name)
    except Exception as e:
        return [f"ADB Error: {e}"]

# --- Fastboot Endpoints ---

@mcp.tool()
def list_fastboot_devices() -> list[str]:
    try:
        return FastbootDeviceManager.get_available_devices()
    except Exception as e:
        return [f"Fastboot Error: {e}"]

@mcp.tool()
def execute_fastboot_command(command: str) -> str:
    try:
        fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
        return fastbootManager.execute_fastboot_command(command)
    except Exception as e:
        return f"Fastboot Error: {e}"

# --- Fastboot OEM Commands ---

ALLOWED_OEM_COMMANDS = [
    "BT",
    "ETHER",
    "MB_SN",
    "SYS_SN",
    "WIFI",
    "abl-version",
    "allow_unlock",
    "checkslc",
    "device-info",
    "disable-charger-screen",
    "enable-charger-screen",
    "lock_all",
    "mlc2slc",
    "off-mode-charge",
    "rebootedl",
    "remaining_reboot",
    "scanner",
    "select-display-panel",
    "shipmode",
    "sku",
    "timestamp",
    "unlock_all",
    "update",
    "veritymode",
    "wan",
]

@mcp.tool()
def execute_fastboot_oem_command(oem_command: str, extra_args: str = "") -> str:
    """
    Executes an allowed OEM fastboot command. Only whitelisted commands are permitted.
    Args:
        oem_command (str): The OEM command to execute (e.g. 'device-info')
        extra_args (str): Any extra arguments for the command (optional)
    Returns:
        str: The output of the fastboot OEM command, or an error if not allowed
    """
    if oem_command not in ALLOWED_OEM_COMMANDS:
        return f"Error: '{oem_command}' is not an allowed OEM fastboot command."
    try:
        fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
        cmd = f"oem {oem_command} {extra_args}".strip()
        return fastbootManager.execute_fastboot_command(cmd)
    except Exception as e:
        return f"Fastboot Error: {e}"

@mcp.tool()
def fastboot_oem_update(update_file: str) -> str:
    """
    Executes 'fastboot oem update <file>' to update the device firmware or partition.
    Args:
        update_file (str): The path to the update file to flash
    Returns:
        str: The output of the fastboot oem update command, or an error message
    """
    if not update_file:
        return "Error: update_file argument is required."
    try:
        fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
        cmd = f"oem update {update_file}"
        return fastbootManager.execute_fastboot_command(cmd)
    except Exception as e:
        return f"Fastboot Error: {e}"

@mcp.tool()
def fastboot_oem_update_avb(avb_args: str) -> str:
    """
    Executes 'fastboot oem update avb <args>' for AVB (Android Verified Boot) update operations.
    Args:
        avb_args (str): The AVB subcommand and arguments (e.g., 'disable-verification')
    Returns:
        str: The output of the fastboot oem update avb command, or an error message
    """
    if not avb_args:
        return "Error: avb_args argument is required."
    try:
        fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
        cmd = f"oem update avb {avb_args}"
        return fastbootManager.execute_fastboot_command(cmd)
    except Exception as e:
        return f"Fastboot Error: {e}"

@mcp.tool()
def llm_unlock_bootloader(start: bool = True) -> str:
    """
    LLM-driven agent to unlock the bootloader using both ADB and fastboot, with trial and error, reboots, and adaptive logic.
    Zebra TC52-specific logic is used if detected. Requires user confirmation for destructive actions.
    Set AZURE_OPENAI_KEY in your environment for LLM reasoning.
    Args:
        start (bool): Set to True to begin the unlock process.
    Returns:
        str: Progress, reasoning, and results at each step.
    """
    if not start:
        return "Send 'start=True' to begin the bootloader unlock agent."

    # Step 1: Detect device info
    try:
        fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
        product = fastbootManager.execute_fastboot_command("getvar product")
        device_info = fastbootManager.execute_fastboot_command("oem device-info")
    except Exception as e:
        return f"Fastboot Error: {e}"
    is_tc52 = "TC52" in product or "TC52" in device_info
    history = []
    state = "start"
    unlocked = False
    step = 0
    max_steps = 20
    response = f"Device info:\n{product}\n{device_info}\n\n"
    zebra_oem_unlock_cmds = [
        "oem allow_unlock",
        "oem unlock",
        "oem device-info",
        "oem checkslc",
        "oem update",
        "oem veritymode",
        "oem BT",
        "oem ETHER",
        "oem MB_SN",
        "oem SYS_SN",
        "oem WIFI",
        "oem abl-version",
        "oem lock_all",
        "oem mlc2slc",
        "oem off-mode-charge",
        "oem rebootedl",
        "oem remaining_reboot",
        "oem scanner",
        "oem select-display-panel",
        "oem shipmode",
        "oem sku",
        "oem timestamp",
        "oem unlock_all",
        "oem wan",
    ]
    # Step 2: LLM-driven loop
    while not unlocked and step < max_steps:
        # Prepare LLM prompt
        messages = [
            {"role": "system", "content": "You are an expert in Android device bootloader unlocking. You must respond with valid JSON only. The device is a Zebra TC52 running Android 8 (Oreo). Use both ADB and fastboot commands. Prefer Zebra-specific OEM commands if available. Always mark destructive actions (unlock, lock, wipe, flash, etc.) as destructive:true."},
            {"role": "user", "content": f"Device info:\n{product}\n{device_info}\n\nPrevious commands tried:\n{history}\n\nAnalyze the device state and provide the next command to unlock the bootloader. You must respond with ONLY a JSON object in this exact format:\n{{\n  \"command\": \"the exact fastboot or adb command\",\n  \"reasoning\": \"brief explanation of why this command\",\n  \"destructive\": true or false\n}}\n\nAvailable Zebra OEM commands: {zebra_oem_unlock_cmds}\nRespond with JSON only, no other text."}
        ]
        llm_response = call_azure_openai(messages)
        
        # Debug: Check if response is empty
        if not llm_response or llm_response.strip() == "":
            return f"LLM returned empty response. This may be a model configuration issue."
        
        # Parse LLM response (expecting JSON)
        import json
        try:
            # Clean the response and try to parse
            cleaned_response = llm_response.strip()
            if not cleaned_response.startswith('{'):
                # Try to extract JSON from the response
                start_idx = cleaned_response.find('{')
                end_idx = cleaned_response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    cleaned_response = cleaned_response[start_idx:end_idx]
                else:
                    return f"LLM response doesn't contain valid JSON format.\nRaw response: {llm_response}"
            
            parsed = json.loads(cleaned_response)
            proposed_command = parsed.get("command", "")
            reasoning = parsed.get("reasoning", "")
            destructive = parsed.get("destructive", False)
            
            if not proposed_command:
                return f"LLM didn't provide a command.\nRaw response: {llm_response}"
                
        except Exception as e:
            return f"LLM response parse error: {e}\nRaw response: {llm_response}"
        # Ask for confirmation if destructive
        if destructive:
            return f"Step {step}: {reasoning}\nProposed command: {proposed_command}\nThis is a destructive action (may wipe data or affect device).\nReply with 'llm_unlock_bootloader_confirm(step={step}, command=\"{proposed_command}\")' to proceed."
        # Run the command
        if proposed_command.startswith("adb "):
            try:
                deviceManager = AdbDeviceManager(device_name)
                output = deviceManager.execute_adb_shell_command(proposed_command[4:])
            except Exception as e:
                output = f"ADB Error: {e}"
        else:
            try:
                fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
                output = fastbootManager.execute_fastboot_command(proposed_command)
            except Exception as e:
                output = f"Fastboot Error: {e}"
        history.append((proposed_command, output))
        response += f"Step {step}: {reasoning}\nCommand: {proposed_command}\nOutput: {output}\n\n"
        if "unlocked: true" in output or "already unlocked" in output:
            unlocked = True
            response += "Bootloader is unlocked!"
            break
        step += 1
    if not unlocked:
        response += "Unable to unlock bootloader after several attempts. See history for details."
    return response

@mcp.tool()
def llm_unlock_bootloader_confirm(step: int, command: str) -> str:
    """
    Confirms and executes the destructive command proposed by llm_unlock_bootloader at the given step.
    Args:
        step (int): The step number to confirm and execute.
        command (str): The command to execute.
    Returns:
        str: The output of the destructive command and next reasoning.
    """
    try:
        if command.startswith("adb "):
            deviceManager = AdbDeviceManager(device_name)
            output = deviceManager.execute_adb_shell_command(command[4:])
        else:
            fastbootManager = FastbootDeviceManager(device_name, exit_on_error=False)
            output = fastbootManager.execute_fastboot_command(command)
    except Exception as e:
        output = f"Command Error: {e}"
    response = f"Confirmed step {step}:\nCommand: {command}\nOutput: {output}\n"
    if "unlocked: true" in output or "already unlocked" in output:
        response += "Bootloader is unlocked!"
    else:
        response += "Continue with 'llm_unlock_bootloader(start=True)' to proceed."
    return response

if __name__ == "__main__":
    mcp.run(transport="stdio")
