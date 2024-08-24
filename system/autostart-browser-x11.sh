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

# Force specific resolution (supported list available with command `DISPLAY=:0 xrandr`)
#FIRST_CONNECTED_SCREEN=$(xrandr | grep " connected" | awk '{print $1}' | head -n 1)
#xrandr --output $FIRST_CONNECTED_SCREEN --mode 800x600

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
  http://localhost:5000
