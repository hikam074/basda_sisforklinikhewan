import psycopg2
import os
import sys
import time
import tabulate
import pandas as pd
import datetime
import textwrap

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

# 1. LAUNCH PAGE v----------------------------------------------------------------------------------
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
    print(" [1] Log-in \n [2] Sign-Up Customer \n [3] EULA \n [4] Exit \n")
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

    def rekam_medis(pilihan, uname, conn, cur):
        match pilihan:
            case '1': # 
                nama_hewan=input('Nama hewan: ') # inputan nama hewan untuk mengecek hewan yang mana yg benar 
                nama_pelanggan=input('Nama pelanggan: ')
                cur.execute(f"select id_hewan from hewan where nama_hewan ilike '{nama_hewan}' and id_pelanggan = (select id_pelanggan from pelanggan where nama_pelanggan ilike '{nama_pelanggan}')")
                no_id_hewan=cur.fetchall() # menghasilkan id nama hewan yang dicari
                cur.execute(f"select id_dokter from dokter where uname_dokter= '{uname}'")
                id_dokter=cur.fetchall() # menggunakan username untuk pencarian id dokter
                cur.execute("select * from layanan")
                data_layanan=cur.fetchall()
                nilai1=pd.DataFrame(data_layanan,columns=['Id Layanan','Nama Layanan','Harga Layanan'])
                print (nilai1)
                id_layanan_hewan=input('Pilih jenis layanan [Ketik Idnya]: ') #pilih layanan
                cur.execute(f'select id_layanan from layanan where id_layanan={id_layanan_hewan}')
                id_layanan=cur.fetchall()
                hasil_medis=input('Hasil Medis: ') # hasil medis
                catatan=input('Catatan:') # hasil catatan
                try:
                    tgl_waktu_pemeriksaan=datetime.datetime.now()
                    cur.execute(f"INSERT INTO rekam_medis (id_hewan,id_dokter,id_layanan,tgl_waktu_pemeriksaan,hasil_medis,catatan_tambahan)  VALUES ({no_id_hewan[0][0]},{id_dokter[0][0]},{id_layanan[0][0]},'{tgl_waktu_pemeriksaan}','{hasil_medis}','{catatan}')")
                    conn.commit()
                except:
                    print("Inputan data Anda salah, cek kembali")
            case'2': # fitur ubah data di rekam medis
                cur.execute("""select h.nama_hewan,d.nama_dokter,l.nama_layanan,
                            r.tgl_waktu_pemeriksaan,r.hasil_medis,r.catatan_tambahan from rekam_medis r join 
                            hewan h on (r.id_hewan=h.id_hewan) 
                            join dokter d on (d.id_dokter=r.id_dokter) join layanan l on (r.id_layanan=l.id_layanan) """)
                df=cur.fetchall()
                columns=['Id Rekam Medis','Nama Hewan','Nama Dokter','Nama Layanan','Tanggal Pemeiksaan','Hasil Medis','Catatan Tambahan']
                tabel = tabulate.tabulate(df,columns,tablefmt='fancy_grid')
                print('[1] Nama Hewan\n[2] Nama Dokter\n[3] Layanan\n[4] Hasil Medis\n[5] Caatatan\n[6] Semua\n[Enter] Exit ')
                lagi=int(input('Pilih: '))
                pilih_lagi=int(lagi-1)
                print(tabel)
                siapa_yang_dirubah=input("No id rekam medis yang akan dirubah:")
                def nama_hewan_yang_benar():
                    hewan=input(f"Nama hewan yang benar: ")
                    try:
                        cur.execute(f" select id_hewan from hewan where nama_hewan='{hewan}'")
                        sintaksi=cur.fetchall()
                        sintaksi_baru=f"update rekam_medis set id_hewan = {sintaksi[0][0]} where id_rekamed={siapa_yang_dirubah}"
                        cur.execute(sintaksi_baru)
                        conn.commit()
                        print("Berhasil")
                        time.sleep(1)
                    except :
                        print(f"Nama hewan tidak ditemukan, cek kembali")
                        time.sleep(1)
                    os.system("cls")
                def nama_doker_yang_benar():
                    dokter=input(f"Nama dokter yang benar: ")
                    try:
                        cur.execute(f" select id_dokter from dokter where nama_dokter='{dokter}'")
                        sintaksi=cur.fetchall()
                        sintaksi_baru=f"update rekam_medis set id_dokter = {sintaksi[0][0]} where id_rekamed={siapa_yang_dirubah}"
                        cur.execute(sintaksi_baru)
                        conn.commit()
                        print("Berhasil")
                        time.sleep(1)
                    except:
                        print("Nama dokter tidak ditemukan, cek kembali")
                        time.sleep(1)
                    os.system("cls")
                def layanan_yang_benar():
                    ketik=input(f"Nama layanan yang benar: ") 
                    try:
                        cur.execute(f" select id_layanan from layanan where nama_layanan='{ketik}'")
                        sintaksi=cur.fetchall()
                        sintaksi_baru=f"update rekam_medis set id_layanan = {sintaksi[0][0]} where id_rekamed={siapa_yang_dirubah}"
                        cur.execute(sintaksi_baru)
                        conn.commit()
                        print("Berhasil")
                        time.sleep(1)
                    except:
                        print("Nama layanan ditemukan, cek kembali")
                        time.sleep(1)
                    os.system("cls")
                            
                def hasil_medis_yang_benar():
                    ketik=input(f"Hasil medis yang benar: ")
                    sintaksi_baru=f"update rekam_medis set hasil_medis= '{ketik}' where id_rekamed={siapa_yang_dirubah}"
                    cur.execute(sintaksi_baru)
                    conn.commit()
                    print("Berhasil")
                    os.system("CLS")
                def catatan_yang_benar():
                    ketik=input(f"Nama catatan tambahan yang benar: ")
                    sintaksi_baru=f"update rekam_medis set catatan_tambahan= '{ketik}' where id_rekamed={siapa_yang_dirubah}"
                    cur.execute(sintaksi_baru)
                    conn.commit()
                    print("Berhasil")
                    time.sleep(1)
                    os.system("CLS")
                if pilih_lagi ==0: 
                        nama_hewan_yang_benar()
                elif pilih_lagi==1:  #uabh dokter yang benar
                        nama_doker_yang_benar()
                elif pilih_lagi==2: # ubah layanan yg benar
                        layanan_yang_benar()
                elif pilih_lagi ==3: # ubah hasil medis yang benar
                        hasil_medis_yang_benar()
                elif pilih_lagi==4: # ubah catatan di rekam medis
                        catatan_yang_benar()
                # Ubah keseluruhan data
                elif pilih_lagi==5:
                    simpan=[nama_hewan_yang_benar(),nama_doker_yang_benar(),layanan_yang_benar(),hasil_medis_yang_benar(),catatan_yang_benar]
                    for i in range(5):
                        simpan[i]
                else: # jika salah ketik terdapat pesan peringatan
                    print('Maaf Anda salah ketik')
            case '3': # Lihat rekam medis
                sintaksis ="""select r.id_rekamed, h.nama_hewan,d.nama_dokter,r.tgl_waktu_pemeriksaan,l.nama_layanan, r.hasil_medis,r.catatan_tambahan 
                from rekam_medis r join hewan h on (h.id_hewan=r.id_hewan)
                join dokter d on (d.id_dokter=r.id_dokter)
                join layanan l on (l.id_layanan=r.id_layanan) order by r.id_rekamed asc"""
                cur.execute(sintaksis)
                nilai=cur.fetchall()
                header = ["Id Rekam Medis", "Nama Hewan", "Nama Dokter","Tanggal Pemeriksaan", "Nama Layanan","Hasil Medis","Catatan Tambahan"]
                tabel = tabulate.tabulate(nilai,headers=header, tablefmt="fancy_grid")
                print(tabel)
            case '4': # penghapusan rekam medis oleh dokter
                id=input('Id rekam medis yang akan di hapus')
                sintaksis_hapus= f"DELETE FROM rekam_medis WHERE id_rekamed = '{id}' " 
                try:
                    cur.execute(sintaksis_hapus)
                    conn.commit()
                except: 
                    print("id rekam medis tidak ditemukan")
            case _:
                print('Kembali lagi dihalaman utama')

    conn, cur = postgresql_connect()
    print(f"selamat datang, {nama_lengkap_logged} !")
    print(" [1] Rekam Medis \n [2] Profil Anda \n [3] Log-out ")
    dokter_choice = input("Silahkan pilih menu anda : ")

    # 2.1 REKAM MEDIS fatal eror
    if dokter_choice == '1':
        print('[1] Buat\n[2] Edit\n[3] Lihat\n[4] Hapus\n[5] Exit')
        pilihan=input('Pilih: ')
        rekam_medis(pilihan, uname, conn, cur)
        mode_dokter(uname, nama_lengkap_logged)
    # 2.2 PROFIL ANDA v
    elif dokter_choice == '2':
        print('[1] Lihat\n[2] Edit')
        pilihan_anda=input('Pilih: ')

        if pilihan_anda=='1':
            sintaksis=f"select * from dokter where uname_dokter = '{uname}'"
            cur.execute(sintaksis)
            nilai = cur.fetchall()
            header = ["Id Dokter", "Nama Dokter", "Telp Dokter", "No STR","Username Dokter","Password Dokter"]
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
                    try:
                        cur.execute(sintaksis)
                    except:
                        print(f'Salah {header[i+1]}')
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

# 3. FITUR KUSTOMER v-------------------------------------------------------------------------------
def mode_pelanggan(uname, nama_lengkap_logged):
    # ambil data id_pelanggan
    conn, cur = postgresql_connect()
    cur.execute(f"SELECT id_pelanggan FROM pelanggan WHERE uname_pelanggan = '{uname}'")
    id_pelanggan = cur.fetchone()
    id_pelanggan = str(id_pelanggan).strip(")(,")
    postgresql_cls(conn, cur)

    os.system('cls')
    print("PELANGGAN>DASHBOARD")
    print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")}\n")
    print(f"Selamat datang, {nama_lengkap_logged} !\n")
    print(" [1] RESERVASI ANDA\n [2] Hewan Peliharaan anda \n [3] Rekam Medis Hewan Anda \n [4] Riwayat Kunjungan Anda \n [5] Profil Anda \n [6] Lihat Dokter \n [7] Layanan Kami \n\n [8] Log-Out")
    pelanggan_choice = input("\nSilahkan pilih menu anda : ")

    # 3.1 RESERVASI v UI FIXED
    if pelanggan_choice == '1':
        def menu_pelanggan_reservasi(nama_lengkap_logged):
            os.system('cls')
            print("PELANGGAN>DASHBOARD>RESERVASI")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            print("MENU RESERVASI :")
            conn, cur = postgresql_connect()
            listdata = postgresql_alldata_akun(conn, cur)

            print("[1] Edit Reservasi")
            print("[2] Lihat Daftar Rencana dan Rincian Reservasi")
            print("[3] Batalkan Reservasi")
            print("\n[4] Kembali ke Dashboard\n")
            inputmenu = input("Masukan menu yang diinginkan : ")

            if inputmenu == '1':    # edit reservasi v UI FIXED
                os.system('cls')
                print("PELANGGAN>DASHBOARD>RESERVASI>EDIT RESERVASI")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                            
                cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.nama_hewan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) WHERE p.uname_pelanggan = '{uname}'")
                datareservasi = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datareservasi, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)

                conn, cur = postgresql_connect()
                editnomor = input("Pilih ID yang ingin di edit : ")
                if editnomor == '':
                    postgresql_commit_nclose(conn, cur)
                    mode_pelanggan(uname, nama_lengkap_logged)
                else:
                    try:
                        cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.id_hewan, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) where r.id_reservasi = '{editnomor}' and p.id_pelanggan = '{id_pelanggan}'")
                        datareservasi = cur.fetchall()
                        headers = [i[0] for i in cur.description]

                        if datareservasi != []:
                            print(tabulate.tabulate(datareservasi, headers=headers, tablefmt=f"{format_table}"))

                            id_hewan                = input("Masukkan ID hewan anda [kosongi bila tidak mengubah] : ")
                            reservasi_tgl_layanan   = input("Hendak reschedule ke tanggal berapa [yyyy-mm-dd, kosongi bila tidak mengubah] : ")
                            reservasi_waktu_layanan = input("Hendak reschedule ke jam berapa [hh:mm, kosongi bila tidak mengubah] : ")
                            print()

                            if id_hewan == '':
                                pass
                            else:
                                try:
                                    # mengecek id yang dimasukkan itu apakah benar hewannya sendiri
                                    cur.execute(f"SELECT id_hewan FROM hewan WHERE  id_pelanggan = {id_pelanggan}")
                                    hewan_dimiliki_pelanggan = cur.fetchall()
                                    if id_hewan in str(hewan_dimiliki_pelanggan) :
                                        cur.execute(f"UPDATE reservasi SET id_hewan = {id_hewan} WHERE id_hewan = (SELECT id_hewan FROM hewan WHERE id_pelanggan = {id_pelanggan} AND id_hewan = (SELECT id_hewan FROM reservasi WHERE id_reservasi = {editnomor})) AND id_reservasi = {editnomor}")
                                        print("ID hewan : Hewan yang hendak diperiksakan diubah!")
                                    else:
                                        print("ID hewan : ID tidak ditemukan untuk hewan anda, batal diubah")
                                except psycopg2.Error as e:
                                    print("PERHATIAN : Terdapat kesalahan pada data yang anda coba ubah! Ubah ID hewan gagal")
                            if reservasi_tgl_layanan == '':
                                pass
                            else:
                                try:
                                    cur.execute(f"UPDATE reservasi SET reservasi_tgl_layanan = '{reservasi_tgl_layanan}' WHERE id_hewan = (SELECT id_hewan FROM hewan WHERE id_pelanggan = {id_pelanggan} AND id_hewan = (SELECT id_hewan FROM reservasi WHERE id_reservasi = {editnomor})) AND id_reservasi = {editnomor}")
                                    print("Tanggal : Jadwal tanggal berhasil di-reschedule!")
                                except psycopg2.Error as e:
                                    print("PERHATIAN : Terdapat kesalahan pada data yang anda coba ubah! Ubah tanggal gagal")
                            if reservasi_waktu_layanan == '':
                                pass
                            else:
                                try:
                                    cur.execute(f"UPDATE reservasi SET reservasi_waktu_layanan = '{reservasi_waktu_layanan}' WHERE id_hewan = (SELECT id_hewan FROM hewan WHERE id_pelanggan = {id_pelanggan} AND id_hewan = (SELECT id_hewan FROM reservasi WHERE id_reservasi = {editnomor})) AND id_reservasi = {editnomor}")
                                    print("Jam : Jam dipesan berhasil di-reschedule!")
                                except psycopg2.Error as e:
                                    print("PERHATIAN : Terdapat kesalahan pada data yang anda coba ubah! Ubah jam gagal")
                        else:
                            print("\nPERHATIAN : ID tidak ditemukan!")

                    except psycopg2.Error as e:
                        print(e)
                    finally:
                        postgresql_commit_nclose(conn, cur)
                        input("\nTekan [Enter] untuk kembali ke Menu RESERVASI : ")
                        menu_pelanggan_reservasi(nama_lengkap_logged)
                
            elif inputmenu == '2':  #lihat riwayat reservasi v UI FIXED
                os.system('cls')
                print("PELANGGAN>DASHBOARD>RESERVASI>LIHAT RESERVASI")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.nama_hewan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) WHERE p.uname_pelanggan = '{uname}'")
                datareservasi = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datareservasi, headers=headers, tablefmt=f"{format_table}"))
                lihatnomor = (input("Masukan id reservasi yang ingin dilihat rinci : "))
                try:
                    os.system('cls')
                    print(f"PELANGGAN>DASHBOARD>RESERVASI>LIHAT RESERVASI>ID:{lihatnomor}")
                    print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                            
                    cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) where r.id_reservasi = '{lihatnomor}' and p.id_pelanggan = '{id_pelanggan}'")
                    lihatdata = cur.fetchall()
                    headers = [i[0] for i in cur.description]
                    print(tabulate.tabulate(lihatdata, headers=headers, tablefmt=f"{format_table}"))
                except psycopg2.Error as e:
                    print("Data tidak ditemukan")
                finally:
                    postgresql_commit_nclose(conn, cur)
                    input("\nTekan [Enter] untuk kembali ke Menu RESERVASI : ")
                    menu_pelanggan_reservasi(nama_lengkap_logged)
            
            elif inputmenu == '3':  # batalkan reservasi v UI FIXED
                cur.execute(f"Select r.id_reservasi, r.reservasi_tgl_layanan||' '||r.reservasi_waktu_layanan as reservasi_untuk, h.nama_hewan, s.nama_staf from reservasi r join hewan h on (h.id_hewan = r.id_hewan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join staf s on (r.id_staf = s.id_staf) WHERE p.uname_pelanggan = '{uname}'")
                datareservasi = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datareservasi, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)

                conn, cur = postgresql_connect()
                id_batalreservasi = input("Masukkan ID yang hendak dibatalkan : ")
                if id_batalreservasi == '':
                    postgresql_commit_nclose(conn, cur)
                    menu_pelanggan_reservasi(nama_lengkap_logged)
                else:
                    try:
                        konfirmasi_hapus = input(f"[Y/N] Apakah anda yakin untuk membatalkan reservasi dengan ID '{id_batalreservasi}'? Tindakan tidak dapat diurungkan : ")
                        if konfirmasi_hapus.upper() == 'Y':
                            cur.execute(f"DELETE FROM reservasi WHERE id_reservasi = {id_batalreservasi} AND id_hewan = (select h.id_hewan FROM hewan h JOIN reservasi r ON (r.id_hewan = h.id_hewan) WHERE h.id_pelanggan = {id_pelanggan} AND r.id_reservasi = {id_batalreservasi})")
                            postgresql_commit_nclose(conn, cur)
                            conn, cur = postgresql_connect()
                            cur.execute(f"select from reservasi where id_reservasi = {id_batalreservasi}")
                            sukses = cur.fetchone()
                            if sukses == None:
                                print("\nData berhasil dihapus")
                            else:
                                print("\nPERHATIAN : ID tidak ditemukan untuk user anda! Tidak ada data yang dihapus")
                        else:
                            print("\nBatal membatalkan reservasi")
                    except psycopg2.IntegrityError as e:
                        print("\nPERHATIAN : Reservasi tersebut sudah diselesaikan sehingga tidak dapat dihapus!")
                    except psycopg2.Error as e:
                        print("\nPERHATIAN : Terjadi kesalahan pada data yang anda masukkan!")
                    finally:
                        postgresql_commit_nclose(conn, cur)
                        input("\nTekan [Enter] untuk kembali ke Menu RESERVASI : ")
                        menu_pelanggan_reservasi(nama_lengkap_logged)

            elif inputmenu == '4':
                mode_pelanggan(uname, nama_lengkap_logged)
            
            else:
                menu_pelanggan_reservasi(nama_lengkap_logged)

        menu_pelanggan_reservasi(nama_lengkap_logged)

    # 3.2 HEWAN PELIHARAAN ANDA v UI FIXED
    elif pelanggan_choice == '2':
        def menu_hewan_pelanggan(nama_lengkap_logged):
            conn, cur = postgresql_connect()
            os.system('cls')
            print("PELANGGAN>DASHBOARD>HEWAN PELIHARAAN")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
            print("MENU HEWAN PELIHARAAN ANDA :")
            print("[1] Tambah Data Hewan Peliharaan")
            print("[2] Lihat Data Hewan Peliharaan Anda")
            print("[3] Ubah Data Hewan Peliharaan Anda")
            print("[4] Hapus Data Hewan Peliharaan Anda")
            print("\n[5] Kembali ke menu Dashboard\n")
            inputmenu = input("Masukan opsi anda : ")
            if inputmenu == '1':    # tambah hewan v UI FIXED
                os.system('cls')
                print("PELANGGAN>DASHBOARD>HEWAN PELIHARAAN>TAMBAH DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                cur.execute('SELECT * FROM jenis_hewan')
                datahewan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datahewan, headers=headers, tablefmt=f"{format_table}"))

                jenishewan   = input("Masukan ID Jenis Hewan Anda : ")
                nama_hewan   = input("Masukan Nama Hewan Anda : ")
                tanggallahir = input("Masukan Tanggal Lahir Hewan Anda (yyyy-mm-dd) : ")
                try:
                    cur.execute(f"INSERT INTO hewan (nama_hewan, tanggal_lahir, id_pelanggan, id_jenishewan) VALUES ('{nama_hewan}', '{tanggallahir}', {id_pelanggan}, {jenishewan})")
                    print("\nData berhasil ditambahkan!")
                except psycopg2.Error as e:
                    print("\nPERHATIAN : Terdapat kesalahan pada data yang anda coba masukkan! silahkan coba lagi")
                finally:
                    postgresql_commit_nclose(conn, cur)
                    input("\nTekan [Enter] untuk kembali ke menu : ")
                    menu_hewan_pelanggan(nama_lengkap_logged)
            
            elif inputmenu == '2':  # lihat list hewan anda v UI FIXED
                os.system('cls')
                print("PELANGGAN>DASHBOARD>HEWAN PELIHARAAN>LIHAT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                cur.execute(f"Select h.id_hewan, h.nama_hewan, jh.nama_jenis, h.tanggal_lahir, p.nama_pelanggan from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan}")
                lihatdata = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(lihatdata, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)
                input("\nTekan [Enter] untuk kembali ke menu : ")
                menu_hewan_pelanggan(nama_lengkap_logged)

            elif inputmenu == '3':  # edit data hewan v UI FIXED
                os.system('cls')
                print("PELANGGAN>DASHBOARD>HEWAN PELIHARAAN>UBAH DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                cur.execute(f'select h.id_hewan, h.nama_hewan, h.tanggal_lahir, jh.nama_jenis from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan}')
                datahewan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datahewan, headers=headers, tablefmt=f"{format_table}"))

                dataygdiubah = input("Masukan no. ID Hewan yang hendak diubah : ")

                try:
                    cur.execute(f'select h.id_hewan, h.nama_hewan, h.tanggal_lahir, jh.nama_jenis from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan} and h.id_hewan = {dataygdiubah}')
                    datahewan = cur.fetchall()
                    headers = [i[0] for i in cur.description]
                    if datahewan == []:
                        print("Data yang anda cari tidak ada! Silahkan coba lagi")
                    else:
                        os.system('cls')
                        print(f"PELANGGAN>DASHBOARD>HEWAN PELIHARAAN>UBAH DATA>ID:{dataygdiubah}")
                        print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                    
                        print(tabulate.tabulate(datahewan, headers=headers, tablefmt=f"{format_table}"))

                        nama_hewan   = input('masukan nama hewan baru [Kosongi bila tidak ingin mengubah]    : ')
                        tanggallahir = input('masukan tanggal lahir baru [Kosongi bila tidak ingin mengubah] : ')
                        idjenis      = input('masukan ID jenis baru [Kosongi bila tidak ingin mengubah]      : ')
                        print()

                        if nama_hewan == '':
                            print("nama_hewan tidak diubah")
                        else:
                            try:
                                cur.execute(f"UPDATE hewan SET nama_hewan = '{nama_hewan}' WHERE id_pelanggan = {id_pelanggan} AND id_hewan = {dataygdiubah}")
                                print("Data nama_hewan BERHASIL diubah")
                            except psycopg2.Error as e:
                                print(e)

                        if tanggallahir == '':
                            print("tanggal_lahir tidak diubah")
                        else:
                            try:
                                cur.execute(f"UPDATE hewan SET tanggal_lahir = '{tanggallahir}' WHERE id_pelanggan = {id_pelanggan} AND id_hewan = {dataygdiubah}")
                                print("Data tanggal_lahir BERHASIL diubah")
                            except psycopg2.Error as e:
                                print(e)

                        if idjenis == '':
                            print("jenis_hewan tidak diubah")
                        else:
                            try:
                                cur.execute(f"UPDATE hewan SET id_jenishewan = '{idjenis}' WHERE id_pelanggan = {id_pelanggan} AND id_hewan = {dataygdiubah}")
                                print("Data nama_jenis BERHASIL diubah")
                            except psycopg2.Error as e:
                                print(e)

                except psycopg2.Error as e:
                    print("PERHATIAN : Data yang anda coba masukkan tidak valid! Silahkan coba lagi")
                
                postgresql_commit_nclose(conn, cur)
                input("\nTekan [Enter] untuk kembali ke menu : ")
                menu_hewan_pelanggan(nama_lengkap_logged)

            elif inputmenu == '4':  # hapus data hewan v
                os.system('cls')
                print("PELANGGAN>DASHBOARD>HEWAN PELIHARAAN>HAPUS DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                # lihat dulu data hewannya
                cur.execute(f"Select h.id_hewan, h.nama_hewan, jh.nama_jenis, h.tanggal_lahir, p.nama_pelanggan from hewan h join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) where p.id_pelanggan = {id_pelanggan}")
                lihatdata = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(lihatdata, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)

                id_hewan = input("Masukkan ID hewan yang ingin dihapus : ")
                if id_hewan == '':
                    mode_pelanggan(uname, nama_lengkap_logged)
                else:
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
                                konfirmasi_hapus = input(f"\n[Y/N] Apakah anda yakin untuk menghapus hewan anda  ber-ID '{id_hewan}'? Tindakan tidak dapat diurungkan : ")
                                if konfirmasi_hapus.upper() == 'Y':
                                    # Menghapus data hewan dari tabel hewan
                                    cur.execute(f"DELETE FROM hewan WHERE id_hewan = {id_hewan} AND id_pelanggan = {id_pelanggan}")
                                    conn.commit()
                                
                                    if cur.rowcount > 0:
                                        print("\nData hewan telah dihapus!")
                                    else:
                                        print("\nPERHATIAN : Hewan dengan ID tersebut tidak ditemukan.")
                                else:
                                    print("Data batal dihapus")
                            else:
                                print("Hewan ini masih terkait dengan rekam medis atau reservasi. Tidak bisa dihapus.")
                        else:
                            print("Hewan dengan ID tersebut tidak ditemukan.")

                    except Exception as e:
                        print(f"PERHATIAN : Data yang anda coba masukkan tidak valid! Silahkan coba lagi")
                        conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                    finally:
                        postgresql_commit_nclose(conn, cur)
                        input("\nTekan [Enter] untuk kembali ke menu : ")
                        menu_hewan_pelanggan(nama_lengkap_logged)

            elif inputmenu == '5':
                mode_pelanggan(uname, nama_lengkap_logged)
            
            menu_hewan_pelanggan(nama_lengkap_logged)
        
        menu_hewan_pelanggan(nama_lengkap_logged)

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
                    try:
                        tanggal = input('Masukan Tanggal Reservasi yang Ingin Dicari! : ')
                        cur.execute(f"select r.id_rekamed, r.tgl_waktu_pemeriksaan, h.nama_hewan, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) where p.id_pelanggan = {id_pelanggan} AND TO_CHAR(tgl_waktu_pemeriksaan :: DATE, 'yyyy-mm-dd') = TO_CHAR(tgl_waktu_pemeriksaan :: DATE, '{tanggal}')")
                        datarekammedis = cur.fetchall()
                        headers = [i[0] for i in cur.description]
                        os.system('cls')
                        print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                        postgresql_cls(conn, cur)
                        input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")  
                    except Exception as e:
                        print(f"Terjadi kesalahan: {e}")
                        result = False
                        conn.rollback()

                elif inputmenu == '2':
                    #MENAMPILKAN RINCIAN JENIS HEWAN
                    try: 
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
                    except Exception as e:
                        print(f"Terjadi kesalahan: {e}")
                        result = False
                        conn.rollback()

                elif inputmenu == '3':
                    #MENAMPILKAN RINCIAN AWAL
                    try:
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
                    except Exception as e:
                        print(f"Terjadi kesalahan: {e}")
                        result = False
                        conn.rollback()

                elif inputmenu == '4':
                    #MENAMPILKAN RINCIAN AWAL  
                    try:
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
                    except Exception as e:
                        print(f"Terjadi kesalahan: {e}")
                        result = False
                        conn.rollback()

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
                try: 
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
                except Exception as e:
                    print(f"Terjadi kesalahan: {e}")
                    result = False
                    conn.rollback()
            if inputmenu == '2':
                #MENAMPILKAN RINCIAN AWAL  
                os.system('cls')
                try:
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
                except Exception as e:
                    print(f"Terjadi kesalahan: {e}")
                    result = False
                    conn.rollback()
            if inputmenu == '3':
                try:
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
                except Exception as e:
                    print(f"Terjadi kesalahan: {e}")
                    result = False
                    conn.rollback()
            if inputmenu == '4':
                try:
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
                except Exception as e:
                    print(f"Terjadi kesalahan: {e}")
                    result = False
                    conn.rollback()
            elif inputmenu =='5':
                mode_pelanggan(uname, nama_lengkap_logged)

            kunjungan_anda(uname, nama_lengkap_logged)
        kunjungan_anda(uname, nama_lengkap_logged)

    # 3.5 PROFIL ANDA v
    elif pelanggan_choice == '5':
        os.system('cls')
        conn, cur = postgresql_connect()
        
        #MENAMPILKAN PROFIL CUSTOMER
        try:
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
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            result = False
            conn.rollback()

    # 3.6 LIHAT DOKTER v
    elif pelanggan_choice == '6':
        os.system('cls')
        conn, cur = postgresql_connect()
        print("Dibawah ini adalah data dokter di Klinik Sat Set Care")
        try: 
            cur.execute('select id_dokter, nama_dokter, tlp_dokter, no_str from dokter')
            datadokter = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datadokter, headers=headers, tablefmt=f"{format_table}"))
            postgresql_cls(conn, cur)
            input("Tekan [Enter] untuk kembali ke MENU UTAMA")
            mode_pelanggan(uname, nama_lengkap_logged)
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            result = False
            conn.rollback()

    # 3.7 LAYANAN KAMI v
    elif pelanggan_choice == '7':
        os.system('cls')
        conn, cur = postgresql_connect()
        print('Dibawah ini adalah layanan di Klinik Sat Set Care!')
        try:
            cur.execute('select id_layanan, nama_layanan, harga_layanan from layanan')
            datalayanan = cur.fetchall()
            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(datalayanan, headers=headers, tablefmt=f"{format_table}"))
            postgresql_cls(conn, cur)
            input("Tekan [Enter] untuk kembali ke MENU UTAMA")
            mode_pelanggan(uname, nama_lengkap_logged)
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            conn.rollback()

    # 3.8 EXIT v
    elif pelanggan_choice == '8':
        launch_page()

    # BILA SALAH INPUT v
    else :
        mode_pelanggan(uname, nama_lengkap_logged)

# -------------------------------------------------------------------------------------------------

# 4. FITUR ADMIN UI FIXED -------------------------------------------------------------------------
def mode_admin(uname, nama_lengkap_logged):
    os.system('cls')
    print("ADMIN>DASHBOARD")
    print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")}")
    print(f"Selamat datang, {nama_lengkap_logged} !\n")
    print(" [1] RESERVASI \n [2] TRANSAKSI \n [3] Rekam Medis \n [4] Data Pelanggan \n [5] Data Hewan Peliharaan \n [6] Data Dokter \n [7] Layanan \n [8] Staff/Admin \n\n [9] Log-out")
    admin_choice = input("\nSilahkan pilih menu anda : ")


    # 4.1 RESERVASI v UI FIXED
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
            headers = [i[0] for i in cur.description]
            # Mengembalikan daftar hewan
            return animals, headers
        
        # Fungsi untuk melihat list layanan
        def lihat_data_layanan(conn, cur):
                cursor = conn.cursor()
                query = "SELECT * FROM layanan"
                cursor.execute(query)
                data_layanan = cursor.fetchall()
                cursor.close()

                headers = [i[0] for i in cursor.description]
                print(tabulate.tabulate(data_layanan, headers=headers, tablefmt=f"{format_table}"))

        # Fungsi untuk memeriksa apakah data pelanggan sudah ada dalam database
        def check_hewan_exists(conn, id_hewan):
            # Membuka kursor untuk mengirim kueri SQL ke database
            cur = conn.cursor()
            # Menjalankan kueri SQL untuk memeriksa keberadaan data pelanggan
            cur.execute("SELECT EXISTS(SELECT 1 FROM hewan WHERE id_hewan=%s)", (id_hewan,))
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
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO reservasi (id_hewan, id_staf, id_layanan, reservasi_tgl_layanan, reservasi_waktu_layanan)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                reservation_data['id_hewan'],
                reservation_data['id_staf'],
                reservation_data['id_layanan'],
                reservation_data['reservasi_tgl_layanan'],
                reservation_data['reservasi_waktu_layanan']
            ))
            conn.commit()

            cur.execute("""
                SELECT id_reservasi FROM reservasi 
                WHERE id_hewan = %s AND id_staf = %s AND id_layanan = %s AND reservasi_tgl_layanan = %s AND reservasi_waktu_layanan = %s
            """, (
                reservation_data['id_hewan'],
                reservation_data['id_staf'],
                reservation_data['id_layanan'],
                reservation_data['reservasi_tgl_layanan'],
                reservation_data['reservasi_waktu_layanan']
            ))
            id_reservasi = cur.fetchone()[0] if cur.rowcount else None
            cur.close()
            return id_reservasi

        # Fungsi untuk mengedit reservasi
        def edit_reservation(conn, id_reservasi, reservation_data):
            cur = conn.cursor()
            updates = []
            values = []

            if 'id_hewan' in reservation_data:
                updates.append("id_hewan = %s")
                values.append(reservation_data['id_hewan'])
            if 'id_staf' in reservation_data:
                updates.append("id_staf = %s")
                values.append(reservation_data['id_staf'])
            if 'id_layanan' in reservation_data:
                updates.append("id_layanan = %s")
                values.append(reservation_data['id_layanan'])
            if 'reservasi_tgl_layanan' in reservation_data:
                updates.append("reservasi_tgl_layanan = %s")
                values.append(reservation_data['reservasi_tgl_layanan'])
            if 'reservasi_waktu_layanan' in reservation_data:
                updates.append("reservasi_waktu_layanan = %s")
                values.append(reservation_data['reservasi_waktu_layanan'])

            values.append(id_reservasi)
            update_query = f"UPDATE reservasi SET {', '.join(updates)} WHERE id_reservasi = %s"
            cur.execute(update_query, tuple(values))
            conn.commit()
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
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id_reservasi, h.nama_hewan, s.nama_staf, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan 
                FROM reservasi r 
                JOIN hewan h ON h.id_hewan = r.id_hewan 
                JOIN staf s ON s.id_staf = r.id_staf 
                JOIN layanan l ON l.id_layanan = r.id_layanan
            """)
            reservasi = cur.fetchall()
            cur.close()

            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(reservasi, headers=headers, tablefmt=f"{format_table}"))
            return reservasi

        # Fungsi utama untuk manajemen reservasi
        def main_reservasi():
            # Membuat koneksi ke database PostgreSQL
            conn, cur = postgresql_connect()
            if conn:
                while True:
                    # Membersihkan layar konsol
                    os.system('cls')
                    print("ADMIN>DASHBOARD>RESERVASI")
                    print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                    print("MENU RESERVASI :")
                    print("[1] Tambah Reservasi")
                    print("[2] Lihat Reservasi")
                    print("[3] Edit Reservasi")
                    print("[4] Hapus Reservasi\n")
                    print("[5] Exit")
                    choice = input("\nMasukkan Pilihan Menu : ")

                    if choice == '1':
                        os.system('cls')
                        print("ADMIN>DASHBOARD>RESERVASI>TAMBAH RESERVASI")
                        print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                        
                        # Menampilkan daftar hewan yang tersedia
                        animals, headers = list_animals(conn)
                        
                        print(tabulate.tabulate(animals, headers=headers, tablefmt=f"{format_table}"))

                        id_hewan = input("Masukkan ID Hewan: ")

                        id_staf = get_staff_id_by_username(conn, uname)

                        lihat_data_layanan(conn, cur)
                        id_layanan = input("Masukkan ID Layanan: ")

                        reservasi_tgl_layanan = input("Masukkan Tanggal Reservasi (YYYY-MM-DD): ")
                        reservasi_waktu_layanan = input("Masukkan Waktu Reservasi (HH:MM:SS): ")

                        reservation_data = {
                            'id_hewan': id_hewan,
                            'id_staf': id_staf,
                            'id_layanan': id_layanan,
                            'reservasi_tgl_layanan': reservasi_tgl_layanan,
                            'reservasi_waktu_layanan': reservasi_waktu_layanan
                        }

                        try:
                            make_reservation(conn, reservation_data)
                            print(f"\nReservasi berhasil.")
                        except:
                            print("\nPERHATIAN : Terjadi kesalahan pada data reservasi yang anda masukkan. Reservasi Gagal, silahkan coba lagi.")

                        input("\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '2':
                        os.system('cls')
                        print("ADMIN>DASHBOARD>RESERVASI>LIHAT RESERVASI")
                        print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                        # Melihat rincian reservasi
                        view_reservation(conn)
                        input("\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '3':
                        os.system('cls')
                        print("ADMIN>DASHBOARD>RESERVASI>EDIT RESERVASI")
                        print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                        
                        # Melihat rincian reservasi sebelum mengedit
                        view_reservation(conn)
                        id_reservasi = input("Masukkan ID Reservasi yang ingin diubah: ")
                        print("Masukkan data baru (biarkan kosong jika tidak ingin diubah):")
                        id_hewan = input("Masukkan ID Hewan baru: ")
                        id_staf = input("Masukkan ID staf baru: ")
                        reservasi_tgl_layanan = input("Masukkan Tanggal Reservasi Baru (YYYY-MM-DD): ")
                        reservasi_waktu_layanan = input("Masukkan Waktu Reservasi Baru (HH:MM:SS): ")

                        reservation_data = {}
                        if id_hewan:
                            reservation_data['id_hewan'] = id_hewan
                        if id_staf:
                            reservation_data['id_staf'] = id_staf
                        if reservasi_tgl_layanan:
                            reservation_data['reservasi_tgl_layanan'] = reservasi_tgl_layanan
                        if reservasi_waktu_layanan:
                            reservation_data['reservasi_waktu_layanan'] = reservasi_waktu_layanan
                        try:
                            edit_reservation(conn, id_reservasi, reservation_data)
                            print("\nData berhasil diedit")
                        except:
                            print("\nPERHATIAN : Terjadi kesalahan pada data reservasi yang anda masukkan. Data gagal diedit, silahkan coba lagi.")
                        input("\nTekan [enter] untuk kembali ke Menu Reservasi")
                        main_reservasi()

                    elif choice == '4':
                        os.system('cls')
                        print("ADMIN>DASHBOARD>RESERVASI>HAPUS RESERVASI")
                        print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                        # Melihat rincian reservasi sebelum menghapus
                        view_reservation(conn)
                        id_reservasi = input("Masukkan ID Reservasi yang ingin dihapus : ")
                        bener_hapus = input(f"[Y/N] Yakin untuk menghapus data '{id_reservasi}'? Tindakan tidak dapat diurungkan : ")
                        if bener_hapus.upper() == 'Y':
                            # Menghapus reservasi
                            try:
                                delete_reservation(conn, id_reservasi)
                                print("\nReservasi BERHASIL dihapus.")
                            except:
                                print("\nPERHATIAN : Terjadi kesalahan saat menghapus data. Data gagal dihapus.")
                        else:
                            print("\nReservasi BATAL dihapus")
                        input("\nTekan [enter] untuk kembali ke Menu Reservasi")
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

    # 4.2 TRANSAKSI v UI FIXED
    elif admin_choice == '2':
        def lihat_reservasi():
            conn, cur = postgresql_connect()
            cur.execute("""
                SELECT r.id_reservasi, h.nama_hewan, s.nama_staf, l.nama_layanan, r.reservasi_tgl_layanan, r.reservasi_waktu_layanan 
                FROM reservasi r 
                JOIN hewan h ON h.id_hewan = r.id_hewan 
                JOIN staf s ON s.id_staf = r.id_staf 
                JOIN layanan l ON l.id_layanan = r.id_layanan
            """)
            reservasi = cur.fetchall()
            postgresql_cls(conn, cur)

            headers = [i[0] for i in cur.description]
            print(tabulate.tabulate(reservasi, headers=headers, tablefmt=f"{format_table}"))
    
        def lihat_data_transaksi():
            conn, cur = postgresql_connect() # Membuat cursor untuk berinteraksi dengan database
           
            query = """
            select
                tr.id_transaksi as "Id Transaksi", tr.tgl_waktu_transaksi as "Tanggal Transaksi", r.reservasi_tgl_layanan as "Tanggal Reservasi", r.reservasi_waktu_layanan as "Waktu Reservasi", h.nama_hewan as "Nama Hewan", l.nama_layanan as "Nama Layanan",  l.harga_layanan as "Harga Layanan", s.nama_staf as "Nama Staf"
            from transaksi tr
            join reservasi r on tr.id_reservasi = r.id_reservasi
            join hewan h on h.id_hewan = r.id_hewan
            join layanan l on l.id_layanan = r.id_layanan
            join staf s on s.id_staf = r.id_staf
            """
           
            cur.execute(query)
            data_transaksi = cur.fetchall()

            postgresql_cls(conn, cur)
           
            # Headers untuk tabel yang akan ditampilkan
            headers = [i[0] for i in cur.description]
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_transaksi, headers=headers, tablefmt=f"{format_table}"))  

        def menu_transaksi(nama_lengkap_logged):
            os.system('cls')
            print("ADMIN>DASHBOARD>TRANSAKSI")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

            choice_2 = input("MENU TRANSAKSI :\n[1] Tambah Data Transaksi\n[2] Lihat Data Transaksi\n[3] Edit Data Transaksi\n[4] Hapus Data Transaksi\n\n[5] Kembali ke Dashboard\n\nPilih menu : ")
            
            if choice_2 == '1':   # tambah data transaksi
                os.system('cls')  
                print("ADMIN>DASHBOARD>TRANSAKSI>TAMBAH TRANSAKSI")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                lihat_reservasi()

                conn, cur = postgresql_connect()

                id_reservasi = input("Masukkan id reservasi: ")

                result = False  # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
                if not id_reservasi :
                    print("Semua field harus diisi!")
                    return False
                else:
                    try:
                        cur = conn.cursor()
                        query = f"""
                        INSERT INTO transaksi (tgl_waktu_transaksi, id_reservasi)
                        VALUES (now(), {id_reservasi})
                        """
                        cur.execute(query) # Menjalankan query dengan data yang diberikan
                        conn.commit() # Melakukan commit perubahan ke database
                        boolean = cur.rowcount # Mengambil jumlah baris yang dimodifikasi oleh query
                        
                        cur.close()  # Menutup cursor
                        print("Transaksi baru telah ditambahkan!")
                        print('Tambah data berhasil')
                    except psycopg2.IntegrityError:
                        print("\nPERHATIAN : Data sudah ada")
                    except:
                        print('\nPERHATIAN : Terjadi kesalahan. Tambah data gagal')
                    input("\nTekan [Enter] untuk kembali ke Menu Transaksi")
                    
                menu_transaksi(nama_lengkap_logged)

            elif choice_2 == '2':   # Lihat data transaksi
                os.system('cls')
                print("ADMIN>DASHBOARD>TRANSAKSI>LIHAT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                lihat_data_transaksi()

                input("\nTekan [enter] untuk kembali ke Menu Transaksi")
                menu_transaksi(nama_lengkap_logged)

            elif choice_2 == '3':   # Edit data transaksi
                os.system('cls') 
                print("ADMIN>DASHBOARD>TRANSAKSI>EDIT TRANSAKSI")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                lihat_data_transaksi()
                id_transaksi = input("Masukkan ID transaksi yang ingin diubah: ") # Meminta ID transaksi yang ingin diubah
                if id_transaksi == '':
                    menu_transaksi(nama_lengkap_logged)
                conn, cur = postgresql_connect()

                try:
                    cur.execute("SELECT COUNT(*) FROM transaksi WHERE id_transaksi = %s", (id_transaksi,)) # Mengecek apakah ID transaksi ada dalam database
                    if cur.fetchone()[0] == 0:
                        print("Maaf, ID pelanggan yang Anda cari tidak ada. Silakan cek kembali.")
                        postgresql_cls(conn, cur)
                        input("\nTekan [enter] untuk kembali ke Menu Transaksi")
                        menu_transaksi(nama_lengkap_logged)
                        return
                
                    tgl_waktu_transaksi_baru  = input("Masukkan tanggal waktu transaksi baru : ")
                    id_reservasi_baru         = input("Masukkan id reservasi baru : ")
                        
                    updates = [] # List untuk menyimpan bagian query yang akan diupdate
                    values = []  # List untuk menyimpan nilai yang akan diisi dalam query

                    if tgl_waktu_transaksi_baru : 
                        updates.append("tgl_waktu_transaksi = %s")
                        values.append(tgl_waktu_transaksi_baru)

                    if id_reservasi_baru:
                        updates.append("id_reservasi = %s")
                        values.append(id_reservasi_baru)

                    values.append(id_transaksi) # Menambahkan id_transaksi ke values, ini diperlukan untuk klausa WHERE

                    if updates: # Jika ada data yang diupdate
                        query = f"UPDATE transaksi SET {', '.join(updates)} WHERE id_transaksi = %s"
                        try:
                            cur.execute(query, values)
                            conn.commit()
                            print("Data transaksi telah diubah!")
                        except psycopg2.Error as e:
                            print("Gagal mengubah data transaksi:", e)
                            conn.rollback()
                    else:
                        print("Tidak ada data yang diubah.")
                except psycopg2.Error as e:
                    print(f"Terjadi kesalahan: {e}")
                    conn.rollback()
                finally:
                    cur.close()
                    conn.close()
                input("\nTekan [enter] untuk kembali ke Menu Transaksi")
                menu_transaksi(nama_lengkap_logged)

            elif choice_2 == '4':   # Hapus data transaksi
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows) 
                print("ADMIN>DASHBOARD>TRANSAKSI>HAPUS TRANSAKSI")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                lihat_data_transaksi()
                id_transaksi = input("Masukkan ID transaksi yang ingin dihapus: ")
                if id_transaksi == '':
                    menu_transaksi(nama_lengkap_logged)
                konfirmasi_hapus = input(f"[Y/N] Apakah anda yakin untuk menghapus data ID '{id_transaksi}'? Tindakan tidak dapat diurungkan : ")
                if konfirmasi_hapus.upper() == 'Y':
                    conn, cur = postgresql_connect()
                    try:
                        cur.execute("SELECT * FROM transaksi WHERE id_transaksi = %s", (id_transaksi,))
                        if cur.fetchone() is None:
                            print("transaksi dengan ID tersebut tidak ditemukan.")
                        else:
                            cur.execute("DELETE FROM transaksi WHERE id_transaksi = %s", (id_transaksi,))
                            conn.commit()
                            if cur.rowcount > 0:
                                print("Data transaksi telah dihapus!")
                            else:
                                print("Gagal menghapus data transaksi.")
                    except Exception as e:
                        print(f"Terjadi kesalahan: {e}")
                        conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                    finally:
                        cur.close()  # Menutup kursor
                        conn.close()  # Menutup koneksi
                else :
                    print("Data batal dihapus")
                input("\nTekan [Enter] untuk kembai ke Menu Transaksi : ")
                menu_transaksi(nama_lengkap_logged)
            
            elif choice_2 == '5':
                mode_admin(uname, nama_lengkap_logged)
        
            else:
                menu_transaksi(nama_lengkap_logged)

        menu_transaksi(nama_lengkap_logged)

    # 4.3 DATA REKAM MEDIS v UI FIXED
    elif admin_choice == '3': 
        def wrap_text(text, width):
            return "\n".join(textwrap.wrap(text, width))
        
        def menu_rekammedis(nama_lengkap_logged):
            os.system('cls')
            print("ADMIN>DASHBOARD>REKAM MEDIS")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            print("MENU DATA REKAM MEDIS : ")
            print("[1] Cari Berdasarkan TANGGAL")
            print("[2] Cari Berdasarkan JENIS HEWAN")
            print("[3] Cari Berdasarkan ID HEWAN")
            print("[4] Cari Berdasarkan ID DOKTER\n")
            print("[5] Kembali ke Dashboard\n")
            inputmenu = input('Silahkan Pilih Menu Rekam Medis : ')
            conn, cur = postgresql_connect()

            if inputmenu == '1':
                os.system('cls')
                print("ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN TANGGAL")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                tanggal = input('\nMasukan Tanggal Reservasi yang Ingin Dicari! : ')

                os.system('cls')
                print(f"ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN TANGGAL>TANGGAL:{tanggal}")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                cur.execute(f"select r.id_rekamed, r.tgl_waktu_pemeriksaan, h.nama_hewan, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) where TO_CHAR(tgl_waktu_pemeriksaan :: DATE, 'yyyy-mm-dd') = TO_CHAR(tgl_waktu_pemeriksaan :: DATE, '{tanggal}')")
                datarekammedis = cur.fetchall()
                
                headers = [i[0] for i in cur.description]

                wrapped_datarekammedis = []
                for row in datarekammedis:
                    wrapped_row = list(row)
                    wrapped_row[-2] = wrap_text(wrapped_row[-2], textwraplen)  # Wrap 'hasil_medis'
                    wrapped_row[-1] = wrap_text(wrapped_row[-1], textwraplen)  # Wrap 'catatan_tambahan'
                    wrapped_datarekammedis.append(wrapped_row)

                print(tabulate.tabulate(wrapped_datarekammedis, headers=headers, tablefmt=f"{format_table}"))
                postgresql_cls(conn, cur)

                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")  
                menu_rekammedis(nama_lengkap_logged)

            elif inputmenu == '2':
                #MENAMPILKAN RINCIAN JENIS HEWAN
                os.system('cls')
                print("ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN JENIS HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                cur.execute("SELECT * FROM jenis_hewan")
                datajenishewan = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datajenishewan, headers=headers, tablefmt=f"{format_table}"))

                jenishewan = input('Masukan ID Jenis Hewan yang Ingin Dicari! : ')
                if jenishewan  == '':
                    menu_rekammedis(nama_lengkap_logged)
                
                # memunculkan data berdasarkan parameter
                os.system('cls')
                print(f"ADMIN>DASHBOARD>REKAM MEDIS> CARI BERDASARKAN JENIS HEWAN>ID:{jenishewan}")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                cur.execute(f"select r.id_rekamed, jh.nama_jenis, h.nama_hewan, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.tgl_waktu_pemeriksaan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where jh.id_jenishewan = {jenishewan}")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]

                wrapped_datarekammedis = []
                for row in datarekammedis:
                    wrapped_row = list(row)
                    wrapped_row[-2] = wrap_text(wrapped_row[-2], textwraplen)  # Wrap 'hasil_medis'
                    wrapped_row[-1] = wrap_text(wrapped_row[-1], textwraplen)  # Wrap 'catatan_tambahan'
                    wrapped_datarekammedis.append(wrapped_row)
                print(tabulate.tabulate(wrapped_datarekammedis, headers=headers, tablefmt=f"{format_table}"))
        
                postgresql_cls(conn, cur)

                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")
                menu_rekammedis(nama_lengkap_logged)

            elif inputmenu == '3':
                #MENAMPILKAN RINCIAN AWAL
                os.system('cls')
                print("ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN ID HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                cur.execute(f"SELECT h.id_hewan, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan FROM hewan h JOIN jenis_hewan jh ON (h.id_jenishewan = jh.id_jenishewan) JOIN pelanggan p ON (h.id_pelanggan = p.id_pelanggan)")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))

                #MENAMPILKAN RINCIAN IDHEWAN

                idhewan = input('Masukan Id Hewan pada Rekam Medis yang Ingin Dicari! : ')

                if idhewan  == '':
                    menu_rekammedis(nama_lengkap_logged)

                os.system('cls')
                print(f"ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN ID HEWAN>ID:{idhewan}")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                cur.execute(f'select r.id_rekamed,h.id_hewan, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, d.nama_dokter, l.nama_layanan, r.tgl_waktu_pemeriksaan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where h.id_hewan = {idhewan}')
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]

                wrapped_datarekammedis = []
                for row in datarekammedis:
                    wrapped_row = list(row)
                    wrapped_row[-2] = wrap_text(wrapped_row[-2], textwraplen)  # Wrap 'hasil_medis'
                    wrapped_row[-1] = wrap_text(wrapped_row[-1], textwraplen)  # Wrap 'catatan_tambahan'
                    wrapped_datarekammedis.append(wrapped_row)
                print(tabulate.tabulate(wrapped_datarekammedis, headers=headers, tablefmt=f"{format_table}"))
        
                postgresql_cls(conn, cur)
                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")
                menu_rekammedis(nama_lengkap_logged)

            elif inputmenu == '4':
                #MENAMPILKAN RINCIAN AWAL  
                os.system('cls')
                print("ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN ID DOKTER")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                cur.execute(f"SELECT id_dokter, nama_dokter, tlp_dokter, no_str FROM dokter")
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate.tabulate(datarekammedis, headers=headers, tablefmt=f"{format_table}"))

                #MENAMPILKAN RINCIAN IDDOKTER

                iddokter = input('Masukan Id Dokter pada Rekam Medis yang Ingin Dicari! : ')
                if iddokter  == '':
                    menu_rekammedis(nama_lengkap_logged)

                os.system('cls')
                print(f"ADMIN>DASHBOARD>REKAM MEDIS>CARI BERDASARKAN ID DOKTER>ID:{iddokter}")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                cur.execute(f'select r.id_rekamed, d.id_dokter, h.nama_hewan, jh.nama_jenis, p.nama_pelanggan, l.nama_layanan, r.tgl_waktu_pemeriksaan, r.hasil_medis, r.catatan_tambahan from rekam_medis r join hewan h on (h.id_hewan = r.id_hewan) join pelanggan p on (p.id_pelanggan = h.id_pelanggan) join dokter d on (d.id_dokter = r.id_dokter) join layanan l on (l.id_layanan = r.id_layanan) join jenis_hewan jh on (jh.id_jenishewan = h.id_jenishewan) where d.id_dokter = {iddokter}')
                datarekammedis = cur.fetchall()
                headers = [i[0] for i in cur.description]

                wrapped_datarekammedis = []
                for row in datarekammedis:
                    wrapped_row = list(row)
                    wrapped_row[-2] = wrap_text(wrapped_row[-2], textwraplen)  # Wrap 'hasil_medis'
                    wrapped_row[-1] = wrap_text(wrapped_row[-1], textwraplen)  # Wrap 'catatan_tambahan'
                    wrapped_datarekammedis.append(wrapped_row)
                print(tabulate.tabulate(wrapped_datarekammedis, headers=headers, tablefmt=f"{format_table}"))
        
                postgresql_cls(conn, cur)

                input("Tekan [Enter] untuk kembali ke menu REKAM MEDIS : ")
                menu_rekammedis(nama_lengkap_logged)

            elif inputmenu == '5':
                mode_admin(uname, nama_lengkap_logged)
            else:
                menu_rekammedis(nama_lengkap_logged)

        menu_rekammedis(nama_lengkap_logged)

    # 4.4 DATA KUSTOMER v UI FIXED
    elif admin_choice == '4':
        def lihat_data_pelanggan():
            conn, cur = postgresql_connect()
            """Menampilkan data pelanggan dari database."""
            # Membuat cursor untuk berinteraksi dengan database
           
            query = """
            SELECT * FROM pelanggan order by id_pelanggan asc
            """
           
            cur.execute(query)
            # Mengambil semua data hasil query
            data_pelanggan = cur.fetchall()


            postgresql_cls(conn, cur)
           
            # Headers untuk tabel yang akan ditampilkan
            headers = [i[0] for i in cur.description]
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_pelanggan, headers=headers, tablefmt=f"{format_table}"))  

        def data_customer(nama_lengkap_logged):
            os.system('cls')
            print("ADMIN>DASHBOARD>DATA PELANGGAN")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            choice_4 = input("MENU DATA PELANGGAN :\n[1] Tambah Data pelanggan\n[2] Lihat Data pelanggan\n[3] Edit Data pelanggan\n[4] Hapus Data pelanggan\n\n[5] Kembali ke DASHBOARD\n\nPilih menu : ")
            
            if choice_4 == '1':    
                os.system('cls')  
                print("ADMIN>DASHBOARD>DATA KUSTOMER>TAMBAH DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                #Input Data pelanggan
                conn, cur = postgresql_connect()
                nama_pelanggan     = input("Masukkan nama pelanggan        : ")
                tlp_pelanggan      = input("Masukkan no. telepon pelanggan : ")
                uname_pelanggan    = input("Masukkan username pelanggan    : ")
                pw_pelanggan       = input("Masukkan password pelanggan    : ")

                # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
                result = False
                if not nama_pelanggan or not tlp_pelanggan or not uname_pelanggan or not pw_pelanggan:
                    print("\nPERHATIAN : Semua field harus diisi! silahkan coba lagi")
                     
                else:
                    try:
                        """Menambahkan data pelanggan baru ke database."""
                        cur = conn.cursor()
                    
                        query = """
                        INSERT INTO pelanggan (nama_pelanggan, tlp_pelanggan, uname_pelanggan, pw_pelanggan)
                        VALUES (%s, %s, %s, %s)
                        """
                    
                        # Menjalankan query dengan data yang diberikan
                        cur.execute(query, (nama_pelanggan, tlp_pelanggan, uname_pelanggan, pw_pelanggan))
                    
                        # Melakukan commit perubahan ke database
                        conn.commit()
                    
                        # Mengambil jumlah baris yang dimodifikasi oleh query
                        boolean = cur.rowcount
                    
                        # Menutup cursor
                        cur.close()
                    
                        print("\nPelanggan baru telah ditambahkan! Tambah data berhasil")
                    except:
                        input('\nPERHATIAN : Terdapat kesalahan! Tambah data gagal')
                    
                input("\nTekan [Enter] untuk kembali ke Menu Pelanggan : ")
                data_customer(nama_lengkap_logged)

            elif choice_4 == '2':   # Lihat data pelanggan 
                os.system('cls')
                print("ADMIN>DASHBOARD>DATA PELANGGAN>LIHAT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                lihat_data_pelanggan()
                input("\nTekan [enter] untuk kembali ke Menu Data Pelanggan")
                data_customer(nama_lengkap_logged)

            elif choice_4 == '3':   # Edit data pelanggan 
                os.system('cls')
                print("ADMIN>DASHBOARD>DATA PELANGGAN>EDIT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                # Meminta ID pelanggan yang ingin diubah
                lihat_data_pelanggan()
                id_pelanggan = (input("Masukkan ID pelanggan yang ingin diubah: "))

                if id_pelanggan == '':
                    data_customer(nama_lengkap_logged)
            
                conn, cur = postgresql_connect()
            
                try:
                    # Mengecek apakah ID pelanggan ada dalam database
                    cur.execute("SELECT COUNT(*) FROM pelanggan WHERE id_pelanggan = %s", (id_pelanggan,))
                    if cur.fetchone()[0] == 0:
                        print("\nMaaf, ID pelanggan yang Anda cari tidak ada. Silakan cek kembali.")
                        postgresql_cls(conn, cur)
                        input("\nTekan [enter] untuk kembali ke Menu Data Pelanggan")
                        data_customer(nama_lengkap_logged)
                
                    # Meminta data baru dari user
                    nama_baru = input("\nMasukkan nama baru pelanggan (kosongkan jika tidak ingin mengubah): ")
                    telp_baru = input("Masukkan nomor telepon baru pelanggan (kosongkan jika tidak ingin mengubah): ")
                    uname_baru = input("Masukkan username baru pelanggan (kosongkan jika tidak ingin mengubah): ")
                    password_baru = input("Masukkan password baru pelanggan (kosongkan jika tidak ingin mengubah): ")

                    # List untuk menyimpan bagian query yang akan diupdate
                    updates = []
                
                    # List untuk menyimpan nilai yang akan diisi dalam query
                    values = []

                    # Mengecek apakah ada nilai baru untuk nama_pelanggan dan menambahkannya ke query jika ada
                    if nama_baru:
                        updates.append("nama_pelanggan = %s")
                        values.append(nama_baru)
                
                    # Mengecek apakah ada nilai baru untuk tlp_pelanggan dan menambahkannya ke query jika ada
                    if telp_baru:
                        updates.append("tlp_pelanggan = %s")
                        values.append(telp_baru)
                
                    # Mengecek apakah ada nilai baru untuk uname_pelanggan dan menambahkannya ke query jika ada
                    if uname_baru:
                        updates.append("uname_pelanggan = %s")
                        values.append(uname_baru)
                
                    # Mengecek apakah ada nilai baru untuk pw_pelanggan dan menambahkannya ke query jika ada
                    if password_baru:
                        updates.append("pw_pelanggan = %s")
                        values.append(password_baru)

                    # Menambahkan id_pelanggan ke values, ini diperlukan untuk klausa WHERE
                    values.append(id_pelanggan)

                    # Jika ada data yang diupdate
                    if updates:
                        # Membuat query update dengan bagian yang perlu diupdate
                        query = f"UPDATE pelanggan SET {', '.join(updates)} WHERE id_pelanggan = %s"
                        try:
                            # Menjalankan query dengan nilai yang disediakan
                            cur.execute(query, values)
                        
                            # Melakukan commit perubahan ke database
                            conn.commit()
                        
                            print("\nData pelanggan telah diubah!")
                        except psycopg2.Error as e:
                            # Menampilkan pesan kesalahan jika gagal melakukan update
                            print("\nGagal mengubah data pelanggan:", e)
                        
                            # Melakukan rollback jika terjadi kesalahan
                            conn.rollback()
                    else:
                        # Pesan jika tidak ada data yang diubah
                        print("\nTidak ada data yang diubah.")
                except psycopg2.Error as e:
                    # Menangani kesalahan koneksi atau query
                    print(f"\nTerjadi kesalahan: {e}")
                    conn.rollback()
                finally:
                    # Menutup kursor dan koneksi
                    cur.close()
                    conn.close()
                
                input("\nTekan [enter] untuk kembali ke Menu Data Pelanggan")
                data_customer(nama_lengkap_logged)
            
            elif choice_4 == '4':   # Hapus data pelanggan 
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA PELANGGAN>HAPUS TRANSAKSI")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                lihat_data_pelanggan()

                id_pelanggan = (input("Masukkan ID pelanggan yang ingin dihapus: "))

                if id_pelanggan == '':
                    data_customer(nama_lengkap_logged) 
                
                konfirmasi = input(f"\n[Y/N] apakah anda yain untuk menghapus data dengan ID '{id_pelanggan}'? Tindakan tidak dapat diurungkan : ")
                if konfirmasi.upper() == 'Y':

                    """Menghapus data pelanggan dari database."""

                    conn, cur = postgresql_connect()
                
                    try:
                        # Memeriksa apakah ada reservasi yang terkait dengan pelanggan ini
                        cur.execute("SELECT COUNT(*) FROM hewan WHERE id_pelanggan = %s", (id_pelanggan,))
                        count_hewan = cur.fetchone()[0]

                        # Jika ada referensi terkait, hapus referensi tersebut terlebih dahulu
                        if count_hewan > 0:
                            cur.execute("DELETE FROM hewan WHERE id_pelanggan = %s", (id_pelanggan,))
                
                        # Menghapus data pelanggan dari tabel pelanggan
                        cur.execute("DELETE FROM pelanggan WHERE id_pelanggan = %s", (id_pelanggan,))
                    
                        # Melakukan commit perubahan ke database
                        conn.commit()
                    
                        # Memeriksa apakah ada baris yang dihapus
                        if cur.rowcount > 0:
                            print("\nData pelanggan telah dihapus!")
                        else:
                            print("\nPERHATIAN : Pelanggan dengan ID tersebut tidak ditemukan.")
                    except Exception as e:
                        print(f"\nPERHATIAN : Terjadi kesalahan: {e}\nData gagal dihapus")
                        conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                    finally:
                        cur.close()  # Menutup kursor
                        conn.close()  # Menutup koneksi
                
                    input("\nTekan [enter] untuk kembali ke Menu pelanggan")
                
                else:
                    input("\nData batal dihapus, tekan [Enter] untuk kembali ke Menu Data Pelanggan")
                data_customer(nama_lengkap_logged)

            elif choice_4 == '5':
                mode_admin(uname, nama_lengkap_logged)

            else:
                data_customer(nama_lengkap_logged)

        data_customer(nama_lengkap_logged)

    # 4.5 DATA HEWAN PELIHARAAN v UI FIXED
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
            ORDER BY hew.id_hewan ASC
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
            ORDER BY id_jenishewan
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

        def menu_hewan_peliharaan(nama_lengkap_logged):
            os.system('cls')
            print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                
            choice_5 = input("MENU DATA HEWAN :\n[1] Tambah Data Hewan Peliharaan\n[2] Edit Data Hewan Peliharaan\n[3] Lihat Data Hewan Peliharaan\n[4] Hapus Data Hewan Peliharaan\n    \n[5] Tambah Data Jenis Hewan\n[6] Edit Data Jenis hewan\n[7] Lihat Jenis Hewan\n[8] Hapus Data Jenis hewan\n\n[9] Kembali ke Menu Admin\n\nPilih menu : ")
            if choice_5 == '1': #FITUR TAMBAH DATA HEWAN PELIHARAAN
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>TAMBAH DATA HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                # Meminta data hewan baru dari user
                conn, cur = postgresql_connect()
                nama_hewan     = input("Masukkan nama hewan     : ")
                tanggal_lahir  = input("Masukkan tanggal lahir  : ")
                id_pelanggan   = input("Masukkan id pelanggan   : ")
                id_jenishewan  = input("Masukkan id jenis hewan : ")

                # Menambah hewan baru ke database
                # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
                if not nama_hewan or not tanggal_lahir or not id_pelanggan or not id_jenishewan:
                    print("\nPERHATIAN : Semua data harus diisi! Batal menambahkan data...")
                else:
                    try:
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
                    
                        print("\nHewan baru BERHASIL ditambahkan!")
                    except psycopg2.Error as e:
                        print("\nPERHATIAN : Terdapat kesalahan pada data yang anda masukkan! Data hewan GAGAL ditambahkan")

                input("\nTekan [Enter] untuk kembali ke menu Hewan : ")
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '5':  # FITUR TAMBAH DATA JENIS HEWAN
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>TAMBAH DATA JENIS HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                # Meminta data hewan baru dari user
                conn, cur = postgresql_connect()
                nama_jenis = input("Masukkan nama_jenis : ")

                # Menambah hewan baru ke database
                # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
                if not nama_jenis:
                    print("PERHATIAN : Nama jenis hewan tidak boleh kosong.")
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
                            print("\nJenis hewan baru telah ditambahkan! Tambah data berhasil")
                        else:
                            print("\nPERHATIAN : Tambah data gagal!")
                    except Exception as e:
                        print(f"PERHATIAN : Terjadi kesalahan: {e}")
                        conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                    finally:
                        cur.close()  # Menutup kursor
                        conn.close()  # Menutup koneksi

                input('\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan')
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '3': #FITUR LIHAT DATA HEWAN
                os.system('cls')
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>LIHAT DATA HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                lihat_data_hewan()
                input("\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '7': #FITUR LIHAT DATA JENIS HEWAN
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>LIHAT DATA JENIS HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                lihat_data_jenishewan()
                input("\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '2': #FITUR EDIT DATA HEWAN
                os.system('cls')
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>EDIT DATA HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                # Meminta ID hewan yang ingin diubah
                lihat_data_hewan()
                id_hewan = input("Masukkan ID hewan yang ingin diubah: ")

                if not id_hewan:
                    menu_hewan_peliharaan(nama_lengkap_logged)
            
                conn, cur = postgresql_connect()
            
                try:
                    # Mengecek apakah ID hewan ada dalam database
                    cur.execute("SELECT COUNT(*) FROM hewan WHERE id_hewan = %s", (id_hewan,))
                    if cur.fetchone()[0] == 0:
                        print("\nMaaf, ID hewan yang Anda cari tidak ada. Silakan cek kembali.")
                        postgresql_cls(conn, cur)
                        input("\nTekan [enter] untuk kembali ke menu hewan peliharaan")
                        menu_hewan_peliharaan(nama_lengkap_logged)
                
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
                        cur.execute(query, values)
                        conn.commit()
                        print("Data hewan telah diubah!")
                        
                    else:
                        # Pesan jika tidak ada data yang diubah
                        print("Tidak ada data yang diubah.")
                except psycopg2.Error as e:
                    # Menangani kesalahan koneksi atau query
                    print(f"\nPERHATIAN : Terjadi kesalahan pada data yang anda masukkan")
                    conn.rollback()
                finally:
                    # Menutup kursor dan koneksi
                    cur.close()
                    conn.close()
                
                input("\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '6': #FITUR EDIT DATA JENIS HEWAN
                os.system('cls')
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>EDIT DATA JENIS HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                # Meminta ID jenis hewan yang ingin diubah
                lihat_data_jenishewan()
                id_jenishewan = input("Masukkan ID jenis hewan yang ingin diubah: ")

                if not id_jenishewan:
                    menu_hewan_peliharaan(nama_lengkap_logged)
            
                conn, cur = postgresql_connect()
            
                try:
                    # Mengecek apakah ID jenis hewan ada dalam database
                    cur.execute("SELECT COUNT(*) FROM jenis_hewan WHERE id_jenishewan = %s", (id_jenishewan,))
                    if cur.fetchone()[0] == 0:
                        print("\nPERHATIAN : ID jenis hewan yang Anda cari tidak ada. Silakan cek kembali.")
                        postgresql_cls(conn, cur)
                        input("\nTekan [enter] untuk kembali ke menu hewan peliharaan")
                        mode_admin(uname, nama_lengkap_logged)
                
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
                        
                            print("\nData jenis hewan telah diubah!")
                        except psycopg2.Error as e:
                            # Menampilkan pesan kesalahan jika gagal melakukan update
                            print("PERHATIAN : Gagal mengubah data jenis hewan:", e)
                        
                            # Melakukan rollback jika terjadi kesalahan
                            conn.rollback()
                    else:
                        # Pesan jika tidak ada data yang diubah
                        print("\nTidak ada data yang diubah")
                except psycopg2.Error as e:
                    # Menangani kesalahan koneksi atau query
                    print(f"\nPERHATIAN : Terjadi kesalahan: {e}")
                    conn.rollback()
                finally:
                    # Menutup kursor dan koneksi
                    cur.close()
                    conn.close()
                
                input("\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
                menu_hewan_peliharaan(nama_lengkap_logged)
            
            elif choice_5 == '4': #FITUR HAPUS DATA HEWAN
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>HAPUS DATA HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                lihat_data_hewan()

                id_hewan = (input("Masukkan ID hewan yang ingin dihapus: "))

                if id_hewan == '':
                    menu_hewan_peliharaan(nama_lengkap_logged)
                    
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
                            konfirmasi_hapus = input(f"[Y/N] Apakah anda yakin untuk menghapus data '{id_hewan}'? TIndakan tidak dapat diurungkan : ")
                            if konfirmasi_hapus.upper() == 'Y':
                                # Menghapus data hewan dari tabel hewan
                                cur.execute("DELETE FROM hewan WHERE id_hewan = %s", (id_hewan,))
                            
                                # Melakukan commit perubahan ke database
                                conn.commit()
                            
                                if cur.rowcount > 0:
                                    print("\nData hewan BERHASIL dihapus!")
                                else:
                                    print("\nPERHATIAN : Hewan dengan ID tersebut tidak ditemukan.")
                            else:
                                print("Data batal dihapus")
                        else:
                            print("\nPERHATIAN : Hewan ini masih terkait dengan rekam medis atau reservasi. Tidak bisa dihapus.")
                    else:
                        print("\nPERHATIAN : Hewan dengan ID tersebut tidak ditemukan!")
                except Exception as e:
                    print(f"\nTerjadi kesalahan pada masukan yang anda masukkan")
                    conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                finally:
                    cur.close()  # Menutup kursor
                    conn.close()  # Menutup koneksi
            
                input("\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '8': #FITUR HAPUS DATA JENIS HEWAN
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA HEWAN PELIHARAAN>HAPUS DATA JENIS HEWAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
           
                lihat_data_jenishewan()

                id_jenishewan = input("Masukkan ID jenis hewan yang ingin dihapus: ")

                if not id_jenishewan :
                    menu_hewan_peliharaan(nama_lengkap_logged)
                konfirmsai_hapus = input(f"[Y/N] Apakah anda yakin untuk menghapus ID'{id_jenishewan}'? Tindakan tidak dapat diurungkan : ")
                if konfirmsai_hapus.upper() == 'Y':
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
                                    print("\nData jenis hewan telah dihapus!")
                                else:
                                    print("\nPERHATIAN : Jenis hewan dengan ID tersebut tidak ditemukan.")
                            else:
                                print("\nPERHATIAN : Jenis hewan ini MASIH terkait dengan hewan. Tidak bisa dihapus.")
                        else:
                            print("\nPERHATIAN : Jenis hewan dengan ID tersebut tidak ditemukan.")
                    except Exception as e:
                        print(f"Terjadi kesalahan: {e}")
                        conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                    finally:
                        cur.close()  # Menutup kursor
                        conn.close()  # Menutup koneksi

                else:
                    print("\nData batal dihapus")
            
                input("\nTekan [enter] untuk kembali ke Menu Hewan Peliharaan")
                menu_hewan_peliharaan(nama_lengkap_logged)

            elif choice_5 == '9':
                mode_admin(uname, nama_lengkap_logged)
            menu_hewan_peliharaan(nama_lengkap_logged)
        
        menu_hewan_peliharaan(nama_lengkap_logged)

    # 4.6 DATA DOKTER v UI FIXED
    elif admin_choice == '6':
        def lihat_data_dokter():
            conn, cur = postgresql_connect()
            """Menampilkan data dokter dari database."""
            # Membuat cursor untuk berinteraksi dengan database
            
            # Query SQL untuk mengambil semua data dari tabel dokter
            query = """
            SELECT *
            FROM dokter ORDER BY id_dokter
            """
            
            # Menjalankan query
            cur.execute(query)
            
            # Mengambil semua data hasil query
            data_dokter = cur.fetchall()
            
            # Menutup cursor
            postgresql_cls(conn, cur)
            
            # Headers untuk tabel yang akan ditampilkan
            headers = [i[0] for i in cur.description]
            
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_dokter, headers=headers, tablefmt=f"{format_table}"))  

        def menu_data_dokter(nama_lengkap_logged):
            os.system('cls')
            print("ADMIN>DASHBOARD>DATA DOKTER")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
            choice_4 = input("MENU DATA DOKTER :\n[1] Tambah Data\n[2] Lihat Data\n[3] Edit Data\n[4] Hapus Data\n\n[5] Kembali ke Dashboard\n\nPilih menu : ")

            if choice_4 == '1':     # Tambah data dokter v
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA DOKTER>TAMBAH DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                # Meminta data dokter baru dari user
                conn, cur = postgresql_connect()
                nama_dokter     = input("Masukkan nama dokter                  : ")
                tlp_dokter      = input("Masukkan no. telepon dokter           : ")
                no_str          = input("Masukkan no. Surat Izin Praktik (SIP) : ")
                uname_dokter    = input("Masukkan username dokter              : ")
                pw_dokter       = input("Masukkan password dokter              : ")
                # Menambah dokter baru ke database
                # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
                result = False
                if not nama_dokter or not tlp_dokter or not no_str or not uname_dokter or not pw_dokter:
                    print("\nPERHATIAN : Semua field harus diisi!")
                else:
                    try:
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
                        
                        print("\nDokter baru BERHASIL ditambahkan!")
                    except:
                        print("\nPERHATIAN : Terjadi kesalahan pada masukan anda. Data gagal ditambahkan")
                input("\nTekan [Enter] Untuk kembali ke Menu Dokter : ")
                menu_data_dokter(nama_lengkap_logged)

            elif choice_4 == '2':   # Lihat data dokter v
                os.system('cls')
                print("ADMIN>DASHBOARD>DATA DOKTER>LIHAT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
                lihat_data_dokter()
                input("\nTekan [enter] untuk kembali ke Menu Data Dokter")
                menu_data_dokter(nama_lengkap_logged)

            elif choice_4 == '3':   # Edit data dokter v
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA DOKTER>EDIT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                lihat_data_dokter()

                # Meminta ID dokter yang ingin diubah
                id_dokter = (input("\nMasukkan ID dokter yang ingin diubah : "))
                if id_dokter == '':
                    menu_data_dokter(nama_lengkap_logged)
                # Meminta data baru dari user
                nama_baru     = input("\nMasukkan nama baru dokter (kosongkan jika tidak ingin mengubah)   : ")
                telp_baru     = input("Masukkan nomor telepon baru (kosongkan jika tidak ingin mengubah) : ")
                no_str_baru   = input("Masukkan nomor SIP baru (kosongkan jika tidak ingin mengubah)     : ")
                uname_baru    = input("Masukkan username baru (kosongkan jika tidak ingin mengubah)      : ")
                password_baru = input("Masukkan password baru (kosongkan jika tidak ingin mengubah)      : ")
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
                        print("\nData dokter telah diubah!")
                    except psycopg2.Error as e:
                        # Menampilkan pesan kesalahan jika gagal melakukan update
                        print("\nPERHATIAN : Terdapat kesalahan pada data yang anda masukkan. Data gagal diubah")
                        
                        # Melakukan rollback jika terjadi kesalahan
                        conn.rollback()
                else:
                    # Pesan jika tidak ada data yang diubah
                    print("\nTidak ada data yang diubah.")
                postgresql_cls(conn, cur)
                input("\nTekan [enter] untuk kembali ke Menu Data Dokter")
                menu_data_dokter(nama_lengkap_logged)

            elif choice_4 == '4':   # Hapus data dokter v
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>DATA DOKTER>HAPUS DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")

                lihat_data_dokter()
                # Meminta ID dokter yang ingin dihapus
                id_dokter = (input("\nMasukkan ID dokter yang ingin dihapus : "))
                if id_dokter == '':
                    menu_data_dokter(nama_lengkap_logged)
                
                konfirmasi_hapus = input(f"[Y/N] Apakah anda yakin menghapus data '{id_dokter}'? Tindakan tidak dapat diurungkan : ")
                if konfirmasi_hapus.upper() == 'Y' : 
                    # Menghapus dokter dari database
                    """Menghapus data dokter dari database."""
                    # Membuat cursor untuk berinteraksi dengan database
                    conn, cur = postgresql_connect()
                    
                    # Memeriksa apakah ada rekam medis yang terkait dengan dokter ini
                    cur.execute("SELECT COUNT(*) FROM rekam_medis WHERE id_dokter = %s", (id_dokter,))
                    count = cur.fetchone()[0]

                    # Jika ada rekam medis terkait, dokter tidak dapat dihapus
                    if count > 0:
                        print("\nPERHATIAN : Tidak dapat menghapus dokter karena masih ada rekam medis yang terkait.")
                    else:
                        try:
                        # Menghapus data dokter dari tabel dokter
                            cur.execute("DELETE FROM dokter WHERE id_dokter = %s", (id_dokter,))
                            
                            # Melakukan commit perubahan ke database
                            conn.commit()
                            
                            # Memeriksa apakah ada baris yang dihapus
                            if cur.rowcount > 0:
                                print("\nData dokter telah dihapus!")
                                cur.close()
                            else:
                                print("\nPERHATIAN : Dokter dengan ID tersebut tidak ditemukan.")
                                cur.close()
                        except:
                            print("\nPERHATIAN : Terjadi kesalahan saat menghapus data. Data gagal dihapus")
                else:
                    print("Data batal dihapus.")

                input("\nTekan [Enter] untuk kembali ke Menu Data Dokter")
                menu_data_dokter(nama_lengkap_logged)

            elif choice_4 == '5':
                mode_admin(uname, nama_lengkap_logged)
            menu_data_dokter(nama_lengkap_logged)

        menu_data_dokter(nama_lengkap_logged)
    
    # 4.7 LAYANAN v UI FIXED
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
            cur.close()

        def lihat_data_layanan(conn, cur):  # v
            """Menampilkan data layanan dari database."""
            # Query untuk mengambil semua data dari tabel 'layanan'
            query = """
            SELECT *
            FROM layanan
            """
            cur.execute(query)
            # Mendapatkan semua data layanan
            data_layanan = cur.fetchall()

            headers = [i[0] for i in cur.description]

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
                    print("PERHATIAN : Terdapat kesalahan pada data yang akan diubah. \nGagal mengubah data layanan:", e)
                    # Rollback perubahan jika terjadi kesalahan
                    conn.rollback()
            else:
                print("Tidak ada data yang diubah.")

        def hapus_data_layanan(conn, cur, id_layanan):  # v
            """Menghapus data layanan dari database."""
            # Check apakah ada rekam medis yang terkait dengan layanan yang akan dihapus
            try:
                cur.execute(f"SELECT COUNT(*) FROM rekam_medis WHERE id_layanan = {id_layanan}")
                count_rekammedis = cur.fetchone()[0]
                postgresql_cls(conn, cur)
                conn, cur = postgresql_connect()
                cur.execute(f"SELECT COUNT(*) FROM reservasi WHERE id_layanan = {id_layanan}")
                count_reservasi = cur.fetchone()[0]

                if count_rekammedis > 0 and count_reservasi > 0:
                    print("Tidak dapat menghapus layanan karena masih ada rekam medis yang terkait.")
                    return False
                else:
                    konfirmasi_hapus = input(f"[Y/N] apakah anda yakin untuk menghapus id'{id_layanan}'? TIndakan tidak dapat diurungkan : ")
                    if konfirmasi_hapus.upper() == 'Y':
                        try:
                            # Query untuk menghapus data layanan berdasarkan id_layanan
                            cur.execute("DELETE FROM layanan WHERE id_layanan = %s", (id_layanan,))
                            conn.commit()
                            
                            if cur.rowcount > 0:
                                print("\nData layanan telah dihapus!")
                            else:
                                print("\nPERHATIAN : Data yang hendak dihapus tidak ada")
                        except:
                            print("\nPERHATIAN : Terjadi kesalahan saat akan menghapus data. Data gagal dihapus")
                    else:
                        input("Data batal dihapus")
            except psycopg2.Error as e:
                print("\nPERHATIAN : Masukan yang anda berikan tidak valid!")
            postgresql_cls(conn, cur)
          
        def menu_menu_layanan(nama_lengkap_logged):
            conn, cur = postgresql_connect()
            os.system('cls')
            print("ADMIN>DASHBOARD>LAYANAN")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
            print("MENU LAYANAN :")
            print("[1] Tambah layanan")
            print("[2] Lihat Data layanan")
            print("[3] Ubah Data layanan")
            print("[4] Hapus Data layanan\n")
            print("[5] Exit")

            pilihan = input("\nMasukkan pilihan Anda: ")

            if pilihan == "1":
                os.system('cls')
                print("ADMIN>DASHBOARD>LAYANAN>TAMBAH LAYANAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                nama_layanan = input("Masukkan nama layanan: ")
                harga_layanan = input("Masukkan harga layanan: ")
                try:
                    tambah_layanan(conn, cur, nama_layanan, harga_layanan)
                    print("\nLayanan baru BERHASIL ditambahkan!")
                except:
                    print("\nPERHATIAN : Terdapat kesalahan pada data yang akan dimasukkan. Data gagal dimasukkan")
                input("\nTekan [enter] untuk kembali ke Main Menu")
                menu_menu_layanan(nama_lengkap_logged)

            elif pilihan == "2":
                os.system('cls')
                print("ADMIN>DASHBOARD>LAYANAN>LIHAT LAYANAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
        
                lihat_data_layanan(conn, cur)
                input("\nTekan [enter] untuk kembali ke Main Menu")
                menu_menu_layanan(nama_lengkap_logged)

            elif pilihan == "3":
                os.system('cls')
                print("ADMIN>DASHBOARD>LAYANAN>EDIT LAYANAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                lihat_data_layanan(conn, cur)
                id_layanan = (input("Masukkan ID layanan yang ingin diubah: "))
                if id_layanan == '':
                    menu_menu_layanan(nama_lengkap_logged)
                layanan_baru = input("Masukkan nama layanan baru (kosongkan jika tidak ingin mengubah): ")
                harga_baru = input("Masukkan harga layanan baru (kosongkan jika tidak ingin mengubah): ")

                ubah_data_layanan(conn, cur, layanan_baru, harga_baru, id_layanan)

                input("\nTekan [enter] untuk kembali ke Main Menu")
                menu_menu_layanan(nama_lengkap_logged)

            elif pilihan == "4":
                os.system('cls')
                print("ADMIN>DASHBOARD>LAYANAN>HAPUS LAYANAN")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
                lihat_data_layanan(conn, cur)
                id_layanan = (input("Masukkan ID layanan yang ingin dihapus: "))
                if id_layanan == '':
                    menu_menu_layanan(nama_lengkap_logged)
                hapus_data_layanan(conn, cur, id_layanan)
                
                input("\nTekan [enter] untuk kembali ke Menu Layanan : ")
                menu_menu_layanan(nama_lengkap_logged)

            elif pilihan == "5":
                mode_admin(uname, nama_lengkap_logged)
            else:
                menu_menu_layanan(nama_lengkap_logged)
            
        menu_menu_layanan(nama_lengkap_logged)

    # 4.8 STAFF/ADMIN v UI FIXED
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
            headers = [i[0] for i in cur.description]
           
            # Menampilkan data dalam format tabel
            print(tabulate.tabulate(data_staf, headers=headers, tablefmt=f"{format_table}"))  

        def menu_staf_admin(nama_lengkap_logged):
            os.system('cls')
            print("ADMIN>DASHBOARD>STAFF/ADMIN")
            print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
            
            choice_8 = input("\nMENU STAFF/ADMIN :\n[1] Tambah Data\n[2] Lihat Data\n[3] Edit Data\n[4] Hapus Data\n\n[5] Kembali ke Dashboard\n\nPilih menu : ")

            if choice_8 == '1':    
                os.system('cls')
                print("ADMIN>DASHBOARD>STAFF/ADMIN>TAMBAH DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
      
                #Input Data Staf
                conn, cur = postgresql_connect()
                nama_staf     = input("Masukkan nama staf        : ")
                tlp_staf      = input("Masukkan no. telepon staf : ")
                uname_staf    = input("Masukkan username staf    : ")
                pw_staf       = input("Masukkan password staf    : ")

                # Cek apakah semua field diisi, jika tidak maka cetak pesan dan return False
                if not nama_staf or not tlp_staf or not uname_staf or not pw_staf:
                    print("Semua field harus diisi!")
                else:
                    try:
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
                    
                        print("Staf baru BERHASIL ditambahkan!")
                    except psycopg2.Error as e:
                        print("PERHATIAN : Terdapat kesalahan pada data yang anda coba masukkan! Tambah data gagal")

                input("\nTekan [Enter] untuk kembali ke Menu Staff/Admin : ")
                menu_staf_admin(nama_lengkap_logged)

            elif choice_8 == '2':   # Lihat data staf v
                os.system('cls')
                print("ADMIN>DASHBOARD>STAFF/ADMIN>LIHAT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
      
                lihat_data_staf()

                input("\nTekan [enter] untuk kembali ke Menu Staf/Admin : ")
                menu_staf_admin(nama_lengkap_logged)

            elif choice_8 == '3':   # Edit data staf v
                os.system('cls')
                print("ADMIN>DASHBOARD>STAFF/ADMIN>EDIT DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
      
                lihat_data_staf()

                # Meminta ID staf yang ingin diubah
                id_staf = input("Masukkan ID staf yang ingin diubah: ")
                if id_staf == '':
                    menu_staf_admin(nama_lengkap_logged)
            
                conn, cur = postgresql_connect()
                try:
                    # Mengecek apakah ID staf ada dalam database
                    cur.execute("SELECT COUNT(*) FROM staf WHERE id_staf = %s", (id_staf,))
                    if cur.fetchone()[0] == 0:
                        print("\nMaaf, ID staf yang Anda cari tidak ada. Silakan cek kembali.")
                    else:
                        # Meminta data baru dari user
                        nama_baru     = input("Masukkan nama baru staf (kosongkan jika tidak ingin mengubah)   : ")
                        telp_baru     = input("Masukkan no. telepon baru (kosongkan jika tidak ingin mengubah) : ")
                        uname_baru    = input("Masukkan username baru  (kosongkan jika tidak ingin mengubah)   : ")
                        password_baru = input("Masukkan password baru  (kosongkan jika tidak ingin mengubah)   : ")

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
                                conn.commit()
                                print("\nData staf telah diubah!")
                            except psycopg2.Error as e:
                                # Menampilkan pesan kesalahan jika gagal melakukan update
                                print("PERHATIAN : Terdapat kesalahan pada data yang anda coba ubah! Data gagal diubah\n", e)
                                # Melakukan rollback jika terjadi kesalahan
                                conn.rollback()
                        else:
                            print("\nTidak ada data yang diubah.")
                except psycopg2.Error as e:
                    # Menangani kesalahan koneksi atau query
                    print(f"Terjadi kesalahan: {e}")
                    conn.rollback()
                finally:
                    # Menutup kursor dan koneksi
                    postgresql_cls(conn, cur)

                input("\nTekan [enter] untuk kembali ke Menu Staff/Admin : ")
                menu_staf_admin(nama_lengkap_logged)

            elif choice_8 == '4':   # Hapus data staf v
                os.system('cls')  # Membersihkan layar (hanya berfungsi di Windows)
                print("ADMIN>DASHBOARD>STAFF/ADMIN>HAPUS DATA")
                print(f"{datetime.datetime.now().strftime("\r%A, %d %B %Y | %H:%M:%S")} | {nama_lengkap_logged}\n")
      
                lihat_data_staf()

                id_staf = (input("Masukkan ID staf yang ingin dihapus: "))

                #  proteksi untuk tidak menghapus data dirinya sendiri
                conn, cur = postgresql_connect()
                cur.execute(f"SELECT id_staf FROM staf WHERE nama_staf = '{nama_lengkap_logged}' AND uname_staf = '{uname}'")
                diri_sendiri = cur.fetchone()

                if id_staf == '':   # batal melanjutkan penghapusan
                    menu_staf_admin(nama_lengkap_logged)
                elif id_staf in str(diri_sendiri):   # datanya dirinya sendiri, proteksi berjalan
                    input("PERHATIAN : Anda tidak bisa menghapus data anda sendiri! \n\nTekan [Enter] untuk kembali ke Menu Staf/Admin : ")
                    menu_staf_admin(nama_lengkap_logged)
                
                konfirmasi_hapus = input(f"[Y/N] Apakah anda yakin untuk menghapus data '{id_staf}'? Tindakan tidak dapat diurungkan : ")
                if konfirmasi_hapus.upper()  == 'Y':
                    """Menghapus data staf dari database."""
                    conn, cur = postgresql_connect()
                    try:
                        # Memeriksa apakah ada reservasi yang terkait dengan staf ini
                        cur.execute("SELECT COUNT(*) FROM reservasi WHERE id_staf = %s", (id_staf,))
                        count_reservasi = cur.fetchone()[0]
                        # Memeriksa apakah ada transaksi yang terkait dengan staf ini
                        cur.execute("SELECT COUNT(*) FROM transaksi WHERE id_reservasi = (SELECT COUNT(*) FROM reservasi WHERE id_staf =  %s)", (id_staf,))
                        count_detail_transaksi = cur.fetchone()[0]

                        # Jika ada referensi terkait maka data tidak dapat dihapus
                        if count_reservasi > 0 or count_detail_transaksi > 0:
                            print("\nPERHATIAN : Terdapat data yang masih berkaitan dengan staf ini! Data tidak dapat dihapus.")
                        elif count_reservasi == 0 and count_detail_transaksi == 0:
                            # Menghapus data staf dari tabel staf
                            cur.execute("DELETE FROM staf WHERE id_staf = %s", (id_staf,))
                            conn.commit()
                            # Memeriksa apakah ada baris yang dihapus
                            if cur.rowcount > 0:
                                print("\nData staf telah dihapus!")
                            else:
                                print("\nPERHATIAN : Staf dengan ID tersebut tidak ditemukan!")
                        else:
                            print("\nPERHATIAN : Terdapat kesalahan! Silahkan coba lagi")
                    except psycopg2.Error as e:
                        print(f"PERHATIAN : Terjadi kesalahan saat hendak menghapus data : \n{e}")
                        conn.rollback()  # Membatalkan perubahan jika terjadi kesalahan
                    finally:
                        postgresql_cls(conn, cur)
                    input("\nTekan [enter] untuk kembali ke Menu staf")
                
                else:
                    input("\nData batal dihapus!\n\nTekan [Enter] untuk kembali ke Menu Staff/Admin : ")
                
                menu_staf_admin(nama_lengkap_logged)

            elif choice_8 == '5':
                mode_admin(uname, nama_lengkap_logged)
            
            else:
                menu_staf_admin(nama_lengkap_logged)

        menu_staf_admin(nama_lengkap_logged)

    # 4.9 EXIT v UI FIXED
    elif admin_choice == '9':
        launch_page()

    mode_admin(uname, nama_lengkap_logged)
# -------------------------------------------------------------------------------------------------

# FITUR MANUAL BOOK -------------------------------------------------------------------------------
def manual_book():
    os.system('cls')
    input("""
    END USER LICENSE AGREEMENT (EULA)

Selamat datang di Program SatSet Care, program sistem  berbasis terminal.
SatSet Care dibuat menggunakan bahasa pemrograman Python dan database PostgreSQL.

Sebelum menggunakan Program SatSet Care harap baca ketentuan penggunaan program kami berikut: 
        
    1. Program ini dapat digunakan oleh admin atau staf dan pelanggan yang telah terdaftar dalam sistem.
    2. Dilarang menggunakan program ini untuk tujuan selain yang telah ditentukan.
    3. Setiap aktivitas yang direkam oleh pengguna dalam program berkaitan dengan
       pengguna yang bersangkutan menjadi tanggung jawab yang bersangkutan.
    4. Kami akan menyimpan data yang terkait dengan penggunaan program ini sesuai dengan
       kebijakan.
    5. DILARANG mengubah dan memodifikasi program ini kemudian mendistribusikannya
       tanpa seizin kami
    6. Pengguna bisa menggunakan Program ini pada perangkat komputer dengan sistem operasi
       Windows dan MacOS
    7. Jika program ini akan digunakan pada sistem operasi Mac, maka perlu mengubah
       perintah 'cls' menjadi 'clear'
        
Dengan melanjutkan, Anda menyetujui semua syarat dan ketentuan diatas.


        Setelah anda menyetujui ketentuan diatas, berikut adalah fitur SatSet Care:

-Fitur Admin
    1. Admin dapat menambah dan mengurangi pengguna yang dapat menggunakan program ini.
    2. Admin dapat melihat dan mengedit Data Reservasi, Rekam Medis, Hewan Peliharaan, Customer atau pelanggan, layanan serta staf atau admin,.

-Fitur Dokter
    1. Dokter dapat menambah dan mengurangi data Rekam Medis.
    2. Dokter dapat melihat dan mengedit Data Rekam Medis, serta profil dokter itu sendiri.

-Fitur Customer
    1. Customer dapat melakukan reservasi sesuai dengan ketentuan yang dibuat oleh admin
    2. Customer dapat menambah dan mengurangi Data hewan peliharaan.
    3. Customer dapat Melihat Data Hewan Peliharaan, Data Rekam Medis Hewan, Dokter, dan layanan yang ada.
    4. Customer dapat mengedit Data Hewan Peliharaan, dan profil customer itu sendiri.
        
                    Terima kasih telah menggunakan program SatSet Care


©Kelompok 3 TA Basda

Tekan [Enter] untuk kembali """)

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
delay_welcome = 0 # ANIMASI PADA WELCOMING PAGE

format_table = 'fancy_grid'
textwraplen = 15

# EKSEKUSI PROGRAM --------------------------------------------------------------------------------

welcome_interface()

admin_pertama()

launch_page()
