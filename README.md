# Android MCP Server

An MCP (Model Context Protocol) server that provides programmatic control over
Android devices through ADB (Android Debug Bridge). This server exposes
various Android device management capabilities that can be accessed by MCP
clients like [Claude desktop](https://modelcontextprotocol.io/quickstart/user)
and Code editors
(e.g. [Cursor](https://docs.cursor.com/context/model-context-protocol))

## Features

- 🔧 **Advanced ADB Command Execution** with comprehensive error handling
- 📸 **Device Screenshot Capture** with automatic image compression
- 🎯 **UI Layout Analysis** with clickable element detection and parsing
- 📱 **Device Package Management** including action intent discovery
- 🚀 **Automatic Device Selection** when only one device is connected
- ⚙️ **Flexible Configuration** with optional config file
- 🧪 **Comprehensive Testing Suite** with unit and integration tests
- 📝 **Enhanced Documentation** with detailed docstrings and type hints

## Prerequisites

- Python 3.11+
- ADB (Android Debug Bridge) installed and configured
- Android device with USB debugging enabled

## Installation

1. Clone the repository:

```bash
git clone https://github.com/minhalvp/android-mcp-server.git
cd android-mcp-server
```

2. Install dependencies:
This project uses [uv](https://github.com/astral-sh/uv) for project
management via various methods of
[installation](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv python install 3.11
uv sync
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

2. Add the Android MCP server configuration to the `mcpServers` section:

```json
{
  "mcpServers": {
    "android": {
      "command": "path/to/uv",
      "args": ["--directory", "path/to/android-mcp-server", "run", "server.py"]
    }
  }
}
```

Replace:

- `path/to/uv` with the actual path to your `uv` executable
- `path/to/android-mcp-server` with the absolute path to where you cloned this
repository

### Available Tools

The server exposes the following tools with enhanced functionality:

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
