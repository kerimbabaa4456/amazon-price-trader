@echo off
:: -------------------------------
:: Amazon Trader PRO - Run
:: -------------------------------

:: 1️⃣ pip upgrade
python -m pip install --upgrade pip

:: 2️⃣ gerekli paketleri yükle
python -m pip install requests beautifulsoup4

:: 3️⃣ Amazon Trader PRO'yu çalıştır
python amazon_trader.py

pause