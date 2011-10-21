from BuildStructure.Fragment import Fragment, RING66
frag = Fragment("quinazoline", [
	("C", (-9.41957, -3.85682, -0.0235259)),
	("H", (-10.3543, -3.30185, -0.0234557)),
	("C", (-8.20163, -3.18241, -0.0234406)),
	("H", (-8.19189, -2.09507, -0.0234369)),
	("C", (-6.99506, -3.91041, -0.0232992)),
	("C", (-5.73983, -3.31732, -0.0230553)),
	("H", (-5.62603, -2.23691, -0.0230526)),
	("N", (-4.58182, -4.00399, -0.0228608)),
	("C", (-4.70967, -5.33762, -0.0228563)),
	("H", (-3.79329, -5.91797, -0.0225895)),
	("N", (-5.8618, -6.02718, -0.0231356)),
	("C", (-6.99506, -5.31058, -0.0232992)),
	("C", (-8.22511, -5.95733, -0.0234692)),
	("H", (-8.24581, -7.04486, -0.0235351)),
	("C", (-9.43157, -5.24773, -0.0235383)),
	("H", (-10.3758, -5.78665, -0.0235681)),
	], [
	((0,1), None),
	((0,2), None),
	((2,3), None),
	((4,2), (-8.21133, -4.57755, -0.0234287)),
	((4,5), None),
	((5,6), None),
	((5,7), (-5.81387, -4.65118, -0.0230844)),
	((7,8), None),
	((8,9), None),
	((8,10), (-5.81387, -4.65118, -0.0230844)),
	((11,10), None),
	((11,4), None),
	((12,11), (-8.21133, -4.57755, -0.0234287)),
	((12,13), None),
	((14,12), None),
	((14,15), None),
	((0,14), (-8.21133, -4.57755, -0.0234287)),
	])

fragInfo = [RING66, frag]