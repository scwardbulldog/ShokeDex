# Input Latency and Responsiveness Guide

## Quick Context
ShokeDex uses GPIO buttons for navigation. Input latency is the time from button press to visible UI response. Target: <50ms on Pi 3B+, <30ms on Pi 4. High latency makes the device feel sluggish and unresponsive.

## Performance Measurement

### Direct Latency Testing
```bash
# Use dedicated latency testing tool
python tools/test_input_latency.py

# Expected output:
# Button A: 25ms avg, 35ms P95
# Button B: 27ms avg, 38ms P95
# D-Pad Up: 22ms avg, 32ms P95
```

### Manual Timing with Logging
```python
import time
from src.hardware.gpio_buttons import ButtonManager

def test_input_response():
    manager = ButtonManager()
    
    def on_press(button):
        press_time = time.perf_counter()
        # ... trigger UI update ...
        response_time = time.perf_counter()
        latency_ms = (response_time - press_time) * 1000
        print(f"{button}: {latency_ms:.1f}ms latency")
    
    manager.register_callback('A', on_press)
```

### Frame-to-Frame Response Measurement
```python
# In main game loop:
input_timestamp = None
render_timestamp = None

# Input handling:
if button_pressed:
    input_timestamp = time.perf_counter()

# Rendering:
if input_timestamp and render_timestamp is None:
    render_timestamp = time.perf_counter()
    latency = (render_timestamp - input_timestamp) * 1000
    print(f"Input-to-render: {latency:.1f}ms")
```

## Common Bottlenecks

### 1. Event Queue Polling Delay
**Issue:** pygame event queue checked only once per frame (30 FPS = every 33ms)  
**Impact:** Up to 33ms delay before input detected  
**Fix:** Poll events multiple times per frame or use interrupt-driven GPIO

### 2. Debounce Time Too Long
**Current:** 100ms debounce (from `test_input_latency.py`)  
**Impact:** Delays response by up to 100ms  
**Optimization:** Reduce debounce to 10-20ms for most buttons
```python
# In src/hardware/gpio_buttons.py
button = Button(pin, bounce_time=0.02)  # 20ms instead of 100ms
```

### 3. Heavy Event Handlers
**Issue:** Button callback does expensive work (DB query, sprite load)  
**Impact:** Blocks until handler completes  
**Fix:** Queue actions, process asynchronously:
```python
action_queue = []

def on_button_press(button):
    action_queue.append(button)  # Fast, non-blocking

# In main loop:
if action_queue:
    action = action_queue.pop(0)
    process_action(action)  # Can take time without blocking input
```

### 4. Frame Rate Bottleneck
**Issue:** Even with instant input detection, response visible only on next frame  
**Impact:** At 30 FPS, visible delay is 0-33ms  
**Fix:** Maintain consistent high frame rate (optimize rendering, see UI guide)

## Optimization Techniques

### Interrupt-Driven GPIO
**Current pattern:** Polling-based  
**Optimized pattern:** Event-driven with callbacks
```python
from gpiozero import Button

button_a = Button(17, bounce_time=0.02)
button_a.when_pressed = lambda: handle_press('A')  # Instant response
```

### Input Prediction
**Technique:** Start loading next Pokémon when D-Pad pressed, before releasing  
**Impact:** 50-100ms head start on sprite loading  
**Implementation:**
```python
# On button press (not release):
if button == 'RIGHT':
    preload_sprite(current_pokemon_id + 1)  # Background load
    
# On button release:
    navigate_to(current_pokemon_id + 1)  # Sprite already loaded!
```

### Input Buffering
**Use case:** Rapid button presses (user mashing buttons)  
**Without buffering:** Inputs dropped if arriving faster than processing  
**With buffering:** Queue inputs, process in order
```python
from collections import deque

input_buffer = deque(maxlen=5)  # Keep last 5 inputs

def on_input(button):
    input_buffer.append(button)

# In main loop:
if input_buffer:
    process_input(input_buffer.popleft())
```

### Optimized Debouncing
**Per-button tuning:**
- A/B buttons (select/back): 20ms debounce (infrequent presses)
- D-Pad: 10ms debounce (rapid navigation)
- Start/Select: 50ms debounce (rare, accidental presses common)

```python
DEBOUNCE_TIMES = {
    'A': 0.020,      # 20ms
    'B': 0.020,      # 20ms
    'UP': 0.010,     # 10ms
    'DOWN': 0.010,   # 10ms
    'LEFT': 0.010,   # 10ms
    'RIGHT': 0.010,  # 10ms
    'START': 0.050,  # 50ms
    'SELECT': 0.050, # 50ms
}
```

## Testing Strategy

### Automated Latency Benchmarks
```bash
# Add to performance test suite
pytest -m performance tests/test_performance_mvp.py::test_input_latency -v

# Assert latency thresholds met
assert avg_latency_ms < 50  # Pi 3B+ target
assert p95_latency_ms < 70  # Allow some variance
```

### Real-World User Testing
**Method:** Have users navigate Pokédex, collect feedback on responsiveness  
**Metrics:**
- Subjective feel (1-10 scale)
- Button misses (how often intended press doesn't register)
- Double-inputs (how often single press registers twice)

### Stress Testing
```bash
# Rapid button press simulation
python -c "
from src.hardware.gpio_buttons import ButtonManager
import time

manager = ButtonManager()
count = 0

def increment(btn):
    global count
    count += 1

manager.register_callback('A', increment)

# Simulate 100 presses at 10 per second
for _ in range(100):
    manager.simulate_press('A')  # If simulation supported
    time.sleep(0.1)

print(f'Registered {count}/100 presses')
"
```

## Pi-Specific Considerations

### GPIO Interrupt Priority
Raspberry Pi can prioritize GPIO interrupts over other tasks:
```python
# Set real-time priority for input thread (requires root)
import os
os.nice(-20)  # Higher priority (requires sudo)
```

### CPU Governor Impact
Powersave mode adds latency due to frequency scaling:
```bash
# Set performance mode for consistent latency
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Pull-Up/Pull-Down Resistors
**Hardware impact:** Weak pull resistors can cause slow signal rise/fall times  
**Fix:** Use 10kΩ external resistors for clean signals

## Development Workflow

### Testing Without Hardware
```python
# Mock GPIO for development on non-Pi systems
try:
    from gpiozero import Button
except ImportError:
    # Fallback keyboard simulation
    import pygame
    
    class MockButton:
        def __init__(self, key):
            self.key = key
        
        def is_pressed(self):
            keys = pygame.key.get_pressed()
            return keys[self.key]
```

### Headless Testing
```bash
# Test input latency in CI (without physical buttons)
SDL_VIDEODRIVER=dummy pytest -m performance --latency-threshold=100
```

## Quick Wins
1. ✅ Reduce debounce time from 100ms to 10-20ms for D-Pad
2. ✅ Use interrupt-driven GPIO (when_pressed) instead of polling
3. ✅ Implement input buffering for rapid presses
4. ✅ Pre-load adjacent sprites on button press (before release)
5. ✅ Add input latency assertions to performance tests (<50ms target)

## Troubleshooting

### Symptom: Buttons feel sluggish
**Causes:** High debounce time, low frame rate, heavy event handlers  
**Debug:** Run `test_input_latency.py`, check if >50ms

### Symptom: Double-inputs (one press = two actions)
**Causes:** Debounce too short, noisy signal, software bug  
**Debug:** Increase debounce time, check hardware connections

### Symptom: Dropped inputs
**Causes:** Event queue full, handler blocking, interrupt priority low  
**Debug:** Implement input buffering, profile event handler duration
