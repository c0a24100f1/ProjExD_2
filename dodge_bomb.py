import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA= {  # 移動量辞書
    pg.K_UP:(0,-5),
    pg.K_DOWN:(0,5),
    pg.K_LEFT:(-5,0),
    pg.K_RIGHT:(5,0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    Rectが画面内にあるかどうかを判定する関数
    戻り値：横方向・縦方向の真理値タプル
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    """
    go_img=pg.Surface((WIDTH,HEIGHT))
    pg.draw.rect(go_img,(0,0,0),(0,0,1100,650))
    go_img.set_alpha(170)
    go_rct = go_img.get_rect()
    go_rct.center=550,325
    screen.blit(go_img,go_rct)

    font = pg.font.Font(None, 80)
    text = font.render("Game Over", True, (255, 255, 255))
    screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 40))

    kk_img = pg.image.load("fig/8.png")
    kk_img = pg.transform.rotozoom(kk_img, 0, 1.0)
    screen.blit(kk_img, (WIDTH//2 - 220, HEIGHT//2 -50 ))
    screen.blit(kk_img, (WIDTH//2 + 180, HEIGHT//2 -50 ))
    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾の画像リストと加速度リストを返す関数
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト
    for r in range(1, 11):
        img = pg.Surface((20*r, 20*r))
        pg.draw.circle(img, (255, 0, 0), (10*r, 10*r), 10*r)
        img.set_colorkey((0, 0, 0))
        bb_imgs.append(img)
    return bb_imgs, bb_accs

def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動方向に対応するこうかとん画像を返す関数
    """
    kk_imgs = {
        (0, 0): pg.image.load("fig/3.png"),
        (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),
        (+5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 180, 0.9),
        (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 270, 0.9),
        (0, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9),
        (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 315, 0.9),
        (-5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9),
        (+5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 315, 0.9),
        (+5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9),
    }
    return kk_imgs.get(sum_mv, kk_imgs[(0, 0)])

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_v: tuple[float, float]) -> tuple[float, float]:
    """
    orgからdstへの方向ベクトルを返す（ノルムをsqrt(50)に）
    """
    dx, dy = dst.centerx - org.centerx, dst.centery - org.centery
    d = max((dx*2 + dy*2)*0.5, 1)
    if d < 300:
        return current_v  # 元の値を返す
    return 5*dx/d, 5*dy/d

def main():
    pg.display.set_caption("逃げろ！こうかとん") #行末
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20))  # Bom>
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0,WIDTH)
    bb_rct.centery = random.randint(0,HEIGHT)
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    vx,vy = 5,5  #<Bom

    # bb_img2 = pg.Surface((20,20))  # Bom2>
    # pg.draw.circle(bb_img2, (0, 255, 0), (10, 10), 10)
    # bb_img2.set_colorkey((0, 0, 0))
    # bb2_rct = bb_img2.get_rect()
    # bb2_rct.centerx = random.randint(0,WIDTH)
    # vy2 = 5  #<Bom2

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key,mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
                kk_rct.move_ip(sum_mv)
            if not check_bound(kk_rct)[0]:
                kk_rct.move_ip(-sum_mv[0], 0)
            if not check_bound(kk_rct)[1]:
                kk_rct.move_ip(0, -sum_mv[1])
        kk_img = get_kk_img((0, 0))
        kk_img = get_kk_img(tuple(sum_mv))
        if sum_mv[0]>0: # こうかとん反転
            if sum_mv[1]>0:
                kk_img = pg.transform.flip(kk_img,True,False)
            elif sum_mv[1]<0:
                kk_img = pg.transform.flip(kk_img,True,False)
            elif sum_mv[1]==0:
                kk_img = pg.transform.flip(kk_img,False,True)
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        # kk_rct.move_ip(sum_mv)
        # avx, avy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        bb_img = bb_imgs[min(tmr//500, 9)]  # 拡大
        # avx = vx*bb_accs[min(tmr//500, 9)]  # x抽出
        # avy = vy*bb_accs[min(tmr//500, 9)]  # y抽出
        avx, avy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        bb_rct.move_ip(avx, avy)
        screen.blit(bb_img, bb_rct)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(kk_img, kk_rct)
        # bb_rct.move_ip(vx,vy)  # Bomspeed
        # screen.blit(bb_img, bb_rct)  # Bom
        # bb2_rct.move_ip(vx2,vy2)  # Bom2speed
        # screen.blit(bb_img2, bb2_rct)
        if kk_rct.colliderect(bb_rct):
            gameover(screen) # GAMEOVER
            return
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
