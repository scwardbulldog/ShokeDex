# Raspberry Pi Hardware Validation Guide

## Story 1.7: Task 8 - Performance on Raspberry Pi Hardware (AC #8)

This guide explains how to validate ShokeDex performance on actual Raspberry Pi 3B+ hardware.

## Prerequisites

### Hardware Requirements

- **Raspberry Pi 3B+** (target hardware)
  - 1.4GHz Quad-core ARM Cortex-A53
  - 1GB RAM
  - VideoCore IV GPU
  - MicroSD card (Class 10 or better recommended)

- **LCD Display** (one of):
  - 3.5" 480x320 LCD (common for Pi projects)
  - 5" 800x480 touchscreen
  - 7" 1024x600 display
  - HDMI monitor for testing

- **Input Devices:**
  - Physical GPIO buttons (preferred for final testing)
  - USB keyboard (for development/debugging)

- **Power Supply:**
  - Official Pi 3 power supply (5V 2.5A recommended)
  - Quality microSD card reader for deployment

### Software Setup

See [Pi Installation Guide](../pi_installation_guide.md) for detailed setup instructions.

**Quick Setup:**
```bash
# On Raspberry Pi (SSH or direct terminal)
cd /home/pi/ShokeDex

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify database exists
ls -lh data/pokedex.db

# Check sprite assets
ls assets/sprites/thumb/ | wc -l  # Should show ~386
```

## Validation Checklist

### 1. Frame Rate Performance (AC #1)

**Requirement:** Maintain 30+ FPS during all operations

**Test Procedure:**
```bash
# Run profiler for 10 minutes
python tools/profile_performance.py --duration 600

# Check output:
# - Average FPS should be ≥30
# - FPS minimum should be ≥25 (allow brief dips)
# - No prolonged FPS drops
```

**Manual Verification:**
- Navigate rapidly with L/R buttons (generation switching)
- Hold Down to scroll through 151 Pokémon quickly
- Watch for stuttering or lag (visual inspection)

**Expected Results:**
- ✅ Average FPS: 30+ (locked to FPS cap)
- ✅ Minimum FPS: 27-30 (brief dips acceptable during sprite loads)
- ✅ No visible stuttering during rapid navigation

### 2. Button Input Latency (AC #2)

**Requirement:** < 100ms from button press to screen update

**Test Procedure:**
```bash
# Run input latency test
python tools/test_input_latency.py --iterations 100

# Check report in data/input_latency_*.txt:
# - Average latency < 80ms
# - P95 latency < 100ms
# - All button types tested
```

**Manual Verification:**
- Press L/R buttons rapidly - should feel instant
- Scroll with Up/Down - no perceived delay
- Test all button types (L, R, Up, Down, A, B, Select)

**Expected Results:**
- ✅ Average latency: 50-80ms
- ✅ P95 latency: < 100ms
- ✅ Instant user perception (no lag feeling)

### 3. LCD Display Quality

**Requirement:** Smooth updates without tearing

**Test Procedure:**
- Navigate continuously for 5 minutes
- Watch for screen tearing during sprite transitions
- Check fade effects (generation switch, sprite transitions)
- Verify text readability

**Manual Verification:**
- Generation switch: Fade should be smooth (not choppy)
- Sprite scrolling: No torn/incomplete sprites visible
- Text rendering: Clear, no artifacts
- Badge glow: Smooth animation

**Expected Results:**
- ✅ No screen tearing visible
- ✅ Smooth sprite transitions (fade-in/fade-out)
- ✅ Clear text rendering
- ✅ Smooth animations

### 4. SD Card I/O Performance

**Requirement:** No degradation from SD card read speeds

**Test Procedure:**
```bash
# Check SD card read speed
sudo hdparm -t /dev/mmcblk0
# Should show > 20 MB/s for Class 10 card

# Test sprite loading during navigation
python -c "
from src.ui import sprite_loader
import time

# Test cold load (SD card read)
start = time.time()
sprite_loader.load_thumb(1)
cold_time = (time.time() - start) * 1000

# Test cached load (memory)
start = time.time()
sprite_loader.load_thumb(1)
cached_time = (time.time() - start) * 1000

print(f'Cold load: {cold_time:.2f}ms')
print(f'Cached load: {cached_time:.2f}ms')
"
```

**Expected Results:**
- ✅ Cold sprite load: < 150ms (first time from SD)
- ✅ Cached sprite load: < 10ms (from memory)
- ✅ State save: < 50ms (verified by logs)
- ✅ No stuttering during sprite loads

### 5. ARM CPU Performance

**Requirement:** No degradation from ARM architecture

**Test Procedure:**
```bash
# Monitor CPU usage during operation
# In one terminal:
python src/main.py

# In another terminal:
watch -n 1 'top -bn1 | grep python'

# CPU usage should be:
# - Idle: < 10%
# - Active navigation: 15-30%
# - Peak (transitions): < 50%
```

**Stress Test:**
```bash
# Run stress test: 100 gen switches + 500 scrolls
python -c "
from src.input_manager import InputAction
from src.ui import HomeScreen
import pygame

pygame.init()
surface = pygame.Surface((480, 320))

# ... simulate navigation ...
# Check CPU doesn't spike > 80% sustained
"
```

**Expected Results:**
- ✅ Idle CPU: < 10% (minimal background processing)
- ✅ Active CPU: 15-30% (normal navigation)
- ✅ Peak CPU: < 50% (brief spikes acceptable)
- ✅ No thermal throttling (check `vcgencmd measure_temp`)

### 6. Memory Constraints

**Requirement:** Operate within 1GB RAM (share with OS)

**Test Procedure:**
```bash
# Check free memory before starting
free -m

# Start application
python src/main.py

# In another terminal, monitor memory
watch -n 5 'ps aux | grep python | grep -v grep'

# Memory (RSS) should be:
# - Initial: ~150-200MB
# - After 30min: < 300MB
# - Never exceed: 400MB
```

**Memory Profiling:**
```bash
# Profile memory over time
mprof run --interval 2.0 python src/main.py

# Navigate for 10+ minutes, then quit
# Check memory graph:
mprof plot
```

**Expected Results:**
- ✅ Initial memory: 150-200MB
- ✅ Stable memory: < 300MB
- ✅ No unbounded growth (memory leak free)
- ✅ System remains responsive (no swapping)

### 7. Comparison to Desktop Baseline

**Desktop Baseline (Reference):**
- Average FPS: 60 (capped)
- Input latency: 40-60ms
- Sprite load (cached): < 1ms
- Sprite load (cold): 20-40ms
- Memory usage: ~150MB

**Pi Expected Performance:**
- Average FPS: 30 (capped, meets requirement)
- Input latency: 60-80ms (within 100ms requirement)
- Sprite load (cached): < 10ms (acceptable)
- Sprite load (cold): < 150ms (acceptable)
- Memory usage: ~200MB (acceptable)

**Validation:**
```bash
# Run same profiling on both platforms
# Desktop:
python tools/profile_performance.py --duration 300 > desktop_profile.txt

# Raspberry Pi:
python tools/profile_performance.py --duration 300 > pi_profile.txt

# Compare FPS, latency, memory metrics
diff desktop_profile.txt pi_profile.txt
```

**Expected Results:**
- ✅ Pi FPS ≥ 30 (meets NFR-P1)
- ✅ Pi latency < 100ms (meets NFR-P2)
- ✅ Pi meets all performance requirements independently
- ℹ️ Pi ~2x slower than desktop (acceptable)

## Common Issues and Solutions

### Issue: FPS Drops Below 30

**Symptoms:**
- Average FPS 25-28
- Stuttering during navigation
- Slow sprite transitions

**Possible Causes:**
1. **Background processes:** Other services consuming CPU
2. **Thermal throttling:** Pi overheating (check `vcgencmd measure_temp`)
3. **SD card too slow:** Use Class 10 or better
4. **Power supply:** Insufficient voltage (under-voltage warning)

**Solutions:**
```bash
# 1. Stop unnecessary services
sudo systemctl stop bluetooth
sudo systemctl stop cups

# 2. Check temperature
vcgencmd measure_temp
# If > 80°C, add heatsink or fan

# 3. Test SD card speed
sudo hdparm -t /dev/mmcblk0
# Should be > 20 MB/s

# 4. Check power supply voltage
vcgencmd get_throttled
# 0x0 = good, anything else = under-voltage
```

### Issue: Input Latency > 100ms

**Symptoms:**
- Button presses feel sluggish
- Delayed visual feedback
- Test reports P95 > 100ms

**Possible Causes:**
1. **GPIO debounce delay:** Too conservative
2. **CPU throttling:** Check temperature
3. **Display lag:** Some LCDs have inherent delay

**Solutions:**
```python
# Adjust GPIO debounce in input_manager.py
from gpiozero import Button

button = Button(pin, bounce_time=0.01)  # Reduce from 0.05 to 0.01
```

### Issue: Screen Tearing

**Symptoms:**
- Horizontal lines during motion
- Incomplete sprite rendering
- Choppy animations

**Possible Causes:**
1. **V-sync disabled:** Display not synced with refresh
2. **LCD refresh rate:** Some cheap LCDs have low refresh
3. **Driver issues:** SPI/DPI display drivers

**Solutions:**
```bash
# Enable V-sync in boot config
sudo nano /boot/config.txt

# Add:
# dtoverlay=vc4-kms-v3d
# max_framebuffers=2

# Reboot
sudo reboot
```

### Issue: Memory Leak

**Symptoms:**
- Memory grows over time
- System becomes sluggish after 30+ min
- Eventually crashes

**Diagnosis:**
```bash
# Run memory profiler
mprof run python src/main.py

# Navigate for 30 minutes
# Check plot
mprof plot

# Look for upward trend (not plateau)
```

**Solutions:**
- See [Memory Profiling Guide](memory-profiling-guide.md)
- Verify sprite cache LRU eviction
- Check for circular references
- Ensure resources cleaned up on screen exit

## Performance Tuning

### Overclocking (Optional)

**WARNING:** May void warranty, require better cooling

```bash
# Edit config
sudo nano /boot/config.txt

# Add (conservative overclock):
over_voltage=2
arm_freq=1400
gpu_freq=500

# Reboot
sudo reboot
```

**After overclocking:**
- Monitor temperature: `watch -n 1 vcgencmd measure_temp`
- Retest all performance metrics
- Add heatsink/fan if > 75°C

### Display Configuration

**For 480x320 LCD:**
```bash
# Set environment variables
export SHOKEDEX_WIDTH=480
export SHOKEDEX_HEIGHT=320
export SHOKEDEX_FPS=30

# Or edit ~/.bashrc:
echo 'export SHOKEDEX_WIDTH=480' >> ~/.bashrc
echo 'export SHOKEDEX_HEIGHT=320' >> ~/.bashrc
echo 'export SHOKEDEX_FPS=30' >> ~/.bashrc
```

### Sprite Cache Tuning

If memory is tight:
```python
# In src/ui/sprite_loader.py
_CACHE_MAX_SIZE = 30  # Reduce from 50 to 30
```

If navigating distant Pokémon frequently:
```python
_CACHE_MAX_SIZE = 75  # Increase to 75 (still bounded)
```

## Success Criteria Summary

All requirements from AC #8 must pass:

- ✅ **FPS:** 30+ during all operations
- ✅ **Latency:** < 100ms button response
- ✅ **Display:** Smooth, no tearing
- ✅ **SD I/O:** No performance impact
- ✅ **CPU:** No ARM architecture issues
- ✅ **Memory:** < 300MB, no leaks
- ✅ **Tested:** Actual Pi 3B+ hardware validation complete

## Deployment Checklist

Before marking Task 8 complete:

- [ ] Deploy code to Pi 3B+ test device
- [ ] Run `tools/profile_performance.py` for 10 minutes
- [ ] Run `tools/test_input_latency.py` with 100 iterations
- [ ] Manually navigate for 30 minutes continuously
- [ ] Check for screen tearing (visual inspection)
- [ ] Monitor memory with `mprof` during operation
- [ ] Compare results to desktop baseline
- [ ] Document any Pi-specific optimizations needed
- [ ] Verify all 8 acceptance criteria met

## References

- Story 1.7: Performance Optimization and 3-Press Navigation Rule
- AC #8: Performance on Raspberry Pi Hardware
- NFR-P1: Frame Rate (30+ FPS on Pi 3B+)
- NFR-P2: Input Latency (< 100ms)
- NFR-P4: Memory Efficiency (1GB RAM constraint)
- Architecture: Raspberry Pi 3B+ Constraints
- [Pi Installation Guide](../pi_installation_guide.md)
- [Pi Optimization Guide](../pi_optimization_guide.md)
