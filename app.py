import streamlit as st
import pandas as pd
import os
from PIL import Image

# Путь к CSV-файлу
CSV_FILE = 'wishlist.csv'
images_dir = 'images'

if not os.path.exists(images_dir):
    os.makedirs(images_dir)

def init_csv():
    # Инициализация CSV-файла, если он не существует
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['item', 'checked', 'link', 'image'])
        df.to_csv(CSV_FILE, index=False)

def load_wishlist():
    try:
        wishlist_df = pd.read_csv(CSV_FILE)
        return wishlist_df
    except Exception as e:
        st.error(f"Ошибка при загрузке вишлиста: {e}")
        return pd.DataFrame(columns=['item', 'checked', 'link', 'image'])  # Возвращаем пустой DataFrame

def save_wishlist(wishlist_df):
    try:
        wishlist_df.to_csv(CSV_FILE, index=False)  # Сохраняем DataFrame в CSV
    except Exception as e:
        st.error(f"Ошибка при сохранении вишлиста: {e}")

def update_wishlist(wishlist_df):
    indices_to_delete = []
    for index, row in wishlist_df.iterrows():
        item_label = str(row['item']) if pd.notna(row['item']) else "Unnamed Item"
        st.markdown(f"### {item_label}")
        checked = st.checkbox('Подарю это', value=row['checked'], key=f'checkbox_{index}')
        del_check = st.checkbox('Выбрать для удаления', value=False, key=f'del_{index}')
        wishlist_df.at[index, 'checked'] = checked  # Обновляем состояние чекбокса

        # Отображаем изображение, если оно есть
        if pd.notna(row['image']) and row['image']:
            img = Image.open(row['image'])
            st.image(img,  width=200)

        if pd.notna(row['link']) and row['link']:
            st.markdown(f"[Ссылка на подарок]({row['link']})")
        st.markdown("---")

        if del_check:
            indices_to_delete.append(index)

    if st.button("❌ Удалить выбранные"):
        if indices_to_delete:
            wishlist_df = wishlist_df.drop(indices_to_delete).reset_index(drop=True)  # Удаляем элементы и обновляем индексы
            save_wishlist(wishlist_df)  # Сохраняем изменения
            st.success("Выбранные элементы удалены из вишлиста!")
        else:
            st.warning("Выберите элементы для удаления.")

    return wishlist_df

st.title("🛍️ Вишлист")

init_csv()

if 'wishlist_df' not in st.session_state:
    st.session_state.wishlist_df = load_wishlist()

with st.sidebar:
    st.header("Добавить новый элемент")
    new_item = st.text_input("Название элемента:")
    new_link = st.text_input("Ссылка на элемент:")
    new_image = st.file_uploader("Загрузите изображение (опционально)", type=['jpg', 'jpeg', 'png'])

    if st.button("➕ Добавить"):
        if new_item:
            image_path = None
            if new_image is not None:
                image_path = os.path.join(images_dir, new_image.name)
                img = Image.open(new_image)
                img.save(image_path)

            new_row = pd.DataFrame({'item': [new_item], 'checked': [False], 'link': [new_link], 'image': [image_path]})
            st.session_state.wishlist_df = pd.concat([st.session_state.wishlist_df, new_row], ignore_index=True)
            save_wishlist(st.session_state.wishlist_df)
            st.success(f"'{new_item}' добавлен в вишлист!")
        else:
            st.warning("Введите название элемента.")

# Обновление вишлиста
st.session_state.wishlist_df = update_wishlist(st.session_state.wishlist_df)

# Кнопка для сохранения состояния
if st.button("💾 Обновить"):
    save_wishlist(st.session_state.wishlist_df)
    st.success("Состояние вишлиста сохранено!")

# Отображение обновленного вишлиста
st.header("Обновленный вишлист:")
st.dataframe(st.session_state.wishlist_df)
