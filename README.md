# Save Editor v3

Editor save untuk game simulasi mining PC (Unity IL2CPP). File `v3.dat` memakai .NET BinaryFormatter tanpa enkripsi, jadi nilainya bisa diedit langsung.

## Versi web (PWA)
Aplikasi web yang bisa dipasang di HP dan jalan tanpa internet. Pilih `v3.dat`, ubah nilainya, lalu tekan **Unduh v3.dat**. Semua diproses di perangkatmu.

### Cara memasang
PWA hanya bisa dipasang kalau dibuka lewat HTTPS, bukan dari file lokal. Cara paling mudah memakai GitHub Pages:
1. Upload semua isi folder ini ke repo GitHub (`index.html` harus di root repo).
2. Buka **Settings > Pages**, pilih branch `main` dan folder `/ (root)`, lalu Save.
3. Tunggu satu sampai dua menit, lalu buka `https://<username>.github.io/<nama-repo>/` di Chrome HP.
4. Tekan tombol **Pasang** di halaman, atau menu Chrome (tiga titik) > **Instal aplikasi** / **Tambahkan ke layar utama**.

Setelah terpasang, aplikasi bisa dibuka dari layar utama dan jalan offline. Kalau kamu mengubah file di repo, naikkan `CACHE` di `sw.js` (misalnya `save-editor-v2`) supaya HP mengambil versi baru.

## Versi Python
```
python3 save_editor.py v3.dat                      # tampilkan semua field
python3 save_editor.py v3.dat Money=500000 Level=15 -o v3_edit.dat
```
`save_editor.py` dan `nrbf.py` harus berada di folder yang sama. Hanya nilai angka dan true/false di class `Player` yang diubah, dan ukuran file tidak berubah.

## Sebelum menimpa save
1. Salin `v3.dat` asli sebagai cadangan.
2. Tutup game sepenuhnya.
3. Timpa `v3.dat`, lalu buka game.

Format bisa berubah kalau game diupdate (misalnya jadi `v4`).
