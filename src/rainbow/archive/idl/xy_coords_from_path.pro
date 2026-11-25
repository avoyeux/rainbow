function xy_coords_from_path, p1, p2, nl=nl, nt=nt

	if ~keyword_set(nl) then nl = 1000
	if ~keyword_set(nt) then nt = 50

	nx1 = p1.xmax - p1.xmin + 1
	x1 = p1.xmin + dindgen(nx1)
	y1 = dblarr(nx1)
	degree1 = n_elements(*p1.coeffs)-1
	for i=0, degree1 do y1 = y1 + (*p1.coeffs)[i]*x1^double(i)

	length1 = dblarr(nx1)
	length1[1] = sqrt((x1[1] - x1[0])^2.0d + (y1[1] - y1[0])^2.0d)
	for i=2, nx1-1 do length1[i] = crvlength(x1[0:i], y1[0:i], /double)
	length1 = length1 / max(length1)

  nx2 = p2.xmax - p2.xmin + 1
  x2 = p2.xmin + dindgen(nx2)
  y2 = dblarr(nx2)
  degree2 = n_elements(*p2.coeffs)-1
  for i=0, degree2 do y2 = y2 + (*p2.coeffs)[i]*x2^double(i)

  length2 = dblarr(nx2)
  length2[1] = sqrt((x2[1] - x2[0])^2.0d + (y2[1] - y2[0])^2.0d)
  for i=2, nx2-1 do length2[i] = crvlength(x2[0:i], y2[0:i], /double)
	length2 = length2 / max(length2)

	l = dindgen(nl)/(nl-1)
	nx1 = interpol(x1, length1, l)
	nx2 = interpol(x2, length2, l)
	ny1 = dblarr(nl)
        for i=0, degree1 do ny1 = ny1 + (*p1.coeffs)[i]*nx1^double(i)
	ny2 = dblarr(nl)
	for i=0, degree2 do ny2 = ny2 + (*p2.coeffs)[i]*nx2^double(i)

	xidx = dindgen(nl) # replicate(1.0d, nt)
	yidx = replicate(1.0d, nl) # (dindgen(nt)/(nt-1))

	x = interpolate([[nx1], [nx2]], xidx, yidx)
	y = interpolate([[ny1], [ny2]], xidx, yidx)

	return, [[[x]], [[y]]]

end
