import pygame as pg


def client():

    pg.init()

    ecran = pg.display.set_mode((300, 200))

    pg.display.set_caption("Mon jeu")
    im_cafe = pg.image.load("icon.png").convert_alpha()
    pos_cafe = (0, 0)
    pg.display.set_icon(im_cafe)

    continuer = True

    while continuer:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    continuer = False
            if event.type == pg.MOUSEMOTION:
                pos_cafe = event.pos

        pg.draw.rect(ecran, (180, 20, 150), (0, 0, 300, 200))
        ecran.blit(im_cafe, pos_cafe)
        pg.display.flip()

    pg.quit()
