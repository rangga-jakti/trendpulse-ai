@echo off
SETLOCAL

echo ============================================================
echo  TrendPulse AI - Windows Setup Script
echo  Platform Deteksi dan Analisis Tren Internet dengan AI
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python tidak ditemukan! Install Python 3.12 dari https://python.org
    pause & exit /b 1
)

echo [OK] Python ditemukan
echo.

:: Create virtual environment
echo [1/6] Membuat virtual environment...
python -m venv venv
IF ERRORLEVEL 1 (echo [ERROR] Gagal membuat venv & pause & exit /b 1)

:: Activate venv
call venv\Scripts\activate.bat
echo [OK] Virtual environment aktif

:: Upgrade pip
echo [2/6] Mengupgrade pip...
python -m pip install --upgrade pip --quiet

:: Install dependencies
echo [3/6] Menginstall dependencies (ini mungkin membutuhkan beberapa menit)...
pip install -r requirements.txt
IF ERRORLEVEL 1 (echo [ERROR] Gagal install requirements & pause & exit /b 1)
echo [OK] Dependencies terinstall

:: Setup .env
echo [4/6] Menyiapkan file konfigurasi...
IF NOT EXIST .env (
    copy .env.example .env
    echo [OK] File .env dibuat dari .env.example
    echo.
    echo *** PENTING: Edit file .env dan isi API keys berikut: ***
    echo   - GROQ_API_KEY: Dapatkan di https://console.groq.com (GRATIS)
    echo   - NEWS_API_KEY: Dapatkan di https://newsapi.org (GRATIS)
    echo   - DB_PASSWORD: Password PostgreSQL Anda
    echo.
) ELSE (
    echo [OK] File .env sudah ada
)

:: Django setup
echo [5/6] Menjalankan migrasi database...
python manage.py makemigrations
python manage.py migrate
IF ERRORLEVEL 1 (echo [ERROR] Migrasi gagal - pastikan PostgreSQL berjalan dan .env sudah dikonfigurasi & pause & exit /b 1)
echo [OK] Database siap

:: Collect static
echo [6/6] Mengumpulkan file statis...
python manage.py collectstatic --noinput --quiet
echo [OK] Static files terkumpul

:: Create superuser prompt
echo.
echo [OPSIONAL] Buat akun admin:
echo Ketik 'y' untuk membuat superuser, atau Enter untuk skip
set /p createsu=Buat superuser? (y/N): 
IF /I "%createsu%"=="y" (
    python manage.py createsuperuser
)

echo.
echo ============================================================
echo  Setup selesai! Pilih cara menjalankan aplikasi:
echo ============================================================
echo.
echo [A] Mode Development (tanpa data real, gunakan demo data):
echo     1. python manage.py fetch_trends --demo
echo     2. python manage.py runserver
echo.
echo [B] Mode Production (dengan data real dari Google Trends + NewsAPI):
echo     1. Edit .env dan isi semua API keys
echo     2. python manage.py fetch_trends
echo     3. python manage.py runserver
echo.
echo [C] Dengan Celery (untuk background tasks):
echo     Terminal 1: celery -A trendpulse worker --loglevel=info -P eventlet
echo     Terminal 2: celery -A trendpulse beat --loglevel=info
echo     Terminal 3: python manage.py runserver
echo.
echo Buka browser: http://127.0.0.1:8000
echo Admin panel:  http://127.0.0.1:8000/admin
echo ============================================================

pause
