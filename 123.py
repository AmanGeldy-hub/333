import matplotlib.pyplot as plt
import numpy as np

# Настройки изображения
fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)  # Full HD
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Генерируем градиент неба
for i in range(100):
    ax.fill_between([0, 10], i * 0.1, (i + 1) * 0.1, color=(0.1, 0.5, 1, i / 150 + 0.2))

# Добавляем солнце
sun_x, sun_y = np.random.uniform(7, 9), np.random.uniform(7.5, 9)
ax.add_patch(plt.Circle((sun_x, sun_y), 0.8, color='yellow', alpha=0.9))

# Генерируем случайные горы
num_mountains = 5
for i in range(num_mountains):
    base_x = np.random.uniform(0, 8)
    height = np.random.uniform(2, 4)
    color = (0.3, 0.3, 0.3, 1 - i * 0.1)  # Градиент глубины
    mountain = plt.Polygon([(base_x, 2), (base_x + 2, 2), (base_x + 1, 2 + height)], color=color)
    ax.add_patch(mountain)

# Добавляем облака
num_clouds = np.random.randint(3, 6)
for _ in range(num_clouds):
    x, y = np.random.uniform(1, 8), np.random.uniform(6, 9)
    for i in range(3):
        ax.add_patch(plt.Circle((x + i * 0.5, y), 0.6, color='white', alpha=0.8))

# Генерируем деревья
num_trees = np.random.randint(10, 20)
for _ in range(num_trees):
    x = np.random.uniform(0.5, 9.5)
    tree_height = np.random.uniform(1.5, 3)
    
    # Ствол
    ax.add_patch(plt.Rectangle((x - 0.1, 2), 0.2, tree_height, color='saddlebrown'))
    
    # Крона
    for j in range(3):
        ax.add_patch(plt.Circle((x, 2 + tree_height - j * 0.5), 0.8 - j * 0.2, color='forestgreen'))

# Показываем изображение
plt.show()
