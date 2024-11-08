import streamlit as st
import pymysql
from PIL import Image
import io


# 数据库连接函数
def get_database_connection():
    return pymysql.connect(
        host='rm-2ze51s440w5h4957mao.mysql.rds.aliyuncs.com',
        port=3306,
        user='HDK1840',
        password='Hdk184018401840',
        database='app_use',
        autocommit=True,  # 自动提交
        charset='utf8mb4'
    )


# 查询图片的函数
def fetch_image(vehicle_model_name):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            # 查询数据库中是否存在指定的 vehicle_model_name
            query = "SELECT pictures FROM cars_pictures WHERE vehicle_model_name = %s"
            cursor.execute(query, (vehicle_model_name,))
            result = cursor.fetchone()
            if result:
                return result[0]  # 返回图片的二进制数据
            else:
                return None
    except pymysql.MySQLError as e:
        st.error(f"Error while querying the database: {e}")
    finally:
        connection.close()


# Streamlit 应用界面
st.title("车辆图片查询")

# 输入框和按钮
vehicle_model_name = st.text_input("请输入车辆型号名称：")
if st.button("查询"):
    if vehicle_model_name:
        # 查询并获取图片数据
        image_data = fetch_image(vehicle_model_name)
        if image_data:
            # 将二进制图片数据转换为 PIL 图像
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption=f"车辆型号：{vehicle_model_name}", use_column_width=True)
        else:
            st.warning("未找到该车型对应的图片，请检查输入的车型名称。")
    else:
        st.warning("请输入车型名称以进行查询。")
