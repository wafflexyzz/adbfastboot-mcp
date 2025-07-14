# ADB/Fastboot MCP Server

An MCP (Model Context Protocol) server that provides programmatic control over
Android devices through ADB (Android Debug Bridge) and Fastboot. This server exposes
various Android device management capabilities that can be accessed by MCP
clients like [Claude desktop](https://modelcontextprotocol.io/quickstart/user)
and Code editors
(e.g. [Cursor](https://docs.cursor.com/context/model-context-protocol))

## Features

- 🔧 **Advanced ADB Command Execution** with comprehensive error handling
- ⚡ **Fastboot Command Execution** with OEM command support
- 📸 **Device Screenshot Capture** with automatic image compression
- 🎯 **UI Layout Analysis** with clickable element detection and parsing
- 📱 **Device Package Management** including action intent discovery
- 🚀 **Automatic Device Selection** when only one device is connected
- ⚙️ **Flexible Configuration** with optional config file
- 🧪 **Comprehensive Testing Suite** with unit and integration tests
- 📝 **Enhanced Documentation** with detailed docstrings and type hints
- 🤖 **LLM-Driven Bootloader Unlock Agent** with Azure OpenAI integration
- 🔓 **Zebra TC52 Specialized Support** with device-specific unlock strategies

## Prerequisites

- Python 3.11+
- ADB (Android Debug Bridge) installed and configured
- Fastboot installed and configured  
- Android device with USB debugging enabled
- Azure OpenAI API key (for LLM unlock agent)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/minhalvp/adbfastboot-mcp.git
cd adbfastboot-mcp
```

2. Install dependencies:
This project uses [uv](https://github.com/astral-sh/uv) for project
management via various methods of
[installation](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv python install 3.11
uv sync
```

3. Set up Azure OpenAI (optional, for LLM unlock agent):

```bash
export AZURE_OPENAI_KEY='your-azure-openai-key-here'
```

## Configuration

The server supports flexible device configuration with multiple usage scenarios.

### Device Selection Modes

**1. Automatic Selection (Recommended for single device)**

- No configuration file needed
- Automatically connects to the only connected device
- Perfect for development with a single test device
- Enhanced error messages when multiple devices are detected

**2. Manual Device Selection**

- Use when you have multiple devices connected
- Specify exact device in configuration file
- Robust error handling for device not found scenarios

### Configuration File (Optional)

The configuration file (`config.yaml`) is **optional**. If not present, the server will automatically select the device if only one is connected.

#### For Automatic Selection

Simply ensure only one device is connected and run the server - no configuration needed!

#### For Manual Selection

1. Create a configuration file:

```bash
cp config.yaml.example config.yaml
```

2. Edit `config.yaml` and specify your device:

```yaml
device:
  name: "your-device-serial-here" # Device identifier from 'adb devices'
```

**For auto-selection**, you can use any of these methods:

```yaml
device:
  name: null              # Explicit null (recommended)
  # name: ""              # Empty string  
  # name:                 # Or leave empty/comment out
```

### Finding Your Device Serial

To find your device identifier, run:

```bash
adb devices
fastboot devices
```

Example output:

```
List of devices attached
13b22d7f        device
emulator-5554   device
```

Use the first column value (e.g., `13b22d7f` or `emulator-5554`) as the device name.

### Usage Scenarios

| Scenario | Configuration Required | Behavior |
|----------|----------------------|----------|
| Single device connected | None | ✅ Auto-connects to the device |
| Multiple devices, want specific one | `config.yaml` with `device.name` | ✅ Connects to specified device |
| Multiple devices, no config | None | ❌ Shows error with available devices |
| No devices connected | N/A | ❌ Shows "no devices" error |

**Note**: If you have multiple devices connected and don't specify which one to use, the server will show an error message listing all available devices.

## Usage

An MCP client is needed to use this server. The Claude Desktop app is an example
of an MCP client. To use this server with Claude Desktop:

1. Locate your Claude Desktop configuration file:

   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the ADB/Fastboot MCP server configuration to the `mcpServers` section:

```json
{
  "mcpServers": {
    "adbfastboot-mcp": {
      "command": "path/to/uv",
      "args": ["--directory", "path/to/adbfastboot-mcp", "run", "server.py"],
      "env": {
        "AZURE_OPENAI_KEY": "your-azure-openai-key-here"
      }
    }
  }
}
```

Replace:

- `path/to/uv` with the actual path to your `uv` executable
- `path/to/adbfastboot-mcp` with the absolute path to where you cloned this repository
- `your-azure-openai-key-here` with your actual Azure OpenAI API key

### Available Tools

The server exposes the following tools with enhanced functionality:

#### ADB Tools

```python
def get_packages() -> str:
    """
    Get all installed packages on the device.
    
    Enhanced features:
    - Comprehensive error handling
    - Auto-retry logic for connection issues
    
    Returns:
        str: A list of all installed packages on the device as a string
    """
```

```python
def execute_adb_shell_command(command: str) -> str:
    """
    Executes an ADB shell command and returns the output or an error.
    
    Enhanced features:
    - Robust error handling and cleanup
    - Input validation and sanitization
    - Detailed error messages
    
    Args:
        command (str): The ADB shell command to execute
    Returns:
        str: The output of the ADB command
    """
```

```python
def get_uilayout() -> str:
    """
    Retrieves information about clickable elements in the current UI.
    
    Enhanced features:
    - Advanced XML parsing with error recovery
    - Center coordinate calculation for elements
    - Detailed element property extraction
    - Temporary file cleanup
    
    Returns a formatted string containing details about each clickable element,
    including their text, content description, bounds, and center coordinates.

    Returns:
        str: A formatted list of clickable elements with their properties
    """
```

```python
def get_screenshot() -> Image:
    """
    Takes a screenshot of the device and returns it.
    
    Enhanced features:
    - Automatic image compression (30% scale factor)
    - Configurable output paths
    - Resource cleanup and error handling
    - Support for different image formats
    
    Returns:
        Image: the compressed screenshot
    """
```

```python
def get_package_action_intents(package_name: str) -> list[str]:
    """
    Get all non-data actions from Activity Resolver Table for a package.
    
    Enhanced features:
    - Input validation
    - Comprehensive error handling
    - Detailed activity intent parsing
    
    Args:
        package_name (str): The name of the package to get actions for
    Returns:
        list[str]: A list of all non-data actions from the Activity Resolver
        Table for the package
    """
```

#### Fastboot Tools

```python
def list_fastboot_devices() -> list[str]:
    """
    List all connected fastboot devices.
    
    Returns:
        list[str]: List of fastboot device serials
    """
```

```python
def execute_fastboot_command(command: str) -> str:
    """
    Executes a fastboot command and returns the output or an error.
    
    Args:
        command (str): The fastboot command to execute (without 'fastboot' prefix)
    Returns:
        str: The output of the fastboot command
    """
```

```python
def execute_fastboot_oem_command(oem_command: str, extra_args: str = "") -> str:
    """
    Executes an allowed OEM fastboot command. Only whitelisted commands are permitted.
    
    Supported OEM commands:
    - allow_unlock, unlock_all, lock_all
    - device-info, sku, timestamp
    - enable-charger-screen, disable-charger-screen
    - mlc2slc, checkslc, veritymode
    - rebootedl, shipmode, remaining_reboot
    - scanner, wan, update
    
    Args:
        oem_command (str): The OEM command to execute (e.g. 'device-info')
        extra_args (str): Any extra arguments for the command (optional)
    Returns:
        str: The output of the fastboot OEM command, or an error if not allowed
    """
```

#### LLM-Driven Bootloader Unlock Agent

```python
def llm_unlock_bootloader(start: bool = True) -> str:
    """
    LLM-driven agent to unlock the bootloader using both ADB and fastboot.
    
    Features:
    - Uses Azure OpenAI (o4-mini) for intelligent reasoning
    - Zebra TC52-specific logic and OEM commands
    - Trial and error with adaptive logic
    - Requires user confirmation for destructive actions
    - Maintains full history for context and auditability
    - Switches between ADB and fastboot modes as needed
    
    Args:
        start (bool): Set to True to begin the unlock process.
    Returns:
        str: Progress, reasoning, and results at each step.
    """
```

```python
def llm_unlock_bootloader_confirm(step: int, command: str) -> str:
    """
    Confirm and execute a destructive command proposed by the LLM unlock agent.
    
    Args:
        step (int): The step number from the unlock process
        command (str): The exact command to confirm and execute
    Returns:
        str: Result of the confirmed command execution
    """
```

## LLM-Driven Bootloader Unlock Agent (Zebra TC52)

This project includes an intelligent, LLM-driven bootloader unlock agent tailored for the Zebra TC52 and other Android devices. The agent uses Azure OpenAI (o4-mini) for reasoning and adapts its strategy based on device responses and history.

### Features
- Uses both ADB and fastboot, switching modes as needed
- Zebra TC52-specific logic: prioritizes Zebra OEM commands and flows
- LLM (Azure OpenAI) proposes the next command and explains its reasoning
- Requires explicit user confirmation for destructive actions (unlock, lock, wipe, flash, etc.)
- Maintains a full history of commands and responses for context and auditability
- Extensible for other devices and unlock strategies

### Setup
1. **Set your Azure OpenAI API key:**
   ```bash
   export AZURE_OPENAI_KEY='your-azure-openai-key-here'
   ```

2. **Start the MCP server:**
   ```bash
   uv run server.py
   ```

### Usage
- From Cursor or your MCP client, call:
  - `llm_unlock_bootloader(start=True)` to begin the unlock process
  - For destructive steps, confirm with `llm_unlock_bootloader_confirm(step=..., command=...)`

### How it Works
- The agent gathers device info (via fastboot getvar product, oem device-info, etc.)
- It maintains a history of all commands and responses
- For each step, it calls Azure OpenAI (o4-mini) with the full context and asks for the next command and reasoning
- If the command is destructive, it prompts you for confirmation before proceeding
- The process continues until the bootloader is unlocked or all options are exhausted

### Security
- The API key is read from the `AZURE_OPENAI_KEY` environment variable for safety
- All destructive actions require explicit user confirmation

## Development and Testing

This project includes a comprehensive testing suite to ensure reliability and robustness.

### Running Tests

```bash
# Run all tests with coverage
python run_tests.py

# Or using pytest directly
uv run pytest

# Run specific test files
uv run pytest tests/test_adb_device_manager.py
uv run pytest tests/test_integration.py
uv run pytest tests/test_config.py
```

### Test Coverage

The testing suite includes:

- **Unit Tests** (`test_adb_device_manager.py`): Test core AdbDeviceManager functionality
- **Integration Tests** (`test_integration.py`): Test server initialization and device selection flows
- **Configuration Tests** (`test_config.py`): Test various configuration scenarios
- **Automated Test Runner** (`run_tests.py`): Installs dependencies and runs tests with coverage

### Key Improvements

#### Enhanced Device Management
- **Auto-device selection**: Automatically connects when only one device is available
- **Dual-mode support**: Seamlessly handles both ADB and Fastboot devices
- **Robust error handling**: Graceful handling of connection failures and device issues
- **Flexible initialization**: Support for both strict and lenient error handling modes
- **Comprehensive logging**: Detailed error messages and status information

#### Better Resource Management
- **Automatic cleanup**: Temporary files are properly cleaned up after operations
- **Memory efficiency**: Image compression reduces memory usage for screenshots
- **Process management**: Proper handling of subprocess operations

#### Code Quality
- **Type hints**: Full type annotation throughout the codebase
- **Comprehensive docstrings**: Detailed documentation for all public methods
- **Modular design**: Clean separation of concerns and reusable components
- **Error recovery**: Graceful degradation when operations fail

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `python run_tests.py`
2. Code follows the existing style and patterns
3. New features include appropriate tests
4. Documentation is updated for any API changes

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)
- Uses [pure-python-adb](https://github.com/Swind/pure-python-adb) for device communication
- Testing with [pytest](https://pytest.org/) framework
- LLM integration with [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
