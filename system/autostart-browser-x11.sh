# Configuration
STUDIO_URL=http://localhost:5000    # Main Obscreen Studio instance URL (could be a specific playlist /use/[playlist-id] or let obscreen manage playlist routing with /)
TARGET_RESOLUTION=auto              # e.g. 1920x1080 - Force specific resolution (supported list available with command `DISPLAY=:0 xrandr`)

# Disable screensaver and DPMS
xset s off
xset -dpms
xset s noblank

# Start unclutter to hide the mouse cursor
unclutter -display :0 -noevents -grab &

# Modify Chromium preferences to avoid restore messages
mkdir -p /home/pi/.config/chromium/Default 2>/dev/null
touch /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exited_cleanly": false/"exited_cleanly": true/' /home/pi/.config/chromium/Default/Preferences

# Resolution setup
if [ "$TARGET_RESOLUTION" != "auto" ]; then
    FIRST_CONNECTED_SCREEN=$(xrandr | grep " connected" | awk '{print $1}' | head -n 1)
    xrandr --output $FIRST_CONNECTED_SCREEN --mode $TARGET_RESOLUTION
fi

# Get screen resolution
RESOLUTION=$(DISPLAY=:0 xrandr | grep '*' | awk '{print $1}')
WIDTH=$(echo $RESOLUTION | cut -d 'x' -f 1)
HEIGHT=$(echo $RESOLUTION | cut -d 'x' -f 2)

# Start Chromium in kiosk mode
chromium-browser \
  --disk-cache-size=2147483648 \
  --disable-features=Translate \
  --ignore-certificate-errors \
  --disable-web-security \
  --disable-restore-session-state \
  --autoplay-policy=no-user-gesture-required \
  --start-maximized \
  --allow-running-insecure-content \
  --remember-cert-error-decisions \
  --noerrdialogs \
  --kiosk \
  --incognito \
  --user-data-dir=/home/pi/.config/chromium \
  --no-sandbox \
  --window-position=0,0 \
  --window-size=${WIDTH},${HEIGHT} \
  --display=:0 \
  ${STUDIO_URL}
