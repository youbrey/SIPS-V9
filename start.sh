#!/bin/bash
# start.sh
# =========
# Menyiapkan "monitor virtual" (Xvfb) supaya aplikasi GUI (CustomTkinter)
# bisa berjalan di Replit (yang tidak punya layar fisik), lalu
# menyiarkannya ke browser lewat noVNC supaya bisa dilihat & dipakai
# langsung dari tab "Webview" Replit.
#
# Alur:
#   1. Install dependensi Python (sekali saja, cache otomatis oleh pip)
#   2. Jalankan Xvfb di display :1 (resolusi 1280x800)
#   3. Jalankan window manager ringan (fluxbox) supaya jendela CTk
#      bisa di-drag/resize seperti biasa
#   4. Jalankan x11vnc untuk "menangkap" tampilan display :1
#   5. Jalankan noVNC sebagai jembatan VNC -> web (port 8080)
#   6. Jalankan main.py dengan DISPLAY=:1
#
# Setelah running, buka tab "Webview" Replit lalu arahkan ke port 8080
# (atau klik link yang muncul di console).

set -e

echo ">> Menginstal dependensi Python..."
python3 -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo ">> Menyiapkan virtual display (Xvfb :1)..."
Xvfb :1 -screen 0 1280x800x24 &
XVFB_PID=$!
sleep 2

export DISPLAY=:1

echo ">> Menjalankan window manager (fluxbox)..."
fluxbox >/tmp/fluxbox.log 2>&1 &
sleep 1

echo ">> Menjalankan VNC server (x11vnc)..."
x11vnc -display :1 -nopw -listen 0.0.0.0 -xkb -forever -shared >/tmp/x11vnc.log 2>&1 &
sleep 1

if [ ! -d "noVNC" ]; then
  echo ">> Mengunduh noVNC (sekali saja, akan tersimpan untuk run berikutnya)..."
  git clone --depth 1 https://github.com/novnc/noVNC.git >/tmp/novnc_clone.log 2>&1
fi

echo ">> Menjalankan jembatan noVNC (web) di port 8080..."
./noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 8080 >/tmp/novnc.log 2>&1 &
sleep 2

echo ""
echo "================================================================"
echo " GUI siap. Buka tab 'Webview' Replit, lalu arahkan ke port 8080"
echo " (atau klik 'Open in new tab' agar tampilan lebih lega)."
echo "================================================================"
echo ""

echo ">> Menjalankan aplikasi SIPS..."
python3 main.py
