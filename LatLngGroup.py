from LatLng import LatLng
import copy

class LatLngGroup:
	
	def __init__ (self , pts = []):
		self.pts = pts
		self.dirty = True
	
	def get_centroid(self):	
		if self.dirty:
			self._calc()
		return self.centroid
		
	def get_gdi(self):
		"""
			Get Group Distance Index (average)
		"""
		if self.dirty:
			self._calc()
		return self.gdi
		
	def get_radius(self):
		if self.dirty:
			self._calc()
		return self.radius
	
	def append(self,pt):
		self.pts.append(pt)
		self.dirty = True
		
	def remove(self,pt):
		self.pts.remove(pt)
		self.dirty = True
		
	def dup(self):
		"""
			Duplicate a copy of this group exclude the contained
			points. 
		"""
		object = copy.copy(self)
		object.pts = self.pts[:]
		object.dirty = True
		return object
	
	def __str__(self):
		pts_str = []
		
		for p in self.pts:
			pts_str.append(str(p))
		
		return ".".join(pts_str)
		
	def _calc(self):
		"""
			Calculate centroid and group distance index
		"""
		
		self.centroid = LatLng()
		self.gdi = 0
		self.radius = 0
		
		n = len(self.pts)
		if n > 0:
			self.radius = 0
			lat = 0
			lng = 0
			for pt in self.pts:
				lat += pt.lat
				lng += pt.lng
#				self.centroid += pt
				
			self.centroid = LatLng(lat / n , lng / n)
			
			for pt in self.pts:
				dist = self.centroid.distance(pt)
				self.gdi += dist
				if dist > self.radius :
					self.radius = dist
			
			self.gdi /= n

		self.dirty = False	

if __name__ == "__main__":
	pts = [LatLng(0,0) , LatLng(10,0),LatLng(0,10),LatLng(10,10)]
	
	group = LatLngGroup(pts)
	
	print group.get_centroid()
	
	pts = [LatLng(22.252195,113.866299)]

	group = LatLngGroup(pts)
	
	print group.get_centroid()
