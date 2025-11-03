# Hardware Assembly Guide

This guide will help you assemble the physical components of your ShokeDex.

## Components Needed

### Required Components

- **Raspberry Pi**: 3B+ or newer (Pi 4 recommended for better performance)
- **MicroSD Card**: 16GB+ (Class 10 or A1/A2 rated)
- **LCD Display**: See [Display Options](#display-options)
- **Buttons**: 7 tactile push buttons (6mm x 6mm recommended)
  - 4 for directional pad (UP, DOWN, LEFT, RIGHT)
  - 2 for action buttons (SELECT, BACK)
  - 1 for START/Settings
- **Resistors**: 10kΩ resistors (optional, software pull-up used)
- **Breadboard or PCB**: For prototyping or final assembly
- **Jumper Wires**: Male-to-Female for Pi connections
- **Power Supply**: 
  - Official Raspberry Pi power supply (5V 3A for Pi 4)
  - Or battery pack for portable use (5V 2.5A minimum)

### Optional Components

- **3D Printed Case**: Custom enclosure design
- **Heat Sinks**: For Raspberry Pi CPU (recommended for Pi 3B+)
- **Cooling Fan**: For extended use or overclocking
- **Speaker**: For future sound effects feature
- **Power Switch**: For easy on/off

## Display Options

### 1. Official Raspberry Pi 7" Touch Display
- **Resolution**: 800x480
- **Connection**: DSI ribbon cable
- **Pros**: Perfect integration, touch support
- **Cons**: Larger size, higher cost
- **Setup**: Plug and play, no drivers needed

### 2. Waveshare 3.5" LCD (480x320)
- **Resolution**: 480x320
- **Connection**: GPIO or SPI
- **Pros**: Compact, affordable, good for handheld
- **Cons**: Requires driver installation
- **Setup**: Follow manufacturer instructions

### 3. Waveshare 5" HDMI LCD (800x480)
- **Resolution**: 800x480
- **Connection**: HDMI + USB (for touch)
- **Pros**: Easy setup, good resolution
- **Cons**: HDMI cable management
- **Setup**: Connect HDMI and USB, configure resolution

### 4. Generic HDMI Display
- **Resolution**: Various (1920x1080 common)
- **Connection**: HDMI
- **Pros**: Cheapest option, easy setup
- **Cons**: Not portable, too large for handheld
- **Setup**: Plug in HDMI cable

## GPIO Pin Layout

### Pin Assignments (BCM Mode)

| Function | GPIO Pin | Physical Pin | Notes                    |
|----------|----------|--------------|--------------------------|
| UP       | GPIO 17  | Pin 11       | D-pad Up                 |
| DOWN     | GPIO 27  | Pin 13       | D-pad Down               |
| LEFT     | GPIO 22  | Pin 15       | D-pad Left               |
| RIGHT    | GPIO 23  | Pin 16       | D-pad Right              |
| SELECT   | GPIO 24  | Pin 18       | A button / Confirm       |
| BACK     | GPIO 25  | Pin 22       | B button / Back          |
| START    | GPIO 16  | Pin 36       | Settings / Start Menu    |

### Ground Pins (Use any)
Physical Pins: 6, 9, 14, 20, 25, 30, 34, 39

### Power Pins (DO NOT use for buttons)
- 3.3V: Pins 1, 17
- 5V: Pins 2, 4

## Button Wiring

### Basic Wiring (Using Software Pull-up)

The simplest wiring method using internal pull-up resistors:

```
GPIO Pin ----[Button]---- GND
```

**For each button:**
1. Connect one leg of button to GPIO pin (via female jumper)
2. Connect other leg to any GND pin
3. No external resistor needed (software pull-up is configured)

### Advanced Wiring (With External Pull-up)

For more reliable operation:

```
         3.3V
          |
      [10kΩ Resistor]
          |
GPIO Pin -+----[Button]---- GND
```

**For each button:**
1. Connect one leg of button to GPIO pin
2. Connect other leg to GND
3. Add 10kΩ resistor between GPIO pin and 3.3V

⚠️ **Warning**: Never connect 5V directly to GPIO pins! This will damage your Pi.

## Assembly Instructions

### Step 1: Prepare Components

1. Gather all components listed above
2. Test Raspberry Pi boots correctly
3. Install Raspberry Pi OS (see [Installation Guide](pi_installation_guide.md))
4. Update system: `sudo apt update && sudo apt upgrade`

### Step 2: Plan Layout

Sketch your button layout on paper:
```
        [UP]
   [LEFT] [RIGHT]
       [DOWN]

    [SELECT] [BACK]

        [START]
```

### Step 3: Connect Display

**For Official Pi Display:**
1. Connect DSI ribbon cable to Pi and display
2. Connect power wires (red to 5V, black to GND)
3. Boot Pi to test

**For Waveshare SPI LCD:**
1. Follow manufacturer's driver installation guide
2. Connect to GPIO header (usually takes all pins)
3. Buttons must be wired to remaining free pins

**For HDMI Display:**
1. Connect HDMI cable
2. Boot and configure resolution if needed:
   ```bash
   sudo nano /boot/config.txt
   # Add: hdmi_mode=87
   # Add: hdmi_cvt=800 480 60 6 0 0 0
   ```

### Step 4: Wire Buttons

**Using a Breadboard (for prototyping):**

1. Insert buttons into breadboard
2. Use jumper wires to connect:
   - Button → GPIO (male-female jumper)
   - Button → GND rail
3. Connect GND rail to Pi GND pin

**Direct Wiring (for permanent install):**

1. Solder wires directly to button terminals
2. Use heat shrink tubing to insulate connections
3. Connect to Pi using female jumpers or GPIO header

### Step 5: Test Each Button

Test each button individually before proceeding:

```bash
# Test UP button (GPIO 17)
python3 -c "from gpiozero import Button; b = Button(17); print('Press UP button...'); b.wait_for_press(); print('UP works!')"

# Repeat for all buttons with their respective GPIO numbers
```

### Step 6: Install ShokeDex

Follow the [Pi Installation Guide](pi_installation_guide.md) to:
1. Clone repository
2. Install dependencies
3. Set up database
4. Configure autostart

### Step 7: Final Assembly

1. Test application with all buttons
2. Secure components in case (if using)
3. Organize wiring for clean look
4. Add cable management (zip ties, etc.)
5. Test for loose connections

## Testing and Calibration

### Button Test

Run the input latency test:

```bash
cd ~/ShokeDex
source venv/bin/activate
python tools/test_input_latency.py gpio
```

Expected results:
- Latency < 50ms per button
- No false triggers
- All buttons respond reliably

### Performance Test

Run performance profiling:

```bash
python tools/profile_performance.py 60
```

Target metrics for Pi 3B+:
- FPS: 25-30
- CPU: < 80%
- Memory: < 150MB
- Smooth navigation

## Troubleshooting

### Button Not Working

1. Check physical connection (loose wire?)
2. Verify GPIO pin number is correct
3. Test with simple gpiozero script
4. Check for short circuit to other pins
5. Try different GPIO pin

### Multiple Buttons Triggering Together

1. Check for short circuit between GPIO pins
2. Verify each button has separate connection to GND
3. Add small delay in code (debounce)
4. Check wiring quality

### Intermittent Button Response

1. Check for loose connections
2. Re-solder connections if needed
3. Increase debounce time in code
4. Use external pull-up resistors

### Display Not Working

1. Check cable connections
2. Verify driver installation (for non-HDMI)
3. Check power supply (adequate current?)
4. Test with different display

### Performance Issues

1. Check CPU temperature: `vcgencmd measure_temp`
2. Ensure adequate cooling
3. Lower FPS target in config
4. See [Pi Optimization Guide](pi_optimization_guide.md)

## Case Design

### 3D Printing

Design considerations for custom case:
- Access to all buttons
- Display mounting
- Cooling vents for Pi
- Access to SD card slot
- Cable routing for power
- Comfortable to hold

Recommended minimum internal dimensions:
- Width: 120mm (for Pi 4)
- Depth: 100mm
- Height: 30mm (without display)

### Materials

- **PLA**: Easy to print, rigid
- **PETG**: More durable, flexible
- **ABS**: Strong but harder to print

## Power Solutions

### USB Power Bank

For portable use:
- Capacity: 10,000mAh minimum
- Output: 5V 2.5A minimum (3A for Pi 4)
- Features: Pass-through charging helpful
- Runtime: ~6-8 hours depending on display

### Battery Pack

For integrated battery:
- LiPo battery (3.7V 5000mAh)
- Step-up converter to 5V
- Battery management system (BMS)
- Charging circuit
- ⚠️ Requires electrical knowledge for safety

### Wired Power

For stationary use:
- Official Raspberry Pi power supply
- 5V 2.5A minimum (3A for Pi 4)
- Good quality USB cable
- Surge protector recommended

## Safety Notes

⚠️ **Important Safety Guidelines:**

1. **Never connect 5V to GPIO pins** - Use only 3.3V or GND
2. **Check polarity** before connecting power
3. **Use proper heat dissipation** - Especially for enclosed cases
4. **Don't short circuit** - Double-check wiring before power on
5. **Handle battery with care** - If using LiPo batteries
6. **Avoid static discharge** - Use anti-static wrist strap when possible

## Next Steps

After completing hardware assembly:

1. ✅ Verify all buttons work correctly
2. ✅ Test display shows properly
3. ✅ Run performance profiling
4. ✅ Configure autostart
5. ✅ Optimize settings for your Pi model
6. ✅ Create backup of working configuration

## Additional Resources

- [Pi Installation Guide](pi_installation_guide.md) - Software setup
- [Pi Optimization Guide](pi_optimization_guide.md) - Performance tuning
- [GPIO Pin Reference](https://pinout.xyz/) - Interactive pinout diagram
- [gpiozero Documentation](https://gpiozero.readthedocs.io/) - Python GPIO library

---

**Enjoy your custom ShokeDex hardware!** 🎮✨
