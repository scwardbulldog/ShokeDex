"""
Unit tests for performance monitoring module
"""

import unittest
import time
from src.performance_monitor import PerformanceMonitor, PerformanceProfiler


class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor(history_size=10)
    
    def test_initialization(self):
        """Test monitor initialization."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(len(self.monitor.frame_times), 0)
        self.assertEqual(len(self.monitor.fps_history), 0)
    
    def test_record_frame(self):
        """Test frame recording."""
        # Record some frames
        for _ in range(5):
            time.sleep(0.016)  # ~60 FPS
            self.monitor.record_frame()
        
        # Check that frames were recorded
        self.assertGreater(len(self.monitor.frame_times), 0)
        self.assertGreater(len(self.monitor.fps_history), 0)
    
    def test_get_stats(self):
        """Test statistics calculation."""
        # Record some frames
        for _ in range(5):
            time.sleep(0.016)
            self.monitor.record_frame()
        
        stats = self.monitor.get_stats()
        
        # Check all required keys exist
        required_keys = [
            'uptime_seconds', 'fps_current', 'fps_avg', 'fps_min', 'fps_max',
            'frame_time_avg_ms', 'frame_time_min_ms', 'frame_time_max_ms',
            'cpu_percent', 'cpu_avg', 'memory_mb', 'memory_avg_mb'
        ]
        
        for key in required_keys:
            self.assertIn(key, stats)
        
        # Check FPS is reasonable
        self.assertGreater(stats['fps_avg'], 0)
        self.assertLess(stats['fps_avg'], 200)  # Sanity check
    
    def test_get_report(self):
        """Test report generation."""
        # Record some frames
        for _ in range(3):
            time.sleep(0.016)
            self.monitor.record_frame()
        
        report = self.monitor.get_report()
        
        # Check report contains expected sections
        self.assertIn("Performance Report", report)
        self.assertIn("FPS:", report)
        self.assertIn("Frame Time:", report)
        self.assertIn("CPU Usage:", report)
        self.assertIn("Memory Usage:", report)
    
    def test_is_performance_adequate(self):
        """Test performance adequacy check."""
        # Create high FPS scenario
        for _ in range(10):
            self.monitor.fps_history.append(60.0)
            self.monitor.cpu_history.append(50.0)
        
        # Should be adequate
        self.assertTrue(self.monitor.is_performance_adequate(target_fps=30.0, max_cpu=80.0))
        
        # Create low FPS scenario
        self.monitor.fps_history.clear()
        for _ in range(10):
            self.monitor.fps_history.append(10.0)
        
        # Should not be adequate
        self.assertFalse(self.monitor.is_performance_adequate(target_fps=30.0, max_cpu=80.0))


class TestPerformanceProfiler(unittest.TestCase):
    """Test PerformanceProfiler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler()
    
    def test_initialization(self):
        """Test profiler initialization."""
        self.assertIsNotNone(self.profiler)
        self.assertEqual(len(self.profiler.sections), 0)
    
    def test_section_profiling(self):
        """Test profiling code sections."""
        # Profile a section
        start = self.profiler.start_section("test_section")
        time.sleep(0.01)  # 10ms
        self.profiler.end_section("test_section", start)
        
        # Check section was recorded
        self.assertIn("test_section", self.profiler.sections)
        self.assertEqual(len(self.profiler.sections["test_section"]), 1)
        
        # Check timing is reasonable
        duration = self.profiler.sections["test_section"][0]
        self.assertGreater(duration, 5)  # Should be > 5ms
        self.assertLess(duration, 50)  # Should be < 50ms
    
    def test_multiple_calls(self):
        """Test profiling same section multiple times."""
        # Profile section 3 times
        for _ in range(3):
            start = self.profiler.start_section("repeated_section")
            time.sleep(0.005)
            self.profiler.end_section("repeated_section", start)
        
        # Check all calls recorded
        self.assertEqual(len(self.profiler.sections["repeated_section"]), 3)
    
    def test_get_section_stats(self):
        """Test getting section statistics."""
        # Profile section multiple times
        for _ in range(5):
            start = self.profiler.start_section("stats_section")
            time.sleep(0.01)
            self.profiler.end_section("stats_section", start)
        
        stats = self.profiler.get_section_stats("stats_section")
        
        # Check all required keys
        self.assertIsNotNone(stats)
        self.assertIn('count', stats)
        self.assertIn('avg_ms', stats)
        self.assertIn('min_ms', stats)
        self.assertIn('max_ms', stats)
        self.assertIn('total_ms', stats)
        
        # Check values are reasonable
        self.assertEqual(stats['count'], 5)
        self.assertGreater(stats['avg_ms'], 5)
        self.assertLess(stats['avg_ms'], 50)
    
    def test_get_section_stats_nonexistent(self):
        """Test getting stats for non-existent section."""
        stats = self.profiler.get_section_stats("nonexistent")
        self.assertIsNone(stats)
    
    def test_get_report(self):
        """Test report generation."""
        # Profile some sections
        for section in ["section1", "section2"]:
            start = self.profiler.start_section(section)
            time.sleep(0.01)
            self.profiler.end_section(section, start)
        
        report = self.profiler.get_report()
        
        # Check report contains expected content
        self.assertIn("Profiling Report", report)
        self.assertIn("section1", report)
        self.assertIn("section2", report)
    
    def test_clear(self):
        """Test clearing profiler data."""
        # Profile a section
        start = self.profiler.start_section("test")
        self.profiler.end_section("test", start)
        
        # Verify data exists
        self.assertGreater(len(self.profiler.sections), 0)
        
        # Clear
        self.profiler.clear()
        
        # Verify data cleared
        self.assertEqual(len(self.profiler.sections), 0)


if __name__ == '__main__':
    unittest.main()
