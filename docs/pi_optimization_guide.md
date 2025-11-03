# Raspberry Pi Optimization Guide

This guide provides performance optimization tips and best practices for running ShokeDex on Raspberry Pi 3B+ and newer models.

## Table of Contents

- [Performance Targets](#performance-targets)
- [CPU Optimization](#cpu-optimization)
- [Memory Optimization](#memory-optimization)
- [Database Optimization](#database-optimization)
- [Graphics Optimization](#graphics-optimization)
- [Input Latency Optimization](#input-latency-optimization)
- [Configuration Tuning](#configuration-tuning)
- [Performance Monitoring](#performance-monitoring)
- [Troubleshooting](#troubleshooting)

## Performance Targets

### Raspberry Pi 3B+
- **Target FPS**: 30 FPS (minimum: 25 FPS)
- **Frame Time**: < 33.33ms per frame
- **CPU Usage**: < 80% average
- **Memory Usage**: < 150 MB
- **Input Latency**: < 50ms per button press
- **Startup Time**: < 3 seconds

### Raspberry Pi 4
- **Target FPS**: 60 FPS (minimum: 50 FPS)
- **Frame Time**: < 16.67ms per frame
- **CPU Usage**: < 60% average
- **Memory Usage**: < 200 MB
- **Input Latency**: < 30ms per button press
- **Startup Time**: < 2 seconds

## CPU Optimization

### 1. Reduce Pygame Event Polling
The default event polling can be CPU-intensive. Optimize by:

```python
# Instead of processing all events every frame
for event in pygame.event.get():
    # process event
    
# Use event pump with selective processing
pygame.event.pump()
# Only get specific event types you need
```

### 2. Frame Rate Limiting
Set appropriate FPS based on your Pi model:

```python
# In src/main.py
FPS = 30  # For Pi 3B+
FPS = 60  # For Pi 4 or better
```

### 3. Limit Background Processes
On Raspberry Pi OS:

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy

# Use lite version of Raspberry Pi OS for headless operation
```

### 4. CPU Governor Settings
For consistent performance:

```bash
# Check current governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Set to performance mode (trades power for speed)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

## Memory Optimization

### 1. Sprite Cache Management
ShokeDex caches sprites in memory. Control cache size in `src/ui/sprite_loader.py`:

```python
# Current implementation uses a simple dictionary cache
# For memory-constrained systems, implement LRU cache:

from functools import lru_cache

@lru_cache(maxsize=50)  # Keep only 50 most recent sprites
def load_thumb(pokemon_id: int):
    # ... existing code
```

### 2. Database Connection Pooling
Use context managers to ensure connections are closed:

```python
# Always use context managers
with Database() as db:
    pokemon = db.get_pokemon_by_id(25)
# Connection automatically closed
```

### 3. Reduce GPU Memory Allocation
If using HDMI output:

```bash
# Edit /boot/config.txt
sudo nano /boot/config.txt

# Add or modify:
gpu_mem=64  # For headless or small displays
gpu_mem=128  # For larger displays with more graphics
```

### 4. Monitor Memory Usage
Use the performance profiling tool:

```bash
python tools/profile_performance.py 60
```

## Database Optimization

### 1. Use Indexes
The database schema already includes indexes on commonly queried columns:
- `pokemon.name`
- `pokemon.generation`
- `types.name`

### 2. Batch Queries
When loading multiple Pokémon, batch queries:

```python
# Instead of:
for pokemon_id in pokemon_ids:
    pokemon = db.get_pokemon_by_id(pokemon_id)
    
# Use:
pokemon_list = db.get_pokemon_batch(pokemon_ids)
```

### 3. Database File Location
For best performance, store the database on:
- **SD Card**: Works but slower
- **USB 3.0 SSD**: Significantly faster (Pi 4 only)
- **RAM Disk**: Fastest but volatile (for testing)

```bash
# Create RAM disk for testing (data lost on reboot)
sudo mkdir -p /mnt/ramdisk
sudo mount -t tmpfs -o size=512M tmpfs /mnt/ramdisk
# Copy database
cp data/pokedex.db /mnt/ramdisk/
```

### 4. PRAGMA Optimizations
The database already uses optimizations, but you can tune further:

```python
# In src/data/database.py, add to connect():
self.conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
self.conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
self.conn.execute("PRAGMA temp_store=MEMORY")  # Use RAM for temp tables
self.conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
```

## Graphics Optimization

### 1. Reduce Display Resolution
For small LCD displays, use native resolution:

```python
# In src/main.py
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# For even better performance on Pi 3B+:
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
```

### 2. Use Hardware Acceleration
When available, use hardware-accelerated display drivers:

```bash
# For official Raspberry Pi displays
# Edit /boot/config.txt
sudo nano /boot/config.txt

# Add:
dtoverlay=vc4-fkms-v3d
```

### 3. Minimize Redraws
Only redraw what changes:

```python
# Use dirty rect updating
dirty_rects = []
# ... determine what changed
pygame.display.update(dirty_rects)

# Instead of full screen flip:
# pygame.display.flip()
```

### 4. Pre-render Static Elements
Cache static UI elements:

```python
# In screen classes, render static elements once
class MyScreen:
    def __init__(self):
        self.background = self.render_background()
        self.static_ui = self.render_static_ui()
    
    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.static_ui, (0, 0))
        # Only render dynamic elements
```

### 5. Sprite Scaling
Pre-scale sprites to target size instead of scaling on each frame:

```python
# Sprites are already pre-processed at correct sizes:
# - thumb: 32x32
# - detail: 96x96
```

## Input Latency Optimization

### 1. GPIO Debounce Time
Adjust debounce time in `src/input_manager.py`:

```python
# Default is 0.1 seconds (100ms)
button = Button(pin, pull_up=True, bounce_time=0.05)  # 50ms for faster response
# Or:
button = Button(pin, pull_up=True, bounce_time=0.2)   # 200ms if getting false triggers
```

### 2. Test Input Latency
Use the latency testing tool:

```bash
# Test keyboard latency (development)
python tools/test_input_latency.py keyboard 20

# Test GPIO latency (on Pi)
python tools/test_input_latency.py gpio 20
```

### 3. Input Polling Rate
Increase event polling rate for better responsiveness:

```python
# In main loop, poll more frequently
self.clock.tick(60)  # Even if rendering at 30 FPS
```

### 4. Use Interrupts (Advanced)
For minimal latency, use GPIO interrupts instead of polling:

```python
# In input_manager.py
button.when_pressed = lambda: self.handle_button_press()
# This uses interrupts internally
```

## Configuration Tuning

### 1. Create Performance Profiles
Add to `src/config.py`:

```python
# Performance profiles
PROFILES = {
    'pi3': {
        'fps': 30,
        'sprite_cache_size': 50,
        'resolution': (480, 320),
        'debounce_time': 0.1,
    },
    'pi4': {
        'fps': 60,
        'sprite_cache_size': 100,
        'resolution': (800, 480),
        'debounce_time': 0.05,
    },
    'performance': {
        'fps': 30,
        'sprite_cache_size': 25,
        'resolution': (320, 240),
        'debounce_time': 0.15,
    }
}
```

### 2. Auto-detect Pi Model
Automatically configure based on hardware:

```python
def detect_pi_model():
    """Detect Raspberry Pi model."""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            if 'Pi 4' in model:
                return 'pi4'
            elif 'Pi 3' in model:
                return 'pi3'
    except:
        pass
    return 'pi3'  # Default to more conservative settings
```

## Performance Monitoring

### 1. Built-in Performance Monitor
The `src/performance_monitor.py` module provides real-time monitoring:

```python
from src.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# In main loop
monitor.record_frame()
monitor.record_cpu_memory()

# Get statistics
stats = monitor.get_stats()
print(f"FPS: {stats['fps_avg']:.1f}")
print(f"CPU: {stats['cpu_avg']:.1f}%")
```

### 2. Profile with Tools
Run comprehensive profiling:

```bash
# Profile for 60 seconds
python tools/profile_performance.py 60

# Review results in data/performance_profile_*.txt
```

### 3. System Monitoring
Use Raspberry Pi system tools:

```bash
# Check CPU frequency and temperature
vcgencmd measure_clock arm
vcgencmd measure_temp

# Monitor system resources
htop

# Check GPU memory
vcgencmd get_mem gpu
```

## Troubleshooting

### Low FPS

**Symptoms:** FPS below 25 on Pi 3B+ or below 50 on Pi 4

**Solutions:**
1. Reduce target FPS in `src/main.py`
2. Lower display resolution
3. Reduce sprite cache size
4. Check CPU temperature (thermal throttling)
5. Disable unnecessary system services

```bash
# Check for throttling
vcgencmd get_throttled
# 0x0 = no throttling
# Non-zero = throttling occurred
```

### High Input Latency

**Symptoms:** Buttons feel sluggish, > 100ms latency

**Solutions:**
1. Reduce debounce time
2. Increase polling rate
3. Check for CPU bottleneck
4. Verify GPIO wiring (loose connections increase latency)

### Memory Issues

**Symptoms:** Application crashes, system becomes unresponsive

**Solutions:**
1. Reduce sprite cache size
2. Close unused applications
3. Increase swap space
4. Use lighter Raspberry Pi OS Lite

```bash
# Increase swap size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Database Performance

**Symptoms:** Slow loading times, screen transitions lag

**Solutions:**
1. Verify database file integrity
2. Rebuild database with optimizations
3. Move database to faster storage
4. Check for disk I/O bottleneck

```bash
# Check disk I/O
iostat -x 1

# Test SD card speed
sudo hdparm -t /dev/mmcblk0
```

## Best Practices Summary

1. **Always profile before optimizing** - Use the profiling tools to identify actual bottlenecks
2. **Start with conservative settings** - Use Pi 3B+ profile even on Pi 4, then increase
3. **Monitor temperature** - Ensure adequate cooling to prevent throttling
4. **Use quality SD cards** - Class 10 or better, prefer A1/A2 rated cards
5. **Update regularly** - Keep Raspberry Pi OS and Python packages updated
6. **Test on target hardware** - Development machine performance != Pi performance

## Additional Resources

- [Raspberry Pi Performance Documentation](https://www.raspberrypi.org/documentation/configuration/)
- [Pygame Optimization Tips](https://www.pygame.org/wiki/OptimizationTips)
- [SQLite Performance Tuning](https://www.sqlite.org/pragma.html)
- ShokeDex Performance Tools:
  - `tools/profile_performance.py` - Full performance profiling
  - `tools/test_input_latency.py` - Input latency testing
  - `src/performance_monitor.py` - Real-time monitoring module
