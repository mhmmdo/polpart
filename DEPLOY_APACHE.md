# Panduan Deploy Aplikasi Streamlit dengan Apache Reverse Proxy

Dokumen ini menjelaskan langkah-langkah untuk melakukan deployment aplikasi **Sistem Prediksi Partisipasi Politik (PolPart RF)** pada VPS Linux menggunakan **Apache** sebagai Reverse Proxy, **Systemd** sebagai process manager, dan **Certbot** untuk SSL (HTTPS) gratis.

---

## Prasyarat
1. VPS dengan OS **Ubuntu Server 20.04/22.04 LTS** atau Debian.
2. Akses user dengan hak `sudo`.
3. Domain **`polpart.simpelcloud.web.id`** sudah diatur DNS-nya (A Record diarahkan ke IP Publik VPS).
4. Port `80` (HTTP) dan `443` (HTTPS) dalam keadaan terbuka di firewall VPS.

---

## Langkah 1: Kloning & Persiapan File di VPS
1. Masuk ke VPS melalui SSH:
   ```bash
   ssh aplik003@20.24.226.102
   ```
2. Pastikan paket sistem VPS up-to-date:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. Instal Git, Python pip, virtualenv, Apache, dan Certbot:
   ```bash
   sudo apt install git python3-pip python3-venv apache2 certbot python3-certbot-apache -y
   ```
4. Salin kode aplikasi ke direktori web server (disarankan di path `/var/www/simpelcloud/public_html/polpart-simpelcloud`):
   ```bash
   # Masuk ke direktori public_html
   cd /var/www/simpelcloud/public_html
   
   # Kloning repositori Github Anda
   git clone https://github.com/mhmmdo/polpart.git polpart-simpelcloud
   ```

---

## Langkah 2: Setup Virtual Environment & Database
1. Masuk ke direktori proyek:
   ```bash
   cd /var/www/simpelcloud/public_html/polpart-simpelcloud
   ```
2. Buat Virtual Environment Python (`venv`) agar library tidak bentrok dengan sistem utama:
   ```bash
   python3 -m venv venv
   ```
3. Aktifkan `venv` dan pasang seluruh dependensi:
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Lakukan inisialisasi basis data SQLite awal:
   ```bash
   python scripts/init_db.py
   ```
   *Catatan: Pastikan skrip berhasil membuat berkas database di `database/polpart.db`.*

---

## Langkah 3: Setup Systemd Service (Menjalankan Aplikasi di Background)
Agar Streamlit tetap aktif secara permanen di server meskipun terminal SSH ditutup, buat layanan sistem background daemon menggunakan **systemd**.

1. Buat berkas konfigurasi service baru:
   ```bash
   sudo nano /etc/systemd/system/polpart.service
   ```
2. Isi berkas tersebut dengan konfigurasi berikut:
   ```ini
   [Unit]
   Description=Streamlit PolPart Application
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/var/www/simpelcloud/public_html/polpart-simpelcloud
   ExecStart=/var/www/simpelcloud/public_html/polpart-simpelcloud/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
3. Simpan dan keluar (`Ctrl + O`, `Enter`, lalu `Ctrl + X`).
4. Jalankan ulang systemd agar mendeteksi service baru, nyalakan service, dan daftarkan agar otomatis aktif saat VPS booting:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start polpart
   sudo systemctl enable polpart
   ```
5. Periksa status service untuk memastikan telah aktif dan berjalan tanpa error:
   ```bash
   sudo systemctl status polpart
   ```

---

## Langkah 4: Konfigurasi Apache Reverse Proxy
1. Aktifkan modul-modul proxy, rewrites, dan headers pada Apache:
   ```bash
   sudo a2enmod proxy proxy_http proxy_wstunnel rewrite headers
   ```
2. Buat berkas konfigurasi Virtual Host Apache baru untuk domain Anda:
   ```bash
   sudo nano /etc/apache2/sites-available/polpart.conf
   ```
3. Isi dengan blok konfigurasi di bawah ini (mengaktifkan web redirect dan tunneling WebSockets):
   ```xml
   <VirtualHost *:80>
       ServerName polpart.simpelcloud.web.id

       RewriteEngine On

       # Mengarahkan koneksi WebSocket Streamlit (_stcore/stream) ke proxy wstunnel
       RewriteCond %{HTTP:Upgrade} =websocket [NC]
       RewriteRule /(.*)           ws://localhost:8501/$1 [P,L]
       
       # Mengarahkan koneksi HTTP biasa
       RewriteCond %{HTTP:Upgrade} !=websocket [NC]
       RewriteRule /(.*)           http://localhost:8501/$1 [P,L]

       # Pengaturan Proxy Pass utama
       ProxyPass / http://localhost:8501/
       ProxyPassReverse / http://localhost:8501/

       # Pengaturan Header Keamanan
       ProxyPreserveHost On
       RequestHeader set X-Forwarded-Proto "http"

       ErrorLog ${APACHE_LOG_DIR}/polpart_error.log
       CustomLog ${APACHE_LOG_DIR}/polpart_access.log combined
   </VirtualHost>
   ```
4. Simpan berkas dan aktifkan konfigurasi situs tersebut:
   ```bash
   sudo a2ensite polpart.conf
   ```
5. Uji kesesuaian sintaks konfigurasi Apache lalu restart layanan Apache:
   ```bash
   sudo apache2ctl configtest
   sudo systemctl restart apache2
   ```

---

## Langkah 5: Pasang SSL (HTTPS) Let's Encrypt
1. Jalankan Certbot untuk menginstal sertifikat SSL otomatis pada Apache:
   ```bash
   sudo certbot --apache -d polpart.simpelcloud.web.id
   ```
2. Masukkan alamat email Anda bila diminta, setujui persyaratan, dan pilih opsi **"Redirect"** agar Certbot otomatis mengalihkan semua akses web HTTP (port 80) langsung ke HTTPS (port 443) yang aman.
3. Certbot akan otomatis memperbarui file virtual host Apache Anda dengan sertifikat SSL terenkripsi.

Aplikasi Anda kini sudah dapat diakses dengan aman di:
👉 **`https://polpart.simpelcloud.web.id`**

---

## Pemeliharaan Proyek (Maintenance)

### Mengambil Pembaruan Kode Terbaru dari Git:
Apabila Anda melakukan perubahan kode di server lokal/PC Anda dan mengunggahnya ke GitHub, lakukan langkah ini di VPS untuk meng-update-nya:
```bash
# Masuk ke folder proyek
cd /var/www/simpelcloud/public_html/polpart-simpelcloud
git pull origin main

# Restart aplikasi Streamlit agar memuat ulang kode baru
sudo systemctl restart polpart
```

### Utilitas Perintah Lainnya:
* **Melihat log aplikasi real-time**: `sudo journalctl -u polpart -f`
* **Restart Apache**: `sudo systemctl restart apache2`
* **Mematikan aplikasi**: `sudo systemctl stop polpart`
