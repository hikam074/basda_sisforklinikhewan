import psycopg2
import os
import sys
import time

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
    print(f"selamat datang, {nama_lengkap_logged} !")
    print(" [1] Rekam Medis \n [2] Profil Anda \n [3] Log-out ")
    dokter_choice = input("Silahkan pilih menu anda : ")

    # 2.1 REKAM MEDIS
    if dokter_choice == '1':
        pass

    # 2.2 PROFIL ANDA
    elif dokter_choice == '2':
        pass

    # 2.3 EXIT
    elif dokter_choice == '3':
        pass

    # BILA SALAH INPUT
    else:
        mode_dokter()

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

    # 4.6 DATA DOKTER
    elif admin_choice == '6':
        pass

    # 4.7 LAYANAN
    elif admin_choice == '7':
        pass

    # 4.8 STAFF/ADMIN
    elif admin_choice == '8':
        pass
    # 4.9 EXIT
    elif admin_choice == '9':
        pass

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
