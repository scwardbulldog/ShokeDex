"""
Performance monitoring module for ShokeDex

Provides tools to monitor CPU usage, memory consumption, FPS, and frame times
for optimization on Raspberry Pi 3B+ and newer models.
"""

import time
import psutil
from typing import Dict, List, Optional
from collections import deque


class PerformanceMonitor:
    """Monitors application performance metrics."""
    
    def __init__(self, history_size: int = 100):
        """
        Initialize performance monitor.
        
        Args:
            history_size: Number of samples to keep in history
        """
        self.history_size = history_size
        
        # Frame time tracking
        self.frame_times: deque = deque(maxlen=history_size)
        self.last_frame_time = time.time()
        
        # FPS tracking
        self.fps_history: deque = deque(maxlen=history_size)
        
        # CPU usage tracking
        self.cpu_history: deque = deque(maxlen=history_size)
        
        # Memory tracking
        self.memory_history: deque = deque(maxlen=history_size)
        
        # Process handle
        self.process = psutil.Process()
        
        # Start time
        self.start_time = time.time()
    
    def record_frame(self):
        """Record a frame completion for FPS and frame time tracking."""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        self.frame_times.append(frame_time * 1000)  # Convert to ms
        
        # Calculate instantaneous FPS
        if frame_time > 0:
            fps = 1.0 / frame_time
            self.fps_history.append(fps)
    
    def record_cpu_memory(self):
        """Record current CPU and memory usage."""
        try:
            # CPU percentage (this call is non-blocking after first call)
            cpu_percent = self.process.cpu_percent()
            self.cpu_history.append(cpu_percent)
            
            # Memory info
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
            self.memory_history.append(memory_mb)
        except Exception as e:
            # Gracefully handle errors (process might not be accessible)
            pass
    
    def get_stats(self) -> Dict[str, float]:
        """
        Get current performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        stats = {
            'uptime_seconds': time.time() - self.start_time,
            'fps_current': 0.0,
            'fps_avg': 0.0,
            'fps_min': 0.0,
            'fps_max': 0.0,
            'frame_time_avg_ms': 0.0,
            'frame_time_min_ms': 0.0,
            'frame_time_max_ms': 0.0,
            'cpu_percent': 0.0,
            'cpu_avg': 0.0,
            'memory_mb': 0.0,
            'memory_avg_mb': 0.0,
        }
        
        # FPS stats
        if self.fps_history:
            stats['fps_current'] = self.fps_history[-1]
            stats['fps_avg'] = sum(self.fps_history) / len(self.fps_history)
            stats['fps_min'] = min(self.fps_history)
            stats['fps_max'] = max(self.fps_history)
        
        # Frame time stats
        if self.frame_times:
            stats['frame_time_avg_ms'] = sum(self.frame_times) / len(self.frame_times)
            stats['frame_time_min_ms'] = min(self.frame_times)
            stats['frame_time_max_ms'] = max(self.frame_times)
        
        # CPU stats
        if self.cpu_history:
            stats['cpu_percent'] = self.cpu_history[-1]
            stats['cpu_avg'] = sum(self.cpu_history) / len(self.cpu_history)
        
        # Memory stats
        if self.memory_history:
            stats['memory_mb'] = self.memory_history[-1]
            stats['memory_avg_mb'] = sum(self.memory_history) / len(self.memory_history)
        
        return stats
    
    def get_report(self) -> str:
        """
        Generate a human-readable performance report.
        
        Returns:
            Formatted string with performance metrics
        """
        stats = self.get_stats()
        
        report = []
        report.append("=== Performance Report ===")
        report.append(f"Uptime: {stats['uptime_seconds']:.1f}s")
        report.append("")
        report.append("FPS:")
        report.append(f"  Current: {stats['fps_current']:.1f}")
        report.append(f"  Average: {stats['fps_avg']:.1f}")
        report.append(f"  Min/Max: {stats['fps_min']:.1f} / {stats['fps_max']:.1f}")
        report.append("")
        report.append("Frame Time:")
        report.append(f"  Average: {stats['frame_time_avg_ms']:.2f}ms")
        report.append(f"  Min/Max: {stats['frame_time_min_ms']:.2f}ms / {stats['frame_time_max_ms']:.2f}ms")
        report.append("")
        report.append("CPU Usage:")
        report.append(f"  Current: {stats['cpu_percent']:.1f}%")
        report.append(f"  Average: {stats['cpu_avg']:.1f}%")
        report.append("")
        report.append("Memory Usage:")
        report.append(f"  Current: {stats['memory_mb']:.1f} MB")
        report.append(f"  Average: {stats['memory_avg_mb']:.1f} MB")
        
        return "\n".join(report)
    
    def is_performance_adequate(self, target_fps: float = 30.0, max_cpu: float = 80.0) -> bool:
        """
        Check if performance is adequate based on targets.
        
        Args:
            target_fps: Target FPS threshold
            max_cpu: Maximum acceptable CPU usage percentage
            
        Returns:
            True if performance meets targets, False otherwise
        """
        stats = self.get_stats()
        
        # Check FPS
        if stats['fps_avg'] < target_fps * 0.9:  # Allow 10% variance
            return False
        
        # Check CPU
        if stats['cpu_avg'] > max_cpu:
            return False
        
        return True


class PerformanceProfiler:
    """Profile specific code sections for optimization."""
    
    def __init__(self):
        """Initialize profiler."""
        self.sections: Dict[str, List[float]] = {}
    
    def start_section(self, name: str) -> float:
        """
        Start timing a code section.
        
        Args:
            name: Name of the section to profile
            
        Returns:
            Start time
        """
        return time.time()
    
    def end_section(self, name: str, start_time: float):
        """
        End timing a code section and record duration.
        
        Args:
            name: Name of the section
            start_time: Start time from start_section
        """
        duration = (time.time() - start_time) * 1000  # Convert to ms
        
        if name not in self.sections:
            self.sections[name] = []
        
        self.sections[name].append(duration)
    
    def get_section_stats(self, name: str) -> Optional[Dict[str, float]]:
        """
        Get statistics for a profiled section.
        
        Args:
            name: Name of the section
            
        Returns:
            Dictionary with timing statistics, or None if section not found
        """
        if name not in self.sections or not self.sections[name]:
            return None
        
        times = self.sections[name]
        return {
            'count': len(times),
            'avg_ms': sum(times) / len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'total_ms': sum(times),
        }
    
    def get_report(self) -> str:
        """
        Generate a report of all profiled sections.
        
        Returns:
            Formatted string with profiling results
        """
        report = []
        report.append("=== Profiling Report ===")
        report.append("")
        
        for name in sorted(self.sections.keys()):
            stats = self.get_section_stats(name)
            if stats:
                report.append(f"{name}:")
                report.append(f"  Calls: {stats['count']}")
                report.append(f"  Average: {stats['avg_ms']:.2f}ms")
                report.append(f"  Min/Max: {stats['min_ms']:.2f}ms / {stats['max_ms']:.2f}ms")
                report.append(f"  Total: {stats['total_ms']:.2f}ms")
                report.append("")
        
        return "\n".join(report)
    
    def clear(self):
        """Clear all profiling data."""
        self.sections.clear()
