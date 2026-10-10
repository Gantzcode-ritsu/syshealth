# 🩺 SysHealth CLI

SysHealth menampilkan kondisi komputer kamu di terminal: CPU, RAM, Swap, Disk, jaringan, dan proses yang paling banyak memakai resource. Data diperbarui otomatis di satu dashboard berwarna.

Aplikasi ini berjalan di Windows, macOS, dan Linux. Semua data dibaca dari komputer kamu dan tidak dikirim ke internet.

## 📑 Daftar Isi

- [🎯 Kegunaan](#-kegunaan)
- [✨ Fitur](#-fitur)
- [🚀 Instalasi](#-instalasi)
- [🎮 Cara Pakai](#-cara-pakai)
- [🔍 Membaca Dashboard](#-membaca-dashboard)
- [📝 Export Laporan](#-export-laporan)
- [🐍 Memakai sebagai Library](#-memakai-sebagai-library)
- [🏗️ Arsitektur](#️-arsitektur)
- [🧪 Pengembangan](#-pengembangan)
- [💡 Tips](#-tips)
- [🛠️ Pemecahan Masalah](#️-pemecahan-masalah)
- [❓ FAQ](#-faq)
- [🗺️ Rencana Pengembangan](#️-rencana-pengembangan)
- [🤝 Berkontribusi](#-berkontribusi)

## 🎯 Kegunaan

Pakai SysHealth saat kamu perlu:

- 🐌 Mencari tahu kenapa komputer lambat. Dashboard menunjukkan apakah CPU, RAM, atau disk yang penuh.
- 🔥 Menemukan program yang memakai CPU atau RAM paling besar.
- 🌐 Memeriksa kecepatan upload dan download yang sedang berjalan.
- 🛰️ Memantau server atau VPS lewat SSH, karena dashboard hanya membutuhkan terminal.
- 📄 Menyimpan kondisi sistem ke file JSON atau Markdown untuk laporan atau skrip.

## ✨ Fitur

| | Fitur | Keterangan |
|---|---|---|
| 📊 | Dashboard live | Angka diperbarui dengan selang yang kamu tentukan |
| 🎨 | Warna status | Hijau, kuning, dan merah mengikuti ambang batas pemakaian |
| 🧮 | Metrik lengkap | CPU total dan per core, RAM, Swap, Disk, Network I/O |
| 🔝 | Top proses | Urutkan berdasarkan CPU atau RAM, tampilkan 1 sampai 50 proses |
| 💾 | Export | Simpan snapshot ke JSON atau Markdown |
| 🖥️ | Lintas platform | Windows, macOS, dan Linux |
| 🔒 | Lokal | Tidak ada data yang keluar dari komputer kamu |

## 🚀 Instalasi

Kamu membutuhkan Python 3.9 atau lebih baru. Cek versinya dengan `python --version`.

### ⭐ Dengan pipx (disarankan)

pipx memasang aplikasi di lingkungan terpisah dan mengatur PATH untuk kamu.

```bash
pip install pipx
pipx ensurepath
pipx install git+https://github.com/Gantzcode-ritsu/syshealth.git
```

Tutup terminal, buka lagi, lalu ketik `syshealth`.

### 📦 Dengan pip

```bash
pip install git+https://github.com/Gantzcode-ritsu/syshealth.git
```

### 🧑‍💻 Dari source

Cara ini cocok untuk developer yang ingin mengubah kode.

```bash
git clone https://github.com/Gantzcode-ritsu/syshealth.git
cd syshealth
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux atau macOS
source .venv/bin/activate

pip install -e ".[dev]"
python -m pytest -v
```

### 🔄 Memperbarui dan menghapus

```bash
pipx upgrade syshealth-cli
pipx uninstall syshealth-cli
```

Kalau kamu memasang dengan pip, gunakan `pip install --upgrade git+https://github.com/Gantzcode-ritsu/syshealth.git` untuk memperbarui dan `pip uninstall syshealth-cli` untuk menghapus.

## 🎮 Cara Pakai

Ketik perintah ini untuk membuka dashboard:

```bash
syshealth
```

Tekan `Ctrl+C` untuk keluar. Kalau terminal Windows kamu tidak mengenali `syshealth`, jalankan `python -m syshealth`.

### 💻 Contoh perintah

```bash
syshealth                            # refresh 2 detik, 10 proses teratas
syshealth -i 1                       # refresh tiap 1 detik
syshealth -t 20                      # tampilkan 20 proses teratas
syshealth -s memory                  # urutkan proses berdasarkan RAM
syshealth -i 0.5 -t 15 -s cpu        # gabungkan beberapa opsi
syshealth --export json              # simpan snapshot JSON
syshealth --export md -o laporan.md  # simpan snapshot Markdown dengan nama pilihan kamu
syshealth --version                  # tampilkan versi
syshealth --help                     # tampilkan bantuan
```

### ⚙️ Daftar opsi

| Opsi | Singkat | Default | Fungsi |
|---|---|---|---|
| `--interval` | `-i` | `2.0` | Selang refresh dalam detik, minimal 0.5 |
| `--top` | `-t` | `10` | Jumlah proses yang tampil, dari 1 sampai 50 |
| `--sort` | `-s` | `cpu` | Urutan proses: `cpu` atau `memory` |
| `--export` | `-e` | tidak ada | Simpan snapshot (`json` atau `md`) tanpa membuka dashboard |
| `--output` | `-o` | dibuat otomatis | Lokasi dan nama file hasil export |
| `--version` | `-v` | tidak ada | Tampilkan versi |
| `--help` | tidak ada | tidak ada | Tampilkan bantuan |

### 🚦 Kode keluar

| Kode | Arti |
|---|---|
| `0` | Berhasil |
| `1` | Gagal: terminal tidak interaktif saat membuka dashboard, atau file export tidak bisa ditulis |
| `2` | Opsi tidak valid, misalnya `-i 0.1` atau `-t 99` |

Skrip kamu bisa membaca kode ini untuk menangani kegagalan.

## 🔍 Membaca Dashboard

Dashboard terbagi menjadi lima area:

| Area | Isi |
|---|---|
| 🏷️ Header | Nama dan versi aplikasi, nama komputer, sistem operasi, uptime, dan waktu sekarang |
| 📈 Metrik Utama | Bar untuk CPU, RAM, Swap, dan Disk |
| 🌐 Network I/O | Kecepatan upload dan download, serta total data sejak komputer menyala |
| 🔝 Top Proses | Tabel program dengan pemakaian terbesar |
| 🧵 CPU per Core | Satu bar untuk setiap core prosesor |

### 🚦 Arti warna

| Pemakaian | Status | Warna | Artinya |
|---|---|---|---|
| Di bawah 70% | Normal | 🟢 Hijau | Kondisi baik |
| 70% sampai 85% | Warning | 🟡 Kuning | Resource mulai padat |
| Di atas 85% | Critical | 🔴 Merah | Resource hampir habis dan perlu ditangani |

Angka tepat 85% masih berstatus Warning. Status Critical dimulai dari 85,1%. Ambang yang sama berlaku untuk kolom CPU % dan MEM % di tabel proses.

### 📊 Arti setiap metrik

| Metrik | Artinya | Kapan perlu diperhatikan |
|---|---|---|
| 🧠 CPU | Beban prosesor, dirata-rata dari semua core | Angka tinggi saat kamu tidak menjalankan apa pun |
| 🧩 RAM | Memori kerja yang terpakai, ditulis `terpakai / total` | RAM penuh memaksa sistem memakai Swap dan komputer melambat |
| 🔁 Swap | Memori cadangan di disk (disebut pagefile di Windows) yang dipakai saat RAM habis | Angka tinggi menandakan RAM kurang. Tulisan `tidak aktif` muncul kalau sistem tidak punya swap |
| 💽 Disk | Ruang terpakai di drive utama: `C:\` di Windows, `/` di Linux dan macOS | Disk hampir penuh menghambat sistem dan update |
| ⬆️⬇️ Upload dan Download | Kecepatan data keluar dan masuk saat ini, per detik | Angka tinggi saat kamu tidak mengunduh atau mengunggah apa pun |
| 📶 Total terkirim dan diterima | Jumlah data sejak komputer menyala | Berguna untuk memperkirakan pemakaian kuota |
| ⏱️ Uptime | Lama komputer menyala sejak boot terakhir | Uptime panjang kadang menandakan komputer perlu restart |

### 🔝 Tabel proses

| Kolom | Artinya |
|---|---|
| PID | Nomor identitas proses di sistem operasi |
| Name | Nama program |
| CPU % | Porsi kapasitas CPU total yang dipakai proses itu, dari 0 sampai 100% |
| MEM % | Porsi RAM total yang dipakai proses itu |

Nilai CPU per proses dihitung terhadap seluruh core, mengikuti Task Manager Windows. Perintah `top` di Linux menghitung per core, jadi pada komputer multi-core angkanya bisa melewati 100% dan berbeda dari tabel ini.

## 📝 Export Laporan

Opsi `--export` mengambil satu snapshot kondisi sistem dan menyimpannya ke file. Dashboard tidak terbuka.

```bash
syshealth --export json
syshealth --export md -o laporan.md
```

| Format | Cocok untuk |
|---|---|
| 🧾 JSON | Diolah oleh program atau skrip lain |
| 📃 Markdown | Dibaca langsung, ditempel ke dokumen, laporan, atau tiket bantuan |

Tanpa `-o`, file muncul di folder saat ini dengan nama `syshealth_snapshot_TAHUNBULANTANGGAL_JAMMENITDETIK.json` atau `.md`. Folder tujuan dibuat otomatis kalau belum ada. Snapshot memakai dua pembacaan berjarak sekitar 1 detik supaya nilai CPU dan jaringan akurat.

### 🧾 Struktur JSON

Semua ukuran memori dan disk memakai satuan byte. Kecepatan jaringan memakai byte per detik. Persentase berada di rentang 0 sampai 100.

```json
{
  "timestamp": "2026-10-10T16:22:49",
  "hostname": "NAMA-PC",
  "os_name": "Windows 10",
  "uptime_seconds": 29740.0,
  "cpu": {
    "total_percent": 33.7,
    "per_core_percent": [37.8, 31.8, 30.1, 35.2],
    "core_count": 4
  },
  "memory": {
    "total": 6350000000,
    "used": 5940000000,
    "free": 410000000,
    "available": 410000000,
    "percent": 93.7
  },
  "swap": { "total": 10737418240, "used": 4724464025, "free": 6012954215, "percent": 44.0 },
  "disk": {
    "path": "C:\\",
    "total": 255000000000,
    "used": 154000000000,
    "free": 101000000000,
    "percent": 60.4
  },
  "network": {
    "bytes_sent": 7130000000,
    "bytes_recv": 146780000000,
    "upload_speed": 218726.4,
    "download_speed": 6353510.4
  },
  "processes": [
    { "pid": 1234, "name": "chrome.exe", "cpu_percent": 12.3, "memory_percent": 4.1 }
  ],
  "process_sort": "cpu"
}
```

Angka di atas hanya contoh untuk menunjukkan bentuk datanya.

### ⏰ Snapshot terjadwal

Contoh cron di Linux atau macOS untuk menyimpan snapshot tiap jam:

```bash
0 * * * * syshealth --export json -o /var/log/syshealth/$(date +\%H).json
```

Di Windows, buat tugas di Task Scheduler yang menjalankan `syshealth --export json -o C:\logs\health.json`.

## 🐍 Memakai sebagai Library

Kamu bisa mengimpor kolektor datanya di skrip Python sendiri:

```python
from syshealth.collector import SystemCollector

collector = SystemCollector(top_n=5, sort_by="memory")
collector.warm_up()          # satu pembacaan awal supaya CPU dan jaringan akurat
snapshot = collector.collect()

print(snapshot.cpu.total_percent)
print(snapshot.memory.percent)
for proc in snapshot.processes:
    print(proc.pid, proc.name, proc.memory_percent)

data = snapshot.to_dict()    # dict siap diubah ke JSON
```

`SystemCollector` menerima empat argumen:

| Argumen | Default | Fungsi |
|---|---|---|
| `top_n` | `5` | Jumlah proses yang dikembalikan, minimal 1 |
| `sort_by` | `"cpu"` | `"cpu"` atau `"memory"` |
| `disk_path` | drive utama | Path disk yang diperiksa |
| `clock` | `time.monotonic` | Fungsi waktu, berguna untuk pengujian |

Nilai CPU dan kecepatan jaringan dihitung dari selisih antar pemanggilan. Panggil `warm_up()` sebelum `collect()` pertama.

## 🏗️ Arsitektur

```
syshealth/
├── __init__.py     # versi paket
├── __main__.py     # python -m syshealth
├── utils.py        # format byte, uptime, dan penentu warna
├── collector.py    # SystemCollector dan dataclass hasil
├── formatter.py    # panel rich, dashboard live, export JSON dan Markdown
└── main.py         # antarmuka command line (typer)
tests/
├── test_collector.py
├── test_formatter.py
└── test_main.py
```

| Modul | Tanggung jawab |
|---|---|
| `utils.py` | Mengubah byte menjadi KB, MB, GB, TB. Menentukan warna dan label status dari persentase |
| `collector.py` | Membaca data lewat psutil dan mengembalikannya sebagai `SystemSnapshot` |
| `formatter.py` | Menyusun layout rich dan menjalankan Live. Membuat teks JSON dan Markdown |
| `main.py` | Membaca opsi command line, memilih antara dashboard dan export |

Alur data berjalan satu arah: `main.py` membuat `SystemCollector`, kolektor menghasilkan `SystemSnapshot`, lalu `formatter.py` mengubahnya menjadi tampilan atau file. Kolektor tidak mengenal tampilan, dan formatter tidak membaca data sistem.

## 🧪 Pengembangan

```bash
pip install -e ".[dev]"
ruff check .
python -m pytest -v
```

- ✅ Test mencakup pengumpulan data, format tampilan, dan perintah command line.
- 🧱 Test jaringan memakai data tiruan supaya hasilnya stabil di semua mesin.
- 🤖 GitHub Actions menjalankan test di Linux, macOS, dan Windows, dengan Python 3.9 sampai 3.13.
- 🧹 Ruff memeriksa gaya kode. Konfigurasinya ada di `pyproject.toml`.

Aturan kode:

1. Tambahkan type hint pada fungsi publik.
2. Taruh logika pembacaan data hanya di `collector.py`, tampilan hanya di `formatter.py`, dan parsing opsi hanya di `main.py`.
3. Tulis test untuk setiap perilaku baru. Validasi struktur dan rentang nilai, atau pakai `monkeypatch` untuk nilai yang berubah-ubah.

## 💡 Tips

- 🔍 Jalankan `syshealth -s memory` untuk melihat pemakan RAM, atau `syshealth -s cpu` untuk pemakan CPU.
- ⚡ Pakai `-i 0.5` kalau kamu ingin melihat perubahan dua kali per detik.
- 📐 Buka terminal berukuran 100 kolom x 30 baris atau lebih supaya semua area tampil utuh.
- 🖥️ Gunakan Windows Terminal, PowerShell, iTerm2, atau GNOME Terminal supaya warna dan garis tampil rapi.
- 🛰️ Dashboard berjalan lewat SSH selama terminalnya interaktif.

## 🛠️ Pemecahan Masalah

<details>
<summary>❌ Perintah <code>syshealth</code> tidak dikenali di Windows</summary>

Folder `Scripts` milik Python belum masuk ke PATH. Pasang dengan pipx, atau jalankan `python -m syshealth`.

</details>

<details>
<summary>❌ Muncul pesan "Live dashboard membutuhkan terminal interaktif"</summary>

Dashboard tidak bisa berjalan kalau output dialihkan lewat pipe atau skrip. Gunakan `--export json` atau `--export md`.

</details>

<details>
<summary>🧩 Tampilan terpotong atau berantakan</summary>

Perbesar jendela terminal dan pindah ke terminal modern.

</details>

<details>
<summary>0️⃣ Nilai CPU di awal menunjukkan 0%</summary>

CPU dan kecepatan jaringan dihitung dari selisih dua pembacaan. Angkanya benar setelah satu siklus refresh.

</details>

<details>
<summary>🔐 Beberapa proses bernilai 0</summary>

Sistem operasi tidak mengizinkan pembacaan proses tersebut. Jalankan SysHealth sebagai administrator atau dengan `sudo`.

</details>

<details>
<summary>📁 Muncul "Permission denied" saat export</summary>

Kamu tidak punya izin menulis di folder tujuan. Pilih folder lain dengan `-o`.

</details>

## ❓ FAQ

**🛡️ Apakah SysHealth mengubah sesuatu di komputer saya?**
Tidak. SysHealth membaca informasi sistem lewat library `psutil` dan tidak menulis apa pun selain file export yang kamu minta.

**⚙️ Apakah SysHealth membebani komputer?**
Beban utamanya berasal dari pembacaan daftar proses di setiap refresh. Naikkan nilai `-i` untuk mengurangi frekuensinya.

**✂️ Bisakah saya menutup proses dari dashboard?**
Belum. SysHealth hanya menampilkan data.

**💽 Kenapa hanya satu disk yang tampil?**
SysHealth membaca drive utama saja. Dukungan banyak disk ada di rencana pengembangan.

## 🗺️ Rencana Pengembangan

Daftar ini berisi ide, bukan janji jadwal.

- [ ] 📚 Tampilkan semua partisi disk
- [ ] 🌡️ Suhu dan baterai, dengan cadangan untuk sistem yang tidak mendukungnya
- [ ] 🎚️ Ambang warna kustom lewat opsi `--warn` dan `--crit`
- [ ] 🔎 Filter proses berdasarkan nama
- [ ] 📉 Grafik mini riwayat CPU dan jaringan
- [ ] 🗂️ Log snapshot berkala dalam format JSONL
- [ ] 1️⃣ Mode `--once` untuk mencetak satu tampilan lalu keluar

## 🤝 Berkontribusi

Kirim bug dan ide fitur lewat [Issues](https://github.com/Gantzcode-ritsu/syshealth/issues). Sertakan sistem operasi, versi Python, perintah yang kamu jalankan, dan pesan error lengkap.

Untuk pull request:

1. Buat branch dari `main`.
2. Tambahkan test untuk perubahanmu.
3. Jalankan `ruff check .` dan `python -m pytest -v`.
4. Jelaskan apa yang berubah dan alasannya di deskripsi PR.

## 🧰 Dibangun dengan

| Library | Fungsi |
|---|---|
| [psutil](https://github.com/giampaolo/psutil) | Membaca data sistem |
| [rich](https://github.com/Textualize/rich) | Tampilan terminal |
| [typer](https://github.com/fastapi/typer) | Antarmuka command line |

## 📜 Lisensi

MIT. Teks lengkap ada di berkas `LICENSE`.
