import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image as PILImage
from ppadb.client import Client as AdbClient
from ppadb.device import Device


class AdbDeviceManager:
    def __init__(self, device_name: str | None = None, exit_on_error: bool = True) -> None:
        """
        Initialize the ADB Device Manager

        Args:
            device_name: Optional name/serial of the device to manage.
                        If None, attempts to auto-select if only one device is available.
            exit_on_error: Whether to exit the program if device initialization fails
        """
        if not self.check_adb_installed():
            error_msg = "adb is not installed or not in PATH. Please install adb and ensure it is in your PATH."
            if exit_on_error:
                print(error_msg, file=sys.stderr)
                sys.exit(1)
            else:
                raise RuntimeError(error_msg)

        available_devices = self.get_available_devices()
        if not available_devices:
            error_msg = "No devices connected. Please connect a device and try again."
            if exit_on_error:
                print(error_msg, file=sys.stderr)
                sys.exit(1)
            else:
                raise RuntimeError(error_msg)

        selected_device_name: str | None = None

        if device_name:
            if device_name not in available_devices:
                error_msg = f"Device {device_name} not found. Available devices: {available_devices}"
                if exit_on_error:
                    print(error_msg, file=sys.stderr)
                    sys.exit(1)
                else:
                    raise RuntimeError(error_msg)
            selected_device_name = device_name
        else:  # No device_name provided, try auto-selection
            if len(available_devices) == 1:
                selected_device_name = available_devices[0]
                print(f"No device specified, automatically selected: {selected_device_name}")
            elif len(available_devices) > 1:
                error_msg = (
                    f"Multiple devices connected: {available_devices}. "
                    "Please specify a device in config.yaml or connect only one device."
                )
                if exit_on_error:
                    print(error_msg, file=sys.stderr)
                    sys.exit(1)
                else:
                    raise RuntimeError(error_msg)
            # If len(available_devices) == 0, it's already caught by the earlier check

        # At this point, selected_device_name should always be set due to the logic above
        # Initialize the device
        self.device = AdbClient().device(selected_device_name)  # type: ignore

    @staticmethod
    def check_adb_installed() -> bool:
        """Check if ADB is installed on the system.
        
        Returns:
            bool: True if ADB is installed and accessible, False otherwise.
        """
        try:
            subprocess.run(["adb", "version"], check=True, stdout=subprocess.PIPE)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_available_devices() -> list[str]:
        """Get a list of available device serials.
        
        Returns:
            list[str]: List of device serial numbers.
        """
        return [device.serial for device in AdbClient().devices()]

    def get_packages(self) -> str:
        """Get a list of all installed packages on the device.
        
        Returns:
            str: Newline-separated list of package names.
        """
        command = "pm list packages"
        packages = self.device.shell(command).strip().split("\n")
        result = [package[8:] for package in packages]  # Remove "package:" prefix
        return "\n".join(result)

    def get_package_action_intents(self, package_name: str) -> list[str]:
        """Get all non-data actions from Activity Resolver Table for a package.
        
        Args:
            package_name: The name of the package to get actions for.
            
        Returns:
            list[str]: List of action intents for the package.
        """
        command = f"dumpsys package {package_name}"
        output = self.device.shell(command)

        resolver_table_start = output.find("Activity Resolver Table:")
        if resolver_table_start == -1:
            return []
        resolver_section = output[resolver_table_start:]

        non_data_start = resolver_section.find("\n  Non-Data Actions:")
        if non_data_start == -1:
            return []

        section_end = resolver_section[non_data_start:].find("\n\n")
        if section_end == -1:
            non_data_section = resolver_section[non_data_start:]
        else:
            non_data_section = resolver_section[non_data_start: non_data_start + section_end]

        actions = []
        for line in non_data_section.split("\n"):
            line = line.strip()
            if line.startswith("android.") or line.startswith("com."):
                actions.append(line)

        return actions

    def execute_adb_shell_command(self, command: str) -> str:
        """Execute an ADB shell command and return the output.
        
        Args:
            command: The command to execute. Can include 'adb shell' prefix which will be stripped.
            
        Returns:
            str: The command output.
        """
        if command.startswith("adb shell "):
            command = command[10:]
        elif command.startswith("adb "):
            command = command[4:]
        result = self.device.shell(command)
        return result

    def take_screenshot(self, output_path: str = "screenshot.png") -> str:
        """Take a screenshot of the device and save it locally.
        
        Args:
            output_path: Local path where the screenshot should be saved.
            
        Returns:
            str: Path to the compressed screenshot file.
        """
        # Use temporary file on device to avoid conflicts
        device_temp_path = f"/sdcard/screenshot_{os.getpid()}.png"
        
        try:
            self.device.shell(f"screencap -p {device_temp_path}")
            self.device.pull(device_temp_path, output_path)
            self.device.shell(f"rm {device_temp_path}")

            # Create compressed version to avoid memory issues
            compressed_path = f"compressed_{Path(output_path).name}"
            self._compress_image(output_path, compressed_path)
            
            return compressed_path
        except Exception as e:
            # Clean up device temp file if it exists
            self.device.shell(f"rm {device_temp_path}")
            raise e

    def _compress_image(self, input_path: str, output_path: str, scale_factor: float = 0.3) -> None:
        """Compress an image to reduce file size.
        
        Args:
            input_path: Path to the input image.
            output_path: Path for the compressed output image.
            scale_factor: Factor by which to scale down the image (default 0.3).
        """
        with PILImage.open(input_path) as img:
            width, height = img.size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resized_img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            resized_img.save(output_path, "PNG", quality=85, optimize=True)

    def get_uilayout(self) -> str:
        """Get UI layout information for clickable elements.
        
        Returns:
            str: Formatted string containing clickable element information.
        """
        # Use temporary file on device to avoid conflicts
        device_temp_path = f"/sdcard/window_dump_{os.getpid()}.xml"
        local_temp_path = f"window_dump_{os.getpid()}.xml"
        
        try:
            self.device.shell(f"uiautomator dump {device_temp_path}")
            self.device.pull(device_temp_path, local_temp_path)
            self.device.shell(f"rm {device_temp_path}")

            clickable_elements = self._parse_ui_xml(local_temp_path)
            
            # Clean up local temp file
            if os.path.exists(local_temp_path):
                os.remove(local_temp_path)
                
            if not clickable_elements:
                return "No clickable elements found with text or description"
            else:
                return "\n\n".join(clickable_elements)
                
        except Exception as e:
            # Clean up temp files
            self.device.shell(f"rm {device_temp_path}")
            if os.path.exists(local_temp_path):
                os.remove(local_temp_path)
            raise e

    def _parse_ui_xml(self, xml_path: str) -> list[str]:
        """Parse UI XML dump file to extract clickable element information.
        
        Args:
            xml_path: Path to the XML file to parse.
            
        Returns:
            list[str]: List of formatted clickable element descriptions.
        """
        import re
        import xml.etree.ElementTree as ET

        def calculate_center(bounds_str: str) -> tuple[int, int] | None:
            """Calculate center coordinates from bounds string."""
            matches = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
            if len(matches) == 2:
                x1, y1 = map(int, matches[0])
                x2, y2 = map(int, matches[1])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                return center_x, center_y
            return None

        tree = ET.parse(xml_path)
        root = tree.getroot()

        clickable_elements = []
        for element in root.findall(".//node[@clickable='true']"):
            text = element.get("text", "")
            content_desc = element.get("content-desc", "")
            bounds = element.get("bounds", "")

            # Only include elements that have either text or content description
            if text or content_desc:
                center = calculate_center(bounds)
                element_info = "Clickable element:"
                if text:
                    element_info += f"\n  Text: {text}"
                if content_desc:
                    element_info += f"\n  Description: {content_desc}"
                element_info += f"\n  Bounds: {bounds}"
                if center:
                    element_info += f"\n  Center: ({center[0]}, {center[1]})"
                clickable_elements.append(element_info)

        return clickable_elements
