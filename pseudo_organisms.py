import matplotlib.pyplot as plt
import japanize_matplotlib
import matplotlib.patches as patches
import numpy as np
rng = np.random.default_rng()
import imageio.v2 as imageio


#Rectangle(aspect_ratio=1.5, velocity=np.array([1.0, 2.0]), position=np.array([0.0, 0.0]), color='red')
class Rectangle:
    def __init__(self, aspect_ratio, velocity, position, gene1=None, gene2=None, f_facter=None, m_facter=None, generation=0):
        self.gene1 = gene1 if gene1 is not None else rng.integers(2, size=9)
        self.gene2 = gene2 if gene2 is not None else np.append(1, rng.integers(2, size=8))
        self.expression = np.array([])
        for i, g in enumerate(self.gene1+self.gene2):
            if i == 0:
                self.expression = np.append(self.expression, [False, False, True][g]).astype(bool)
            if 0 < i <= 4:
                self.expression = np.append(self.expression, [False, True, True][g]).astype(bool)
            else:
                self.expression = np.append(self.expression, [True, False, False][g]).astype(bool)
        
        self.sex = "f" if self.expression[0] else "m"
        self.life = np.clip(10+round(rng.normal(1, 5)), 1, 25)
        self.age = 0
        self.aspect_ratio = [1, np.sqrt(2), 1+np.sqrt(5)][self.gene1[1]+self.gene2[1]]
        self.velocity = velocity
        self.position = position
        self.color = {"m": "blue", "f": "pink"}[self.sex]
        self.width = rng.integers(1, 6)
        self.height = self.width * self.aspect_ratio
        self.child_num = 0
        self.f_facter = f_facter if f_facter is not None else rng.choice(("A", "B", "C", "D", "E"))
        self.m_facter = m_facter if m_facter is not None else rng.choice(np.arange(1, 6).astype(str))
        self.generation = generation

    def overlaps(self, other):
        # この長方形と他の長方形が重なっているかどうかを判定
        return not (self.position[0] + self.width < other.position[0] or
                    self.position[0] > other.position[0] + other.width or
                    self.position[1] + self.height < other.position[1] or
                    self.position[1] > other.position[1] + other.height)

    def get_overlapping_rectangles(self, rectangles):
        # この長方形と重なっている長方形のリストを返す
        return [rect for rect in rectangles if self.overlaps(rect) and rect is not self]
    
    def aging(self):
        self.age += 1

    def growth(self):
        self.width *= 1.05
        self.heigth = self.width * self.aspect_ratio
    
    def is_death(self):
        if self.age >= self.life:
            return True
        else:
            return False
    
    def is_opposite(self, other):
        if self.sex != other.sex:
            return True
        else:
            return False
    
    def courtship(self, other):
        return rng.choice([True, False], p=(0.4, 0.6))
    
    def reproduction(self, other):
        aspect_ratio = rng.choice([self.aspect_ratio, other.aspect_ratio])
        velocity = (self.velocity+other.velocity)/2
        position = (self.position+other.position)/2
        gene1, gene2, f_facter, m_facter = [None] * 4
        
        if self.sex == "m":
            gene1 = rng.choice([self.gene1, self.gene2])
            gene2 = rng.choice([other.gene1, other.gene2])
            f_facter = self.f_facter
            m_facter = other.m_facter              
        else:
            gene1 = rng.choice([other.gene1, other.gene2])
            gene2 = rng.choice([self.gene1, self.gene2])
            f_facter = other.f_facter
            m_facter = self.m_facter
        if rng.random() < 0.01:
            num = rng.integers(1, 9)
            if rng.random() < 0.5:
                gene1[num] = gene1[num]^1
            else:
                gene2[num] = gene2[num]^1
        if rng.random() < 0.01:
            num = rng.integers(1, 9)
            c1, c2 = gene1[num], gene2[num]
            gene1[num] = c2
            gene2[num] = c1
            
        child = Rectangle(aspect_ratio, velocity, position, gene1, gene2)
        child.generation += max(self.generation, other.generation) + 1
        self.child_num += 1
        other.child_num += 1
        return child

class Animation:
    def __init__(self, rectangles, width=200):
        self.rectangles = rectangles
        self.width = width
        self.height = width

    def add_rectangle(self, rectangle):
        self.rectangles.append(rectangle)

    def remove_rectangle(self, rectangle):
        self.rectangles.remove(rectangle)

    def create_animation(self):
        # gif画像のフレームを保存するディレクトリを作成
        os.makedirs('frames', exist_ok=True)

        # 各フレームを生成
        for t in range(366):
            fig = plt.figure(figsize=(6, 6))
            ax = fig.add_subplot(111)
            ax.set_title(f"{t}日後")

            # 長方形を描画
            for rect in self.rectangles:
                others = list({rect}^set(self.rectangles))
                overlapping = rect.get_overlapping_rectangles(others)
                opposites = [rect.is_opposite(o) for o in overlapping]
                oo_list = [r for r, j in zip(overlapping, opposites) if j]
                if rng.choice([True, False], p=(0.2, 0.8)):
                    #print(overlapping)
                    #print(oo_list)
                    pass
                if len(oo_list) > 0:
                    for o in oo_list:
                        if all([rect.courtship(o), len(self.rectangles)<=200]):
                            #print("born!")
                            self.add_rectangle(rect.reproduction(o))
                    
                rect.aging()
                rect.growth()
                if rect.is_death():
                    self.remove_rectangle(rect)
                if len(self.rectangles) == 0:
                    break
                ax.add_patch(patches.Rectangle(rect.position, width=rect.width, height=rect.height, color=rect.color, alpha=0.5))
                ax.text(*rect.position, str(rect.generation))

            # 長方形の位置を更新
            for rect in self.rectangles:
                rect.position += rect.velocity * rng.choice(np.linspace(-3, 3, 7), 2)
                # 長方形が画面外に出た場合は反対側から出てくるようにする
                rect.position %= self.width

            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)

            # フレームを保存
            plt.savefig(f'frames/frame{t:03d}.png')
            plt.close()

        # すべてのフレームを読み込み
        frames = [imageio.imread(f'frames/frame{i:03d}.png') for i in range(366)]

        # gifアニメーションを作成
        imageio.mimsave('animation.gif', frames)


def main():
    rects = [Rectangle(rng.choice([1, np.sqrt(2), (1+np.sqrt(5))/2, 1]), rng.random(2)*9.9-0.1, rng.integers(1, 99, 2).astype(float)) for _ in range(50)]
    facter0 = [r.f_facter + r.m_facter for r in rects]
    
    plt.hist(facter0, density=True)
    plt.xticks(rotation=45)
    plt.show()
    
    anime = Animation(rects)
    anime.create_animation()
    
    facter1 = [r.f_facter + r.m_facter for r in anime.rectangles]
    
    plt.hist(facter1, density=True)
    plt.xticks(rotation=45)
    plt.show()
    


if __name__ == "__main__":
    main()