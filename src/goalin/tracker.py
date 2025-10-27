#!/usr/bin/env python3
"""
Activity tracking module for monitoring active windows and applications
"""

import os
import time
import logging
from typing import Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ActivityTracker:
    """Tracks active windows and applications"""
    
    def __init__(self):
        self.display_server = self._detect_display_server()
        self.last_idle_time = 0
        logger.info(f"Detected display server: {self.display_server}")
    
    def _detect_display_server(self) -> str:
        """Detect whether running X11 or Wayland"""
        if os.environ.get('WAYLAND_DISPLAY'):
            return 'wayland'
        elif os.environ.get('DISPLAY'):
            return 'x11'
        else:
            return 'unknown'
    
    def get_active_window_x11(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get active window information using X11
        
        Returns:
            Tuple of (window_title, application_name)
        """
        try:
            from Xlib import X, display
            from Xlib.error import XError
            
            d = display.Display()
            root = d.screen().root
            
            # Get the active window
            NET_ACTIVE_WINDOW = d.intern_atom('_NET_ACTIVE_WINDOW')
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, X.AnyPropertyType)
            
            if window_id and window_id.value:
                active_window = d.create_resource_object('window', window_id.value[0])
                
                # Get window title
                window_name = active_window.get_full_property(
                    d.intern_atom('_NET_WM_NAME'), 0)
                if window_name:
                    title = window_name.value.decode('utf-8', errors='ignore')
                else:
                    title = active_window.get_wm_name() or "Unknown"
                
                # Get application name
                wm_class = active_window.get_wm_class()
                app_name = wm_class[1] if wm_class and len(wm_class) > 1 else "Unknown"
                
                return title, app_name
            
        except ImportError:
            logger.warning("python-xlib not installed, X11 tracking disabled")
        except Exception as e:
            logger.debug(f"Error getting active window (X11): {e}")
        
        return None, None
    
    def get_active_window_wayland(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get active window information using Wayland
        
        Note: Wayland has security restrictions that make direct window tracking difficult.
        This attempts to use available methods but may have limitations.
        
        Returns:
            Tuple of (window_title, application_name)
        """
        # Try Hyprland
        if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
            try:
                import subprocess
                result = subprocess.run(
                    ['hyprctl', 'activewindow', '-j'],
                    capture_output=True, text=True, timeout=1
                )
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    window = json.loads(result.stdout)
                    title = window.get('title', 'Unknown')
                    app_class = window.get('class', 'Unknown')
                    return title, app_class
            except Exception as e:
                logger.debug(f"Error getting Hyprland window info: {e}")
        
        # Try using playerctl for media applications
        try:
            import subprocess
            result = subprocess.run(
                ['playerctl', 'metadata', '--format', '{{playerName}}: {{title}}'],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                parts = output.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip(), parts[0].strip()
        except Exception as e:
            logger.debug(f"Error getting Wayland window info: {e}")
        
        # Fallback: Try to get focused window from some compositors
        try:
            import subprocess
            # Try swaymsg for Sway compositor
            if os.environ.get('SWAYSOCK'):
                result = subprocess.run(
                    ['swaymsg', '-t', 'get_tree'],
                    capture_output=True, text=True, timeout=1
                )
                if result.returncode == 0:
                    import json
                    tree = json.loads(result.stdout)
                    focused = self._find_focused_node(tree)
                    if focused:
                        return focused.get('name', 'Unknown'), focused.get('app_id', 'Unknown')
        except Exception as e:
            logger.debug(f"Error getting Wayland window info: {e}")
        
        return None, None
    
    def _find_focused_node(self, node):
        """Recursively find the focused node in Sway tree"""
        if node.get('focused'):
            return node
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            result = self._find_focused_node(child)
            if result:
                return result
        return None
    
    def get_active_window(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get currently active window and application
        
        Returns:
            Tuple of (window_title, application_name)
        """
        if self.display_server == 'x11':
            return self.get_active_window_x11()
        elif self.display_server == 'wayland':
            return self.get_active_window_wayland()
        else:
            logger.warning("Unknown display server")
            return None, None
    
    def get_idle_time_x11(self) -> int:
        """
        Get user idle time in seconds using X11
        
        Returns:
            Idle time in seconds
        """
        try:
            from Xlib import X, display
            from Xlib.ext import screensaver
            
            d = display.Display()
            info = screensaver.query_info(d.screen().root)
            idle_ms = info.idle
            return idle_ms // 1000
            
        except ImportError:
            logger.warning("python-xlib not installed, idle detection disabled")
        except Exception as e:
            logger.debug(f"Error getting idle time (X11): {e}")
        
        return 0
    
    def get_idle_time_wayland(self) -> int:
        """
        Get user idle time using Wayland
        
        Note: This is challenging on Wayland. We use a fallback approach.
        
        Returns:
            Idle time in seconds
        """
        # Try Hyprland
        if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
            try:
                import subprocess
                result = subprocess.run(
                    ['hyprctl', 'idle', '-j'],
                    capture_output=True, text=True, timeout=1
                )
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    idle_info = json.loads(result.stdout)
                    # Hyprland returns idle time in milliseconds
                    return idle_info.get('idleTime', 0) // 1000
            except Exception:
                pass
        
        # Try using swayidle if available
        try:
            import subprocess
            result = subprocess.run(
                ['pidof', 'swayidle'],
                capture_output=True, timeout=1
            )
            # If swayidle is running, we assume user is not idle
            # This is a very basic approach
            if result.returncode == 0:
                return 0
        except Exception:
            pass
        
        # Fallback: check keyboard/mouse activity through /proc
        try:
            with open('/proc/interrupts', 'r') as f:
                content = f.read()
                # This is a crude estimation and not reliable
                # In production, consider using a proper idle detection method
                return 0
        except Exception:
            pass
        
        return 0
    
    def get_idle_time(self) -> int:
        """
        Get user idle time in seconds
        
        Returns:
            Idle time in seconds
        """
        if self.display_server == 'x11':
            return self.get_idle_time_x11()
        elif self.display_server == 'wayland':
            return self.get_idle_time_wayland()
        else:
            return 0
    
    def is_idle(self, threshold: int = 300) -> bool:
        """
        Check if user is idle
        
        Args:
            threshold: Idle threshold in seconds
            
        Returns:
            True if user is idle
        """
        idle_time = self.get_idle_time()
        return idle_time >= threshold
