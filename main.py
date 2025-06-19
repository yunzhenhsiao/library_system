import sqlite3
import os

# 定義資料庫檔案名稱
DB_FILE = 'library.db'

def create_database():
    """
    連接到 SQLite 資料庫並創建 'books' 資料表。
    如果資料庫檔案或資料表已存在，則不會重複創建。
    """
    # 連接到資料庫檔案。如果檔案不存在，sqlite3 會自動創建它。
    conn = sqlite3.connect(DB_FILE)
    # 創建一個 cursor 物件，用於執行 SQL 命令
    cursor = conn.cursor()

    # 定義創建 'books' 資料表的 SQL 語句
    # IF NOT EXISTS 確保只有在資料表不存在時才創建，避免重複執行時報錯
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        publisher TEXT,
        isbn TEXT UNIQUE NOT NULL,
        pub_year INTEGER,
        quantity INTEGER NOT NULL DEFAULT 0
    )
    """

    try:
        # 執行 SQL 語句以創建資料表
        cursor.execute(create_table_sql)
        # 提交變更到資料庫，使創建的資料表生效
        conn.commit()
        print(f"資料庫 '{DB_FILE}' 和 'books' 資料表已建立或已存在。")
    except sqlite3.Error as e:
        # 捕捉並列印任何可能發生的資料庫錯誤
        print(f"創建資料庫或資料表時發生錯誤: {e}")
    finally:
        # 無論成功或失敗，最後都關閉資料庫連接
        conn.close()

# 這是在程式碼檔案被直接執行時會運行的部分
if __name__ == "__main__":
    # 呼叫函式來創建或連接資料庫
    create_database()

    # 簡單驗證資料庫檔案是否已生成
    if os.path.exists(DB_FILE):
        print(f"確認資料庫檔案 '{DB_FILE}' 已成功生成在專案資料夾中。")
    else:
        print(f"錯誤：資料庫檔案 '{DB_FILE}' 未生成。")

    print("\n請執行此檔案一次即可完成資料庫初始化。")
    print("之後可以在這個檔案中繼續添加其他書籍管理功能。")

# --- 階段二：核心 CRUD 功能實作 ---

def add_book(title, author, publisher, isbn, pub_year, quantity):
    """
    新增一本新書到資料庫中。
    :param title: 書名 (string)
    :param author: 作者 (string)
    :param publisher: 出版社 (string)
    :param isbn: ISBN 號碼，必須是唯一的 (string)
    :param pub_year: 出版年份 (integer)
    :param quantity: 庫存數量 (integer)
    :return: 成功返回 True，失敗返回 False
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 插入書籍資訊到 'books' 資料表
        # 使用問號 (?) 作為佔位符，並將參數作為元組傳遞，防止 SQL 注入
        cursor.execute("""
            INSERT INTO books (title, author, publisher, isbn, pub_year, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, author, publisher, isbn, pub_year, quantity))
        conn.commit()
        print(f"書籍 '{title}' (ISBN: {isbn}) 已成功新增。")
        return True
    except sqlite3.IntegrityError:
        # 如果 ISBN 重複，會捕獲 IntegrityError
        print(f"錯誤：ISBN '{isbn}' 已存在。書籍新增失敗。")
        return False
    except sqlite3.Error as e:
        print(f"新增書籍時發生錯誤: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_books():
    """
    查詢並返回資料庫中所有書籍的資訊。
    :return: 包含所有書籍資訊的列表，每本書是一個元組。如果沒有書籍則返回空列表。
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 選擇所有欄位的所有書籍
        cursor.execute("SELECT id, title, author, publisher, isbn, pub_year, quantity FROM books")
        books = cursor.fetchall() # 獲取所有查詢結果
        return books
    except sqlite3.Error as e:
        print(f"查詢所有書籍時發生錯誤: {e}")
        return []
    finally:
        if conn:
            conn.close()

def search_books(search_term):
    """
    根據書名、作者或 ISBN 模糊查詢書籍資訊。
    :param search_term: 查詢關鍵字 (string)
    :return: 包含符合條件書籍資訊的列表，每本書是一個元組。如果沒有符合條件的書籍則返回空列表。
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 使用 LIKE 運算符進行模糊查詢，% 是萬用字元
        # 查詢書名、作者或 ISBN 包含關鍵字的書籍
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT id, title, author, publisher, isbn, pub_year, quantity
            FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
        """, (search_pattern, search_pattern, search_pattern))
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"查詢書籍時發生錯誤: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_book_info(isbn, new_title, new_author, new_publisher, new_pub_year):
    """
    根據 ISBN 更新書籍的標題、作者、出版社和出版年份。
    :param isbn: 要更新書籍的 ISBN (string)
    :param new_title: 新的書名 (string)
    :param new_author: 新的作者 (string)
    :param new_publisher: 新的出版社 (string)
    :param new_pub_year: 新的出版年份 (integer)
    :return: 成功返回 True，失敗返回 False
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 更新書籍資訊
        cursor.execute("""
            UPDATE books
            SET title = ?, author = ?, publisher = ?, pub_year = ?
            WHERE isbn = ?
        """, (new_title, new_author, new_publisher, new_pub_year, isbn))
        conn.commit()
        if cursor.rowcount > 0: # 檢查是否有行被更新
            print(f"書籍 (ISBN: {isbn}) 資訊已成功更新。")
            return True
        else:
            print(f"錯誤：未找到 ISBN '{isbn}' 的書籍，資訊更新失敗。")
            return False
    except sqlite3.Error as e:
        print(f"更新書籍資訊時發生錯誤: {e}")
        return False
    finally:
        if conn:
            conn.close()

def borrow_book(isbn):
    """
    根據 ISBN 借閱書籍，將庫存數量減少 1。
    :param isbn: 要借閱書籍的 ISBN (string)
    :return: 成功返回 True，失敗返回 False
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 先查詢當前庫存數量
        cursor.execute("SELECT quantity FROM books WHERE isbn = ?", (isbn,))
        result = cursor.fetchone() # 獲取一條結果

        if result:
            current_quantity = result[0]
            if current_quantity > 0:
                # 減少庫存數量
                cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE isbn = ?", (isbn,))
                conn.commit()
                print(f"書籍 (ISBN: {isbn}) 已成功借閱。剩餘數量: {current_quantity - 1}")
                return True
            else:
                print(f"錯誤：書籍 (ISBN: {isbn}) 庫存不足，無法借閱。")
                return False
        else:
            print(f"錯誤：未找到 ISBN '{isbn}' 的書籍。")
            return False
    except sqlite3.Error as e:
        print(f"借閱書籍時發生錯誤: {e}")
        return False
    finally:
        if conn:
            conn.close()

def return_book(isbn):
    """
    根據 ISBN 歸還書籍，將庫存數量增加 1。
    :param isbn: 要歸還書籍的 ISBN (string)
    :return: 成功返回 True，失敗返回 False
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 增加庫存數量
        cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE isbn = ?", (isbn,))
        conn.commit()
        if cursor.rowcount > 0: # 檢查是否有行被更新
            print(f"書籍 (ISBN: {isbn}) 已成功歸還。")
            return True
        else:
            print(f"錯誤：未找到 ISBN '{isbn}' 的書籍，歸還失敗。")
            return False
    except sqlite3.Error as e:
        print(f"歸還書籍時發生錯誤: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_book(isbn):
    """
    根據 ISBN 從資料庫中刪除書籍。
    :param isbn: 要刪除書籍的 ISBN (string)
    :return: 成功返回 True，失敗返回 False
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # 刪除書籍
        cursor.execute("DELETE FROM books WHERE isbn = ?", (isbn,))
        conn.commit()
        if cursor.rowcount > 0: # 檢查是否有行被刪除
            print(f"書籍 (ISBN: {isbn}) 已成功刪除。")
            return True
        else:
            print(f"錯誤：未找到 ISBN '{isbn}' 的書籍，刪除失敗。")
            return False
    except sqlite3.Error as e:
        print(f"刪除書籍時發生錯誤: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- 階段三：使用者介面與主程式邏輯 (CLI 選單) ---

def display_menu():
    """顯示主選單選項"""
    print("\n" + "="*25)
    print("====== 圖書館管理系統 ======")
    print("1. 新增書籍")
    print("2. 查詢書籍 (所有書籍)")
    print("3. 查詢書籍 (依關鍵字)")
    print("4. 借閱書籍")
    print("5. 歸還書籍")
    print("6. 修改書籍資訊")
    print("7. 刪除書籍")
    print("0. 離開系統")
    print("="*25)

def run_cli_app():
    """執行命令列應用程式主邏輯"""
    # 確保資料庫在應用程式啟動時就被創建
    create_database()

    while True:
        display_menu()
        choice = input("請輸入您的選擇: ").strip() # 移除空白字元

        if choice == '1':
            print("\n--- 新增書籍 ---")
            title = input("書名: ")
            author = input("作者: ")
            publisher = input("出版社: ")
            isbn = input("ISBN: ")
            try:
                pub_year = int(input("出版年份: "))
                quantity = int(input("數量: "))
                add_book(title, author, publisher, isbn, pub_year, quantity)
            except ValueError:
                print("輸入錯誤：出版年份和數量必須是數字。")

        elif choice == '2':
            print("\n--- 查詢所有書籍 ---")
            books = get_all_books()
            if books:
                for book in books:
                    # 格式化輸出，更易閱讀
                    print(f"ID: {book[0]}, 書名: {book[1]}, 作者: {book[2]}, 出版社: {book[3]}, ISBN: {book[4]}, 出版年份: {book[5]}, 數量: {book[6]}")
            else:
                print("資料庫中目前沒有書籍。")

        elif choice == '3':
            print("\n--- 依關鍵字查詢書籍 ---")
            search_term = input("請輸入書名、作者或ISBN關鍵字: ")
            books = search_books(search_term)
            if books:
                for book in books:
                    print(f"ID: {book[0]}, 書名: {book[1]}, 作者: {book[2]}, 出版社: {book[3]}, ISBN: {book[4]}, 出版年份: {book[5]}, 數量: {book[6]}")
            else:
                print(f"未找到包含 '{search_term}' 的書籍。")

        elif choice == '4':
            print("\n--- 借閱書籍 ---")
            isbn = input("請輸入要借閱書籍的ISBN: ")
            borrow_book(isbn)

        elif choice == '5':
            print("\n--- 歸還書籍 ---")
            isbn = input("請輸入要歸還書籍的ISBN: ")
            return_book(isbn)

        elif choice == '6':
            print("\n--- 修改書籍資訊 ---")
            isbn = input("請輸入要修改書籍的ISBN: ")
            # 可以先查詢書籍資訊顯示出來，讓使用者確認
            search_results = search_books(isbn)
            if search_results:
                print("目前書籍資訊：")
                for book in search_results:
                     print(f"ID: {book[0]}, 書名: {book[1]}, 作者: {book[2]}, 出版社: {book[3]}, ISBN: {book[4]}, 出版年份: {book[5]}, 數量: {book[6]}")
                
                print("\n請輸入新的資訊 (留空表示不修改該欄位):")
                new_title = input(f"新書名 (原: {search_results[0][1]}): ")
                new_author = input(f"新作者 (原: {search_results[0][2]}): ")
                new_publisher = input(f"新出版社 (原: {search_results[0][3]}): ")
                
                new_pub_year_str = input(f"新出版年份 (原: {search_results[0][5]}): ")
                new_pub_year = int(new_pub_year_str) if new_pub_year_str.isdigit() else search_results[0][5] # 如果不是數字，則保留原值

                # 只更新使用者有輸入值的欄位，否則保持原值
                title_to_update = new_title if new_title else search_results[0][1]
                author_to_update = new_author if new_author else search_results[0][2]
                publisher_to_update = new_publisher if new_publisher else search_results[0][3]
                
                update_book_info(isbn, title_to_update, author_to_update, publisher_to_update, new_pub_year)
            else:
                print(f"未找到 ISBN '{isbn}' 的書籍，無法修改。")

        elif choice == '7':
            print("\n--- 刪除書籍 ---")
            isbn = input("請輸入要刪除書籍的ISBN: ")
            delete_book(isbn)

        elif choice == '0':
            print("\n感謝使用圖書館管理系統，再見！")
            break # 退出迴圈，結束程式

        else:
            print("無效的選擇，請輸入選單中的數字。")

        input("\n按下 Enter 鍵繼續...") # 暫停，讓使用者看到結果後再繼續

        
# --- 主程式執行區塊 (用於測試和未來整合 CLI 選單) ---
if __name__ == "__main__":
    # 呼叫函式來創建或連接資料庫
    run_cli_app()