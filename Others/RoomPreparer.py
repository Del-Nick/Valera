import numpy as np
from numba import njit

@njit
def search_rectangle(x_0, y_0, array):
    x = x_0
    while True:
        if (np.sum(array[x - 1:x + 1, y_0 - 50:y_0]) != 0) & (np.sum(array[x - 1:x + 1, y_0:y_0 + 50]) != 0):
            x -= 1
            # print(f'x_1     {x}:    {array[x][y_0]}     {np.sum(array[x][y_0-50:y_0])}      {np.sum(array[x][y_0:y_0+50])}')
        else:
            break

    x -= 1
    x_1 = x

    y = y_0

    while array[x + 10][y] != 0:
        y -= 1
        # print(f'y_1     {y}:    {array[x+2][y]}')

    y_1 = y - 1
    x += 60

    while array[x][y + 10] != 0:
        x += 1
        # print(f'x_2     {x}:    {array[x][y+10]}')

    x_2 = x + 1
    y += 50

    while array[x - 10][y] != 0:
        y += 1
        # print(f'y_2     {y}:    {array[x-2][y]}')

    y_2 = y + 1

    return x_1, y_1, x_2, y_2


@njit
def search_polygon(x_0, y_0, array):
    x = x_0
    while True:
        if (np.sum(array[x - 1:x + 1, y_0 - 50:y_0]) != 0) & (np.sum(array[x - 1:x + 1, y_0:y_0 + 50]) != 0):
            x -= 1
            print(f'x_1     {x}:    {array[x][y_0]}     {np.sum(array[x][y_0-50:y_0])}      {np.sum(array[x][y_0:y_0+50])}')
        else:
            break

    x -= 1
    x_1 = x

    y = y_0

    while array[x + 10][y] != 0:
        y -= 1
        print(f'y_1     {y}:    {array[x+2][y]}')

    y_1 = y - 1
    x += 130

    while array[x][y + 10] != 0:
        x += 1
        print(f'x_2     {x}:    {array[x][y+2]}')

    x_2 = x + 1
    y += 50

    while array[x - 10][y] != 0:
        y += 1
        print(f'y_2     {y}:    {array[x-2][y]}')

    y_2 = y + 1

    return x_1, y_1, x_2, y_2


@njit
def fill(array, x_1, y_1, x_2, y_2, room):
    for x in range(x_1, x_2):
        for y in range(y_1, y_2):
            if array[y][x][0] > 50:
                array[y][x][0] = array[y][x][0] / 255 * 255
                array[y][x][1] = array[y][x][1] / 255 * 145
                array[y][x][2] = 0

    return array


def steps(steps_img, img, x_1, y_1, x_2, y_2, floor):
    print(x_1, y_1, x_2, y_2)

    if floor == 5:
        x_0 = 4488
        y_0 = 3564
        width, height = steps_img.size

    if (x_1 > 1879) and (y_1 > 3300) and (x_2 < 4350) and (y_2 < 4150):

        temp = steps_img.rotate(270, expand=True)
        img.paste(temp, (x_0, y_0), temp)

        koef = 96.5

        y_0 += 71
        # x_0 += koef

        for k in range(3):
            alpha_0 = 270 - 45 * k
            temp = steps_img.rotate(alpha_0, expand=True)
            img.paste(temp, (int(x_0 - 1.5 * koef * k / 3), int(y_0 + koef * k / 3)), temp)

        x_0 -= 163
        y_0 += 63

        temp = steps_img.rotate(180, expand=True)
        # adding = int(((x_0 - (x_1 + x_2) / 2 - width*1.2) % width) / (int((x_0 - (x_1 + x_2) / 2 - width*1.2) / width)))
        adding = (x_0 - (x_1 + x_2) / 2 - width * 1.2) / width
        for k in range(int((x_0 - (x_1 + x_2) / 2 - width * 1.2) / width)):
            img.paste(temp, (x_0 - k * width - int(k * adding), y_0), temp)
        print((x_0 - (x_1 + x_2) / 2) % width, (int(round((x_0 - (x_1 + x_2) / 2) / width))), adding)

        x_0 -= k * (width + adding) + 20

        if y_1 > y_0:
            temp = steps_img.rotate(180, expand=True)
            img.paste(temp, (x_0, y_0), temp)

            temp = steps_img.rotate(225, expand=True)
            img.paste(temp, (x_0 - width, y_0), temp)

            temp = steps_img.rotate(270, expand=True)
            img.paste(temp, (x_0 - int(width * 1.2), y_0 + width), temp)

        else:
            temp = steps_img.rotate(180, expand=True)
            img.paste(temp, (x_0, y_0), temp)

            temp = steps_img.rotate(135, expand=True)
            img.paste(temp, (x_0 - width, y_0 - int(width / 2)), temp)

            temp = steps_img.rotate(90, expand=True)
            img.paste(temp, (x_0 - int(width), y_0 - width), temp)

    elif (x_1 > 800) and (y_1 > 3600) and (x_2 < 2050) and (y_2 < 4400):

        temp = steps_img.rotate(270, expand=True)
        img.paste(temp, (x_0, y_0), temp)

        koef = 96.5

        y_0 += 71
        # x_0 += koef

        for k in range(3):
            alpha_0 = 270 - 45 * k
            temp = steps_img.rotate(alpha_0, expand=True)
            img.paste(temp, (int(x_0 - 1.5 * koef * k / 3), int(y_0 + koef * k / 3)), temp)

        x_0 -= 163
        y_0 += 63

        temp = steps_img.rotate(180, expand=True)
        adding = int((x_0 - 1650 + koef) % width / (int((x_0 - 1800 + koef) / width)))
        for k in range(int((x_0 - 1800 + koef) / width)):
            img.paste(temp, ((x_0 - k * width - k * adding), y_0), temp)
        print((x_0 - 1650 + koef) % width, int((x_0 - 1800 + koef) / width),
              int(((x_0 - 1650 + koef) % width * width) / (int((x_0 - 1800 + koef) / width))))

        x_0 = 1700

        temp = steps_img.rotate(180, expand=True)
        img.paste(temp, (x_0, y_0), temp)

        temp = steps_img.rotate(225, expand=True)
        img.paste(temp, (x_0 - width, y_0), temp)

        temp = steps_img.rotate(270, expand=True)
        img.paste(temp, (x_0 - int(width * 1.2), y_0 + width), temp)

        x_0 -= int(width * 1.2)
        y_0 += width * 2

        temp = steps_img.rotate(270, expand=True)
        img.paste(temp, (x_0, y_0), temp)

        y_0 += k * width + 35

        if x_1 < 1500:
            temp = steps_img.rotate(270, expand=True)
            img.paste(temp, (x_0, y_0), temp)

            temp = steps_img.rotate(225, expand=True)
            img.paste(temp, (x_0 - int(width / 2), y_0 + int(width / 2)), temp)

            temp = steps_img.rotate(180, expand=True)
            img.paste(temp, (x_0 - width, y_0 + int(width)), temp)

    return img


@njit
def binary(array):
    width, height = np.shape(array)
    for x in range(width):
        for y in range(height):
            if array[x][y] < 100:
                array[x][y] = 0
            else:
                array[x][y] = 255
    return array