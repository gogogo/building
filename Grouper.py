import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "../gogogo-hk"))
from gogogo.geo.LatLng import LatLng
from gogogo.geo.LatLngGroup import LatLngGroup


class Grouper:
	"""
	A simple points grouping algorithm (preprocessing)
	"""
	
	def __init__(self,radius=0.4,max_walking_distance=1.0):
		self.groups = []
		
		self.tgdi = radius
		self.threshold = max_walking_distance / 2
		
	def append(self,latlng):
		"""
			Append a point to groups
		@param latlng
		@type latlng gogogo.geo.LatLng
		"""
		target = None
		min = sys.maxint
		for g in self.groups:
			c = g.get_centroid()
			dist = c.distance(latlng)
			if dist < self.threshold:
				ng = g.dup()
				ng.append(latlng)
				if ng.get_radius() < self.threshold and ng.get_gdi() < self.tgdi:
					diff = ng.get_gdi() - g.get_gdi()
					if diff < min:
						min = diff
						target = g
		
		if target:
			target.append(latlng)
		else:
			self.groups.append(LatLngGroup([latlng]))

class GroupSwapOptimizer:
	"""
	Optimize the grouping result by swap points between groups
	"""
	
	def __init__(self,grouper):
		self.grouper = grouper
		
		#No. of swap performed
		self.swap_count = 0
	
	def process(self):
		groups = self.grouper.groups
		
		for g1 in groups:
			ops = []
			for pt in g1.pts:
				target = None
				distance = g1.get_centroid().distance(pt)
				
				for g2 in groups:
					if g1 != g2:
						new_distance  = g2.get_centroid().distance(pt)
						if new_distance < distance:
							distance = new_distance
							target = g2
				
				if target: #swap
					ops.append( (pt,target) )
					#g1.remove(pt)
					#target.append(pt)
					
			for o in ops:
				g1.remove(o[0])
				o[1].append(o[0])
				self.swap_count+=1
		
	#def process(self):
		#groups = self.grouper.groups
		
		#for g1 in groups:
			
			#gdi1 = g1.get_gdi()
			
			#for pt in g1.pts:
				#max_gain = -sys.maxint
				#target = None
				
				#ng1 = g1.dup()
				#ng1.remove(pt)
				
				#ngdi1 = ng1.get_gdi()
				
				#for g2 in groups:
					#if g1 != g2 and g2.get_centroid().distance(pt) < self.grouper.threshold:
						#gdi2 = g2.get_gdi()
						
						#ng2 = g2.dup()
						#ng2.append(pt)
						
						#ngdi2 = ng2.get_gdi()
						
						#diff = (gdi1 + gdi2 ) - (ngdi2 + ngdi1)
						#if diff > max_gain:
							#max_gain = diff
							#target = g2
				
				#if max_gain > 0: #swap
					#g1.remove(pt)
					#gdi1 = g1.get_gdi()
					#target.append(pt)		
					#self.swap_count+=1
				
