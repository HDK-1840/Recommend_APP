import pymysql
import os

def save_images_to_database(folder_path):
    try:
        # 连接到 MySQL 数据库
        connection = pymysql.connect(
            host='rm-2ze51s440w5h4957mao.mysql.rds.aliyuncs.com',
            port=3306,
            user='HDK1840',
            password='Hdk184018401840',
            database='app_use',
            autocommit=True,  # 自动提交
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # 创建表（如果表不存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars_pictures (
                    vehicle_model_name TEXT,
                    pictures LONGBLOB
                )
            """)

            # 遍历文件夹中的每个图片文件
            for filename in os.listdir(folder_path):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    # 获取文件名不带扩展名的部分，作为车型名
                    vehicle_model_name = os.path.splitext(filename)[0]

                    # 获取图片的二进制数据
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'rb') as file:
                        image_data = file.read()

                    # 插入数据到 cars_pictures 表中
                    insert_query = """
                    INSERT INTO cars_pictures (vehicle_model_name, pictures) VALUES (%s, %s)
                    """
                    cursor.execute(insert_query, (vehicle_model_name, image_data))

            print("All images have been saved to the database.")

    except pymysql.MySQLError as e:
        print("Error while connecting to MySQL:", e)

    finally:
        if connection:
            connection.close()
            print("MySQL connection is closed.")

# 指定存放图片的文件夹路径
folder_path = r'D:\桌面\Digital twins\cars_pictures'
save_images_to_database(folder_path)
