# ShokeDex Performance and Testing Tools

This directory contains tools for profiling, testing, and optimizing ShokeDex performance on Raspberry Pi.

## Available Tools

### 1. Performance Profiler (`profile_performance.py`)

Runs the application with comprehensive performance monitoring enabled and generates detailed reports.

**Usage:**
```bash
# Profile for default 60 seconds
python tools/profile_performance.py

# Profile for custom duration (in seconds)
python tools/profile_performance.py 120
```

**What it measures:**
- FPS (frames per second) - current, average, min, max
- Frame time - average, min, max
- CPU usage - current, average
- Memory usage - current, average
- Per-section profiling (event handling, update, render)

**Output:**
- Real-time overlay on screen showing FPS, CPU, Memory
- Console report with detailed statistics
- Text file saved to `data/performance_profile_<timestamp>.txt`
- Performance assessment vs. Raspberry Pi targets

**Target Metrics:**
- **Pi 3B+**: 30 FPS, <80% CPU, <150MB RAM
- **Pi 4**: 60 FPS, <60% CPU, <200MB RAM

### 2. Input Latency Tester (`test_input_latency.py`)

Measures button input latency to ensure responsive controls.

**Usage:**
```bash
# Test keyboard input (for development)
python tools/test_input_latency.py keyboard 10

# Test GPIO buttons (on Raspberry Pi)
python tools/test_input_latency.py gpio 10

# Default mode is keyboard with 10 samples
python tools/test_input_latency.py
```

**Arguments:**
- First argument: `keyboard` or `gpio` (default: keyboard)
- Second argument: number of samples per button (default: 10)

**What it measures:**
- Latency per button action (UP, DOWN, LEFT, RIGHT, SELECT, BACK)
- Average latency across all buttons
- Min/Max latency values
- Standard deviation (consistency)

**Output:**
- Per-button statistics in console
- Overall latency report
- Performance assessment
- Text file saved to `data/latency_test_<mode>_<timestamp>.txt`

**Target Latency:**
- **Excellent**: <16.67ms (60 FPS)
- **Good**: <33.33ms (30 FPS)
- **Acceptable**: <50ms
- **Poor**: >50ms

### 3. Performance Monitor Module (`src/performance_monitor.py`)

Python module for integrating performance monitoring into applications.

**Usage in Code:**
```python
from src.performance_monitor import PerformanceMonitor, PerformanceProfiler

# Create monitor
monitor = PerformanceMonitor(history_size=100)

# In main loop
monitor.record_frame()
monitor.record_cpu_memory()

# Get statistics
stats = monitor.get_stats()
print(f"FPS: {stats['fps_avg']:.1f}")

# Check performance
if monitor.is_performance_adequate(target_fps=30.0, max_cpu=80.0):
    print("Performance OK")

# Generate report
report = monitor.get_report()
print(report)
```

**Profiler Usage:**
```python
profiler = PerformanceProfiler()

# Profile a section
start = profiler.start_section("my_function")
# ... code to profile ...
profiler.end_section("my_function", start)

# Get statistics
stats = profiler.get_section_stats("my_function")
print(f"Average: {stats['avg_ms']:.2f}ms")

# Generate report
print(profiler.get_report())
```

## Quick Start Guide

### Step 1: Performance Profiling

Run the performance profiler to establish baseline metrics:

```bash
cd ~/ShokeDex
source venv/bin/activate
python tools/profile_performance.py 60
```

Navigate through the application normally during profiling to generate realistic data. Review the generated report in `data/performance_profile_*.txt`.

### Step 2: Input Latency Testing

Test button responsiveness:

```bash
# On development machine
python tools/test_input_latency.py keyboard 20

# On Raspberry Pi with GPIO buttons
python tools/test_input_latency.py gpio 20
```

Follow the prompts to test each button. Review results in `data/latency_test_*.txt`.

### Step 3: Analyze Results

Compare your results against target metrics:

**For Raspberry Pi 3B+:**
- FPS should be ≥25 (target: 30)
- CPU should be <80%
- Memory should be <150MB
- Input latency should be <50ms

**For Raspberry Pi 4:**
- FPS should be ≥50 (target: 60)
- CPU should be <60%
- Memory should be <200MB
- Input latency should be <30ms

### Step 4: Optimize if Needed

If performance doesn't meet targets, see:
- [Pi Optimization Guide](../docs/pi_optimization_guide.md) - Comprehensive optimization tips
- [Pi Installation Guide](../docs/pi_installation_guide.md) - System configuration

Common optimizations:
- Reduce target FPS in `src/main.py`
- Lower display resolution
- Reduce sprite cache size
- Enable hardware acceleration
- Tune database queries

## Interpreting Results

### FPS Analysis

**Good Performance:**
- Consistent FPS close to target
- Low variance (small difference between min/max)
- Smooth visual experience

**Poor Performance:**
- FPS drops significantly below target
- High variance (large gaps between min/max)
- Stuttering or lag

**Causes & Solutions:**
- **CPU bottleneck**: Reduce FPS target, optimize rendering
- **GPU bottleneck**: Lower resolution, reduce sprite cache
- **Thermal throttling**: Add cooling, check temperature

### CPU Usage Analysis

**Good Performance:**
- Average CPU <80% on Pi 3B+, <60% on Pi 4
- Headroom for system processes
- Consistent usage without spikes

**Poor Performance:**
- CPU consistently >90%
- Thermal throttling occurring
- System responsiveness issues

**Causes & Solutions:**
- **Event processing**: Optimize event handling
- **Rendering**: Reduce redraws, cache static elements
- **Database queries**: Add indexes, batch queries
- **Background processes**: Disable unnecessary services

### Memory Analysis

**Good Performance:**
- Stable memory usage over time
- No memory leaks (gradual increase)
- Well below system RAM limit

**Poor Performance:**
- Memory usage increasing over time
- Approaching system RAM limit
- Swapping to disk

**Causes & Solutions:**
- **Sprite cache**: Implement LRU cache with size limit
- **Database connections**: Use context managers
- **Event objects**: Clear old events
- **Memory leaks**: Profile with memory_profiler

### Input Latency Analysis

**Good Performance:**
- Average latency <30ms
- Low standard deviation (<10ms)
- Consistent response across all buttons

**Poor Performance:**
- Average latency >50ms
- High variance (>20ms std dev)
- Some buttons slower than others

**Causes & Solutions:**
- **Debounce time**: Reduce in `src/input_manager.py`
- **Polling rate**: Increase event loop frequency
- **CPU load**: Reduce other processing
- **Wiring**: Check for loose connections, EMI

## Continuous Monitoring

For ongoing performance monitoring during development:

```python
# Add to src/main.py for development
from src.performance_monitor import PerformanceMonitor

class ShokeDexApp:
    def __init__(self):
        # ... existing code ...
        self.monitor = PerformanceMonitor()
        self.show_debug_overlay = True  # Toggle with key
    
    def render(self):
        # ... existing rendering ...
        
        if self.show_debug_overlay:
            self.draw_debug_overlay()
    
    def draw_debug_overlay(self):
        stats = self.monitor.get_stats()
        # Draw FPS, CPU, Memory on screen
```

## Benchmarking

For comparing different configurations or optimizations:

1. **Baseline Test**: Profile with default settings
2. **Make Changes**: Modify one variable at a time
3. **Test Again**: Profile with new settings
4. **Compare**: Use saved reports to compare metrics
5. **Iterate**: Keep changes that improve performance

Example workflow:
```bash
# Test current configuration
python tools/profile_performance.py 60 > baseline.txt

# Make optimization change
# ... edit code ...

# Test again
python tools/profile_performance.py 60 > optimized.txt

# Compare results
diff baseline.txt optimized.txt
```

## Tips

- **Profile on actual hardware**: Performance on Pi differs from desktop
- **Test with realistic usage**: Navigate all screens during profiling
- **Multiple runs**: Run tests 3-5 times and average results
- **Document settings**: Note configuration when capturing metrics
- **Track changes**: Keep performance reports in version control
- **Temperature matters**: Ensure consistent thermal conditions

## Troubleshooting

### Tools Don't Run

**Error: Module not found**
```bash
pip install -r requirements.txt
```

**Error: Display not found (pygame)**
```bash
export DISPLAY=:0
# Or for framebuffer:
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
```

### Inconsistent Results

- Run tests multiple times
- Check CPU temperature (`vcgencmd measure_temp`)
- Close other applications
- Let system idle before testing
- Use consistent test duration

### High Latency Values

- Test with simpler program first
- Check button wiring
- Verify GPIO pin assignments
- Test different debounce values
- Check for USB polling interference

## Additional Resources

- [Pi Optimization Guide](../docs/pi_optimization_guide.md)
- [Pi Installation Guide](../docs/pi_installation_guide.md)
- [Hardware Guide](../docs/hardware_guide.md)
- [Troubleshooting Guide](../docs/troubleshooting.md)

---

**Happy Optimizing!** 🚀
