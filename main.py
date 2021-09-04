

def get_length(c_1, c_2):
	return math.sqrt((c_1[0] - c_2[0]) ** 2 + (c_1[1] - c_2[1]) ** 2)

class particle:
	def collision(self, collision_grid):
		for i in range(len(collision_grid)):
			other_particle = self.p_list[i]
			distance = get_length([self.x, self.y], [other_particle.x, other_particle.y])
			if distance < self.radius + other_particle.radius and other_particle != self:
				diffx = self.x - other_particle.x
				diffy = self.y - other_particle.y
				try:
					difference = ((self.radius + other_particle.radius) - distance) / distance 
					self.x += diffx * 0.5 * difference
					self.y += diffy * 0.5 * difference
					self.vx *= (-1)
					self.vy *= (-1)
				except Exception as e:
					pass

	def tick(self, TPS, decay = 0.5):
		ix = self.x - self.px
		iy = self.y - self.py

		self.px = self.x
		self.py = self.y

		self.x += ix + self.vx
		self.y += iy + self.vy

		self.vx *= decay
		self.vy *= decay

	def __init__(self, x, y, color, particle_list):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.px = x
		self.py = y
		self.radius = 10
		self.color = color
		self.id = len(particle_list)
		self.p_list = particle_list
		particle_list.append(self)

class link:
	def tick(self):
		distance = get_length([self.p1.x, self.p1.y], [self.p2.x, self.p2.y])
		diffx = self.p1.x - self.p2.x
		diffy = self.p1.y - self.p2.y
		difference = (self.length - distance) / distance

		if distance > self.length * 2: self.link_list.remove(self)

		self.p1.x += diffx * 0.4 * difference
		self.p1.y += diffy * 0.4 * difference

		self.p2.x -= diffx * 0.4 * difference
		self.p2.y -= diffy * 0.4 * difference


	def __init__(self, p1, p2, link_list):
		self.p1 = p1
		self.p2 = p2
		self.color = (0, 0, 0)
		self.length = get_length([p1.x, p1.y], [p2.x, p2.y]) 
		self.link_list = link_list
		link_list.append(self)

class container:
	def add_link(self, p1, p2):
		return link(p1, p2, self.link_list)

	def add_particle(self, x, y, color):
		return particle(x, y, color, self.all_particles)

	def tick(self, TPS):
		ctl = []
		ctr = []
		cdl = []
		cdr = []

		if len(self.all_particles) > 0:
			cx = sum(self.all_particles[i].x for i in range(len(self.all_particles))) / len(self.all_particles)
			cy = sum(self.all_particles[i].y for i in range(len(self.all_particles))) / len(self.all_particles)

		for p in self.all_particles:
			p.y += self.gravity / TPS
			p.tick(TPS, 1)

			if p.y + p.radius > self.y + self.h:
				p.y = self.y + self.h - p.radius
				p.py = p.y
				p.vy = 0
			elif p.y < self.y:
				p.y = self.y + p.radius
				p.py = p.y
				p.vy = 0
			if p.x + p.radius > self.x + self.w:
				p.x = self.x + self.w - p.radius
				p.px = p.x
				p.vx = 0
			elif p.x < self.x:
				p.x = self.x + p.radius
				p.px = p.x
				p.vx = 0

			if p.x + p.radius > cx:
				if p.y + p.radius > cy:
					ctl.append(p.id)
				elif p.y - p.radius < cy:
					cdr.append(p.id)
			elif p.x - p.radius < cx:
				if p.y + p.radius > cy:
					cdl.append(p.id)
				elif p.y - p.radius < cy:
					ctr.append(p.id)


		c_grid = [ctl, ctr, cdl, cdr]
		[[p.collision(grid) if p.id in grid else None for grid in c_grid] for p in self.all_particles]

		for l in self.link_list:
			l.tick()



	def display(self, display, scroll, zoom_percent):
		pygame.draw.rect(display, self.border_color, ((self.x + scroll[0] - self.border_size / 2) * zoom_percent, (self.y + scroll[1] - self.border_size / 2) * zoom_percent, (self.w + self.border_size) * zoom_percent, (self.h + self.border_size) * zoom_percent))
		pygame.draw.rect(display, self.BG, ((self.x + scroll[0]) * zoom_percent, (self.y + scroll[1]) * zoom_percent, self.w * zoom_percent, round(self.h * zoom_percent)))

		for l in self.link_list:
			pygame.draw.line(display, l.color, ((l.p1.x + scroll[0]) * zoom_percent, (l.p1.y + scroll[1]) * zoom_percent), ((l.p2.x + scroll[0]) * zoom_percent, (l.p2.y + scroll[1]) * zoom_percent), round(10 * zoom_percent))

		for p in self.all_particles:
			pygame.draw.circle(display, p.color, ((p.x + scroll[0]) * zoom_percent, (p.y + scroll[1]) * zoom_percent), round(p.radius * zoom_percent))

	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.border_size = 10
		self.BG = (150, 150, 150)
		self.border_color = (255, 255, 255)
		self.center = (x + w / 2, y + h / 2)
		self.gravity = 9
		self.link_list = []
		self.all_particles = []

def main():
	WIN_SIZE = (640, 640)
	BG = (0, 0, 0)
	TPS = 60
	title = "Particle_Sim v_2"
	display = pygame.display.set_mode(WIN_SIZE)
	pygame.display.set_caption(title)
	clock = pygame.time.Clock()

	inputs = [False, False, False, False]
	click = [False, False, False]
	scroll = [0, 0]
	scroll_speed = 5
	zoom_percent = 1
	running = True

	c = container(0, 0, 640, 640)

	jelly = []
	d = 40
	for y in range(6):
		for x in range(10):
			jelly.append(c.add_particle(x * d + 100, y * d + 100, (255, 255, 255)))

	for p1 in jelly:
		for p2 in jelly:
			if p1 != p2:
				if get_length([p1.x, p1.y], [p2.x, p2.y]) < d * 1.5:
					c.add_link(p1, p2)


	while running:
		clock.tick(TPS)
		mx, my = pygame.mouse.get_pos()
		if zoom_percent < 0.1:
			zoom_percent = 0.1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				running = False

			#Click Event
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					click[0] = True
				if event.button == 2:
					click[1] = True
				if event.button == 3:
					click[2] = True

			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					click[0] = False
				if event.button == 2:
					click[1] = False
				if event.button == 3:
					click[2] = False

			#Key Event
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_w:
					inputs[0] = True
				if event.key == pygame.K_a:
					inputs[1] = True
				if event.key == pygame.K_s:
					inputs[2] = True 
				if event.key == pygame.K_d:
					inputs[3] = True
				if event.key == pygame.K_i:
					zoom_percent -= 0.1
				if event.key == pygame.K_o:
					zoom_percent += 0.1

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_w:
					inputs[0] = False
				if event.key == pygame.K_a:
					inputs[1] = False
				if event.key == pygame.K_s:
					inputs[2] = False
				if event.key == pygame.K_d:
					inputs[3] = False

		if running == False: break

		if inputs[0]: scroll[1] += scroll_speed
		if inputs[1]: scroll[0] += scroll_speed
		if inputs[2]: scroll[1] -= scroll_speed
		if inputs[3]: scroll[0] -= scroll_speed

		c.tick(TPS)
		display.fill(BG)
		c.display(display, scroll, zoom_percent)
		pygame.display.update()

if __name__ == "__main__":
	import pygame, math, random, array
	pygame.init()
	main()