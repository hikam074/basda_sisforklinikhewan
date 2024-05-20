import psycopg2
import os
import sys
import time
import tabulate

# SESUAIKAN DENGAN POSTGRE KALIAN -----------------------------------------------------------------
def postgresql_connect():                   # menghubungkan postgresql dan python
    conn = psycopg2.connect(
        dbname="SatSet Care",
        user="postgres",
        password="dammahom51",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    return conn, cur

def postgresql_commit_nclose(conn, cur):    # commit dan tutup
    conn.commit()
    boolean = cur.rowcount
    cur.close()
    conn.close()
    return boolean

def postgresql_cls(conn, cur):              # tutup
    cur.close()
    conn.close()

def posgresql_alldata_akun(conn, cur):      # memasukkan semua data akun ke satu variabel
    cur.execute('SELECT * FROM pelanggan')
    listdatapelanggan = cur.fetchall()
    cur.execute('SELECT * FROM staf')
    listdatastaf = cur.fetchall()
    cur.execute('SELECT * FROM dokter')
    listdatadokter = cur.fetchall()
    listdata = listdatapelanggan
    listdata.append(listdatastaf)
    listdata.append(listdatadokter)
    return listdata
# -------------------------------------------------------------------------------------------------
 
# 0. WELCOMING INTERFACE --------------------------------------------------------------------------
def welcome_interface():
    os.system('cls')
    print(header_fancy)
    input("Ketik [ENTER] untuk melanjutkan  ")

    for i in range(0,delay_welcome):
        os.system('cls')
        print(mini_header)
        print("Memeriksa status database", '.'*(i+1))
        time.sleep(1)
    try :
        postgresql_connect()
        print("\nDATABASE SIAP")
        time.sleep(1)
    except:
        print("Database tidak ada, membuat database baru ")
        time.sleep(1)
        db_pertama()

# -------------------------------------------------------------------------------------------------

# 1. LAUNCH PAGE ----------------------------------------------------------------------------------
def launch_page():

    # 1.1 LOGIN v
    def login():
        # input username dan password
        os.system('cls')
        uname = input("Masukkan username anda : ")
        password = input("Masukkan password anda : ")

        conn, cur = postgresql_connect()    # mengakses postgresql
        # cek tabel pelanggan
        cur.execute(f"""
                    SELECT * FROM pelanggan
                    WHERE
                        uname_pelanggan = \'{uname}\'
                        AND pw_pelanggan = \'{password}\'
                    """)
        is_pelanggan = cur.fetchone()
        # cek tabel dokter
        cur.execute(f"""
                    SELECT * FROM dokter
                    WHERE
                        uname_dokter = \'{uname}\'
                        AND pw_dokter = \'{password}\'
                    """)
        is_dokter = cur.fetchone()
        # cek tabel staf
        cur.execute(f"""
                    SELECT * FROM staf
                    WHERE
                        uname_staf = \'{uname}\'
                        AND pw_staf = \'{password}\'
                    """)
        is_staf = cur.fetchone()
        postgresql_cls(conn, cur)   # menutup postgresql

        # pengecekan apakah pelanggan, dokter atau staf
        if is_pelanggan :
            mode_pelanggan(uname, nama_lengkap_logged = is_pelanggan[1])
        elif is_dokter :
            mode_dokter(uname, nama_lengkap_logged = is_dokter[1])
        elif is_staf :
            mode_admin(uname, nama_lengkap_logged = is_staf[1])
        else :
            relogin = input("username atau password anda salah, tekan [ENTER] untuk coba lagi atau [Q] untuk kembali : ")
            if relogin == '':
                login()
            else :
                launch_page()

    # 1.2 SIGNUP v
    def signup():
        os.system('cls')
        # daftarkan data
        namapelanggan       = (input("Masukkan nama lengkap anda : "))
        notelppengguna      = (input("Masukkan nomor telepon anda : "))
        usernamepelanggan   = (input("Masukkan username (untuk digunakan login) : "))
        passwordpelanggan   = (input("Masukkan password (untuk digunakan login) : "))

        if namapelanggan == '':
            namapelanggan = 'null'
        else :
            namapelanggan = f"'{namapelanggan}'"
        if notelppengguna == '':
            notelppengguna = 'null'
        else :
            notelppengguna = f"'{notelppengguna}'"
        if usernamepelanggan == '':
            usernamepelanggan = 'null'
        else :
            usernamepelanggan = f"'{usernamepelanggan}'"
        if passwordpelanggan == '':
            passwordpelanggan = 'null'
        else :
            passwordpelanggan = f"'{passwordpelanggan}'"

        conn, cur = postgresql_connect()    # sambungkan ke postgresql

        try:    # bila sata bisa ditambahkan ke postgresql
            insert_script = f"INSERT INTO pelanggan (nama_pelanggan,tlp_pelanggan,uname_pelanggan,pw_pelanggan) VALUES ({namapelanggan},{notelppengguna},{usernamepelanggan},{passwordpelanggan})"
            cur.execute(insert_script)
            postgresql_commit_nclose(conn, cur)         # commit dan close postgresql

            input('Registrasi Berhasil')
            launch_page()   # kembali ke menu

        except Exception as error:      # bila data gagal ditambahkan
            print(error)
            postgresql_cls(conn, cur)
            input('Tekan [Enter] untuk kembali ke menu : ')
            launch_page()   # kembali ke menu

    # I.4 EXIT v
    def exit():
        sys.exit()

    # Interface Launch Page
    os.system('cls')
    print(header)
    print("Selamat datang di Klinik Satwa Sehat\n")
    print(" [1] Log-in \n [2] Sign-Up Customer \n [3] Manual Book \n [4] Exit \n")
    # Pilih menu
    launch_choice = input("Silahkan pilih menu anda : ")

    # 1.1 LOGIN v
    if launch_choice == '1':
        login()

    # 1.2 SIGNUP v
    elif launch_choice == '2':
        signup()

    # 1.3 MANUAL BOOK v
    elif launch_choice == '3':
        manual_book()
        launch_page()

    # 1.4 EXIT v
    elif launch_choice == '4':
        exit()

    # BILA SALAH INPUT v
    else:
        launch_page()

# -------------------------------------------------------------------------------------------------

# 2. FITUR DOKTER ---------------------------------------------------------------------------------
def mode_dokter(uname, nama_lengkap_logged):
    def lihat_data_layanan(conn, cur):  # v
        """Menampilkan data layanan dari database."""
        cursor = conn.cursor()
        # Query untuk mengambil semua data dari tabel 'layanan'
        query = """
        SELECT *
        FROM layanan
        """
        cursor.execute(query)
        # Mendapatkan semua data layanan
        data_layanan = cursor.fetchall()
        cursor.close()
            
        headers = ['ID', 'Nama Layanan', 'Harga Layanan']
        # Menampilkan data layanan dalam bentuk tabel
        print(tabulate.tabulate(data_layanan, headers=headers, tablefmt="grid"))

    def rekam_medis_buat(conn, cur, uname): # fatal eror
        nm_hwn=input('Nama hewan: ')
        nm_plnggn=input('Nama pelanggan: ')
        lihat_data_layanan(conn, cur)
        id_layanan_hewan = input('masukkan id layanan')

        hewannya= f"select id_hewan from hewan join where nama_hewan = '{nm_hwn}' and nama_pelanggan = '{nm_plnggn}'"
        no_id_hewan=cur.execute(hewannya)

        dokternya = f'select id_dokter from dokter where uname={uname}'
        id_dokter=cur.execute(dokternya)

        layanannya=f'select id_layananan from layanan where id_layanan={id_layanan_hewan}'
        id_layanan=cur.execute(layanannya)

        keterangan=input('Hasil Medis: ')
        nilai=[no_id_hewan,id_dokter,id_layanan,keterangan]
        sintaksi=f'insert into rekam_medis (id_hewan,id_dokter,id_layanan,hasil_medis) values({nilai})'
        cur.execute(sintaksi)

        postgresql_commit_nclose(conn, cur)

    def rekam_medis_edit(conn, cur, uname): # fatal eror
        print('[1] Nama Hewan\n[2] Nama Dokter\n[3] Layanan\n[4] Hasil Medis\n[5] Semua\n[Enter] Exit ')
        pilih_lagi=input('Pilih: ')
        hal_yang_dirubah=["hewan","dokter","layanan","rekam_medis"]
        siapa_yang_dirubah=input("No id rekam medis yang akan dirubah:")
        pilih=hal_yang_dirubah[int(pilih_lagi)-1]
        if '0'<=pilih_lagi<='2':
            ketik=input(f"Nama {pilih} yang benar: ")
            pilihan=f'id_{pilih}'
            sintaksi =f' select {pilihan} from {pilih} where nama_{pilih}={ketik}'
            sintaksi_baru=f'update rekam_medis set id_{pilih}={sintaksis} where id_rekamed={siapa_yang_dirubah}'
            cur.execute(sintaksi_baru)
            conn.commit()
            conn.close()
            cur.close()
        elif pilih_lagi=='3': 
            baru=input("Hasil medis yang benar: ")
            sintaksi_baru=f'update rekam_medis set hasil_medis={baru} where id_rekamed={siapa_yang_dirubah}'
            cur.execute(sintaksi_baru)
            conn.commit()
            conn.close()
            cur.close()
        elif pilih_lagi=='4':
            sintaksis1=[]
            for i in range(len(hal_yang_dirubah)-1):
                pilih=hal_yang_dirubah[i]
                ketik=input(f"Nama {pilih} yang benar: ")
                pilihan=f'id_{pilih}'
                id +=f' select {pilihan} from {pilih} where nama_{pilih}={ketik}'
            ketik=input("Hasil medis yang benar: ")
            sintaksis= f"""update rekam_medis set id_hewan={id[0]},id_dokter={id[1]},id_layanan={id[2]},hasil_medis={ketik} where id_rekamed={siapa_yang_dirubah}"""
            cur.execute(sintaksis)
            conn.commit()
            conn.close()
            cur.close()
        else:
            print("Kembali ke halaman sebelumnya") 

    conn, cur = postgresql_connect()

    print(f"selamat datang, {nama_lengkap_logged} !")
    print(" [1] Rekam Medis \n [2] Profil Anda \n [3] Log-out ")
    dokter_choice = input("Silahkan pilih menu anda : ")

    # 2.1 REKAM MEDIS fatal eror
    if dokter_choice == '1':
        print('[1] Buat\n[2] Edit\n[3] Lihat')
        pilihan=input('Pilih: ')
        if pilihan=='1' or pilihan.lower() =='buat':
            rekam_medis_buat(conn, cur, uname)

        elif pilihan  == '2' or  pilihan.lower()=='edit':
            rekam_medis_edit(conn, cur, uname)

        elif pilihan=='3' or pilihan.lower()=='lihat':
            sintaksis ="""select r.id_rekamed, h.nama_hewan,d.nama_dokter,l.nama_layanan, r.hasil_medis 
            from rekam_medis r join hewan h on (h.id_hewan=r.id_hewan)
            join dokter d on (d.id_dokter=r.id_dokter)
            join layanan l on (l.id_layanan=r.id_layanan)"""
            nilai=cur.execute(sintaksis)
            header = ["Id Rekam Medis", "Nama Hewan", "Nama Dokter", "Nama Layanan","Hasil Medis"]
            print(tabulate.tabulate(nilai,headers=header, tablefmt="fancy_grid"))

            postgresql_commit_nclose(conn, cur)

        elif pilihan=='4':
            id=input('Id rekam medis yang akan di hapus')
            sintaksis_hapus= f"DELETE FROM rekam_medis WHERE id_rekamed = '{id}' " 
            cur.execute(sintaksis_hapus)
            postgresql_commit_nclose(conn, cur)

        mode_dokter(uname, nama_lengkap_logged)

    # 2.2 PROFIL ANDA v
    elif dokter_choice == '2':
        print('[1] Lihat\n[2] Edit')
        pilihan_anda=input('Pilih: ')

        if pilihan_anda=='1':
            sintaksis=f"select * from dokter where uname_dokter = '{uname}'"
            cur.execute(sintaksis)
            nilai = cur.fetchall()
            header = ["Id Dokter", "Nama Dokter", "Telp Dokter", "Nama Layanan","Hasil Medis"]
            print(tabulate.tabulate(nilai,headers=header, tablefmt="fancy_grid"))

        elif pilihan_anda=='2':
            simpan=["nama_dokter","tlp_dokter","no_stp","uname_dokter","pw_dokter"]
            for i,value in enumerate(simpan):
                yes=input(f'Apakah {value} salah? (y/t)')
                if yes=='y':
                    if value == 'tlpn_dokter':
                        update=input('Perbaiki: ')
                        sintaksis= f"update dokter set {simpan[i]}= {update} where uname_dokter='{uname}'"
                    else:
                        update=input('Perbaiki: ')
                        sintaksis= f"update dokter set {simpan[i]}= '{update}' where uname_dokter='{uname}'"
                    cur.execute(sintaksis)
            postgresql_commit_nclose(conn, cur)
        mode_dokter(uname, nama_lengkap_logged)

    # 2.3 EXIT v
    elif dokter_choice == '3':
        launch_page()

    # BILA SALAH INPUT
    else:
        mode_dokter(uname, nama_lengkap_logged)

# -------------------------------------------------------------------------------------------------

# 3. FITUR KUSTOMER -------------------------------------------------------------------------------
def mode_pelanggan(uname, nama_lengkap_logged):
    print(f"Selamat datang, {nama_lengkap_logged} !")
    print(" [1] RESERVASI \n [2] Hewan Peliharaan anda \n [3] Rekam Medis Hewan Anda \n [4] Riwayat Kunjungan Anda \n [5] Profil Anda \n [6] Lihat Dokter \n [7] Layanan Kami \n [8] Log-Out")
    pelanggan_choice = input("Silahkan pilih menu anda : ")

    # 3.1 RESERVASI
    if pelanggan_choice == '1':
        pass

    # 3.2 HEWAN PELIHARAAN ANDA
    elif pelanggan_choice == '2':
        pass

    # 3.3 REKAM MEDIS HEWAN
    elif pelanggan_choice == '3':
        pass

    # 3.4 KUNJUNGAN ANDA
    elif pelanggan_choice == '4':
        pass

    # 3.5 PROFIL ANDA
    elif pelanggan_choice == '5':
        pass

    # 3.6 LIHAT DOKTER
    elif pelanggan_choice == '6':
        pass

    # 3.7 LAYANAN KAMI
    elif pelanggan_choice == '7':
        pass

    # 3.8 EXIT
    elif pelanggan_choice == '8':
        pass

    # BILA SALAH INPUT
    else :
        pass

# -------------------------------------------------------------------------------------------------

# 4. FITUR ADMIN ----------------------------------------------------------------------------------
def mode_admin(uname, nama_lengkap_logged):
    os.system('cls')
    print(f"Selamat datang, {nama_lengkap_logged} !")
    print(" [1] RESERVASI \n [2] TRANSAKSI \n [3] Data Rekam Medis \n [4] Data Kustomer \n [5] Data Hewan Peliharaan \n [6] Data Dokter \n [7] Layanan \n [8] Staff/Admin \n [9] Log-out")
    admin_choice = input("Silahkan pilih menu anda : ")

    # 4.1 RESERVASI
    if admin_choice == '1':
        pass

    # 4.2 TRANSAKSI
    elif admin_choice == '2':
        pass

    # 4.3 DATA REKAM MEDIS
    elif admin_choice == '3': 
        pass

    # 4.4 DATA KUSTOMER
    elif admin_choice == '4':
        pass

    # 4.5 DATA HEWAN PELIHARAAN
    elif admin_choice == '5':
        pass

    # 4.6 DATA DOKTER v
    elif admin_choice == '6':
        def lihat_data_dokter():
            conn, cur = postgresql_connect()
            """Menampilkan data dokter dari database."""
            # Membuat cursor untuk berinteraksi dengan database
            
            # Query SQL untuk mengambil semua data dari tabel dokter
            query = """
            SELECT *
            FROM dokter
            """
            
            # Menjalankan query
            cur.execute(query)
            
            # Mengambil semua data hasil query
            data_dokter = cur.fetchall()
            
            # Menutup cursor
            postgresql_cls(conn, cur)
            
            # Headers untuk tabel yang akan ditampilkan
            headers = ["ID", 'Nama Dokter', 'Telepon', 'No. STR', 'Username', 'Password']
            
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_dokter, headers=headers, tablefmt="grid"))  

        choice_4 = input("[1] Tambah [2] Lihat [3] Edit [4] Hapus Pilih menu : ")
        if choice_4 == '1':     # Tambah data dokter v
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            # Meminta data dokter baru dari user
            conn, cur = postgresql_connect()
            nama_dokter     = input("Masukkan nama dokter: ")
            tlp_dokter      = input("Masukkan nomor telepon dokter: ")
            no_str          = input("Masukkan nomor surat tanda registrasi dokter: ")
            uname_dokter    = input("Masukkan username dokter: ")
            pw_dokter       = input("Masukkan password dokter: ")
            # Menambah dokter baru ke database
            # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
            result = False
            if not nama_dokter or not tlp_dokter or not no_str or not uname_dokter or not pw_dokter:
                print("Semua field harus diisi!")
                return False
            else:
                """Menambahkan data dokter baru ke database."""
                # Membuat cursor untuk berinteraksi dengan database
                cur = conn.cursor()
                
                # Query SQL untuk menambahkan data dokter baru
                query = """
                INSERT INTO dokter (nama_dokter, tlp_dokter, no_str, uname_dokter, pw_dokter)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                # Menjalankan query dengan data yang diberikan
                cur.execute(query, (nama_dokter, tlp_dokter, no_str, uname_dokter, pw_dokter))
                
                # Melakukan commit perubahan ke database
                conn.commit()
                
                # Mengambil jumlah baris yang dimodifikasi oleh query
                boolean = cur.rowcount
                
                # Menutup cursor
                cur.close()
                
                print("Dokter baru telah ditambahkan!")
                result = True

            if result:
                input('Tambah data berhasil')
            else:
                input('Tambah data gagal')
            mode_admin(uname, nama_lengkap_logged)
        elif choice_4 == '2':   # Lihat data dokter v
            lihat_data_dokter()
            input("\n\nTekan [enter] untuk kembali ke Menu Dokter")
            mode_admin(uname, nama_lengkap_logged)
        elif choice_4 == '3':   # Edit data dokter v
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            # Meminta ID dokter yang ingin diubah
            id_dokter = int(input("Masukkan ID dokter yang ingin diubah: "))
            # Meminta data baru dari user
            nama_baru = input("Masukkan nama baru dokter (kosongkan jika tidak ingin mengubah): ")
            telp_baru = input("Masukkan nomor telepon baru dokter (kosongkan jika tidak ingin mengubah): ")
            no_str_baru = input("Masukkan nomor STR baru dokter (kosongkan jika tidak ingin mengubah): ")
            uname_baru = input("Masukkan username baru dokter (kosongkan jika tidak ingin mengubah): ")
            password_baru = input("Masukkan password baru dokter (kosongkan jika tidak ingin mengubah): ")
            # Mengubah data dokter
            """Mengubah data dokter yang ada di database."""
            # Membuat cursor untuk berinteraksi dengan database
            conn,cur = postgresql_connect()
            
            # List untuk menyimpan bagian query yang akan diupdate
            updates = []
            
            # List untuk menyimpan nilai yang akan diisi dalam query
            values = []

            # Mengecek apakah ada nilai baru untuk nama_dokter dan menambahkannya ke query jika ada
            if nama_baru:
                updates.append("nama_dokter = %s")
                values.append(nama_baru)
            
            # Mengecek apakah ada nilai baru untuk tlp_dokter dan menambahkannya ke query jika ada
            if telp_baru:
                updates.append("tlp_dokter = %s")
                values.append(telp_baru)
            
            # Mengecek apakah ada nilai baru untuk no_str dan menambahkannya ke query jika ada
            if no_str_baru:
                updates.append("no_str = %s")
                values.append(no_str_baru)
            
            # Mengecek apakah ada nilai baru untuk uname_dokter dan menambahkannya ke query jika ada
            if uname_baru:
                updates.append("uname_dokter = %s")
                values.append(uname_baru)
            
            # Mengecek apakah ada nilai baru untuk pw_dokter dan menambahkannya ke query jika ada
            if password_baru:
                updates.append("pw_dokter = %s")
                values.append(password_baru)

            # Menambahkan id_dokter ke values, ini diperlukan untuk klausa WHERE
            values.append(id_dokter)

            # Jika ada data yang diupdate
            if updates:
                # Membuat query update dengan bagian yang perlu diupdate
                query = f"UPDATE dokter SET {', '.join(updates)} WHERE id_dokter = %s"
                try:
                    # Menjalankan query dengan nilai yang disediakan
                    cur.execute(query, values)
                    
                    # Melakukan commit perubahan ke database
                    conn.commit()
                    
                    # Menutup cursor
                    print("Data dokter telah diubah!")
                except psycopg2.Error as e:
                    # Menampilkan pesan kesalahan jika gagal melakukan update
                    print("Gagal mengubah data dokter:", e)
                    
                    # Melakukan rollback jika terjadi kesalahan
                    conn.rollback()
            else:
                # Pesan jika tidak ada data yang diubah
                print("Tidak ada data yang diubah.")
            postgresql_cls(conn, cur)
            input("\n\nTekan [enter] untuk kembali ke Menu Dokter")
            mode_admin(uname, nama_lengkap_logged)
        elif choice_4 == '4':   # Hapus data dokter v
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            lihat_data_dokter()
            # Meminta ID dokter yang ingin dihapus
            id_dokter = int(input("Masukkan ID dokter yang ingin dihapus: "))
            # Menghapus dokter dari database
            """Menghapus data dokter dari database."""
            # Membuat cursor untuk berinteraksi dengan database
            conn, cur = postgresql_connect()
            
            # Memeriksa apakah ada rekam medis yang terkait dengan dokter ini
            cur.execute("SELECT COUNT(*) FROM rekam_medis WHERE id_dokter = %s", (id_dokter,))
            count = cur.fetchone()[0]

            # Jika ada rekam medis terkait, dokter tidak dapat dihapus
            if count > 0:
                print("Tidak dapat menghapus dokter karena masih ada rekam medis yang terkait.")
                return False
            else:
                # Menghapus data dokter dari tabel dokter
                cur.execute("DELETE FROM dokter WHERE id_dokter = %s", (id_dokter,))
                
                # Melakukan commit perubahan ke database
                conn.commit()
                
                # Memeriksa apakah ada baris yang dihapus
                if cur.rowcount > 0:
                    print("Data dokter telah dihapus!")
                    cur.close()
                    result = True
                else:
                    print("Dokter dengan ID tersebut tidak ditemukan.")
                    cur.close()
                    result = False
            input("\n\nTekan [enter] untuk kembali ke Menu Dokter")
            mode_admin(uname, nama_lengkap_logged)
            
            if result == True:
                print('Data berhasil terhapus')
            else:
                print('Data gagal dihapus')

    # 4.7 LAYANAN v
    elif admin_choice == '7':
        def tambah_layanan(conn, cur, nama_layanan, harga_layanan):  # v
            """Menambahkan data layanan baru ke database."""
            cur = conn.cursor()
            # Query untuk menambahkan layanan baru ke tabel 'layanan'
            query = f"""
            INSERT INTO layanan (nama_layanan, harga_layanan)
            VALUES ('{nama_layanan}', '{harga_layanan}')
            """
            # Eksekusi query
            cur.execute(query)
            # Commit perubahan ke database
            conn.commit()
            # Mendapatkan jumlah baris yang terpengaruh oleh operasi terakhir
            boolean = cur.rowcount
            cur.close()
            return boolean

        def lihat_data_layanan(conn, cur):  # v
            """Menampilkan data layanan dari database."""
            cursor = conn.cursor()
            # Query untuk mengambil semua data dari tabel 'layanan'
            query = """
            SELECT *
            FROM layanan
            """
            cursor.execute(query)
            # Mendapatkan semua data layanan
            data_layanan = cursor.fetchall()
            cursor.close()
            
            headers = ['ID', 'Nama Layanan', 'Harga Layanan']
            # Menampilkan data layanan dalam bentuk tabel
            print(tabulate.tabulate(data_layanan, headers=headers, tablefmt="grid"))

        def ubah_data_layanan(conn, cur, layanan_baru, harga_baru, id_layanan):  # v
            """Mengubah data layanan yang ada di database."""
            updates = []

            # Jika nama layanan baru diberikan, tambahkan ke daftar update
            if layanan_baru:
                updates.append(f"nama_layanan = '{layanan_baru}'")
            # Jika harga layanan baru diberikan, tambahkan ke daftar update
            if harga_baru:
                updates.append(f"harga_layanan = '{harga_baru}'")

            if updates:
                # Query untuk mengubah data layanan berdasarkan id_layanan
                query = f"UPDATE layanan SET {', '.join(updates)} WHERE id_layanan = {id_layanan}"
                try:
                    # Eksekusi query
                    cur.execute(query)
                    # Commit perubahan ke database
                    conn.commit()
                    cur.close()
                    print("Data layanan telah diubah!")
                except psycopg2.Error as e:
                    print("Gagal mengubah data layanan:", e)
                    # Rollback perubahan jika terjadi kesalahan
                    conn.rollback()
            else:
                print("Tidak ada data yang diubah.")

        def hapus_data_layanan(conn, cur, id_layanan):  # v
            """Menghapus data layanan dari database."""
            # Check apakah ada rekam medis yang terkait dengan layanan yang akan dihapus
            cur.execute(f"SELECT COUNT(*) FROM rekam_medis WHERE id_layanan = {id_layanan}")
            count = cur.fetchone()[0]

            if count > 0:
                print("Tidak dapat menghapus layanan karena masih ada rekam medis yang terkait.")
                return False
            else:
                # Query untuk menghapus data layanan berdasarkan id_layanan
                cur.execute("DELETE FROM layanan WHERE id_layanan = %s", (id_layanan,))
                conn.commit()
                if cur.rowcount > 0:
                    print("Data layanan telah dihapus!")
                    cur.close()
                    return True
                else:
                    print("Layanan dengan ID tersebut tidak ditemukan.")
                    cur.close()
                    return False

        conn, cur = postgresql_connect()
        print("\nMenu layanan:")
        print("[1] Tambah layanan")
        print("[2] Lihat Data layanan")
        print("[3] Ubah Data layanan")
        print("[4] Hapus Data layanan")
        print("[5] Exit")

        pilihan = input("Masukkan pilihan Anda: ")

        if pilihan == "1":
            os.system('cls')
            nama_layanan = input("Masukkan nama layanan: ")
            harga_layanan = input("Masukkan harga layanan: ")
            result = tambah_layanan(conn, cur, nama_layanan, harga_layanan)
            if result:
                print('Tambah data berhasil')
            else:
                print('Tambah data gagal')
        elif pilihan == "2":
            lihat_data_layanan(conn, cur)
        elif pilihan == "3":
            os.system('cls')
            lihat_data_layanan(conn, cur)
            id_layanan = int(input("Masukkan ID layanan yang ingin diubah: "))
            layanan_baru = input("Masukkan nama layanan baru (kosongkan jika tidak ingin mengubah): ")
            harga_baru = input("Masukkan harga layanan baru (kosongkan jika tidak ingin mengubah): ")
            result = ubah_data_layanan(conn, cur, layanan_baru, harga_baru, id_layanan)
        elif pilihan == "4":
            os.system('cls')
            lihat_data_layanan(conn, cur)
            id_layanan = int(input("Masukkan ID layanan yang ingin dihapus: "))
            hapus_data_layanan(conn, cur, id_layanan)
        elif pilihan == "5":
            os.system('cls')
        else:
            print("Pilihan tidak valid, silakan coba lagi.")
        input("\n\nTekan [enter] untuk kembali ke Main Menu")
        mode_admin(uname, nama_lengkap_logged)

    # 4.8 STAFF/ADMIN
    elif admin_choice == '8':
        pass
    # 4.9 EXIT
    elif admin_choice == '9':
        launch_page()

    mode_admin(uname, nama_lengkap_logged)
# -------------------------------------------------------------------------------------------------

# FITUR MANUAL BOOK -------------------------------------------------------------------------------
def manual_book():
    input("""
    bruh
    """ "\n")

# -------------------------------------------------------------------------------------------------

# FITUR ADMIN PERTAMA -----------------------------------------------------------------------------
def admin_pertama():
    indikator_admin = []    # wadah seluruh data admin
    # mengakses postgresql_connect
    conn,cur = postgresql_connect()

    # menambahkan data staf dari postgresql_connect ke variabel python
    cur.execute("SELECT * FROM staf")
    for i in cur:
        indikator_admin.append(i)   # menambahkan tiap baris
    # jika data indikator kosong (tidak ada data admin yang terdaftar)
    if not indikator_admin:
        os.system('cls')
        print(f"{mini_header}\nProgram belum memiliki admin, Silahkan masukkan admin pertama\n")
        # memasukkan data admin berdasarkan entitiy staf
        nama_staf  = input("Nama                         : ")
        tlp_staf   = input("No. Telepon                  : ")
        uname_staf = input("Username Admin (untuk login) : ")
        pw_staf    = input("Password (untuk login)       : ")
        # mencoba memasukkan data ke postgresql_connect
        try:
            cur.execute(f"""
                        INSERT INTO staf (nama_staf, tlp_staf, uname_staf, pw_staf)
                        VALUES (\'{nama_staf}\', \'{tlp_staf}\', \'{uname_staf}\', \'{pw_staf}\')
                        """)

            input("\nAkun berhasil ditambahkan, tekan [ENTER] untuk melanjutkan ")
        except:
            print()
            reregister = input("Kesalahan input, tekan [ENTER] untuk coba lagi atau [Q] untuk keluar : ")
            # apakah mau mencoba lagi atau keluar dari aplikasi
            if reregister == '':
                admin_pertama()
            else:
                sys.exit()
        finally:
            postgresql_cls(conn, cur)

# -------------------------------------------------------------------------------------------------

# FITUR MEMBUAT DATABASE --------------------------------------------------------------------------
def db_pertama():
    welcome_interface()

# -------------------------------------------------------------------------------------------------

# HEADER LOGO -------------------------------------------------------------------------------------
minihead_a = (r"  ___       _   ___      _      ___               ")
minihead_b = (r" / __| __ _| |_/ __| ___| |_   / __|__ _ _ _ ___  ")
minihead_c = (r" \__ \/ _` |  _\__ \/ -_)  _| | (__/ _` | '_/ -_) ")
minigead_d = (r" |___/\__,_|\__|___/\___|\__|  \___\__,_|_| \___| ")
                                                 
head_a = (r"        _____       _    _____      _      _____                     ")
head_b = (r"       / ____|     | |  / ____|    | |    / ____|                    ")
head_c = (r"      | (___   __ _| |_| (___   ___| |_  | |     __ _ _ __ ___       ")
head_d = (r"       \___ \ / _` | __|\___ \ / _ \ __| | |    / _` | '__/ _ \      ")
head_e = (r"       ____) | (_| | |_ ____) |  __/ |_  | |___| (_| | | |  __/      ")
head_f = (r"      |_____/ \__,_|\__|_____/ \___|\__|  \_____\__,_|_|  \___|      ")
head_g = (r"                                                                     ")

titl_a = (r"          SATWA SEHAT CARE : APLIKASI LAYANAN KLINIK HEWAN           ") 

header = head_a+'\n'+head_b+'\n'+head_c+'\n'+head_d+'\n'+head_e+'\n'+head_f+'\n'+head_g+'\n'
header_fancy =  '+'+'='*69+'+'+'\n'+ \
                '|'+head_a+'|'+'\n'+ \
                '|'+head_b+'|'+'\n'+ \
                '|'+head_c+'|'+'\n'+ \
                '|'+head_d+'|'+'\n'+ \
                '|'+head_e+'|'+'\n'+ \
                '|'+head_f+'|'+'\n'+ \
                '|'+head_g+'|'+'\n'+ \
                '|'+' '*69+'|'+'\n'+ \
                '|'+titl_a+'|'+'\n'+ \
                '+'+'='*69+'+'+'\n'
mini_header = minihead_a+'\n'+minihead_b+'\n'+minihead_c+'\n'+minigead_d+'\n'

# ┏┓   ┏┓     ┏┓      
# ┗┓┏┓╋┗┓┏┓╋  ┃ ┏┓┏┓┏┓
# ┗┛┗┻┗┗┛┗ ┗  ┗┛┗┻┛ ┗ 
                    
#  __       __          __         
# (_  _ _|_(_  _ _|_   /   _  __ _ 
# __)(_| |___)(/_ |_   \__(_| | (/_

#  __    __   _____  __   ____ _____      __     __    ___   ____ 
# ( (`  / /\   | |  ( (` | |_   | |      / /`   / /\  | |_) | |_  
# _)_) /_/--\  |_|  _)_) |_|__  |_|      \_\_, /_/--\ |_| \ |_|__ 

# ____ ____ ___ ____ ____ ___    ____ ____ ____ ____ 
# [__  |__|  |  [__  |___  |     |    |__| |__/ |___ 
# ___] |  |  |  ___] |___  |     |___ |  | |  \ |___ 
                                                   

# (`  |-(` _ |-  /`     _ 
# _)(||__)(/_|_  \,(||`(/_

# -------------------------------------------------------------------------------------------------                        

# VARIABEL-VARIABEL PENTNG ------------------------------------------------------------------------
delay_welcome = 1 # ANIMASI PADA WELCOMING PAGE






# EKSEKUSI PROGRAM --------------------------------------------------------------------------------

welcome_interface()

admin_pertama()

launch_page()
