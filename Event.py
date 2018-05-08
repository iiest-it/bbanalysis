from Constant import Constant
from Moment import Moment
from Team import Team
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
from scipy.spatial import ConvexHull, Voronoi, voronoi_plot_2d
from matplotlib.collections import LineCollection, PolyCollection
import time
import sys

class Event:
    def __init__(self, event, analytics=""):
        moments = event['moments']
        self.analytics=analytics
        self.moments = [Moment(moment) for moment in moments]
        home_players = event['home']['players']
        guest_players = event['visitor']['players']
        players = home_players + guest_players
        player_ids = [player['playerid'] for player in players]
        player_names = [" ".join([player['firstname'],
                        player['lastname']]) for player in players]
        player_jerseys = [player['jersey'] for player in players]
        values = list(zip(player_names, player_jerseys))
        self.player_ids_dict = dict(zip(player_ids, values))
        self.pause=False

    def press(self, event):
        if event.key=='p':
            if self.pause:
                self.anim.event_source.start()
            else:
                self.anim.event_source.stop()
            self.pause^=True
        elif event.key=='v':
            self.analytics='voronoi'
        elif event.key=='h':
            self.analytics='hull'
        elif event.key=='b':
            self.analytics=''

    def draw_voronoi(self, points, lc, poly):
        vor = Voronoi(points)
        poly_vert = []
        for reg in vor.point_region:
            vertices = vor.regions[reg]
            if all(v >= 0 for v in vertices):
                polyv = [vor.vertices[v] for v in vertices]
                poly_vert.append(polyv)
        poly.set_verts(poly_vert)
        poly.set_alpha(0.1)
        ptp_bound = vor.points.ptp(axis=0)
        line_segments = []
        center = vor.points.mean(axis=0)
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0]
                t = vor.points[pointidx[1]] - vor.points[pointidx[0]]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = vor.points[pointidx].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[i] + direction * ptp_bound.max()
                line_segments.append([(vor.vertices[i, 0], vor.vertices[i, 1]),
                                    (far_point[0], far_point[1])])
        lc.set_segments(line_segments)

    def update_radius(self, i, player_circles, ball_circle, home_hull, guest_hull, lc, poly, annotations, all_text):
        moment = self.moments[i]
        for j, circle in enumerate(player_circles):
            circle.center = moment.players[j].x, moment.players[j].y
            annotations[j].set_position(circle.center)
            clock_test = 'Quarter {:d}\n {:02d}:{:02d}\n {:03.1f}'.format(
                         moment.quarter,
                         int(moment.game_clock) % 3600 // 60,
                         int(moment.game_clock) % 60,
                         moment.shot_clock)
            all_text['clock_info'].set_text(clock_test)
        ball_circle.center = moment.ball.x, moment.ball.y
        ball_circle.radius = moment.ball.radius / Constant.NORMALIZATION_COEF
        home_points=[p.center for p in player_circles[:5]]
        guest_points=[p.center for p in player_circles[5:]]      
        if self.analytics=="hull":
            lc.set_verts([])
            poly.set_verts([])
            home_hull_points=ConvexHull(home_points)
            guest_hull_points=ConvexHull(guest_points)
            home_hull.set_xy([home_points[i] for i in home_hull_points.vertices])
            guest_hull.set_xy([guest_points[i] for i in guest_hull_points.vertices])
            all_text['home_hull'].set_text(str(int(home_hull_points.volume)))
            all_text['guest_hull'].set_text(str(int(guest_hull_points.volume)))
        elif self.analytics=="voronoi":
            home_hull.set_xy([[0, 0]])
            guest_hull.set_xy([[0, 0]])
            all_text['home_hull'].set_text('')
            all_text['guest_hull'].set_text('')
            self.draw_voronoi(home_points+guest_points, lc, poly)
        else:
            home_hull.set_xy([[0, 0]])
            guest_hull.set_xy([[0, 0]])
            lc.set_verts([])
            poly.set_verts([])
        return player_circles, ball_circle

    def show(self):
        ax = plt.axes(xlim=(Constant.X_MIN,
                            Constant.X_MAX),
                      ylim=(Constant.Y_MIN,
                            Constant.Y_MAX))
        ax.axis('off')
        fig = plt.gcf()
        ax.grid(False)
        start_moment = self.moments[0]
        player_dict = self.player_ids_dict
        sorted_players = sorted(start_moment.players, key=lambda player: player.team.id)
        home_player = sorted_players[0]
        guest_player = sorted_players[5]
        all_text={}
        all_text['clock_info'] = ax.annotate('', xy=[Constant.X_CENTER, Constant.Y_CENTER],
                                 color='black', horizontalalignment='center',
                                   verticalalignment='center')
        all_text['home_hull']=ax.annotate('', xy=[40, 2],
                                 color=home_player.color, horizontalalignment='center',
                                   verticalalignment='center')
        all_text['guest_hull']=ax.annotate('', xy=[57, 2],
                                 color=guest_player.color, horizontalalignment='center',
                                   verticalalignment='center')

        annotations = [ax.annotate(self.player_ids_dict[player.id][1], xy=[0, 0], color='w',
                                   horizontalalignment='center',
                                   verticalalignment='center', fontweight='bold')
                       for player in start_moment.players]
        # column_labels = tuple([home_player.team.name, guest_player.team.name])
        # column_colours = tuple([home_player.team.color, guest_player.team.color])
        # cell_colours = [column_colours for _ in range(5)]
        # home_players = [' #'.join([player_dict[player.id][0], player_dict[player.id][1]]) for player in sorted_players[:5]]
        # guest_players = [' #'.join([player_dict[player.id][0], player_dict[player.id][1]]) for player in sorted_players[5:]]
        # players_data = list(zip(home_players, guest_players))
        # table = plt.table(cellText=players_data,
        #                       colLabels=column_labels,
        #                       colColours=column_colours,
        #                       colWidths=[Constant.COL_WIDTH, Constant.COL_WIDTH],
        #                       loc='bottom',
        #                       cellColours=cell_colours,
        #                       fontsize=Constant.FONTSIZE,
        #                       cellLoc='center')
        # table.scale(1, Constant.SCALE)
        # table_cells = table.properties()['child_artists']
        # for cell in table_cells:
        #     cell._text.set_color('white')
        player_circles = [plt.Circle((0, 0), Constant.PLAYER_CIRCLE_SIZE, color=player.color)
                          for player in start_moment.players]
        ball_circle = plt.Circle((0, 0), Constant.PLAYER_CIRCLE_SIZE,
                                 color=start_moment.ball.color)
        home_hull=plt.Polygon([[0, 0]], closed=True, color=home_player.color, alpha=0.5)
        guest_hull=plt.Polygon([[0, 0]], closed=True, color=guest_player.color, alpha=0.5)
        lc = LineCollection([], colors='k', lw=1.0, linestyle='dashed')
        poly = PolyCollection([], edgecolors='k')
        for circle in player_circles:
            ax.add_patch(circle)
        ax.add_patch(ball_circle)
        ax.add_patch(home_hull)
        ax.add_patch(guest_hull)
        ax.add_collection(lc)        
        ax.add_collection(poly)
        fig.canvas.mpl_connect('key_press_event', self.press)
        self.anim = animation.FuncAnimation(
                         fig, self.update_radius,
                         fargs=(player_circles, ball_circle, home_hull, guest_hull, lc, poly, annotations, all_text),
                         frames=len(self.moments), interval=Constant.INTERVAL)
        court = plt.imread("court.png")
        plt.imshow(court, zorder=0, extent=[Constant.X_MIN, Constant.X_MAX - Constant.DIFF,
                                            Constant.Y_MAX, Constant.Y_MIN])
        plt.show()
