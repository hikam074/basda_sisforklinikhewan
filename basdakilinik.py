import psycopg2
import os
import sys
import time
import tabulate
import pandas as pd

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

def postgresql_alldata_akun(conn, cur):      # memasukkan semua data akun ke satu variabel
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
        print(tabulate.tabulate(data_layanan, headers=headers, tablefmt=f"{format_table}"))

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
            print(tabulate.tabulate(nilai,headers=header, tablefmt=f"{format_table}"))

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
            print(tabulate.tabulate(nilai,headers=header, tablefmt=f"{format_table}"))

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
    # ambil data id_pelanggan
    conn, cur = postgresql_connect()
    cur.execute(f"SELECT id_pelanggan FROM pelanggan WHERE uname_pelanggan = '{uname}'")
    id_pelanggan = cur.fetchone()
    id_pelanggan = str(id_pelanggan).strip(")(,")
    postgresql_cls(conn, cur)

    os.system('cls')
    print(f"Selamat datang, {nama_lengkap_logged} !")
    print(" [1] RESERVASI ANDA\n [2] Hewan Peliharaan anda \n [3] Rekam Medis Hewan Anda \n [4] Riwayat Kunjungan Anda \n [5] Profil Anda \n [6] Lihat Dokter \n [7] Layanan Kami \n [8] Log-Out")
    pelanggan_choice = input("Silahkan pilih menu anda : ")

    # 3.1 RESERVASI mid
    if pelanggan_choice == '1':
        conn, cur = postgresql_connect()
        listdata = postgresql_alldata_akun(conn, cur)

        print("1. Edit Reservasi")
        print("2. Lihat Daftar Rencana dan Rincian Reservasi")
        inputmenu = input("Masukan menu yang diinginkan")

        if inputmenu == '1':    # edit reservasi
            cur.execute('SELECT * FROM reservasi')
            datareservasi = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datareservasi, headers=headers, tablefmt=f"{format_table}"))
            editnomor = int(input("Pilih id yang ingin di edit"))
            
        elif inputmenu == '2':  #lihat riwayat reservasi
            cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.nama_hewan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) WHERE p.uname_pelanggan = '{uname}'")
            datareservasi = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datareservasi, headers=headers, tablefmt=f"{format_table}"))
            lihatnomor = int(input("Masukan id reservasi yang ingin dilihat rinci"))
            cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) where id_reservasi = '{lihatnomor}'")
            lihatdata = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(lihatdata, headers=headers, tablefmt=f"{format_table}"))

            postgresql_cls(conn, cur)
            input("Tekan [Enter] untuk kembali")


    # 3.2 HEWAN PELIHARAAN ANDA
    elif pelanggan_choice == '2':
        conn, cur = postgresql_connect()
        print(" 1. Tambah Data Hewan Peliharaan")
        print(" 2. Lihat Data Hewan Peliharaan Anda")
        print(" 3. Ubah Data Hewan Anda")
        print(" 4. Hapus Data Hewan Anda")
        inputmenu = input("Masukan opsi selanjutnya : ")
        if inputmenu == '1':    # tambah hewan v
            cur.execute('SELECT * FROM jenis_hewan')
            datahewan = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datahewan, headers=headers, tablefmt=f"{format_table}"))

            jenishewan = input("Masukan ID Jenis Hewan Anda : ")
            nama_hewan = input("Masukan Nama Hewan Anda : ")
            tanggallahir = input("Masukan Tanggal Lahir Hewan Anda (yyyy-mm-dd) : ")
            try:
                cur.execute(f"INSERT INTO hewan (nama_hewan, tanggal_lahir, id_pelanggan, id_jenishewan) VALUES ('{nama_hewan}', '{tanggallahir}', {id_pelanggan}, {jenishewan})")
                postgresql_commit_nclose(conn, cur)
                print("Data berhasil ditambahkan!")
            except psycopg2.Error as e:
                print(e)
                postgresql_cls(conn, cur)
                print("Terdapat kesalahan pada data hewan, silahkan coba lagi")
        
        elif inputmenu == '2':  # lihat list hewan anda v
            cur.execute(f"Select h.id_hewan, h.nama_hewan, jh.nama_jenis, h.tanggal_lahir, p.nama_pelanggan from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan}")
            lihatdata = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(lihatdata, headers=headers, tablefmt=f"{format_table}"))
            postgresql_cls(conn, cur)

        elif inputmenu == '3':  # edit data hewan mid
            cur.execute(f'select h.id_hewan, h.nama_hewan, h.tanggal_lahir, jh.nama_jenis from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan}')
            datahewan = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datahewan, headers=headers, tablefmt=f"{format_table}"))

            dataygdiubah = int(input("masukan no id_hewan yang ingin dirubah "))
            cur.execute(f'select h.id_hewan, h.nama_hewan, h.tanggal_lahir, jh.nama_jenis from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan} and h.id_hewan = {dataygdiubah}')
            datahewan = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datahewan, headers=headers, tablefmt=f"{format_table}"))

            nama_hewan = input('masukan nama hewan baru')
            tanggallahir = input('masukan tanggal lahir baru')
            namajenis = input('masukan namajenis')

        elif inputmenu == '4':  # hapus data hewan
            pass
        
        input("Tekan [Enter] untuk kembali ke menu : ")
        mode_pelanggan(uname, nama_lengkap_logged)

    # 3.3 REKAM MEDIS HEWAN v
    elif pelanggan_choice == '3':
        def menu_pelanggan_4(uname, nama_lengkap_logged):
            os.system('cls')
            conn, cur = postgresql_connect()
            print(" 1. Cari Berdasarkan Tanggal")
            print(" 2. Cari Berdasarkan Jenis Hewan")
            print(" 3. Cari Berdasarkan id Hewan")
            print(" 4. Cari Berdasarkan id Dokter")
            print(" 5. Kembali ke MENU UTAMA")
            inputmenu = input('Silahkan Masukan Menu Rekam Medis! : ')

            if inputmenu == '1':
                #MENAMPILKAN RINCIAN TANGGAL
                tanggal = input('Masukan Tanggal Reservasi yang Ingin Dicari! : ')
                cur.execute(f"select r.id_rekamed, r.tgl_waktu_pemeriksaan, h.nama_hewan, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) where p.id_pelanggan = {id_pelanggan} AND TO_CHAR(tgl_waktu_pemeriksaan :: DATE, 'yyyy-mm-dd') = TO_CHAR(tgl_waktu_pemeriksaan :: DATE, '{tanggal}')")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                os.system('cls')
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")  

            elif inputmenu == '2':
                #MENAMPILKAN RINCIAN JENIS HEWAN
                os.system('cls')
                cur.execute("SELECT * FROM jenis_hewan")
                datajenishewan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datajenishewan, headers=headers, tablefmt=f"{format_table}"))
                jenishewan = input('Masukan ID Jenis Hewan yang Ingin Dicari! : ')
                cur.execute(f'select r.id_rekamed, jh.nama_jenis, h.nama_hewan, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.tgl_waktu_pemeriksaan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where jh.id_jenishewan = {jenishewan} AND h.id_pelanggan = {id_pelanggan}')
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                os.system('cls')
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")  

            elif inputmenu == '3':
                #MENAMPILKAN RINCIAN AWAL
                cur.execute(f"SELECT h.id_hewan, h.nama_hewan, h.tanggal_lahir, j.nama_jenis FROM hewan h JOIN jenis_hewan j ON (h.id_jenishewan = j.id_jenishewan) WHERE id_pelanggan = {id_pelanggan}")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))

                #MENAMPILKAN RINCIAN IDHEWAN
                idhewan = input('Masukan Id Hewan pada Rekam Medis yang Ingin Dicari! : ')
                cur.execute(f'select r.id_rekamed,h.id_hewan, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.tgl_waktu_pemeriksaan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where h.id_hewan = {idhewan}')
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")  

            elif inputmenu == '4':
                #MENAMPILKAN RINCIAN AWAL  
                cur.execute(f"SELECT d.id_dokter, d.nama_dokter FROM dokter d JOIN rekam_medis r ON (r.id_dokter = d.id_dokter) WHERE r.id_dokter = d.id_dokter")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                os.system('cls')
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))

                #MENAMPILKAN RINCIAN IDDOKTER
                iddokter = input('Masukan Id Dokter pada Rekam Medis yang Ingin Dicari! : ')
                cur.execute(f'select r.id_rekamed, d.id_dokter, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.tgl_waktu_pemeriksaan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where d.id_dokter = {iddokter} and p.id_pelanggan = {id_pelanggan}')
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                os.system('cls')
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")  

            elif inputmenu == '5':
                mode_pelanggan(uname, nama_lengkap_logged)
            
            menu_pelanggan_4(uname, nama_lengkap_logged)

        menu_pelanggan_4(uname, nama_lengkap_logged)

    # 3.4 KUNJUNGAN ANDA v
    elif pelanggan_choice == '4':
        def kunjungan_anda(uname, nama_lengkap_logged):
            os.system('cls')
            conn, cur = postgresql_connect()
            print(" 1. Cari Berdasarkan Tanggal")
            print(" 2. Cari Berdasarkan Jenis Hewan")
            print(" 3. Cari Berdasarkan id Hewan")
            print(" 4. Cari Berdasarkan id Dokter")
            print(" 5. EXIT")
            inputmenu = input('Silahkan Masukan Menu Kunjungan! : ')
            if inputmenu == '1':
                
                #MENAMPILKAN RINCIAN AWAL 
                print('Ini adalah riwayat kunjungan anda sebelumnya.')
                cur.execute(f'select r.id_reservasi, h.nama_hewan, jh.nama_jenis, d.nama_dokter, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan from rekam_medis re join hewan h on (h.id_hewan = re.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = re.id_dokter) join layanan l on (l.id_layanan = re.id_layanan) join reservasi r on (r.id_hewan = re.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) WHERE h.id_pelanggan = {id_pelanggan}')
                datakunjungan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datakunjungan, headers=headers, tablefmt=f"{format_table}"))

                #MENAMPILKAN RINCIAN TANGGAL
                tanggal = input('Masukan Tanggal Kunjungan yang Ingin Dicari! : ')
                cur.execute(f"select r.id_reservasi, h.nama_hewan, jh.nama_jenis, d.nama_dokter, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan from rekam_medis re join hewan h on (h.id_hewan = re.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = re.id_dokter) join layanan l on (l.id_layanan = re.id_layanan) join reservasi r on (r.id_hewan = re.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) WHERE h.id_pelanggan = {id_pelanggan} AND TO_CHAR(r.reservasi_tgl_layanan :: DATE, 'yyyy-mm-dd') = TO_CHAR(r.reservasi_tgl_layanan :: DATE, '{tanggal}')")
                datakunjungan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datakunjungan, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("tekan [Enter] untuk KEMBALI KE MENU : ")

            if inputmenu == '2':
                #MENAMPILKAN RINCIAN AWAL  
                os.system('cls')
                cur.execute("SELECT * FROM jenis_hewan")
                datajenishewan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datajenishewan, headers=headers, tablefmt=f"{format_table}"))

                #MENAMPILKAN RINCIAN JENIS HEWAN
                jenishewan = input('Masukan ID jenis hewan yang Ingin Dicari! : ')
                cur.execute(f'select r.id_reservasi, h.nama_hewan, jh.nama_jenis, d.nama_dokter, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan from rekam_medis re join hewan h on (h.id_hewan = re.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = re.id_dokter) join layanan l on (l.id_layanan = re.id_layanan) join reservasi r on (r.id_hewan = re.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where h.id_pelanggan = {id_pelanggan} AND h.id_jenishewan = {jenishewan}')
                datakunjungan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datakunjungan, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("tekan [Enter] untuk KEMBALI KE MENU : ")

            if inputmenu == '3':
                cur.execute(f"SELECT h.id_hewan, h.nama_hewan, h.tanggal_lahir, j.nama_jenis FROM hewan h JOIN jenis_hewan j ON (h.id_jenishewan = j.id_jenishewan) WHERE id_pelanggan = {id_pelanggan}")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))


                #MENAMPILKAN RINCIAN ID HEWAN
                idhewan = int(input('Masukan ID Hewan yang Ingin Dicari! : '))
                cur.execute(f'select r.id_reservasi, h.id_hewan, h.nama_hewan, jh.nama_jenis, d.nama_dokter, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan from rekam_medis re join hewan h on (h.id_hewan = re.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = re.id_dokter) join layanan l on (l.id_layanan = re.id_layanan) join reservasi r on (r.id_hewan = re.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where h.id_pelanggan = {id_pelanggan} AND h.id_hewan = {idhewan}')
                datakunjungan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datakunjungan, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("tekan [Enter] untuk KEMBALI KE MENU : ")
                
            if inputmenu == '4':
                cur.execute(f"SELECT d.id_dokter, d.nama_dokter FROM dokter d JOIN rekam_medis r ON (r.id_dokter = d.id_dokter) WHERE r.id_dokter = d.id_dokter")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                os.system('cls')
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                
                #MENAMPILKAN RINCIAN IDDOKTER
                iddokter = int(input('Masukan Tanggal Reservasi yang Ingin Dicari!'))
                cur.execute(f'select r.id_reservasi, d.id_dokter, h.nama_hewan, jh.nama_jenis, d.nama_dokter, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan from rekam_medis re join hewan h on (h.id_hewan = re.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = re.id_dokter) join layanan l on (l.id_layanan = re.id_layanan) join reservasi r on (r.id_hewan = re.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where h.id_pelanggan = {id_pelanggan} AND d.id_dokter = {iddokter}')
                datakunjungan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datakunjungan, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("tekan [Enter] untuk KEMBALI KE MENU : ")
            elif inputmenu =='5':
                mode_pelanggan(uname, nama_lengkap_logged)

            kunjungan_anda(uname, nama_lengkap_logged)
        kunjungan_anda(uname, nama_lengkap_logged)

    # 3.5 PROFIL ANDA v
    elif pelanggan_choice == '5':
        os.system('cls')
        conn, cur = postgresql_connect()
        
        #MENAMPILKAN PROFIL CUSTOMER
        cur.execute(f"select nama_pelanggan, tlp_pelanggan from pelanggan where id_pelanggan = {id_pelanggan}")
        profil = cur.fetchall()
        namapelanggan = profil[0][0]
        tlppelanggan = profil[0][1]
        print(f'Halo kak {namapelanggan}')
        print(f'Ini Nomor Telfon Kamu {tlppelanggan}')

        #MENAMPILKAN HEWAN CUSTOMER
        cur.execute(f'select h.nama_hewan, jh.nama_jenis, h.tanggal_lahir from hewan h join pelanggan p on (p.id_pelanggan = h.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where h.id_pelanggan = {id_pelanggan}')
        profilhewananda = cur.fetchall()
        print("Dibawah ini List Hewan Peliharaan Kamu")
        headers = [i[0] for i in cur.description]
        print(tabulate.tabulate(profilhewananda, headers=headers, tablefmt=f"{format_table}"))
        postgresql_cls(conn, cur)
        input("Tekan [Enter] untuk kembali ke MENU UTAMA : ")
        mode_pelanggan(uname, nama_lengkap_logged)

    # 3.6 LIHAT DOKTER v
    elif pelanggan_choice == '6':
        os.system('cls')
        conn, cur = postgresql_connect()
        print("Dibawah ini adalah data dokter di Klinik Sat Set Care")
        cur.execute('select id_dokter, nama_dokter, tlp_dokter, no_str from dokter')
        datadokter = cur.fetchall()
        headers = [i[0] for i in cur.description]
        print(tabulate.tabulate(datadokter, headers=headers, tablefmt=f"{format_table}"))
        postgresql_cls(conn, cur)
        input("Tekan [Enter] untuk kembali ke MENU UTAMA")
        mode_pelanggan(uname, nama_lengkap_logged)

    # 3.7 LAYANAN KAMI v
    elif pelanggan_choice == '7':
        os.system('cls')
        conn, cur = postgresql_connect()
        print('Dibawah ini adalah layanan di Klinik Sat Set Care!')
        cur.execute('select id_layanan, nama_layanan, harga_layanan from layanan')
        datalayanan = cur.fetchall()
        headers = [i[0] for i in cur.description]
        print(tabulate.tabulate(datalayanan, headers=headers, tablefmt=f"{format_table}"))
        postgresql_cls(conn, cur)
        input("Tekan [Enter] untuk kembali ke MENU UTAMA")
        mode_pelanggan(uname, nama_lengkap_logged)

    # 3.8 EXIT v
    elif pelanggan_choice == '8':
        launch_page()

    # BILA SALAH INPUT v
    else :
        mode_pelanggan(uname, nama_lengkap_logged)

    

# -------------------------------------------------------------------------------------------------

# 4. FITUR ADMIN ----------------------------------------------------------------------------------
def mode_admin(uname, nama_lengkap_logged):
    os.system('cls')
    print(f"Selamat datang, {nama_lengkap_logged} !")
    print(" [1] RESERVASI \n [2] TRANSAKSI \n [3] Data Rekam Medis \n [4] Data Kustomer \n [5] Data Hewan Peliharaan \n [6] Data Dokter \n [7] Layanan \n [8] Staff/Admin \n [9] Log-out")
    admin_choice = input("Silahkan pilih menu anda : ")

    # 4.1 RESERVASI v
    if admin_choice == '1':
        # Fungsi untuk membuat daftar hewan yang tersedia dalam database
        def list_animals(conn):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk mendapatkan ID dan nama hewan
            cur.execute("SELECT id_hewan, nama_hewan FROM hewan")
            # Mengambil semua baris hasil kueri
            animals = cur.fetchall()
            # Menutup kursor setelah selesai digunakan
            cur.close()
            # Mengembalikan daftar hewan
            return animals

        # Fungsi untuk memeriksa apakah data pelanggan sudah ada dalam database
        def check_customer_exists(conn, id_pelanggan):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk memeriksa keberadaan data pelanggan
            cur.execute("SELECT EXISTS(SELECT 1 FROM customers WHERE id_pelanggan=%s)", (id_pelanggan,))
            # Mengambil hasil kueri dan mengekstrak nilai eksistensinya
            exists = cur.fetchone()[0]
            # Menutup kursor setelah selesai digunakan
            cur.close()
            # Mengembalikan hasil eksistensi
            return exists

        # Fungsi untuk mengambil ID staf berdasarkan username dari database
        def get_staff_id_by_username(conn, uname):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk mendapatkan ID staf berdasarkan username
            cur.execute("SELECT id_staf FROM staf WHERE uname_staf = %s", (uname,))
            # Mengambil hasil kueri dan mengekstrak ID staf jika ada
            id_staf = cur.fetchone()
            # Menutup kursor setelah selesai digunakan
            cur.close()
            # Mengembalikan ID staf atau None jika tidak ditemukan
            return id_staf[0] if id_staf else None

        # Fungsi untuk melakukan reservasi
        def make_reservation(conn, reservation_data):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk menyimpan data reservasi ke database
            cur.execute("""
                INSERT INTO reservasi (id_hewan, id_staf, reservasi_tgl_layanan, reservasi_waktu_layanan)
                VALUES (%s, %s, %s, %s)
            """, (
                reservation_data['id_hewan'],
                reservation_data['id_staf'],
                reservation_data['reservasi_tgl_layanan'],
                reservation_data['reservasi_waktu_layanan']
            ))
            # Melakukan commit untuk menyimpan perubahan ke database
            conn.commit()

            # Mengambil id_reservasi dengan kueri terpisah
            cur.execute("SELECT id_reservasi FROM reservasi WHERE id_hewan = %s AND id_staf = %s AND reservasi_tgl_layanan = %s AND reservasi_waktu_layanan = %s",
                        (
                            reservation_data['id_hewan'],
                            reservation_data['id_staf'],
                            reservation_data['reservasi_tgl_layanan'],
                            reservation_data['reservasi_waktu_layanan']
                        ))
            # Mengambil id_reservasi jika tersedia atau None jika tidak
            id_reservasi = cur.fetchone()[0] if cur.rowcount else None

            # Menutup kursor setelah selesai digunakan
            cur.close()
            # Mengembalikan id_reservasi hasil reservasi
            return id_reservasi

        # Fungsi untuk mengedit reservasi
        def edit_reservation(conn, id_reservasi, reservation_data):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            updates = []
            values = []

            # Mengecek setiap item dalam data reservasi untuk menentukan perubahan yang diperlukan
            if 'id_hewan' in reservation_data:
                updates.append("id_hewan = %s")
                values.append(reservation_data['id_hewan'])
            if 'id_staf' in reservation_data:
                updates.append("id_staf = %s")
                values.append(reservation_data['id_staf'])
            if 'reservasi_tgl_layanan' in reservation_data:
                updates.append("reservasi_tgl_layanan = %s")
                values.append(reservation_data['reservasi_tgl_layanan'])
            if 'reservasi_waktu_layanan' in reservation_data:
                updates.append("reservasi_waktu_layanan = %s")
                values.append(reservation_data['reservasi_waktu_layanan'])

            # Menambahkan id_reservasi ke dalam values untuk kueri UPDATE
            values.append(id_reservasi)
            
            # Membuat kueri UPDATE berdasarkan perubahan yang diperlukan
            update_query = f"UPDATE reservasi SET {', '.join(updates)} WHERE id_reservasi = %s"
            # Menjalankan kueri UPDATE untuk memperbarui data reservasi
            cur.execute(update_query, tuple(values))
            # Melakukan commit untuk menyimpan perubahan ke database
            conn.commit()
            # Menutup kursor setelah selesai digunakan
            cur.close()

        # Fungsi untuk menghapus reservasi
        def delete_reservation(conn, id_reservasi):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk menghapus data reservasi dari database
            cur.execute("DELETE FROM reservasi WHERE id_reservasi = %s", (id_reservasi,))
            # Melakukan commit untuk menyimpan perubahan ke database
            conn.commit()
            # Menutup kursor setelah selesai digunakan
            cur.close()

        # Fungsi untuk melihat rincian reservasi
        def view_reservation(conn):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk mendapatkan rincian reservasi dari database
            cur.execute("select r.id_reservasi, h.nama_hewan, s.nama_staf, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan from reservasi r join hewan h ON (h.id_hewan = r.id_hewan) join staf s ON (s.id_staf = r.id_staf)")
            # Mengambil semua baris hasil kueri
            reservasi = cur.fetchall()
            # Menutup kursor setelah selesai digunakan
            cur.close()
            
            # Menampilkan rincian reservasi dalam format tabel
            headers = ['ID', 'Nama Hewan', 'Nama Staf', 'Tanggal Layanan', 'Waktu Layanan']
            print(tabulate.tabulate(reservasi, headers=headers, tablefmt=f"{format_table}"))
            # Mengembalikan daftar reservasi
            return reservasi

        # Fungsi utama untuk manajemen reservasi
        def main_reservasi():
            # Membuat koneksi ke database PostgreSQL
            conn, cur = postgresql_connect()
            if conn:
                while True:
                    # Membersihkan layar konsol
                    os.system('cls')
                    print("\nReservation Menu:")
                    print("1. tambah Reservasi")
                    print("2. lihat Reservasi")
                    print("3. edit Reservasi")
                    print("4. hapus Reservasi")
                    print("5. Exit")
                    choice = input("Masukkan Pilihan: ")

                    if choice == '1':
                        os.system('cls')
                        # Menampilkan daftar hewan yang tersedia
                        print("Hewan yang Tersedia:")
                        animals = list_animals(conn)
                        for animal in animals:
                            print(f"ID: {animal[0]}, Name: {animal[1]}")
                        
                        # Meminta input untuk reservasi
                        id_hewan = input("Masukkan ID Hewan: ")
                        id_staf = get_staff_id_by_username(conn, uname)
                        
                        if id_staf is None:
                            print("Staf tidak ditemukan.")
                            continue
                        
                        reservasi_tgl_layanan = input("Masukkan Tanggal Reservasi (YYYY-MM-DD): ")
                        reservasi_waktu_layanan = input("Masukkan Waktu Reservasi (HH:MM:SS): ")
                        
                        # Menyusun data reservasi
                        reservation_data = {
                            'id_hewan': id_hewan,
                            'id_staf': id_staf,
                            'reservasi_tgl_layanan': reservasi_tgl_layanan,
                            'reservasi_waktu_layanan': reservasi_waktu_layanan
                        }
                        
                        # Membuat reservasi
                        id_reservasi = make_reservation(conn, reservation_data)
                        
                        # Menampilkan pesan keberhasilan atau kegagalan reservasi
                        if id_reservasi:
                            print(f"Reservasi berhasil.")
                        else:
                            print("Reservasi Gagal. Coba lagi.")

                        input("\n\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '2':
                        os.system('cls')
                        # Melihat rincian reservasi
                        view_reservation(conn)
                        input("\n\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '3':
                        os.system('cls')
                        # Melihat rincian reservasi sebelum mengedit
                        view_reservation(conn)
                        id_reservasi = input("Masukkan ID Reservasi yang ingin diubah: ")
                        print("Masukkan data baru (biarkan kosong jika tidak ingin diubah):")
                        id_hewan = input("Masukkan ID Hewan baru: ")
                        id_staf = input("Masukkan ID staf baru: ")
                        reservasi_tgl_layanan = input("Masukkan Tanggal Reservasi Baru (YYYY-MM-DD): ")
                        reservasi_waktu_layanan = input("Masukkan Waktu Reservasi Baru  (HH:MM:SS): ")
                        
                        # Menyusun data reservasi yang akan diubah
                        reservation_data = {}
                        if id_hewan:
                            reservation_data['id_hewan'] = id_hewan
                        if id_staf:
                            reservation_data['id_staf'] = id_staf
                        if reservasi_tgl_layanan:
                            reservation_data['reservasi_tgl_layanan'] = reservasi_tgl_layanan
                        if reservasi_waktu_layanan:
                            reservation_data['reservasi_waktu_layanan'] = reservasi_waktu_layanan
                        
                        # Mengedit reservasi
                        edit_reservation(conn, id_reservasi, reservation_data)
                        print("Reservasi Berhasil Diperbahui.")
                        input("\n\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '4':
                        os.system('cls')
                        # Melihat rincian reservasi sebelum menghapus
                        view_reservation(conn)
                        id_reservasi = input("Masukkan ID Reservasi yang ingin dihapus: ")
                        # Menghapus reservasi
                        delete_reservation(conn, id_reservasi)
                        print("Reservasi berhasil dihapus.")
                        input("\n\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '5':
                        os.system('cls')
                        mode_admin(uname, nama_lengkap_logged)

                    else:
                        print("Pilihan tidak valid, silakan coba lagi..")

                # Menutup koneksi ke database setelah selesai digunakan
                conn.close()
            else:
                print("Gagal Menghubungkan ke database")

        main_reservasi()

    # 4.2 TRANSAKSI
    elif admin_choice == '2':
        pass

    # 4.3 DATA REKAM MEDIS v
    elif admin_choice == '3': 
        def lihat_data_rekammedis():
            conn, cur = postgresql_connect()
            """Menampilkan data rekam medis dari database."""
            # Membuat cursor untuk berinteraksi dengan database
           
            query = """
            SELECT
                rm.id_rekamed, hew.nama_hewan, pel.nama_pelanggan, dok.nama_dokter, lay.nama_layanan, rm.tgl_waktu_pemeriksaan, rm.hasil_medis, rm.catatan_tambahan
            FROM rekam_medis rm
            JOIN hewan hew on hew.id_hewan = rm.id_hewan
            JOIN pelanggan pel on pel.id_pelanggan = hew.id_pelanggan
            JOIN dokter dok on dok.id_dokter = rm.id_dokter
            JOIN layanan lay on lay.id_layanan = rm.id_layanan
            """
           
            cur.execute(query)
            # Mengambil semua data hasil query
            data_rekammedis = cur.fetchall()

            postgresql_cls(conn, cur)
           
            # Headers untuk tabel yang akan ditampilkan
            headers = [i[0] for i in cur.description]
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_rekammedis, headers=headers, tablefmt=f"{format_table}"))  

        choice_3 = input("\n[1] Tambah Data Rekam Medis\n[2] Lihat Data Rekam Medis\n[3] Edit Data Rekam Medis\n[4] Hapus Data Rekam Medis\nPilih menu : ")
        if choice_3 == '1':     # tambah data rekam medis v
            os.system('cls')  
            #Input Data rekam medis
            conn, cur = postgresql_connect()
            id_hewan                = input("1. Masukkan id hewan: ")
            id_dokter               = input("2. Masukkan id_dokter: ")
            id_layanan              = input("3. Masukkan id_layanan: ")
            tgl_waktu_pemeriksaan   = input("4. Masukkan tgl_waktu_pemeriksaan: ")
            hasil_medis             = input("5. Masukkan hasil_medis: ")
            catatan_tambahan        = input("6. Masukkan catatan_tambahan : ")

            # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
            result = False
            if not id_hewan or not id_dokter or not id_layanan or not tgl_waktu_pemeriksaan or not hasil_medis:
                print("Semua field harus diisi!")
                return False
            else:
                """Menambahkan data rekam medis baru ke database."""
                cur = conn.cursor()
               
                query = """
                INSERT INTO rekam_medis (id_hewan, id_dokter, id_layanan, tgl_waktu_pemeriksaan, hasil_medis, catatan_tambahan)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
               
                # Menjalankan query dengan data yang diberikan
                cur.execute(query, (id_hewan, id_dokter, id_layanan, tgl_waktu_pemeriksaan, hasil_medis, catatan_tambahan))
               
                # Melakukan commit perubahan ke database
                conn.commit()
               
                # Mengambil jumlah baris yang dimodifikasi oleh query
                boolean = cur.rowcount
               
                # Menutup cursor
                cur.close()
               
                print("Rekam medis baru telah ditambahkan!")
                result = True

            if result:
                input('Tambah data berhasil')
            else:
                input('Tambah data gagal')
            mode_admin(uname, nama_lengkap_logged)

        elif choice_3 == '2':   # Lihat data rekam medis v
            lihat_data_rekammedis()
            input("\n\nTekan [enter] untuk kembali ke Menu rekam medis")
            mode_admin(uname, nama_lengkap_logged)

        elif choice_3 == '3':   # Edit data rekam medis v
            os.system('cls')
            # Meminta ID rekam medis yang ingin diubah
            lihat_data_rekammedis()
            id_rekamed = int(input("Masukkan ID rekam medis yang ingin diubah: "))
           
            conn, cur = postgresql_connect()
           
            try:
                # Mengecek apakah ID rekammedis ada dalam database
                cur.execute("SELECT COUNT(*) FROM rekam_medis WHERE id_rekamed = %s", (id_rekamed,))
                if cur.fetchone()[0] == 0:
                    print("Maaf, ID pelanggan yang Anda cari tidak ada. Silakan cek kembali.")
                    postgresql_cls(conn, cur)
                    input("\n\nTekan [enter] untuk kembali ke Menu pelanggan")
                    mode_admin(uname, nama_lengkap_logged)
                    return
               
                # Meminta data baru dari user
                id_hewan_baru               = input("1. Masukkan id hewan baru (kosongkan jika tidak ingin mengubah): ")
                id_dokter_baru              = input("2. Masukkan id dokter baru (kosongkan jika tidak ingin mengubah): ")
                id_layanan_baru             = input("3. Masukkan id hewan baru (kosongkan jika tidak ingin mengubah): ")
                tgl_waktu_pemeriksaan_baru  = input("4. Masukkan tanngal waktu pemeriksaan baru (kosongkan jika tidak ingin mengubah): ")
                hasil_medis_baru            = input("5. Masukkan hasil medis baru (kosongkan jika tidak ingin mengubah): ")
                catatan_tambahan_baru       = input("6. Masukkan catatan tambahan baru (kosongkan jika tidak ingin mengubah): ")
                # List untuk menyimpan bagian query yang akan diupdate
                updates = []
               
                # List untuk menyimpan nilai yang akan diisi dalam query
                values = []

                # Mengecek apakah ada nilai baru untuk id_hewan baru dan menambahkannya ke query jika ada
                if id_hewan_baru :
                    updates.append("id_hewan = %s")
                    values.append(id_hewan_baru )
               
                # Mengecek apakah ada nilai baru untuk id_dokter_baru dan menambahkannya ke query jika ada
                if id_dokter_baru:
                    updates.append("id_dokter = %s")
                    values.append(id_dokter_baru)
               
                # Mengecek apakah ada nilai baru untuk id_layanan_baru dan menambahkannya ke query jika ada
                if id_layanan_baru:
                    updates.append("id_layanan = %s")
                    values.append(id_layanan)
               
                # Mengecek apakah ada nilai baru untuk tgl_waktu_pemeriksaan_baru dan menambahkannya ke query jika ada
                if tgl_waktu_pemeriksaan_baru:
                    updates.append("tgl_waktu_pemeriksaan = %s")
                    values.append(tgl_waktu_pemeriksaan_baru)

                # Mengecek apakah ada nilai baru untuk hasil_medis_baru dan menambahkannya ke query jika ada
                if hasil_medis_baru:
                    updates.append("hasil_medis = %s")
                    values.append(hasil_medis_baru)

                # Mengecek apakah ada nilai baru untuk tgl_waktu_pemeriksaan_baru dan menambahkannya ke query jika ada
                if catatan_tambahan_baru:
                    updates.append("catatan_tambahan = %s")
                    values.append(catatan_tambahan_baru)

                # Menambahkan id_rekam medis ke values, ini diperlukan untuk klausa WHERE
                values.append(id_rekamed)

                # Jika ada data yang diupdate
                if updates:
                    # Membuat query update dengan bagian yang perlu diupdate
                    query = f"UPDATE rekam_medis SET {', '.join(updates)} WHERE id_rekamed = %s"
                    try:
                        # Menjalankan query dengan nilai yang disediakan
                        cur.execute(query, values)
                       
                        # Melakukan commit perubahan ke database
                        conn.commit()
                       
                        print("Data rekam medis telah diubah!")
                    except psycopg2.Error as e:
                        # Menampilkan pesan kesalahan jika gagal melakukan update
                        print("Gagal mengubah data rekam medis:", e)
                       
                        # Melakukan rollback jika terjadi kesalahan
                        conn.rollback()
                else:
                    # Pesan jika tidak ada data yang diubah
                    print("Tidak ada data yang diubah.")
            except psycopg2.Error as e:
                # Menangani kesalahan koneksi atau query
                print(f"Terjadi kesalahan: {e}")
                conn.rollback()
            finally:
                # Menutup kursor dan koneksi
                cur.close()
                conn.close()
               
            input("\n\nTekan [enter] untuk kembali ke Menu Rekam Medis")
            mode_admin(uname, nama_lengkap_logged)

        elif choice_3 == '4':   # Hapus data rekam medis v
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            lihat_data_rekammedis()

            id_rekamed = int(input("Masukkan ID rekam medis yang ingin dihapus: "))
            """Menghapus data rekam medis dari database."""

            conn, cur = postgresql_connect()

            try:
                # First, check if the medical record exists
                cur.execute("SELECT * FROM rekam_medis WHERE id_rekamed = %s", (id_rekamed,))
                if cur.fetchone() is None:
                    print("Rekam medis dengan ID tersebut tidak ditemukan.")
                    result = False
                else:
                    # If it exists, proceed with deletion
                    cur.execute("DELETE FROM rekam_medis WHERE id_rekamed = %s", (id_rekamed,))
                    conn.commit()

                    # Checking if the record was successfully deleted
                    if cur.rowcount > 0:
                        print("Data rekam medis telah dihapus!")
                        result = True
                    else:
                        print("Gagal menghapus data rekam medis.")
                        result = False

            except Exception as e:
                print(f"Terjadi kesalahan: {e}")
                conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                result = False
            finally:
                cur.close()  # Menutup kursor
                conn.close()  # Menutup koneksi
           
            input("\n\nTekan [enter] untuk kembali ke Menu Rekam Medis")
            mode_admin(uname, nama_lengkap_logged)

            if result:
                print('Data berhasil terhapus')
            else:
                print('Data gagal dihapus')

    # 4.4 DATA KUSTOMER
    elif admin_choice == '4':
        pass

    # 4.5 DATA HEWAN PELIHARAAN v
    elif admin_choice == '5':
        def lihat_data_hewan():
            conn, cur = postgresql_connect()
            """Menampilkan data hewan dari database."""
            # Membuat cursor untuk berinteraksi dengan database
           
            # Query SQL untuk mengambil semua data dari tabel hewan
            query = """
            SELECT hew.id_hewan, hew.nama_hewan, hew.tanggal_lahir, pel.nama_pelanggan, jen.nama_jenis
            FROM hewan hew
            JOIN pelanggan pel on pel.id_pelanggan = hew.id_pelanggan
            JOIN jenis_hewan jen on jen.id_jenishewan = hew.id_jenishewan
            """
           
            # Menjalankan query
            cur.execute(query)
           
            # Mengambil semua data hasil query
            data_hewan = cur.fetchall()
           
            # Menutup cursor
            postgresql_cls(conn, cur)
           
            # Headers untuk tabel yang akan ditampilkan
            headers = [i[0] for i in cur.description]
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_hewan, headers=headers, tablefmt=f"{format_table}"))
       
        def lihat_data_jenishewan():
            conn, cur = postgresql_connect()
            """Menampilkan data jenis hewan dari database."""
            # Membuat cursor untuk berinteraksi dengan database
           
            # Query SQL untuk mengambil semua data dari tabel hewan
            query = """
            SELECT *
            FROM jenis_hewan
            """
           
            # Menjalankan query
            cur.execute(query)
           
            # Mengambil semua data hasil query
            data_jenishewan = cur.fetchall()
           
            # Menutup cursor
            postgresql_cls(conn, cur)
           
            # Headers untuk tabel yang akan ditampilkan
            headers = [i[0] for i in cur.description]
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_jenishewan, headers=headers, tablefmt=f"{format_table}"))

        choice_5 = input("[1] Tambah Data Hewan Peliharaan\n[2] Tambah Data Jenis Hewan\n[3] Lihat Data Hewan Peliharaan\n[4] Lihat Jenis Hewan\n[5] Edit Data Hewan Peliharaan\n[6] Edit Data Jenis hewan\n[7] Hapus Data Hewan Peliharaan\n[8] Hapus Data Jenis hewan\nPilih menu : ")
        if choice_5 == '1': #FITUR TAMBAH DATA HEWAN PELIHARAAN
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            # Meminta data hewan baru dari user
            conn, cur = postgresql_connect()
            nama_hewan     = input("Masukkan nama_hewan: ")
            tanggal_lahir  = input("Masukkan tanggal lahir: ")
            id_pelanggan   = input("Masukkan id pelanggan: ")
            id_jenishewan  = input("Masukkan id jenis hewan: ")

            # Menambah hewan baru ke database
            # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
            result = False
            if not nama_hewan or not tanggal_lahir or not id_pelanggan or not id_jenishewan:
                return False
            else:
                """Menambahkan data hewan baru ke database."""
                # Membuat cursor untuk berinteraksi dengan database
                cur = conn.cursor()
               
                # Query SQL untuk menambahkan data hewan baru
                query = """
                INSERT INTO hewan (nama_hewan, tanggal_lahir, id_pelanggan, id_jenishewan)
                VALUES (%s, %s, %s, %s)
                """
               
                # Menjalankan query dengan data yang diberikan
                cur.execute(query, (nama_hewan, tanggal_lahir, id_pelanggan, id_jenishewan))
               
                # Melakukan commit perubahan ke database
                conn.commit()
               
                # Mengambil jumlah baris yang dimodifikasi oleh query
                boolean = cur.rowcount
               
                # Menutup cursor
                cur.close()
               
                print("hewan baru telah ditambahkan!")
                result = True


            if result:
                input('Tambah data berhasil')
            else:
                input('Tambah data gagal')
            mode_admin(uname, nama_lengkap_logged)

        elif choice_5 == '2':  # FITUR TAMBAH DATA JENIS HEWAN
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            # Meminta data hewan baru dari user
            conn, cur = postgresql_connect()
            nama_jenis = input("Masukkan nama_jenis: ")


            # Menambah hewan baru ke database
            # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
            if not nama_jenis:
                print("Nama jenis hewan tidak boleh kosong.")
                input("\n\nTekan [enter] untuk kembali ke Menu jenis hewan")
                mode_admin(uname, nama_lengkap_logged)
            else:
                try:
                    """Menambahkan data hewan baru ke database."""
                    # Query SQL untuk menambahkan data hewan baru
                    query = """
                    INSERT INTO jenis_hewan (nama_jenis)
                    VALUES (%s)
                    """


                    # Menjalankan query dengan data yang diberikan
                    cur.execute(query, (nama_jenis,))
                   
                    # Melakukan commit perubahan ke database
                    conn.commit()


                    # Mengambil jumlah baris yang dimodifikasi oleh query
                    if cur.rowcount > 0:
                        print("Jenis hewan baru telah ditambahkan!")
                        result = True
                    else:
                        print("Tambah data gagal.")
                        result = False
                except Exception as e:
                    print(f"Terjadi kesalahan: {e}")
                    result = False
                    conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                finally:
                    cur.close()  # Menutup kursor
                    conn.close()  # Menutup koneksi

                if result:
                    input('Tambah data berhasil\n\nTekan [enter] untuk kembali ke Menu jenis hewan')
                else:
                    input('Tambah data gagal\n\nTekan [enter] untuk kembali ke Menu jenis hewan')
                mode_admin(uname, nama_lengkap_logged)

        elif choice_5 == '3': #FITUR LIHAT DATA HEWAN
            lihat_data_hewan()
            input("\n\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
            mode_admin(uname, nama_lengkap_logged)

        elif choice_5 == '4': #FITUR LIHAT DATA JENIS HEWAN
            lihat_data_jenishewan()
            input("\n\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
            mode_admin(uname, nama_lengkap_logged)

        elif choice_5 == '5': #FITUR EDIT DATA HEWAN
            os.system('cls')
            # Meminta ID hewan yang ingin diubah
            lihat_data_hewan()
            id_hewan = int(input("Masukkan ID hewan yang ingin diubah: "))
           
            conn, cur = postgresql_connect()
           
            try:
                # Mengecek apakah ID hewan ada dalam database
                cur.execute("SELECT COUNT(*) FROM hewan WHERE id_hewan = %s", (id_hewan,))
                if cur.fetchone()[0] == 0:
                    print("Maaf, ID hewan yang Anda cari tidak ada. Silakan cek kembali.")
                    postgresql_cls(conn, cur)
                    input("\n\nTekan [enter] untuk kembali ke menu hewan peliharaan")
                    mode_admin(uname, nama_lengkap_logged)
                    return
               
                # Meminta data baru dari user
                nama_hewan_baru = input("Masukkan nama baru hewan (kosongkan jika tidak ingin mengubah): ")
                tanggal_lahir_baru = input("Masukkan tanggal lahir baru hewan (kosongkan jika tidak ingin mengubah): ")
                id_pelanggan_baru = input("Masukkan id pelanggan baru (kosongkan jika tidak ingin mengubah): ")
                id_jenishewan_baru = input("Masukkan id jenis hewan baru  (kosongkan jika tidak ingin mengubah): ")

                # List untuk menyimpan bagian query yang akan diupdate
                updates = []
               
                # List untuk menyimpan nilai yang akan diisi dalam query
                values = []

                # Mengecek apakah ada nilai baru untuk nama_hewan dan menambahkannya ke query jika ada
                if nama_hewan_baru:
                    updates.append("nama_hewan = %s")
                    values.append(nama_hewan_baru)
               
                # Mengecek apakah ada nilai baru untuk tanggal_lahir dan menambahkannya ke query jika ada
                if tanggal_lahir_baru:
                    updates.append("tanggal_lahir = %s")
                    values.append(tanggal_lahir_baru)
               
                # Mengecek apakah ada nilai baru untuk id_pelanggan dan menambahkannya ke query jika ada
                if id_pelanggan_baru:
                    updates.append("id_pelanggan = %s")
                    values.append(id_pelanggan_baru)
               
                # Mengecek apakah ada nilai baru untuk id_jenishewan gan dan menambahkannya ke query jika ada
                if id_jenishewan_baru:
                    updates.append("id_jenishewan = %s")
                    values.append(id_jenishewan_baru)

                # Menambahkan id_hewan ke values, ini diperlukan untuk klausa WHERE
                values.append(id_hewan)

                # Jika ada data yang diupdate
                if updates:
                    # Membuat query update dengan bagian yang perlu diupdate
                    query = f"UPDATE hewan SET {', '.join(updates)} WHERE id_hewan = %s"
                    try:
                        # Menjalankan query dengan nilai yang disediakan
                        cur.execute(query, values)
                       
                        # Melakukan commit perubahan ke database
                        conn.commit()
                       
                        print("Data hewan telah diubah!")
                    except psycopg2.Error as e:
                        # Menampilkan pesan kesalahan jika gagal melakukan update
                        print("Gagal mengubah data hewan:", e)
                       
                        # Melakukan rollback jika terjadi kesalahan
                        conn.rollback()
                else:
                    # Pesan jika tidak ada data yang diubah
                    print("Tidak ada data yang diubah.")
            except psycopg2.Error as e:
                # Menangani kesalahan koneksi atau query
                print(f"Terjadi kesalahan: {e}")
                conn.rollback()
            finally:
                # Menutup kursor dan koneksi
                cur.close()
                conn.close()
               
            input("\n\nTekan [enter] untuk kembali ke Menu pelanggan")
            mode_admin(uname, nama_lengkap_logged)

        elif choice_5 == '6': #FITUR EDIT DATA JENIS HEWAN
            os.system('cls')
            # Meminta ID jenis hewan yang ingin diubah
            lihat_data_jenishewan()
            id_jenishewan = int(input("Masukkan ID jenis hewan yang ingin diubah: "))
           
            conn, cur = postgresql_connect()
           
            try:
                # Mengecek apakah ID jenis hewan ada dalam database
                cur.execute("SELECT COUNT(*) FROM jenis_hewan WHERE id_jenishewan = %s", (id_jenishewan,))
                if cur.fetchone()[0] == 0:
                    print("Maaf, ID jenis hewan yang Anda cari tidak ada. Silakan cek kembali.")
                    postgresql_cls(conn, cur)
                    input("\n\nTekan [enter] untuk kembali ke menu hewan peliharaan")
                    mode_admin(uname, nama_lengkap_logged)
                    return
               
                # Meminta data baru dari user
                nama_jenis_baru = input("Masukkan nama baru jenis hewan (kosongkan jika tidak ingin mengubah): ")

                # List untuk menyimpan bagian query yang akan diupdate
                updates = []
               
                # List untuk menyimpan nilai yang akan diisi dalam query
                values = []

                # Mengecek apakah ada nilai baru untuk nama_jenis dan menambahkannya ke query jika ada
                if nama_jenis_baru:
                    updates.append("nama_jenis = %s")
                    values.append(nama_jenis_baru)

                # Menambahkan id_jenishewan ke values, ini diperlukan untuk klausa WHERE
                values.append(id_jenishewan)

                # Jika ada data yang diupdate
                if updates:
                    # Membuat query update dengan bagian yang perlu diupdate
                    query = f"UPDATE jenis_hewan SET {', '.join(updates)} WHERE id_jenishewan = %s"
                    try:
                        # Menjalankan query dengan nilai yang disediakan
                        cur.execute(query, values)
                       
                        # Melakukan commit perubahan ke database
                        conn.commit()
                       
                        print("Data jenis hewan telah diubah!")
                    except psycopg2.Error as e:
                        # Menampilkan pesan kesalahan jika gagal melakukan update
                        print("Gagal mengubah data jenis hewan:", e)
                       
                        # Melakukan rollback jika terjadi kesalahan
                        conn.rollback()
                else:
                    # Pesan jika tidak ada data yang diubah
                    print("Tidak ada data yang diubah.")
            except psycopg2.Error as e:
                # Menangani kesalahan koneksi atau query
                print(f"Terjadi kesalahan: {e}")
                conn.rollback()
            finally:
                # Menutup kursor dan koneksi
                cur.close()
                conn.close()
               
            input("\n\nTekan [enter] untuk kembali ke Menu hewan")
            mode_admin(uname, nama_lengkap_logged)
        
        elif choice_5 == '7': #FITUR HAPUS DATA HEWAN
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            lihat_data_hewan()

            id_hewan = int(input("Masukkan ID hewan yang ingin dihapus: "))
            """Menghapus data hewan dari database."""

            conn, cur = postgresql_connect()
           
            try:
                # Memeriksa apakah hewan tersebut ada
                cur.execute("SELECT COUNT(*) FROM hewan WHERE id_hewan = %s", (id_hewan,))
                count_hewan = cur.fetchone()[0]


                if count_hewan > 0:
                    # Memeriksa apakah hewan tersebut ada di rekam_medis
                    cur.execute("SELECT COUNT(*) FROM rekam_medis WHERE id_hewan = %s", (id_hewan,))
                    count_rekam_medis = cur.fetchone()[0]
                   
                    # Memeriksa apakah hewan tersebut ada di reservasi
                    cur.execute("SELECT COUNT(*) FROM reservasi WHERE id_hewan = %s", (id_hewan,))
                    count_reservasi = cur.fetchone()[0]
                   
                    if count_rekam_medis == 0 and count_reservasi == 0:
                        # Menghapus data hewan dari tabel hewan
                        cur.execute("DELETE FROM hewan WHERE id_hewan = %s", (id_hewan,))
                       
                        # Melakukan commit perubahan ke database
                        conn.commit()
                       
                        if cur.rowcount > 0:
                            print("Data hewan telah dihapus!")
                            result = True
                        else:
                            print("Hewan dengan ID tersebut tidak ditemukan.")
                            result = False
                    else:
                        print("Hewan ini masih terkait dengan rekam medis atau reservasi. Tidak bisa dihapus.")
                        result = False
                else:
                    print("Hewan dengan ID tersebut tidak ditemukan.")
                    result = False
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")
                result = False
                conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
            finally:
                cur.close()  # Menutup kursor
                conn.close()  # Menutup koneksi
           
            input("\n\nTekan [enter] untuk kembali ke Menu hewan")
            mode_admin(uname, nama_lengkap_logged)
           
            if result:
                print('Data berhasil terhapus')
            else:
                print('Data gagal dihapus')

        elif choice_5 == '8': #FITUR HAPUS DATA JENIS HEWAN
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            lihat_data_jenishewan()

            id_jenishewan = int(input("Masukkan ID jenis hewan yang ingin dihapus: "))
            """Menghapus data jenis hewan dari database."""

            conn, cur = postgresql_connect()
           
            try:
                # Memeriksa apakah jenis hewan tersebut ada
                cur.execute("SELECT COUNT(*) FROM jenis_hewan WHERE id_jenishewan = %s", (id_jenishewan,))
                count_jenishewan = cur.fetchone()[0]

                if count_jenishewan > 0:
                    # Memeriksa apakah jenis hewan tersebut ada di tabel hewan
                    cur.execute("SELECT COUNT(*) FROM hewan WHERE id_jenishewan = %s", (id_jenishewan,))
                    count_hewan = cur.fetchone()[0]
                   
                    if count_hewan == 0:
                        # Menghapus data jenis hewan dari tabel jenis_hewan
                        cur.execute("DELETE FROM jenis_hewan WHERE id_jenishewan = %s", (id_jenishewan,))
                       
                        # Melakukan commit perubahan ke database
                        conn.commit()
                       
                        if cur.rowcount > 0:
                            print("Data jenis hewan telah dihapus!")
                            result = True
                        else:
                            print("Jenis hewan dengan ID tersebut tidak ditemukan.")
                            result = False
                    else:
                        print("Jenis hewan ini masih terkait dengan hewan. Tidak bisa dihapus.")
                        result = False
                else:
                    print("Jenis hewan dengan ID tersebut tidak ditemukan.")
                    result = False
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")
                result = False
                conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
            finally:
                cur.close()  # Menutup kursor
                conn.close()  # Menutup koneksi
           
            input("\n\nTekan [enter] untuk kembali ke Menu jenis hewan")
            mode_admin(uname, nama_lengkap_logged)
           
            if result:
                print('Data berhasil terhapus')
            else:
                print('Data gagal dihapus')

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
            print(tabulate.tabulate(data_dokter, headers=headers, tablefmt=f"{format_table}"))  

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
            print(tabulate.tabulate(data_layanan, headers=headers, tablefmt=f"{format_table}"))

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

    # 4.8 STAFF/ADMIN v
    elif admin_choice == '8':
        def lihat_data_staf():
            conn, cur = postgresql_connect()
            """Menampilkan data staf dari database."""
            # Membuat cursor untuk berinteraksi dengan database
           
            query = """
            SELECT * FROM staf
            """
           
            cur.execute(query)
            # Mengambil semua data hasil query
            data_staf = cur.fetchall()


            postgresql_cls(conn, cur)
           
            # Headers untuk tabel yang akan ditampilkan
            headers = ["ID", 'Nama Staf', 'Telepon', 'Username', 'Password']
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_staf, headers=headers, tablefmt=f"{format_table}"))  


        choice_8 = input("\n[1] Tambah Data Staf\n[2] Lihat Data Staf\n[3] Edit Data Staf\n[4] Hapus Data Staf\nPilih menu : ")
        if choice_8 == '1':    
            os.system('cls')  
            #Input Data Staf
            conn, cur = postgresql_connect()
            nama_staf     = input("1. Masukkan nama staf: ")
            tlp_staf      = input("2. Masukkan nomor telepon staf: ")
            uname_staf    = input("3. Masukkan username staf: ")
            pw_staf       = input("4. Masukkan password staf: ")


            # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
            result = False
            if not nama_staf or not tlp_staf or not uname_staf or not pw_staf:
                print("Semua field harus diisi!")
                return False
            else:
                """Menambahkan data staf baru ke database."""
                cur = conn.cursor()
               
                query = """
                INSERT INTO staf (nama_staf, tlp_staf, uname_staf, pw_staf)
                VALUES (%s, %s, %s, %s)
                """
               
                # Menjalankan query dengan data yang diberikan
                cur.execute(query, (nama_staf, tlp_staf, uname_staf, pw_staf))
               
                # Melakukan commit perubahan ke database
                conn.commit()
               
                # Mengambil jumlah baris yang dimodifikasi oleh query
                boolean = cur.rowcount
               
                # Menutup cursor
                cur.close()
               
                print("staf baru telah ditambahkan!")
                result = True


            if result:
                input('Tambah data berhasil')
            else:
                input('Tambah data gagal')
            mode_admin(uname, nama_lengkap_logged)
        elif choice_8 == '2':   # Lihat data staf v
            lihat_data_staf()
            input("\n\nTekan [enter] untuk kembali ke Menu staf")
            mode_admin(uname, nama_lengkap_logged)
        elif choice_8 == '3':   # Edit data staf v
            os.system('cls')
            # Meminta ID staf yang ingin diubah
            lihat_data_staf()
            id_staf = int(input("Masukkan ID staf yang ingin diubah: "))
           
            conn, cur = postgresql_connect()
           
            try:
                # Mengecek apakah ID staf ada dalam database
                cur.execute("SELECT COUNT(*) FROM staf WHERE id_staf = %s", (id_staf,))
                if cur.fetchone()[0] == 0:
                    print("Maaf, ID staf yang Anda cari tidak ada. Silakan cek kembali.")
                    postgresql_cls(conn, cur)
                    input("\n\nTekan [enter] untuk kembali ke Menu staf")
                    mode_admin(uname, nama_lengkap_logged)
                    return
               
                # Meminta data baru dari user
                nama_baru = input("Masukkan nama baru staf (kosongkan jika tidak ingin mengubah): ")
                telp_baru = input("Masukkan nomor telepon baru staf (kosongkan jika tidak ingin mengubah): ")
                uname_baru = input("Masukkan username baru staf (kosongkan jika tidak ingin mengubah): ")
                password_baru = input("Masukkan password baru staf (kosongkan jika tidak ingin mengubah): ")


                # List untuk menyimpan bagian query yang akan diupdate
                updates = []
               
                # List untuk menyimpan nilai yang akan diisi dalam query
                values = []


                # Mengecek apakah ada nilai baru untuk nama_staf dan menambahkannya ke query jika ada
                if nama_baru:
                    updates.append("nama_staf = %s")
                    values.append(nama_baru)
               
                # Mengecek apakah ada nilai baru untuk tlp_staf dan menambahkannya ke query jika ada
                if telp_baru:
                    updates.append("tlp_staf = %s")
                    values.append(telp_baru)
               
                # Mengecek apakah ada nilai baru untuk uname_staf dan menambahkannya ke query jika ada
                if uname_baru:
                    updates.append("uname_staf = %s")
                    values.append(uname_baru)
               
                # Mengecek apakah ada nilai baru untuk pw_staf dan menambahkannya ke query jika ada
                if password_baru:
                    updates.append("pw_staf = %s")
                    values.append(password_baru)


                # Menambahkan id_staf ke values, ini diperlukan untuk klausa WHERE
                values.append(id_staf)


                # Jika ada data yang diupdate
                if updates:
                    # Membuat query update dengan bagian yang perlu diupdate
                    query = f"UPDATE staf SET {', '.join(updates)} WHERE id_staf = %s"
                    try:
                        # Menjalankan query dengan nilai yang disediakan
                        cur.execute(query, values)
                       
                        # Melakukan commit perubahan ke database
                        conn.commit()
                       
                        print("Data staf telah diubah!")
                    except psycopg2.Error as e:
                        # Menampilkan pesan kesalahan jika gagal melakukan update
                        print("Gagal mengubah data staf:", e)
                       
                        # Melakukan rollback jika terjadi kesalahan
                        conn.rollback()
                else:
                    # Pesan jika tidak ada data yang diubah
                    print("Tidak ada data yang diubah.")
            except psycopg2.Error as e:
                # Menangani kesalahan koneksi atau query
                print(f"Terjadi kesalahan: {e}")
                conn.rollback()
            finally:
                # Menutup kursor dan koneksi
                cur.close()
                conn.close()
               
            input("\n\nTekan [enter] untuk kembali ke Menu staf")
            mode_admin(uname, nama_lengkap_logged)


           
        elif choice_8 == '4':   # Hapus data staf v
            os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
            lihat_data_staf()


            id_staf = int(input("Masukkan ID staf yang ingin dihapus: "))
            """Menghapus data staf dari database."""


            conn, cur = postgresql_connect()
           
            try:
                # Memeriksa apakah ada reservasi yang terkait dengan staf ini
                cur.execute("SELECT COUNT(*) FROM reservasi WHERE id_staf = %s", (id_staf,))
                count_reservasi = cur.fetchone()[0]
               
                # Memeriksa apakah ada detail transaksi yang terkait dengan staf ini
                cur.execute("SELECT COUNT(*) FROM detail_transaksi WHERE id_staf = %s", (id_staf,))
                count_detail_transaksi = cur.fetchone()[0]


                # Jika ada referensi terkait, hapus referensi tersebut terlebih dahulu
                if count_reservasi > 0:
                    cur.execute("DELETE FROM reservasi WHERE id_staf = %s", (id_staf,))
                if count_detail_transaksi > 0:
                    cur.execute("DELETE FROM detail_transaksi WHERE id_staf = %s", (id_staf,))
               
                # Menghapus data staf dari tabel staf
                cur.execute("DELETE FROM staf WHERE id_staf = %s", (id_staf,))
               
                # Melakukan commit perubahan ke database
                conn.commit()
               
                # Memeriksa apakah ada baris yang dihapus
                if cur.rowcount > 0:
                    print("Data staf telah dihapus!")
                    result = True
                else:
                    print("Staf dengan ID tersebut tidak ditemukan.")
                    result = False
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")
                result = False
                conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
            finally:
                cur.close()  # Menutup kursor
                conn.close()  # Menutup koneksi
           
            input("\n\nTekan [enter] untuk kembali ke Menu staf")
            mode_admin(uname, nama_lengkap_logged)
           
            if result == True:
                print('Data berhasil terhapus')
            else:
                print('Data gagal dihapus')

    # 4.9 EXIT v
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

format_table = 'fancy_grid'




# EKSEKUSI PROGRAM --------------------------------------------------------------------------------

welcome_interface()

admin_pertama()

launch_page()
