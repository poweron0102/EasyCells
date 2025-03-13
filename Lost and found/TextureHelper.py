import pygame as pg

img_size: tuple[int, int] = tuple(map(int, input("Enter the image size (width, height): ").split()))
tile_size: tuple[int, int] = tuple(map(int, input("Enter the tile size (width, height): ").split()))

img: pg.Surface = pg.Surface(img_size)
pg.font.init()
font = pg.font.Font(None, 16)

colors: list[pg.Color] = [pg.Color("Red"), pg.Color("Green")]
cont = 0
for y in range(0, img_size[1], tile_size[1]):
    for x in range(0, img_size[0], tile_size[0]):
        img.fill(colors[(x // tile_size[0] + y // tile_size[1]) % 2], (x, y, tile_size[0], tile_size[1]))
        # write the index on this tile
        text = font.render(str(cont), True, pg.Color("Black"))
        cont += 1
        print(cont)
        img.blit(text, (x + tile_size[0] // 2 - text.get_width() // 2, y + tile_size[1] // 2 - text.get_height() // 2))

pg.image.save(img, "checkerboard.png")
print("Image saved as 'checkerboard.png'")
